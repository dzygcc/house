#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3


class Sqlite3Utils():
    def __init__(self, curr_date, logger, db_path):
        self.curr_date = curr_date
        self.logger = logger
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        if self.conn is None:
            self.logger.error("connect sqlite3 path: %s failed" % (self.db_path))
            exit(-1)

    def close(self):
        self.conn.close()

    def check_project_info_existed(self, project_name):
        check_existed = "select id from area_project_list where project_name=\'%s\'" % (project_name)
        cursor = self.conn.cursor()
        cursor.execute(check_existed)
        id_res = cursor.fetchall()
        cursor.close()
        if len(id_res) == 1:
            return [True, id_res[0][0]]
        else:
            if len(id_res) == 0:
                return [False, 0]
            else:
                self.logger.error("project name: %s has duplicate" % (project_name))
                return [False, 0]

    def check_project_sell_info(self, id):
        check_existed = "select project_id from project_sell_info where project_id = \'%s\' and sell_info_date=\'%s\'" % (
        id, self.curr_date)
        cursor = self.conn.cursor()
        cursor.execute(check_existed)
        id_res = cursor.fetchall()
        cursor.close()
        if len(id_res) >= 1:
            return [True, id_res[0][0]]
        else:
            if len(id_res) == 0:
                return [False, 0]
            else:
                return [False, 0]

    # return [existed, project_id]
    def insert_project_info(self, area_id, area_name, project_name, project_info):
        insert_sql = "insert into area_project_list (\
                            area_id,\
                            area_name,\
                            project_name,\
                            project_addr,\
                            project_begin_date,\
                            project_finish_date,\
                            project_sell_date,\
                            project_land_area,\
                            project_build_area,\
                            project_people_rate,\
                            project_build_num,\
                            project_house_num,\
                            create_time) values(%s, \'%s\', \'%s\', \'%s\', date(\'%s\'), date(\'%s\'), date(\'%s\'), %s, %s, %s, %s, %s, date(\'%s\'))" \
                     % (area_id, area_name, project_name, project_info["project_addr"], \
                        project_info["project_begin_date"], project_info["project_finish_date"],
                        project_info["project_sell_date"], \
                        project_info["project_land_area"], project_info["project_build_area"],
                        project_info["project_people_rate"], \
                        project_info["project_build_num"], project_info["project_house_num"], self.curr_date)
        self.logger.debug(insert_sql)
        cursor = self.conn.cursor()
        cursor.execute(insert_sql)
        self.conn.commit()

        data_id_sql = "select last_insert_rowid() from area_project_list"
        data_id_res = cursor.execute(data_id_sql).fetchall()
        cursor.close()

        return data_id_res[0][0]

    def insert_area_project_num(self, area_id, area_project_num):
        insert_sql = "insert into area_project_num (area_id, area_project_num, parse_date) values(%s, %s, date(\'%s\'))" \
                     % (area_id, area_project_num, self.curr_date)
        cursor = self.conn.cursor()
        cursor.execute(insert_sql)
        self.conn.commit()
        cursor.close()

    def insert_project_sell_info(self, project_id, project_sell_info):
        insert_sql = "insert into project_sell_info (\
                            project_id,\
                            project_total,\
                            project_h_selled,\
                            project_h_sell,\
                            project_c_selled,\
                            project_c_sell,\
                            sell_info_date) values(%s, %s, %s, %s, %s, %s, date(\'%s\'))" \
                     % (project_id, project_sell_info["total"], \
                        project_sell_info["h_selled"], project_sell_info["h_sell"], \
                        project_sell_info["c_selled"], project_sell_info["c_sell"], \
                        self.curr_date)

        cursor = self.conn.cursor()
        cursor.execute(insert_sql)
        self.conn.commit()
        cursor.close()

    def insert_project(self, info):
        sql = "insert into house_project (name, city, developer, district, " \
              "total, zhuzai, total_area, zhuzai_area) " \
              "values(%s, %s, %s, %s, %s, %s, %s, %s)" \
              % (info["name"], info["city"], info["developer"], info["district"],
                 info["total"], info["zhuzai"], info["total_area"], info["zhuzai_area"])
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def has_project(self, name):
        sql = "select id from house_project where name = %s" % (name)
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
        sql = "select id from project_sell_info where name = %s and date=%s" % (
            name, self.curr_date)
        print sql
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
              "values(%s, %s, %s, %s, %s)" % (info["name"], info["project_id"],
                                              info["avg_price"], info["sold"], self.curr_date)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
