#!/usr/bin/python
# -*- coding: utf-8 -*-


import sqlite3


class DailyVolDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        if self.conn is None:
            print("connect sqlite3 path: %s failed" % self.db_path)
            exit(-1)

    def close(self):
        self.conn.close()

    def has_item(self, district, date):
        sql = "select id from daily_vol where district = \'%s\' " \
              "and date=date(\'%s\')" % (district, date)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        id_res = cursor.fetchall()
        cursor.close()
        if len(id_res) >= 1:
            return [True, id_res[0][0]]
        else:
            if len(id_res) == 0:
                return [False, 0]
            else:
                return [False, 0]

    def insert_item(self, info):
        sql = "insert into daily_vol (city, district, total, zhuzai, `date`) " \
               "values(\'%s\', \'%s\', %s, %s, date(\'%s\'))" \
              % (info["city"], info["district"], info["total"], info["zhuzai"], info["date"])
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()

    def get_items(self, city, district):
        sql = "select total, zhuzai, date from daily_vol where city = \'%s\' and district=\'%s\' order by `date` asc" \
              "" % (city, district)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        id_res = cursor.fetchall()
        cursor.close()
        return id_res