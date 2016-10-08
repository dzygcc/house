#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
from datetime import datetime

sys.path.append(".")
sys.path.append("..")
from src.tasks.sh_vol import ShanghaiVol
from src.tasks.draw_image import VolDataGenerator, VolImgProducer, LijiaPriceTrendsGenerator
from src.tasks.bj_gov import BeijingGov
from src.dao.lianjia import LianjiaDAO
from src.parser.lianjia import Lianjia
from src.dao.hz import HangZhouDAO
from src.tasks.wh_vol_parser import DailyVol
from src.tasks.hz_gov import HangzhouGov
from src.dao.vol import DailyVolDAO
from src.tasks.hz_vol import HangZhouVol

if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../db/house.db"])
    update_hour = 0
    while True:
        cur_datetime = datetime.today()
        if abs(cur_datetime.hour - update_hour) < 5:
            time.sleep(30 * 60)
            continue
        dv_dao = DailyVolDAO(db_path)
        ljdao = LianjiaDAO(cur_datetime, db_path)
        if 0 <= cur_datetime.hour < 5 or update_hour == 0:
            vol_data = VolDataGenerator(dv_dao)
            price_tool = LijiaPriceTrendsGenerator(ljdao)
            img_tool = VolImgProducer(vol_data, price_tool, "/app/www/img/")
            img_tool.run()
        update_hour = cur_datetime.hour
        shanghai = ShanghaiVol(dv_dao)
        shanghai.run()
        hz_vol = HangZhouVol(dv_dao)
        hz_vol.run()
        bj = BeijingGov(dv_dao)
        bj.run()
        dv = DailyVol(dv_dao)
        dv.run()
        lianjia = Lianjia(ljdao)
        lianjia.run()
        dao = HangZhouDAO(datetime.today(), db_path)
        hangzhou = HangzhouGov(dao)
        hangzhou.run()

