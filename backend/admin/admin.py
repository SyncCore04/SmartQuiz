# -*- coding: utf-8 -*-
"""
SmartQuiz 管理后台 —— 独立启动入口
================
与小程序接口（backend/app.py，端口 5000）完全分离：

  - 独立文件、独立进程、独立端口（默认 5001）
  - 只 import app.py 复用数据库路径，不改它一行代码
  - 与小程序共用同一个 database/smartquiz.db，
    因此后台改完题目，小程序端刷新即可看到，无需重启后端、无需删库

启动：python admin.py   （或双击项目根目录的 start-admin.bat）
默认账号：admin / admin123   （改密码见 config.py）
"""

import os
import sys

# 把 backend/admin 加入模块搜索路径，保证各模块能被正常 import
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, redirect, request, send_from_directory, session, url_for

from auth import PUBLIC_ENDPOINTS, auth_bp, is_logged_in
from config import HOST, PORT, SECRET_KEY
from db import DB_PATH
from views.dashboard import dashboard_bp
from views.question import question_bp
from views.swiper import swiper_bp
from views.taxonomy import taxonomy_bp
from views.user import user_bp

# ---------------------------------------------------------------------------
# 侧边栏导航（图标用内联 SVG，避免额外图标库依赖）
# ---------------------------------------------------------------------------
ICON_GRID = ('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>'
             '<rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>')
ICON_FILE = ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'
             '<line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="15" y2="17"/>')
ICON_FOLDER = '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
ICON_LAYERS = ('<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/>'
               '<polyline points="2 12 12 17 22 12"/>')
ICON_CLIPBOARD = ('<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
                  '<rect x="8" y="2" width="8" height="4" rx="1"/>')
ICON_USERS = ('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
              '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>')
ICON_IMAGE = ('<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>'
              '<polyline points="21 15 16 10 5 21"/>')

NAV_ITEMS = [
    {'label': '数据看板', 'url': '/', 'exact': True, 'icon': ICON_GRID},
    {'label': '题目管理', 'url': '/questions', 'icon': ICON_FILE},
    {'label': '学科分类', 'url': '/categories', 'icon': ICON_FOLDER},
    {'label': '热门题库', 'url': '/banks', 'icon': ICON_LAYERS},
    {'label': '模拟考试', 'url': '/exams', 'icon': ICON_CLIPBOARD},
    {'label': '用户与记录', 'url': '/users', 'icon': ICON_USERS},
    {'label': '首页轮播图', 'url': '/swipers', 'icon': ICON_IMAGE},
]

# ---------------------------------------------------------------------------
# 创建应用
#   显式指定模板/静态目录的绝对路径，
#   避免以脚本方式运行时 Flask 推断 root_path 出错。
# ---------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)
app.secret_key = SECRET_KEY

# 开发期改模板立即生效，不用重启
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True


def _asset_version(filename):
    """
    静态资源版本号（用文件修改时间）。
    加在 <link>/<script> 后面可避免浏览器缓存了旧样式，改了 CSS 却看不到效果。
    """
    path = os.path.join(BASE_DIR, 'static', filename)
    try:
        return int(os.path.getmtime(path))
    except OSError:
        return 0


@app.context_processor
def inject_layout():
    """给所有模板注入侧边栏、当前管理员、静态资源版本号"""
    path = request.path
    items = []
    for item in NAV_ITEMS:
        if item.get('exact'):
            active = path == item['url']
        else:
            active = path.startswith(item['url'])
        items.append(dict(item, active=active))
    return {
        'nav_items': items,
        'admin_user': session.get('admin_user', ''),
        'asset_v': _asset_version('css/admin.css'),
    }


@app.before_request
def require_login():
    """
    全局登录拦截：默认「所有页面都要登录」，登录页和静态资源除外。
    这样新增模块时忘记加装饰器也不会漏权限。
    """
    if request.endpoint in PUBLIC_ENDPOINTS:
        return None
    if not is_logged_in():
        return redirect(url_for('auth.login', next=request.path))
    return None


app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(question_bp)
app.register_blueprint(taxonomy_bp)
app.register_blueprint(user_bp)
app.register_blueprint(swiper_bp)


# ---------------------------------------------------------------------------
# 图片预览
#   小程序里的封面/轮播图用的是包内路径，例如 /images/photo-xxx_w400.jpg，
#   实际文件放在 front/images/。这里只做「只读预览」，让后台填路径时能核对是否写对。
#   注意：后台不提供图片上传，新增图片仍需手动放进 front/images/ 目录。
# ---------------------------------------------------------------------------
FRONT_IMAGES_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'front', 'images'))


@app.route('/media/<path:filename>')
def media(filename):
    """预览 front/images 目录下的图片（登录后才能访问，send_from_directory 自带路径穿越防护）"""
    return send_from_directory(FRONT_IMAGES_DIR, filename)


def image_url(path):
    """把 /images/xxx.jpg 转成后台可访问的预览地址；外链或空值原样返回"""
    path = (path or '').strip()
    if path.startswith('/images/'):
        return url_for('media', filename=path[len('/images/'):])
    return path


app.jinja_env.globals['image_url'] = image_url


if __name__ == '__main__':
    print('=' * 52)
    print('  SmartQuiz 管理后台')
    print('=' * 52)
    print('  地址     : http://%s:%d' % (HOST, PORT))
    print('  账号     : admin / admin123')
    print('  数据库   : %s' % os.path.abspath(DB_PATH))
    print('  小程序端 : 另一个窗口运行 app.py（端口 5000）')
    print('  停止服务 : Ctrl+C')
    print('=' * 52)
    # debug=False：避免 reloader 双进程导致端口占用、session 反复失效
    app.run(host=HOST, port=PORT, debug=False)