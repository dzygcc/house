#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import time

def convert2datetime(str):
    # 20160101
    if len(str) == 8:
        print time.strptime(str, '%Y%m%d')
        return datetime.datetime(*time.strptime(str, '%Y%m%d')[:6])
    # 2016-01-01
    if len(str) == 10:
        return datetime.datetime(*time.strptime(str, '%Y-%m-%d')[:6])

def is_in_same_month(str1, str2):
    d1 = convert2datetime(str1)
    d2 = convert2datetime(str2)
    if d1.month == d2.month and d1.year == d2.year:
        return True
    else:
        return False

if __name__ == "__main__":
    print convert2datetime("20160101")
    print convert2datetime("2016-01-01")