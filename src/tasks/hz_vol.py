#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import time
from src.dao.vol import DailyVolDAO
from src.utils.logger import logger
from src.parser.http_utils import download
from bs4 import BeautifulSoup
import re


class HangZhouVol:
    def __init__(self, dao):
        self.host = "http://www.tmsf.com"
        self.url_pattern = "http://www.tmsf.com/upload/report/mrhqbb/%s/index.html"
        self.dao = dao

    def run(self):
        try:
            logger.info("start hangzhou vol crawler.")
            prev_url = self.get_month_vol(datetime.date.today() - datetime.timedelta(days=1), None)
            while prev_url:
                prev_url = self.get_month_vol(None, prev_url)
                time.sleep(6)
            logger.info("end hangzhou vol crawler.")
        except:
            logger.error("error")

    def get_month_vol(self, dt, url):
        if not url:
            url = self.url_pattern % dt.strftime('%Y%m%d')
        else:
            match = re.findall("(\\d{8})", url)
            if not match:
                return None
            dt = datetime.datetime(*time.strptime(match[0], '%Y%m%d')[:6])
        logger.info(url)
        html = download(url, charset="utf-8")
        if not html:
            return None
        new_vols = re.findall("ss1\.push\((\\d+)\);", html)
        old_vols = re.findall("ss2\.push\((\\d+)\);", html)
        days = re.findall("tickss\.push\((\\d+)\);", html)
        if len(new_vols) != len(old_vols) or len(days) != len(new_vols):
            logger.info(new_vols)
            logger.info(old_vols)
            logger.info(days)
            return
        for i in range(0, len(days), 1):
            vol_date = dt.replace(dt.year, dt.month, int(days[i]))
            city = "杭州"
            district = "杭州"
            has = self.dao.has_item(district, vol_date)
            if not has[0] and int(new_vols[i]) > 0 and int(old_vols[i]) > 0:
                self.dao.insert_item({"city": city, "district": district,
                                      "total": new_vols[i], "zhuzai": old_vols[i],
                                      "date": vol_date})

        soup = BeautifulSoup(html, "html.parser")
        div_date = soup.find("div", {"class": "date"});
        if div_date:
            if div_date.find("a"):
                path = div_date.find("a")["href"]
                if path:
                    return self.host + path

        return None


if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../../db/house.db"])
    dao = DailyVolDAO(datetime.date.today(), db_path)
    hz = HangZhouVol(dao)
    hz.run()
