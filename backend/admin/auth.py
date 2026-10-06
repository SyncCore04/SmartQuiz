# -*- coding: utf-8 -*-
"""
后台登录鉴权
================
现有小程序接口是完全没有登录态的（游客登录），所以后台必须自己一套：
  - 用 Flask session 保存登录标记（cookie 存的是签名后的 session id）
  - 全局拦截在 admin.py 里统一挂 before_request，默认「全部需要登录」
  - 账号密码来自 config.py，不新建数据库表，零 schema 变更
"""

from functools import wraps

from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from config import ADMIN_PASSWORD_HASH, ADMIN_USERNAME

auth_bp = Blueprint('auth', __name__)

# 免登录即可访问的 endpoint（登录页本身 + 静态资源）
PUBLIC_ENDPOINTS = {'auth.login', 'static'}


def is_logged_in():
    """当前会话是否已登录"""
    return bool(session.get('admin_logged_in'))


def login_required(view):
    """给单个视图用的装饰器；全局拦截见 admin.py 的 before_request"""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('auth.login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard.index'))

    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            session['admin_user'] = username

            # 登录后跳回原页面；只接受站内相对路径，防开放重定向
            nxt = request.args.get('next') or ''
            if not nxt.startswith('/') or nxt.startswith('//'):
                nxt = url_for('dashboard.index')
            return redirect(nxt)

        error = '用户名或密码错误'

    return render_template('login.html', error=error)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))