#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : ${DATE} ${HOUR}:${MINUTE}
# @Author  : wuweizeng
# @Email   : tielemao@163.com
# @Site    : ${SITE}
# @File    : ${NAME}.py
# @Software: ${PRODUCT_NAME}

import os.path
import time
from datetime import datetime, timedelta
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_apscheduler import APScheduler

# 注册APScheduler
scheduler = APScheduler()

# 每天一小时自检一次
@scheduler.task('interval', id='do_job_1', hours=1)
def check_self():
    """
    插入一条自检信息到当天的log中
    :return:
    """
    if time.localtime().tm_isdst:
        # 如果是夏令时（dst）则只需加15小时时差 获取服务器上最新log的日期
        now_time = datetime.now() + timedelta(hours=15)
    else:
        # 冬令时为加16小时
        now_time = datetime.now() + timedelta(hours=16)
    filename = str(now_time.date()) + '.log'
    base_path = "/opt/skype/logs"
    logfile = os.path.sep.join((base_path, filename))
    try:
        with open(logfile, 'a', encoding='utf-8', errors='ignore') as f:
            f.write("\n [CRITICAL] [ %s ] ShowAlertLog进行自检测试，如能看到此信息，表示读取当天LOG并获取报警的工作正常。\n" % time.strftime("%Y-%m-%d %H:%M", time.localtime()))
    except IOError:
        result = "Not such file or directory. Please call wuweizeng."
        print(result)
        return result

app = Flask(__name__)
app.debug = False
app.use_reloader = False
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bookstrap = Bootstrap(app)

from alert import routes, models
scheduler.init_app(app)
scheduler.start()