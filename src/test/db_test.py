#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from datetime import *

from src.dao.hz import HangZhouDAO
from src.dao.lianjia import LianjiaDAO
from src.dao.vol import DailyVolDAO


from src.dao.db_schema import *


class TestHangZhouDAO(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = current_dir + "/../../db/test.db"
        create_hangzhou_tables(db_path)
        self.dao = HangZhouDAO(datetime.today(), db_path)
        self.whdao = DailyVolDAO(datetime.today(), db_path)
        self.ljdao = LianjiaDAO(datetime.today(), db_path)

    def testProject(self):
        project = {"name": "test", "district": "海淀", "city": "北京", "developer": "dzy",
                   "total": 100, "zhuzai": 69, "zhuzai_area": 21.0, "total_area": 90.0}
        self.dao.insert_project(project)
        ret = self.dao.has_project(project["name"])
        self.assertEqual(True, ret[0])

    def testSellInfo(self):
        info = {"name":"test", "project_id":1, "avg_price":1.0, "sold":100, "date":"2016-04-06"}
        has = self.dao.has_sell_info(info["name"])
        if not has[0]:
            self.dao.insert_sell_info(info)

    def testProjectOpen(self):
        ret = self.dao.has_project_open("123")
        self.assertEqual(False, ret[0])
        self.dao.insert_project_open("test", "123", "a", 1, 100, "2016-04-09")
        ret = self.dao.has_project_open("123")
        self.assertEqual(True, ret[0])

    def testDailyVol(self):
        ret = self.whdao.has_item("haidian", "2016-01-01")
        self.assertEqual(False, ret[0])
        self.whdao.insert_item({"district":"haidian", "total":1, "zhuzai":100,
                                "date":"2016-01-01", "city":"sss"})
        ret = self.whdao.has_item("haidian", "2016-01-01")
        self.assertEqual(True, ret[0])

    def testLianjia(self):
        ret = self.ljdao.get_item("wh", "wc", "2016-01-01")
        self.assertEqual(None, ret)
        print ret
        self.ljdao.insert_item({"district": "haidian", "total": 1, "price": 100.0,
                                "date": "2016-01-01", "city": "wh"})
        ret = self.ljdao.get_item("wh", "haidian", "2016-01-01")
        self.assertNotEqual(None, ret)
        print ret
        self.ljdao.update_item("wh", "haidian", 10, 0.1, "2016-01-01")
        ret = self.ljdao.get_item("wh", "haidian", "2016-01-01")
        print ret
        self.assertEqual(10, ret[3])


