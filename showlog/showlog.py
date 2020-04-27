#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-08-15
# @Author  : tielemao
# @Email   : tielemao@163.com
# @File    : showlog.py

from alert import app, db
from alert.models import User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
