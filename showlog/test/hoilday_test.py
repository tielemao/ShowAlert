#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 19:36
# @Update  : 2019/9/26
# @Author  : tielemao
# @Email   : tielemao@163.com
# @File    : hoilday_test.py
# @Desc    : 测试判断法定节假日

import datetime
from chinese_calendar import is_workday, is_holiday


def test_chinesecalendar():
    """
    测试判断chinese_calendar这个库CC
    :return:
    """
    test_day = datetime.date(2019, 10, 1)
    print("是工作日：%s" % is_workday(test_day))
    print("是假日：%s" % is_holiday(test_day))


def test_holiday_and_dev(line):
    """
    判断是否为假期和开发服务器，同时为True才返回True。
    :return: 布尔值
    """
    now = datetime.datetime.now()
    now2 = now + datetime.timedelta(hours=15)  # 需要加15小时时差才能获取到服务器上最新log的日期
    test_day = datetime.date(2019, 10, 2) # 测试的时候修改这里, 分别测2019，10，2；2019，10，8；2020，10，2之类
    dev = ["devel","beta"]
    for hostname in dev:
        try:
            if is_holiday(test_day) and hostname in line:
            # 测试的时候使用 if is_holiday(test_day) and hostname in line:
                return "holiday"
        except NotImplementedError:
            return "NotImplementedError"

def test_flush(filepath):
    """
    传入文件路径，测试判断法定假期及开发服务器和Critical级别的报警
    :param filepath: 测试用的log文件路径
    :return: TestHolidayAndDev.log 及 TestFlushCritical.log
    """
    flush_list = []
    holiday_list = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'CRITICAL' in line or 'URGENCY' in line:
                    holiday = test_holiday_and_dev(line)  # 判断今天是否为假期且服务器为开发类
                    if holiday == "holiday":
                        # 将该行line放一下列表中，之后再统一追加到一个HolidayAndDev.log中
                        holiday_list.append(line)
                        # 满足条件则跳过展示，忽略显示开发类服务器的消息
                        continue  # 不再往下执行语句，开始下一轮循环
                    if holiday == "NotImplementedError":
                        # 补入一句警报，并且继续录入日志，不能加continue跳过
                        flush_list.append("no available data for year 2020, only year between [2004, 2019] supported.")
                    flush_list.append(line)
        try:
            with open('../logs/TestHolidayAndDev.log', 'a', encoding='utf-8', errors='ignore') as f:
                # 测试追加写入过滤掉的日志来做检查
                for i in holiday_list:
                    print(i, file=f)
            with open('../logs/TestFlushCritical.log', 'a', encoding='utf-8', errors='ignore') as f:
                # 测试追加写入CRITICAL级别的日志
                for i in flush_list:
                    print(i, file=f)
        except IOError:
            result = "Not such file or directory."
            return result
    except IOError:
        result = "Not such file or directory."
        return result

test_flush("../logs/2019-04-10.log")
