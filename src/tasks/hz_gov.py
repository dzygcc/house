#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
import time
import re
from bs4 import BeautifulSoup

from src.dao.hz import HangZhouDAO
from src.parser.http_utils import download, get_binary_file
from src.utils.logger import logger


def parse_int(text):
    match = re.findall("(\\d+)", text)
    if len(match) == 1:
        return int(match[0])
    return 0


def parse_float(text):
    match = re.findall("(\\d+\\.?\\d+)", text)
    if len(match) == 1:
        return float(match[0])
    return 0.


class HangzhouGov:
    def __init__(self, dao):
        self.name = "Wuhan"
        self.dao = dao
        self.date = datetime.today()
        self.host = "http://www.hzfc.gov.cn"

    def get_name_with_date(self, prefix):
        today = datetime.today()
        return "".join([prefix, str(today.year), "-", str(today.month).zfill(2),
                        "-", str(today.day).zfill(2), ".jpg"])

    def get_name_with_month(self, prefix):
        today = datetime.today()
        return "".join([prefix, str(today.year), "-", str(today.month).zfill(2),
                         ".jpg"])

    def daily_pic(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = file_dir + "/../../hz-img/"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        url = "http://www.hzfc.gov.cn/scxx/"
        html = download(url)
        soup = BeautifulSoup(html, "html.parser")
        supply = soup.find("marquee").find("img")
        supply_url = "".join([url, supply["src"]])
        new_month_vol = soup.find("dd", {"id": "hzfc_002_Content0"}).find("img")
        new_daily_vol = soup.find("dd", {"id": "hzfc_002_Content1"}).find("img")
        old_month_vol = soup.find("dd", {"id": "hzfc_003_Content0"}).find("img")
        old_daily_vol = soup.find("dd", {"id": "hzfc_003_Content1"}).find("img")
        new_month_url = "".join([url, new_month_vol["src"]])
        new_daily_url = "".join([url, new_daily_vol["src"]])
        old_month_url = "".join([url, old_month_vol["src"]])
        old_daily_url = "".join([url, old_daily_vol["src"]])
        get_binary_file(supply_url, self.get_name_with_date(img_dir + "supply-"))
        get_binary_file(new_daily_url, self.get_name_with_date(img_dir + "vol-new-"))
        get_binary_file(old_daily_url, self.get_name_with_date(img_dir + "vol-old-"))
        get_binary_file(new_month_url, self.get_name_with_month(img_dir + "vol-new-"))
        get_binary_file(old_month_url, self.get_name_with_month(img_dir + "vol-old-"))
        get_binary_file(supply_url, "/app/www/img/hz_supply.jpg")

    def get_url(self, page):
        return ''.join(["http://www.hzfc.gov.cn/scxx/xmcx_more.php?page=", str(page)]);

    def parse_page_num(self, html):
        soup = BeautifulSoup(html, "html.parser")
        nodes = soup.findAll("font", {"color": "#000000"})
        if len(nodes) == 0:
            return 0
        for node in nodes:
            if node.text:
                text = node.text.encode("utf-8")
                match = re.findall("页数\\s+\\d+/(\\d+)", text)
                if len(match) == 1:
                    return int(match[0])
        return 0

    def parse_project(self, html):
        soup = BeautifulSoup(html, "html.parser")
        trs = soup.findAll("tr")
        projects = []
        for tr in trs:
            tds = tr.findAll("td")
            project = {}
            if len(tds) <= 6:
                continue
            tda = tds[0].find("a")
            if tda:
                project["name"] = tda.contents[0].encode("utf-8")
                tda = tds[1].find("a")
                if tda:
                    project["district"] = tda.contents[0].encode("utf-8")
                if tda["href"]:
                    time.sleep(8)
                    self.parse_detail(self.host + tda["href"], project)
                tda = tds[2].find("a")
                if tda:
                    project["developer"] = tda.contents[0].encode("utf-8")
                tda = tds[3].find("a")
                if tda:
                    project["sold"] = parse_int(tda.contents[0])
                tda = tds[5].find("a")
                if tda:
                    project["avg_price"] = parse_float(tda.contents[0])
                if project["name"]:
                    projects.append(project)
        return projects

    def parse_detail(self, url, project):
        html = download(url)
        if not html:
            return
        soup = BeautifulSoup(html, "html.parser")
        trs = soup.findAll("tr")
        total = 0
        zhuzai = 0
        total_area = 0.
        zhuzai_area = 0.
        for tr in trs:
            tds = tr.findAll("td")
            if len(tds) < 8:
                continue
            tda = tds[2].find("a")
            if tda:
                total += parse_int(tda.contents[0])
            tda = tds[3].find("a")
            if tda:
                zhuzai += parse_int(tda.contents[0])
            tda = tds[4].find("a")
            if tda:
                total_area += parse_float(tda.contents[0])
            tda = tds[5].find("a")
            if tda:
                zhuzai_area += parse_float(tda.contents[0])
            if tds[0].find("a") and tds[1].find("a"):
                open_id = tds[0].find("a").contents[0].encode("utf-8").strip()
                open_date = tds[1].find("a").contents[0].encode("utf-8").strip()
                if open_id and re.findall("\\d{4}-\\d{2}-\\d{2}", open_date):
                    ret = self.dao.has_project_open(open_id)
                    if not ret[0]:
                        self.dao.insert_project_open(project["name"], open_id,
                                                     project["district"], total, zhuzai, open_date)
        project["zhuzai"] = str(zhuzai)
        project["total"] = str(total)
        project["total_area"] = str(total_area)
        project["zhuzai_area"] = str(zhuzai_area)

    def schedule(self):
        url = "http://www.hzfc.gov.cn/scxx/xmcx_more.php"
        html = download(url)
        page_num = self.parse_page_num(html)
        for page in range(1, page_num + 1, 1):
            print "hz page %s " % page
            html = download(self.get_url(page))
            if not html:
                continue
            projects = self.parse_project(html)
            for project in projects:
                project["city"] = "杭州"
                # print project
                has = self.dao.has_project(project["name"])
                if not has[0]:
                    project["project_id"] = self.dao.insert_project(project)
                else:
                    project["project_id"] = has[1]
                has = self.dao.has_sell_info(project["name"])
                if not has[0]:
                    self.dao.insert_sell_info(project)

    def run(self):
        try:
            logger.info("start hz gov crawler.")
            self.schedule()
            self.daily_pic()
            logger.info("end hz gov crawler.")
        except Exception, e:
            logger.error("error", e)

if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../../db/house.db"])
    dao = HangZhouDAO(datetime.today(), db_path)
    hangzhou = HangzhouGov(dao)
    hangzhou.daily_pic()