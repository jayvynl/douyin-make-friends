import atexit
import itertools
import logging
import math
import random
import subprocess
import time
import typing

from appium import webdriver
from selenium.common import exceptions

import save
import settings
from logger import get_logger


def shutdown(cancel: bool = False) -> None:
    if cancel:
        subprocess.run(['shutdown', '/a'])
    else:
        subprocess.run(['shutdown', '/s'])


class DouYin(object):
    def __init__(self, reset: bool = False):
        self.logger = get_logger()
        self.desired_caps = {
            'platformName': 'Android',
            'platformVersion': '7.1.1',
            'deviceName': 'OnePlus3T',
            'appPackage': 'com.ss.android.ugc.aweme',
            'appActivity': '.splash.SplashActivity',
            'noReset': 'False' if reset else 'True',
            # 'unicodeKeyboard': 'True',
            'automationName': 'uiautomator2'
        }
        self.server = 'http://localhost:4723/wd/hub'
        self.driver = webdriver.Remote(self.server, desired_capabilities=self.desired_caps)
        self.driver.implicitly_wait(15)
        window_size = self.driver.get_window_size()
        self.width = window_size['width']
        self.height = window_size['height']
        if not (self.width == 720 and self.height == 1280):
            raise Exception('请将手机分辨率设置为1280 * 720')
        if reset:  # 如果清空历史数据，需要点击电话权限等按钮。
            time.sleep(5)
            self.click('com.ss.android.ugc.aweme:id/b9s')
            self.click('com.android.packageinstaller:id/permission_deny_button')
            self.click('com.android.packageinstaller:id/permission_deny_button')

    def close(self) -> None:
        self.driver.close_app()

    def swipe(self) -> None:
        self.driver.swipe(
            360, 960,
            360, 640,
        )

    def tap(self, point) -> None:
        self.driver.tap([point])

    def click(self, element_id: str, retry: int = 2) -> None:
        while retry > 0:
            try:
                self.driver.find_element_by_id(element_id).click()
            except exceptions.NoSuchElementException:
                retry -= 1
            else:
                return
        raise exceptions.NoSuchElementException()

    def active_search(self) -> None:
        self.click('com.ss.android.ugc.aweme:id/doj')
        time.sleep(4)

    def search(self, text: str, cat: str = 'all') -> None:
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/aia').send_keys(text)
        time.sleep(2)
        self.click('com.ss.android.ugc.aweme:id/jye')
        time.sleep(2)
        if cat == 'video':
            self.driver.find_elements_by_id('android:id/text1')[1].click()
        elif cat == 'user':
            self.driver.find_elements_by_id('android:id/text1')[2].click()
        elif cat == 'live':
            self.driver.find_elements_by_id('android:id/text1')[5].click()

    def back_home(self) -> None:
        while True:
            try:
                self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/cdn')
            except exceptions.NoSuchElementException:
                self.driver.back()
            else:
                break

    def enter_live(self) -> None:
        self.back_home()
        self.click('com.ss.android.ugc.aweme:id/ck8')

    def get_audiences(self, history_users: typing.Set[str], collected_users: typing.List[str]) -> None:
        """
        获取直播间观众列表
        :param history_users: 所有历史采集的用户
        :param collected_users: 此次任务采集的用户
        :return:
        """
        try:
            self.tap((self.width / 2 + random.randint(-10, 10), self.height / 2 + random.randint(-10, 10)))
        except exceptions.InvalidElementStateException:
            pass
        try:
            viewers = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/g1l')
            num_viewers = int(viewers.text)
            if num_viewers > 200:  # 最多只展示200个用户
                num_viewers = 200
            viewers.click()  # 进入观众列表

            try:
                for _ in range(math.ceil(num_viewers / 7)):
                    for audience in self.driver.find_elements_by_id('com.ss.android.ugc.aweme:id/d4l'):
                        try:
                            audience.click()  # 进入观众菜单
                        except exceptions.StaleElementReferenceException:  # 观众列表已更新
                            continue
                        try:
                            self.click('com.ss.android.ugc.aweme:id/d2t')  # 进入观众主页
                        except exceptions.NoSuchElementException:  # 自己的菜单中没有主页按钮
                            self.driver.back()
                            continue
                        idx = self.get_user_profile()['id']
                        if idx not in history_users:
                            history_users.add(idx)
                            collected_users.append(idx)
                        self.driver.back()  # 退出观众主页
                        self.driver.back()  # 退出观众菜单
                    self.driver.swipe(360, 1180, 360, 491, duration=3000)  # 滑动观众列表
            except exceptions.NoSuchElementException:  # 主播设置不允许查看观众信息
                pass
        except exceptions.StaleElementReferenceException:  # 直播已结束
            return
        self.driver.back()  # 退出观众列表

    def get_commenter(self,
                      history_users: typing.Set[str],
                      collected_users: typing.List[str],
                      history_videos: typing.Set[str]) -> None:
        """
        获取视频评论者信息
        :param history_users: 所有历史采集的用户
        :param collected_users: 此次任务采集的用户
        :param history_videos: 所有历史采集的视频
        """
        video_name = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/a9_').text
        if video_name in history_videos:
            return
        else:
            history_videos.add(video_name)
            save.save_video(video_name)
        num_comments_text = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/b3u').text
        if num_comments_text.endswith('w'):
            num_comments = int(float(num_comments_text) * 10000)
        else:
            num_comments = int(num_comments_text)
        self.click('com.ss.android.ugc.aweme:id/b46')  # 点击打开评论列表
        while num_comments > 0:
            for user_icon in self.driver.find_elements_by_id('com.ss.android.ugc.aweme:id/jv'):
                user_icon.click()  # 进入用户主页
                idx = self.get_user_profile()['id']
                if idx not in history_users:
                    history_users.add(idx)
                    collected_users.append(idx)
                num_comments -= 1
                self.driver.back()  # 退出用户主页
            self.driver.swipe(360, 1200, 360, 530, duration=3000)  # 滑动评论列表
        self.driver.back()  # 退出评论列表

    def get_user_profile(self) -> typing.Dict[str, str]:
        return {
            'name': self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/fvf').text,
            'id': self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/kcq').text[4:],  # 抖音号：126540011
            'zan': self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/bmk').text,
            'following': self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/co9').text,
            'followed': self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/co3').text
        }

    def send_message(self, message: str, userid: str, cat: typing.Optional[str] = None) -> None:
        self.search(userid, cat=cat)
        self.click('com.ss.android.ugc.aweme:id/ado')  # 点击第一个搜索结果，进入用户主页
        # time.sleep(2)
        # self.tap((self.width / 2, 240))
        try:
            self.click('com.ss.android.ugc.aweme:id/gq1')  # 点击关注
        except exceptions.NoSuchElementException:
            self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/cnj')  # 取消关注按钮
            self.click('com.ss.android.ugc.aweme:id/l6')  # 点击返回，退出用户主页，回到搜索界面
            return
        try:
            self.click('com.ss.android.ugc.aweme:id/ivf')  # 点击右上角更多
        except exceptions.NoSuchElementException:  # 用户设置了私密账户
            time.sleep(1)
            self.driver.back()
            time.sleep(1)
        self.click('com.ss.android.ugc.aweme:id/hr9')  # 点击发私信，进入对话界面
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/fkc').send_keys(message)  # 对话框输入消息
        try:
            self.click('com.ss.android.ugc.aweme:id/hqm')  # 点击发送
        except exceptions.NoSuchElementException:
            self.click('com.ss.android.ugc.aweme:id/hql')
        self.click('com.ss.android.ugc.aweme:id/eir')  # 点击返回，退出对话界面
        time.sleep(2)
        self.click('com.ss.android.ugc.aweme:id/l6')  # 点击返回，退出用户主页，回到搜索界面

    def make_friends(
            self,
            message: typing.Union[str, typing.Sequence[str]],
            users: typing.List[str],
            sent_users: typing.List[str],
            max_users: int = 100,
            wait: int = 10) -> None:
        """
        发送交朋友私信
        :param message: 消息列表
        :param users: 待发送用户
        :param sent_users: 已发送的用户
        :param max_users: 最多发送的用户
        :param wait: 每个用户之间的发送间隔
        :return:
        """
        self.active_search()
        if isinstance(message, str):
            messages = [message]
        else:
            messages = message
        searched = False
        for message in itertools.cycle(messages):
            try:
                user = users.pop()
            except IndexError:
                break

            try:
                if searched:
                    self.send_message(message, user)
                else:
                    self.send_message(message, user, cat='user')
                    searched = True
            except Exception:
                self.logger.exception(f'send message to {user} failed.')
                raise
            time.sleep(wait)
            self.logger.info(f'send message to {user}.')
            sent_users.append(user)
            if len(sent_users) >= max_users:
                break

    def find_friends_live(
            self,
            history_users: typing.Set[str],
            collected_users: typing.List[str],
            key_words: str,
            max_users: int = 1000) -> None:
        """
        从直播间找朋友
        :param history_users: 所有历史采集的用户
        :param collected_users: 此次任务采集的用户
        :param key_words: 直播间关键词
        :param max_users: 找朋友数量
        :return:
        """
        self.active_search()
        self.search(key_words, cat='live')
        time.sleep(5)
        self.tap((self.width / 2 + random.randint(-10, 10), self.height / 2 + random.randint(-10, 10)))
        time.sleep(5)
        # self.click('com.ss.android.ugc.aweme:id/kho')
        while True:
            self.get_audiences(history_users, collected_users)
            if len(collected_users) >= max_users:
                return
            self.swipe()

    def find_friends_video(
            self,
            history_users: typing.Set[str],
            collected_users: typing.List[str],
            key_words: str,
            max_users: int = 1000) -> None:
        """
        从视频找朋友
        :param history_users: 所有历史采集的用户
        :param collected_users: 此次任务采集的用户
        :param key_words: 直播间关键词
        :param max_users: 找朋友数量
        :return:
        """
        self.active_search()
        self.search(key_words, cat='video')
        time.sleep(5)
        self.tap((self.width / 4 + random.randint(-10, 10), self.height / 2 + random.randint(-10, 10)))
        time.sleep(5)
        history_videos = set(save.videos())
        while True:
            self.get_commenter(history_users, collected_users, history_videos)
            if len(collected_users) >= max_users:
                return
            self.swipe()


def save_make(log: logging.Logger, users: typing.Sequence[str]):
    save.update(users)
    save.conn.close()
    log.info(f'{len(users)} users sent to.')


def save_find(log: logging.Logger, users: typing.Sequence[str]):
    save.save_user(users)
    save.conn.close()
    log.info(f'{len(users)} users collected.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='抖音交朋友')
    parser.add_argument('job', nargs='?', default='make',
                        choices=['make', 'findlive', 'findvideo', 'noshut'],
                        help='make: 交朋友 findlive: 直播间找朋友 findvideo: 视频找朋友 noshut: 取消关机')
    parser.add_argument('--count', '-c', type=int, help='交朋友或找朋友的数量')
    parser.add_argument('--keyword', '-k', help='朋友关键词')
    parser.add_argument('--shutdown', '-s', help='任务完成后关机', action='store_true')
    args = parser.parse_args()
    logger = get_logger()
    if args.job == 'make':
        users_list = list(save.users(False))
        sent_users_list = []
        atexit.register(save_make, logger, sent_users_list)
        while True:
            try:
                c = DouYin(reset=False)
                c.make_friends(
                    settings.MESSAGES,
                    users_list,
                    sent_users_list,
                    args.count or 100,
                    5
                )
            except Exception:
                logger.exception('')
            else:
                break
    elif args.job == 'findlive' or args.job == 'findvideo':
        history_users_set = set(save.users())
        collected_users_list = []
        atexit.register(save_find, logger, collected_users_list)
        while True:
            try:
                c = DouYin(reset=False)
                if args.job == 'findlive':
                    c.find_friends_live(
                        history_users_set,
                        collected_users_list,
                        args.keyword or settings.KEYWORD,
                        args.count or 1000
                    )
                else:
                    c.find_friends_video(
                        history_users_set,
                        collected_users_list,
                        args.keyword or settings.KEYWORD,
                        args.count or 1000
                    )
            except Exception:
                logger.exception('')
            else:
                break
    elif args.job == 'noshut':
        shutdown(cancel=True)
    if args.shutdown:
        shutdown()
