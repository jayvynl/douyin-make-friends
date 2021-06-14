import logging
import logging.config

import settings


def get_logger():
    logging.config.dictConfig(settings.LOG_CONFIG)
    return logging.getLogger('douyin')
