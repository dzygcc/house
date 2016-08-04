#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from src.dao.vol import DailyVolDAO
from src.parser.http_utils import download
from src.utils.logger import logger


class BeijingGov:
    def __init__(self, dao):
        self.url = "http://www.bjjs.gov.cn/tabid/2167/default.aspx"
        self.dao = dao

    def get_wangqian(self):
        html = download(self.url, charset="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        total_div = soup.find("span", {"id": "ess_ctr5112_FDCJY_SignOnlineStatistics_totalCount4"})
        zhuzai_div = soup.find("span", {"id": "ess_ctr5112_FDCJY_SignOnlineStatistics_residenceCount4"})
        date_div = soup.find("span", {"id": "ess_ctr5115_FDCJY_HouseTransactionStatist_timeMark4"})
        if total_div and zhuzai_div:
            total = total_div.text.encode("utf-8")
            zhuzai = zhuzai_div.text.encode("utf-8")
            date = date_div.text.strip().encode("utf-8")
            tmp = date.split("-")
            if len(tmp) == 3:
                date = datetime.today().replace(year=int(tmp[0]), month=int(tmp[1]), day=int(tmp[2]))
            else:
                logger.error("beijing gov get wangqian.")
            row = {"city": "北京", "district": "bj", "zhuzai": zhuzai,
                   "total": total, "date": date}
            has = self.dao.has_item("bj", date)
            if not has[0]:
                logger.debug(row)
                self.dao.insert_item(row)

    def get_history(self):
        today = datetime.now().strftime('%y-%m-%d')
        has = self.dao.has_item("bj", today)
        if has[0]:
            logger.debug("find history.")
            return
        html = download("http://www.fangchanzixun.com/volume",
                        charset="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find('table', attrs={'class': 'table'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if len(cols) != 5:
                continue
            col_date = cols[0]
            total = cols[1].encode("utf-8")
            zhuzai = cols[3].encode("utf-8")
            date = datetime.strptime(col_date, "%Y-%m-%d").date()
            info = {"city": "北京", "district": "bj", "total": total, "zhuzai": zhuzai, "date": date}
            logger.debug(info)
            has = self.dao.has_item("bj", date)
            if not has[0]:
                self.dao.insert_item(info)

    def run(self):
        try:
            logger.info("start bj gov crawler.")
            self.get_wangqian()
            self.get_history()
            logger.info("end bj gov crawler.")
        except Exception, e:
            logger.error("error", e)

if __name__ == "__main__":
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../../db/house.db"])
    dao = DailyVolDAO(db_path)
    tool = BeijingGov(dao)
    tool.get_history()
    tool.get_wangqian()
