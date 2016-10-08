#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import datetime


class HangZhouDAO:
    def __init__(self, curr_date, db_path):
        self.curr_date = curr_date
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        if self.conn is None:
            print("connect sqlite3 path: %s failed" % self.db_path)
            exit(-1)

    def close(self):
        self.conn.close()

    def insert_project(self, info):
        sql = "insert into house_project (name, city, developer, district, " \
              "total, zhuzai, total_area, zhuzai_area) " \
              "values(\'%s\', \'%s\', \'%s\', \'%s\', %s, %s, %s, %s)" \
              % (info["name"], info["city"], info["developer"], info["district"],
                 info["total"], info["zhuzai"], info["total_area"], info["zhuzai_area"])
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        row_id = cursor.lastrowid
        cursor.close()
        return row_id

    def has_project(self, name):
        sql = "select id from house_project where name = \'%s\'" % (name)
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

    def has_sell_info(self, name):
        sql = "select id from project_sell_info where name = \'%s\' and date=date(\'%s\')" % (
            name, self.curr_date)
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

    def insert_sell_info(self, info):
        sql = "insert into project_sell_info (name, project_id, avg_price, sold, date) " \
              "values(\'%s\', %s, %s, %s, date(\'%s\'))" % (info["name"], info["project_id"],
                                                            info["avg_price"], info["sold"], self.curr_date)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def has_project_open(self, open_id):
        sql = "select id from project_open where open_id = \'%s\'" % open_id
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

    def insert_project_open(self, name, open_id, district, total, zhuzai, date):
        sql = "insert into project_open (name, open_id, district, total, zhuzai, date) " \
              "values(\'%s\', \'%s\', \'%s\', %s, %s, date(\'%s\'))" % \
              (name, open_id, district, total, zhuzai, date)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

if __name__ == "__main__":
    hz = HangZhouDAO(datetime.today())
