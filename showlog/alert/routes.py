#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-08-01
# @Update  : 2019-10-30
# @Author  : wuweizeng
# @Email   : tielemao@163.com
# @File    : routes.py
# @Desc    : 路由分发

from alert import app, db
from parse import Parse, log_parse
from alert.models import User
from alert.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, flash, redirect, url_for


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', tiele='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/warn')
def warn():
    result = log_parse.warn()  # 与下面的flush不同，这个是获取全部的critical信息
    return render_template('warn.html', res=result)


@app.route('/critical')
def critical():
    result = log_parse.critical()  # 与下面的flush不同，这个是获取全部的critical信息
    return render_template('critical.html', res=result)


@app.route('/flush')
def flush():
    result = log_parse.flush()
    return render_template('flush.html', res=result)


@app.route('/json_flush')
def json_flush():
    result = log_parse.json_flush()
    return render_template('json_flush.html', res=result)


@app.route('/self_test')
def self_test():
    """
    程序自检
    :return:
    """
    result = log_parse.self_test()
    return render_template('self_test.html', res=result)


@app.route('/ignore', methods=['GET', 'POST'])
@login_required
def ignore():
    """
    过滤器，用于在flush页面忽略展示
    :return:
    """
    show = log_parse.show_conf()
    if request.method == 'POST':
        if request.form['keyword_key'] == '' or request.form['keyword_list'] == '':
            flash("关键词不能为空")
            return redirect(request.url)
        keyword_key = request.form['keyword_key']
        keyword_list = request.form['keyword_list']
        result = log_parse.append_cond(keyword_key, keyword_list)
        flash(result)
        return redirect(request.url)
    return render_template('ignore.html', res=show)