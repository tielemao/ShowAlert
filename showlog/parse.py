#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-15
# @update  : 2019-11-07
# @Author  : tielemao
# @Email   : tielemao@163.com
# @File    : parse.py


import os, sys, re
import chardet
import json
import time
from datetime import datetime, timedelta
from chinese_calendar import is_workday, is_holiday


class Parse:

    def __init__(self):
        self.critical_json = []
        self.flush_list = []
        self.holiday_list = []
        self.filter_list = []

    def file_path(self):
        """server path: /opt/skype/logs
        e.g: /opt/skype/logs/2019-04-28.log
        """
        if time.localtime().tm_isdst:
            # 如果是夏令时（dst）则只需加15小时时差 获取服务器上最新log的日期
            now = datetime.now() + timedelta(hours=15)
        else:
            # 冬令时为加16小时
            now = datetime.now() + timedelta(hours=16)
        filename = str(now.date()) + '.log'
        base_path = "/opt/skype/logs"
        logfile = os.path.sep.join((base_path, filename))
        return logfile

    def code_type(self):
        """
        获取编码类型
        """
        try:
            with open(self.file_path(), 'rb') as f:
                content = f.read(1024)
            # 判断编码类型来进行解码，因为出现过是windows-1252的
            coding_type = chardet.detect(content)["encoding"]
            return coding_type
        except IOError:
            print("Not such file or directory.")

    def self_test(self):
        """
        程序自检
        """
        logfile = self.file_path()
        try:
            if os.stat(logfile).st_size == 0:
                return "【CRITICAL】【 %s 】ShowAlertLog 自检中，当天Log日志疑为空白，请联系值班同事 \n" % time.strftime("%Y-%m-%d %H:%M",
                                                                                                       time.localtime())
            if os.stat(logfile).st_size > 0:
                # with open(self.file_path(), 'a', encoding='utf-8', errors='ignore') as f:
                    # f.write("[CRITICAL] [ %s ] ShowAlertLog进行自检测试，如能看到此信息，表示读取当天LOG并获取报警的工作正常。\n" % time.strftime("%Y-%m-%d %H:%M", time.localtime())
                return "【自检信息】【 %s 】ShowAlertLog 自检中，目前工作正常。\n" % time.strftime("%Y-%m-%d %H:%M", time.localtime())
        except IOError:
            result = "Not such file or directory."
            return result

    def holiday_and_dev(self, line):
        """
        判断是否为假期和开发服务器，同时为True才返回holiday。
        line为传进来的每一行日志。
        :return:
        """
        now = datetime.now()
        now2 = now + timedelta(hours=15)  # 需要加15小时时差才能获取到服务器上最新log的日期
        dev = ["devel","beta"]
        for hostname in dev:
            try:
                # 判断是假期的同时满足是开发服务器
                if is_holiday(now2) and hostname in line:
                    return "holiday"
            except NotImplementedError:
                return "NotImplementedError"

    def show_conf(self):
        """
        展示过滤条件的配置用
        :return:
        """
        basedir = os.path.abspath(os.path.dirname(__file__))
        filter_json = os.path.sep.join((basedir, 'conf/filter_cond.json'))
        try:
            with open(filter_json, 'r', encoding='utf-8', errors='ignore') as f:
                cond_json = json.load(f)
            return cond_json['cond']
        except IOError:
            result = "filter_cond.json 文件可能不存在，请联系值班同事。"
            return result

    def append_cond(self, keyword_key, keyword_list):
        """
        追加过滤条件到filter_cond.json文件中
        :param keyword_key: 键名
        :param keyword_list: 以空格分隔的键值，方便转为列表
        :return:
        """
        basedir = os.path.abspath(os.path.dirname(__file__))
        filter_json = os.path.sep.join((basedir, 'conf/filter_cond.json'))
        keyword_value = keyword_list.split()
        try:
            with open(filter_json, 'r', encoding='utf-8', errors='ignore') as f:
                cond_json = json.load(f)
            cond_json['cond'].append({keyword_key:keyword_value})
            update_cond_json = json.dumps(cond_json)
            with open(filter_json, 'w', encoding='utf-8', errors='ignore') as f2:
                f2.write(update_cond_json)
            return update_cond_json
        except IOError:
            result = "filter_cond.json 文件可能不存在，请联系值班同事。"
            return result

    def judge(self, line, value):
        """
        读取过滤条件，判断是否忽略报警,类似all方法
        :param line: log的每一行
        :param value: 列表，每一个元素为过滤关键词，不能为空
        :return: 不符合的时候返回False，符合忽略的时候返回True
        """
        for cond in value:
            if cond not in line:
                return False
        return True

    def filter_alter(self, line):
        """
        判断是否符合过滤展示
        :param line: log的一行日志
        :param cond_json: 读取过滤条件的json配置文件后返回的json
        :return: 使用any方法判断逻辑结果的列表中有否存在True，有则返回True
        """
        basedir = os.path.abspath(os.path.dirname(__file__))
        filter_json = os.path.sep.join((basedir, 'conf/filter_cond.json'))
        try:
            with open(filter_json, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
        except IOError:
            # 不存在这个过滤配置文件的时候，直接返回None表示全部展示。
            return
        cond_list = []
        cond_json = data['cond']
        for dic in cond_json:
            for value in dic.values():
                cond_list.append(self.judge(line, value))
        return any(cond_list)

    def ignore(self):
        """
        执行类过滤器
        :return:
        """
        pass

    def read_log(self):
        try:
            with open(self.file_path(), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # 替换`#n#`
            new_content = content.replace("#n#", '\n')
            return new_content
        except IOError:
            result = "Not such file or directory."
            return result

    def warn(self):
        """
        警报级别的日志
        :return: 生成器
        """
        try:
            with open(self.file_path(), 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'WARN' in line:
                        yield line
        except IOError:
            result = "Not such file or directory."
            return result


    def critical(self):
        """
        生成critical+urgency级别的全部日志
        :return: 生成器
        """
        try:
            with open(self.file_path(), 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'CRITICAL' in line or 'URGENCY' in line:
                        yield line
        except IOError:
            result = "Not such file or directory."
            return result

    def flush(self):
        """
        生成critical+urgency级别日志最新的N行，用于自动刷新
        :return: List
        """
        try:
            self.flush_list.clear()
            self.holiday_list.clear()
            self.filter_list.clear()
            with open(self.file_path(), 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'CRITICAL' in line or 'URGENCY' in line:
                        holiday = self.holiday_and_dev(line)  # 判断今天是否为假期且服务器为开发类
                        if self.filter_alter(line):
                        # 判断是否满足过滤忽略警报,有一个过滤器为真则跳过展示
                            self.filter_list.append(line)
                            continue
                        if holiday == "holiday":
                            # 将该行line放一下列表中，之后再统一追加到一个HolidayAndDev.log中
                            self.holiday_list.append(line)
                            # 满足条件则跳过展示，忽略显示开发类服务器的消息
                            continue  # 不再往下执行语句，开始下一轮循环
                        if holiday == "NotImplementedError":
                            # 补入一句警报，并且继续录入日志，不能加continue跳过
                            self.flush_list.append("no available data for year 2020, only year between [2004, 2019] supported.")
                        self.flush_list.append(line)
            # with open('/ShowAlertLog/showlog/logs/HolidayAndDev.log', 'a', encoding='utf-8', errors='ignore') as f:
                # 追加写入过滤掉的日志来做检查
                # for i in self.holiday_list:
                    # print(i, file=f)
            try:
                result = self.flush_list[-1:-21:-1]
            except StopIteration:
                result = self.flush
            return result
        except IOError:
            result = "Not such file or directory."
            return result


    def json_flush(self):
        """
        获取10条以json展示的最新critical级别的警报
        :return: list，嵌套json
        """
        try:
            self.critical_json.clear()
            with open(self.file_path(), 'r', encoding='utf-8', errors='ignore') as f:
                i = 0
                for line in f:
                    if 'CRITICAL' in line or 'URGENCY' in line:
                        i += 1
                        if 'UE-ALERT' not in line:
                            log_time = line.split('- DROP(*)')[0]
                            server_time = line.split('- DROP(*)')[1].split("[")[2].split("]")[0].strip()
                            alert_level = line.split('[')[1].replace(']', '').strip()
                            content = line.split("-", 6)[6].strip()
                            self.critical_json.append({
                                i: {
                                    'log_time': log_time,
                                    'level': alert_level,
                                    'server_time': server_time,
                                    'content': content,
                                }
                            })
                        else:
                            log_time = line.split('- DROP - UE-ALERT (*)')[0]
                            server_time = line.split('- DROP - UE-ALERT (*)')[1].split("[")[2].split("]")[0].strip()
                            alert_level = line.split('[')[1].replace(']', '').strip()
                            content = line.split("-", 8)[8].strip()
                            self.critical_json.append({
                                i: {
                                    'log_time': log_time,
                                    'level': alert_level,
                                    'server_time': server_time,
                                    'content': content,
                                }
                            })
            try:
                result = self.critical_json[-1:-11:-1]
            except StopIteration:
                result = self.critical_json
            result.reverse()
            return result
        except IOError:
            result = "Not such file or directory."
            return result

log_parse = Parse()  # 采用单例模式
