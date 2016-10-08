#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3


class LianjiaDAO:
    def __init__(self, curr_date, db_path):
        self.curr_date = curr_date
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        if self.conn is None:
            print("connect sqlite3 path: %s failed" % self.db_path)
            exit(-1)

    def close(self):
        self.conn.close()

    def get_item(self, city, district, date):
        sql = "select * from lianjia where city = \'%s\' and " \
              "district = \'%s\' and date=date(\'%s\')" % (city, district, date)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        if len(res) >= 1:
            return res[0]
        else:
            return None

    def get_items(self, city, district):
        sql = "select city, price, date from lianjia where city = \'%s\' and district=\'%s\' order by `date` asc" \
              "" % (city, district)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        id_res = cursor.fetchall()
        cursor.close()
        return id_res

    def insert_item(self, info):
        sql = "insert into lianjia (city, district, total, price, date) " \
              "values(\'%s\', \'%s\', %s, %s, date(\'%s\'))" % \
              (info["city"], info["district"], info["total"], info["price"], info["date"])
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def update_item(self, city, district, total, price, date):
        sql = "update lianjia set total = %s, price= %s where city = \'%s\' and " \
              "district = \'%s\' and `date`=date(\'%s\')" % (total, price, city, district, date)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def has_stat(self, city, date):
        sql = "select id from lianjia_stat where city = \'%s\' and " \
              " `date`=date(\'%s\')" % (city, date)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        if len(res) >= 1:
            return True
        else:
            return False

    def insert_stat(self, info):
        sql = "insert into lianjia_stat (city, vol, price, rate, date) " \
              "values(\'%s\', \'%s\', %s, %s, date(\'%s\'))" % \
              (info["city"], info["vol"], info["price"], info["rate"], info["date"])
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()