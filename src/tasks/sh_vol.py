#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime
from src.dao.vol import DailyVolDAO
from src.parser.http_utils import download
from src.utils.logger import logger


class ShanghaiVol:
    def __init__(self, dao):
        self.url ="http://www.fangdi.com.cn/Report.asp"
        self.dao = dao

    def run(self):
        try:
            logger.info("start shanghai vol crawler.")
            html = download(self.url)
            soup = BeautifulSoup(html, "html.parser")
            soup.find("div", {})
            match = re.findall("出售各类商品房<b>(\\d+)</b>套", html)
            if match:
                vol = match[0]
                ds = re.findall("今日楼市（(\\d+)-(\\d+)-(\\d+)）", html)
                date = datetime.now().replace(year=int(ds[0][0]), month=int(ds[0][1]), day=int(ds[0][2]))
                info = {"city": "上海", "district": "sh", "total": vol, "zhuzai": 0, "date": date}
                has = self.dao.has_item("sh", date)
                if not has[0]:
                    self.dao.insert_item(info)
            logger.info("end shanghai vol crawler.")
        except Exception, e:
            logger.error(e)


if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../../db/house.db"])
    dao = DailyVolDAO(db_path)
    sh = ShanghaiVol(dao)
    sh.run()
