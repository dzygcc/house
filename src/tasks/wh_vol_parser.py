#!/usr/bin/python
# -*- coding: utf-8 -*-
from src.parser.http_utils import *
from bs4 import BeautifulSoup
import re
from src.utils.logger import logger


class DailyVol:
    def __init__(self, dao):
        self.dao = dao
        self.host = "http://scxx.whfcj.gov.cn"

    def caturl(self, part):
        if part:
            if part.startswith("/"):
                return self.host + part
            else:
                return "".join(self.host, "/", part)
        return None

    def nextpage(self, html):
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        nodes = soup.find("td", {"align": "left"}).findAll("a")
        for node in nodes:
            if "下一页" == node.text.strip().encode("utf-8"):
                return self.caturl(node["href"])
        return None

    def detail(self, url, date):
        html = download(url)
        ret = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            div = soup.find("div", {"id": "artibody"})
            if div:
                trs = div.findAll("tr")
            for tr in trs:
                tds = tr.findAll("td")
                if len(tds) > 9:
                    if not re.findall("\\d+", tds[1].text):
                        continue
                    item = {
                        "city": "武汉",
                        "district": tds[0].text.encode("utf-8"),
                        "zhuzai": tds[1].text.encode("utf-8"),
                        "total": tds[9].text.encode("utf-8"),
                        "date": date
                    }
                    ret.append(item)
            return ret

    def parse(self):
        next_page = "http://scxx.whfcj.gov.cn/scxxbackstage/whfcj/channels/854.html"
        while next_page:
            html = download(next_page)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            tmp = soup.find("td", {"class": "text"})
            if tmp:
                for tr in tmp.findAll("a"):
                    text = tr.text.encode("utf-8")
                    if text:
                        match = re.findall("(\\d+)年(\\d+)月(\\d+)", text)
                        date = "".join([match[0][0], "-", match[0][1].zfill(2),
                                        "-", match[0][2].zfill(2)])
                        ds = self.detail(self.caturl(tr["href"]), date)
                        for dv in ds:
                            has = self.dao.has_item(dv["district"], dv["date"])
                            if not has[0]:
                                self.dao.insert_item(dv)
            #next_page = self.nextpage(html)
            #print next_page
            next_page = None
        return

    def run(self):
        try:
            logger.info("start wuhan vol crawler.")
            self.parse()
            logger.info("end wuhan vol crawler.")
        except Exception, e:
            logger.error("error", e)