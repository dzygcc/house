#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.handlers
import os
import logging

LOG_FILE = "".join([os.path.dirname(os.path.abspath(__file__)), "/../../logs/stdout.log"])
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=5)
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)      # 实例化formatter
handler.setFormatter(formatter)         # 为handler添加formatter
logger = logging.getLogger("+")   # 获取名为tst的logger
logger.addHandler(handler)        # 为logger添加handler
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
