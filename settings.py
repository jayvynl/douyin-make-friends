import os.path

BASE_DIR = os.path.dirname(__file__)

# sqlite数据库文件路径
DB_FILE = os.path.join(BASE_DIR, 'douyin.db')

# 日志设置
LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'filename': os.path.join(BASE_DIR, 'douyin.log'),
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'simple',
        }
    },
    'loggers': {
        'douyin': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    }
}

# 要发送的消息列表，依次循环使用这些消息
MESSAGES = [
    'test，交个朋友！',
]
# 朋友关键词
KEYWORD = '妹妹'

try:
    from local_settings import *
except ImportError:
    pass
