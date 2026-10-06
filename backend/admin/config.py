# -*- coding: utf-8 -*-
"""
管理后台配置
================
管理员账号、会话密钥、监听地址集中在这里，改配置只动这一个文件。
"""

import os

from werkzeug.security import generate_password_hash

# ---------------------------------------------------------------------------
# 管理员账号
#   默认账号 / 密码：admin / admin123
#   想改密码：改下面的默认值，或在启动前设置环境变量 SMARTQUIZ_ADMIN_PASSWORD
#   密码不明文保存，启动时用 werkzeug（Flask 自带依赖）生成哈希，登录时比对哈希。
# ---------------------------------------------------------------------------
ADMIN_USERNAME = os.environ.get('SMARTQUIZ_ADMIN_USER') or 'admin'

ADMIN_PASSWORD_HASH = os.environ.get('SMARTQUIZ_ADMIN_PASSWORD_HASH') or generate_password_hash(
    os.environ.get('SMARTQUIZ_ADMIN_PASSWORD') or 'admin123',
    method='pbkdf2:sha256',
)

# ---------------------------------------------------------------------------
# session 签名密钥：改了会导致已登录的管理员掉线
#   正式对外部署请用环境变量换成一段随机长字符串
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get('SMARTQUIZ_ADMIN_SECRET') or 'smartquiz-admin-dev-secret-2026'

# ---------------------------------------------------------------------------
# 监听地址：后台是内部工具，默认只允许本机访问
#   如需局域网内其他电脑访问，把 HOST 改成 0.0.0.0（注意后台无频率限制，慎用）
# ---------------------------------------------------------------------------
HOST = os.environ.get('SMARTQUIZ_ADMIN_HOST') or '127.0.0.1'
PORT = int(os.environ.get('SMARTQUIZ_ADMIN_PORT') or 5001)