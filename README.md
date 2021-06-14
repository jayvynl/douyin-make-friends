# 抖音交朋友

本项目使用Appium模拟了抖音APP上寻找用户并私信交朋友的过程.

**注意：**
1. 本项目仅供个人学习使用，请勿用于其他用途，否则一切后果由使用者自负.
2. 本项目对抖音 version14.7.1测试通过，无法在较新版本抖音使用.
3. 本项目在Windows 10, Python 3.9.1测试通过, 理论上可以在Python >= 3.5上运行, 但是没有试过.
4. 本项目任存在一些BUG, 功能也有待完善, 不过作者不保证一定会进行维护.


## 安装

1. 安装Appium参考[Appium环境搭建超详细教程](https://zhuanlan.zhihu.5com/p/49193525).
2. 下载本项目代码, `git clone https://github.com/jayvynl/douyin-make-friends`.
3. 安装Appium Python Client, `pip install Appium-Python-Client`.


## 使用

1. 打开模拟器或连接手机, 如果是交朋友, 需要确保预先登录抖音, 找朋友可以不用登录.
2. adb连接设备.
3. 打开Appium服务器.
4. `python main.py make`交朋友, `python main.py findlive`或`python main.py findvideo`找朋友.

有一些选项可以通过 `python main.py --help` 进行查看:

```
usage: main.py [-h] [--count COUNT] [--keyword KEYWORD] [--shutdown] [{make,findlive,findvideo,noshut}]

抖音交朋友

positional arguments:
  {make,findlive,findvideo,noshut}
                        make: 交朋友 findlive: 直播间找朋友 findvideo: 视频找朋友 noshut: 取消关机

optional arguments:
  -h, --help            show this help message and exit
  --count COUNT, -c COUNT
                        交朋友或找朋友的数量
  --keyword KEYWORD, -k KEYWORD
                        朋友关键词
  --shutdown, -s        任务完成后关机
```


## 设置

设置项都放在 `settings.py` 文件中，如果需要修改设置项，请新建 `local_settings.py`，并将需要修改的设置项放到 `local_settings.py` 文件里.

选项：

### MESSAGES

消息列表，存放需要发送的一组消息，对每个用户发送其中的一条消息，下个用户发送下一条，如果达到消息列表尾部，则重新从第一条消息开始。

### KEYWORD

找朋友所使用的关键字，如果不想每次都在命令行输入关键字，可以设置这个选项。
