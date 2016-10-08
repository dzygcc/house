#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
sys.path.append(".")
sys.path.append("..")
from src.dao.lianjia import LianjiaDAO
from src.utils.logger import logger
import plotly.graph_objs as go
import plotly.plotly as py
from src.dao.vol import DailyVolDAO
from src.utils.my_datetime import is_in_same_month


class LijiaPriceTrendsGenerator:
    def __init__(self, dao):
        self.dao = dao

    def get_items(self, city):
        rows = self.dao.get_items(city, "月趋势")
        line = []
        dates = []
        for row in rows:
            line.append(row[1])
            dates.append(row[2])
        ret = [
            go.Scatter(
                x=dates,
                y=line,
                mode='lines+markers',
                name=city,
                marker=dict(
                    size=2,
                    line=dict(
                        width=1,
                    )
                )
            )]
        return ret

class VolDataGenerator:
    def __init__(self, dao):
        self.dao = dao

    def get_items(self, city, district, rate):
        rows = self.dao.get_items(city, district)
        if not rows:
            return None
        totals = []
        zhuzais = []
        dates = []
        for row in rows:
            totals.append(row[0])
            zhuzais.append(row[1])
            dates.append(row[2])
        line1 = self.shrink(dates, totals, rate)
        line2 = self.shrink(dates, zhuzais, rate)
        names = self.getLineNames(city)
        ret = [
            go.Scatter(
                x=line1[0],
                y=line1[1],
                mode='lines+markers',
                name=names[0],
                marker=dict(
                    size=2,
                    line=dict(
                        width=1,
                    )
                )
            )
        ]
        if len(names) == 2:
            ret.append(go.Scatter(
                x=line2[0],
                y=line2[1],
                mode='lines+markers',
                name=names[1],
                marker=dict(
                    size=2,
                    line=dict(
                        width=1,
                    )
                )
            ))
        return ret

    def getLineNames(self, city):
        if city == "北京":
            return ["二手房", "二手住宅"]
        elif city == "武汉":
            return ["新房", "新房住宅"]
        elif city == "杭州":
            return ["新房", "二手房"]

    # rate: 每多少个点合并成一个点
    def shrink(self, dates, datas, rate):
        if rate == 30:
            return self.shrink_month(dates, datas)
        if rate == 1:
            dates = dates[-100:-1]
            datas = datas[-100:-1]
            return [dates, datas]
        size = len(dates)
        ret_dates = []
        ret_datas = []
        sum = 0
        for i in range(0, size, 1):
            if i % rate == 0:
                sum = 0
                ret_dates.append(dates[i])
            sum += datas[i]
            if i % rate == rate - 1:
                ret_datas.append(sum)
        if len(ret_datas) < len(ret_dates):
            ret_dates.pop()
        return [ret_dates, ret_datas]

    def shrink_month(self, dates, datas):
        size = len(dates)
        ret_dates = []
        ret_datas = []
        sum = 0
        begin_month = "1978-01-01"
        for i in range(0, size, 1):
            if not is_in_same_month(begin_month, dates[i]):
                if sum > 0:
                    ret_datas.append(sum)
                sum = 0
                begin_month = dates[i]
                ret_dates.append(dates[i])
            sum += datas[i]
        if sum > 0:
            ret_datas.append(sum)
        if len(ret_datas) < len(ret_dates):
            ret_dates.pop()
        return [ret_dates, ret_datas]


class VolImgProducer:
    def __init__(self, vol_tool, price_tool, directory):
        py.sign_in(username='dzy', api_key='4dkuzf1c70')
        self.vol_tool = vol_tool
        self.price_tool = price_tool
        self.directory = directory

    @staticmethod
    def get_vol_layout():
        title = "成交量趋势"
        return go.Layout(
            autosize=False,
            title=title,
            xaxis=dict(
                titlefont=dict(
                    size=18,
                )
            ),
            yaxis=dict(
                title='成交量',
                titlefont=dict(
                    size=18,
                )
            ),
            margin=dict(
                l=60,
                r=1,
                b=40,
                t=40,
            ),
            width=600,
            height=400
        )

    @staticmethod
    def get_price_layout():
        title = "二手房成交价格趋势"
        return go.Layout(
            autosize=False,
            title=title,
            xaxis=dict(
                titlefont=dict(
                    size=18,
                )
            ),
            yaxis=dict(
                title='成交价',
                titlefont=dict(
                    size=18,
                )
            ),
            margin=dict(
                l=60,
                r=1,
                b=40,
                t=40,
            ),
            width=600,
            height=400
        )

    def draw_vol(self, data, file_name):
        fig = go.Figure(data=data, layout=self.get_vol_layout())
        py.image.save_as(fig, filename=file_name)

    def draw_price(self, data, file_name):
        fig = go.Figure(data=data, layout=self.get_price_layout())
        py.image.save_as(fig, filename=file_name)

    def draw_price_trends(self):
        cites = ["北京", "广州", "深圳", "杭州", "武汉", "成都", "重庆"]
        names = ["bj_lp.jpeg", "gz_lp.jpeg", "sz_lp.jpeg", "hz_lp.jpeg",
                 "wh_lp.jpeg", "cd_lp.jpeg", "cq_lp.jpeg"]
        for i in range(0, len(cites), 1):
            self.draw_price(self.price_tool.get_items(cites[i]),
                          os.path.join(self.directory, names[i]))

    def draw_vol_1days(self):
        data = self.vol_tool.get_items("杭州", "杭州", 1)
        self.draw_vol(data, os.path.join(self.directory, "hz_1.jpeg"))
        data = self.vol_tool.get_items("武汉", "合计", 1)
        self.draw_vol(data, os.path.join(self.directory, "wh_1.jpeg"))
        data = self.vol_tool.get_items("北京", "bj", 1)
        self.draw_vol(data, os.path.join(self.directory, "bj_1.jpeg"))

    def draw_vol_7days(self):
        data = self.vol_tool.get_items("杭州", "杭州", 7)
        self.draw_vol(data, os.path.join(self.directory, "hz_7.jpeg"))
        data = self.vol_tool.get_items("武汉", "合计", 7)
        self.draw_vol(data, os.path.join(self.directory, "wh_7.jpeg"))
        data = self.vol_tool.get_items("北京", "bj", 7)
        self.draw_vol(data, os.path.join(self.directory, "bj_7.jpeg"))

    def draw_vol_monthly(self):
        data = self.vol_tool.get_items("杭州", "杭州", 30)
        self.draw_vol(data, os.path.join(self.directory, "hz_30.jpeg"))
        data = self.vol_tool.get_items("武汉", "合计", 30)
        self.draw_vol(data, os.path.join(self.directory, "wh_30.jpeg"))
        data = self.vol_tool.get_items("北京", "bj", 30)
        self.draw_vol(data, os.path.join(self.directory, "bj_30.jpeg"))

    def run(self):
        try:
            logger.info("start draw img.")
            self.draw_vol_1days()
            self.draw_vol_7days()
            self.draw_vol_monthly()
            self.draw_price_trends()
            logger.info("end draw img.")
        except:
            logger.error("error.")


if __name__ == "__main__":
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(file_dir, "../../db/house.db")
    directory = "/app/www/img/"
    dao = DailyVolDAO(db_path)
    lj_dao = LianjiaDAO(None, db_path)
    price_tool = LijiaPriceTrendsGenerator(lj_dao)
    vol_tool = VolDataGenerator(dao)
    draw_tool = VolImgProducer(vol_tool, price_tool, directory)
    draw_tool.run()
