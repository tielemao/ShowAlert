#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : update: 2019-08-15
# @Author  : wuweizeng
# @Email   : tielemao@163.com
# @File    : config.py
# @description : 配置文件

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'K46338A11d6752d9'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'alert.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False