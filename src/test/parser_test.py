#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import unittest
from datetime import *

from src.dao.db_schema import *
from src.dao.hz import HangZhouDAO
from src.dao.vol import DailyVolDAO
from src.tasks.hz_parser import HangZhouParser
from src.tasks.wh_vol_parser import DailyVol


class TestHangZhouParser(unittest.TestCase):
    def setUp(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = ''.join([file_dir, "/../../db/test.db"])
        create_hangzhou_tables(db_path)
        dao = HangZhouDAO(datetime.today(), db_path)
        dvdao = DailyVolDAO(datetime.today(), db_path)
        self.parser = HangZhouParser(dao)
        self.wh_parser = DailyVol(dvdao)

    def testParsePageNum(self):
        url = self.parser.get_url(1)
        html = self.parser.downloadHtml(url)
        num = self.parser.parse_page_num(html)
        self.assertGreater(num, 0)

    def testParseProject(self):
        url = self.parser.get_url(1)
        html = self.parser.downloadHtml(url)
        projects = self.parser.parse_project(html)
        for p in projects:
            print p

    def testParseDetail(self):
        url = "http://www.hzfc.gov.cn/scxx/xmcx.php?lpid=Mzc5NTA1MTA=&key=1460076267653"
        project = {}
        self.parser.parse_detail(url, project)
        print project

    def testReFindAll(self):
        if re.findall("\\d{4}", "abc"):
            print "if"
        print " abc ".strip()

    def test_page_num(self):
        print self.wh_parser.parse()