#!/usr/bin/env python
# coding=utf-8
import os
import re
from src.utils.logger import logger
from datetime import *
from src.dao.lianjia import LianjiaDAO
from src.parser.http_utils import *
from bs4 import BeautifulSoup


class Lianjia:
    def __init__(self, dao):
        self.sources = [
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=110000",
                "city": "北京",
                "home": "http://bj.lianjia.com/",
                "trends": "http://bj.lianjia.com/fangjia/priceTrend/"
            },
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=310000",
                "city": "上海",
                "home": "http://sh.lianjia.com/",
            },
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=440100",
                "city": "广州",
                "home": "http://gz.lianjia.com/",
                "trends": "http://gz.lianjia.com/fangjia/priceTrend/"
            },
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=440300",
                "city": "深圳",
                "home": "http://sz.lianjia.com/",
                "trends": "http://sz.lianjia.com/fangjia/priceTrend/"
            },
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=330100",
                "city": "杭州",
                "home": "http://hz.lianjia.com/",
                "trends": "http://hz.lianjia.com/fangjia/priceTrend/"
            },
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=420100",
                "city": "武汉",
                "home": "http://wh.lianjia.com/",
                "trends": "http://wh.lianjia.com/fangjia/priceTrend/"
            },
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=510100",
                "city": "成都",
                "home": "http://cd.lianjia.com/",
                "trends": "http://cd.lianjia.com/fangjia/priceTrend/"
            },
            {
                "url": "http://ajax.lianjia.com/ajax/mapsearch/area/district?city_id=500000",
                "city": "重庆",
                "home": "http://cq.lianjia.com/",
                "trends": "http://cq.lianjia.com/fangjia/priceTrend/"
            }
        ]
        self.date = datetime.today()
        self.dao = dao

    def craw_open(self):
        for c in self.sources:
            logger.debug(c["city"] + ": " + c["url"])
            arr = get_json(c["url"])
            if arr and arr["data"]:
                for item in arr["data"]:
                    if not item["avg_unit_price"]:
                        item["avg_unit_price"] = -1.0
                    if not item["name"] or not["house_count"]:
                        logger.debug(item)
                        continue
                    row = {"city": c["city"], "district": item["name"].encode("utf-8"),
                           "total": item["house_count"],
                           "price": item["avg_unit_price"], "date": self.date}
                    old = self.dao.get_item(row["city"], row["district"], row["date"])
                    if not old:
                        self.dao.insert_item(row)
                    elif old[3] < row["total"]:
                        self.dao.update_item(row["city"], row["district"], row["total"],
                                        row["price"], row["date"])

    def craw_stat(self):
        for c in self.sources:
            logger.debug(c["city"] + ": " + c["home"])
            html = download(c["home"], charset="utf-8")
            soup = BeautifulSoup(html, "html.parser")
            deal_div = soup.find("div", {"class": "deal-price"})
            deal_price = 0.0
            list_price = 0.0
            rate = 0.0
            vol = 0
            if deal_div and deal_div.find("label", {"class": "dataAuto"}):
                 deal_price = deal_div.find("label", {"class": "dataAuto"}).text.strip().encode("utf-8")
            list_div = soup.find("div", {"class": "listing-price"})
            if list_div and list_div.find("label", {"class": "dataAuto"}):
                list_price = list_div.find("label", {"class": "dataAuto"}).text.strip().encode("utf-8")
            ul = soup.find("div", {"class": "main"}).findAll("li")
            for li in ul:
                if li.find("p").text:
                    if re.findall("客房比", li.find("p").text.encode("utf-8")):
                        rate = li.find("label").text.strip().encode("utf-8")
                    if re.findall("成交", li.find("p").text.encode("utf-8")):
                        vol = li.find("label").text.strip().encode("utf-8")
            item = {"price": deal_price, "rate": rate,
                    "city": c["city"], "vol": vol, "date": self.date}
            logger.debug(item)
            if float(deal_price) <=0.0 or float(rate) <= 0.0:
                continue;
            if not self.dao.has_stat(c["city"], self.date):
                self.dao.insert_stat(item)

    def crawPriceTrends(self):
        for c in self.sources:
            city = c["city"]
            if c.has_key("trends"):
                print c["trends"]
                json = get_json(c["trends"])
                year = int(json["time"]["year"])
                month = json["time"]["month"]
                month = int(re.compile(u"(\\d+)月").findall(month)[0])
                last = datetime(year, month, 1)
                price_trends = json["currentLevel"]["dealPrice"]["total"]
                price_trends.reverse()
                for price in price_trends:
                    print last, price
                    price = price.encode("utf-8")
                    row = {"city": city, "district":"月趋势", "total": 0, "price": price, "date": last}
                    old = self.dao.get_item(row["city"], row["district"], row["date"])
                    if not old:
                        self.dao.insert_item(row)
                    else:
                        self.dao.update_item(city, "月趋势", 0, price, last)
                    month -= 1
                    if month == 0:
                        year -= 1
                        month = 12
                    last = datetime(year, month, 1)

    def run(self):
        try:
            logger.info("start lianjia crawler")
            self.craw_stat()
            self.craw_open()
            self.crawPriceTrends()
            logger.info("end lianjia crawler")
        except Exception, e:
            logger.error("error", e)

if __name__ == "__main__":
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../../db/house.db"])
    logger.info("start.")
    dao = LianjiaDAO(datetime.today(), db_path)
    tool = Lianjia(dao)
    tool.crawPriceTrends()
    logger.info("end.")

