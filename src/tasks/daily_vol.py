#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

from src.tasks.wh_vol_parser import DailyVol
from ..dao.vol import DailyVolDAO


def wh_vol():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../../db/house.db"])
    dao = DailyVolDAO(datetime.today(), db_path)
    parser = DailyVol(dao)
    parser.parse()

