# -*- coding: utf-8 -*-
"""
页面公用小工具
================
题型映射、选项文本「拆分 / 合并」、分页参数计算。
拆出来是为了让各个 views 模块不用重复写同样的逻辑。
"""

import re
from urllib.parse import urlencode

from flask import request

from db import execute

# ---------------------------------------------------------------------------
# 常量（与小程序后端 app.py 的 seed_data 保持一致）
# ---------------------------------------------------------------------------
TYPE_DISPLAY = {'single': '单选', 'multi': '多选', 'judge': '判断', 'fill': '填空'}
TYPE_KEYS = ['single', 'multi', 'judge', 'fill']
DIFFICULTIES = ['简单', '中等', '困难']
OPTION_LETTERS = ['A', 'B', 'C', 'D']
PER_PAGE_CHOICES = [10, 20, 50]
DEFAULT_PER_PAGE = 10

# 判断题固定两个选项
JUDGE_OPTIONS = {'A': '正确', 'B': '错误'}

# ---------------------------------------------------------------------------
# 选项文本处理
#   数据库里选项存成一整串 "A. 甲 B. 乙"，后台表单要拆成 4 个输入框，
#   保存时再拼回去，避免手工拼接出错。
# ---------------------------------------------------------------------------
_OPTION_RE = re.compile(r'([A-Z])[\.、]?\s*(.*?)(?=\s+[A-Z][\.、]|$)')


def split_options(text):
    """'A. 甲 B. 乙' -> {'A': '甲', 'B': '乙'}，供编辑表单回填"""
    result = {}
    if not text:
        return result
    for match in _OPTION_RE.finditer(text.strip()):
        result[match.group(1)] = match.group(2).strip()
    return result


def join_options(values):
    """{'A': '甲', 'B': '乙'} -> 'A. 甲 B. 乙'，空值跳过"""
    parts = []
    for letter in OPTION_LETTERS:
        value = (values.get(letter) or '').strip()
        if value:
            parts.append('%s. %s' % (letter, value))
    return ' '.join(parts)


# ---------------------------------------------------------------------------
# 分页
# ---------------------------------------------------------------------------
def request_page_args():
    """从 URL query 里取 (page, per_page)，非法值一律回退到默认"""
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get('per_page', DEFAULT_PER_PAGE))
    except (TypeError, ValueError):
        per_page = DEFAULT_PER_PAGE
    if per_page not in PER_PAGE_CHOICES:
        per_page = DEFAULT_PER_PAGE
    return max(1, page), per_page


def build_pager(total, page, per_page):
    """
    计算分页信息，返回 (page, offset, pager)。
    page 会被夹到合法范围内，避免「删到最后一页时空列表」或 offset 越界。
    """
    pages = max(1, (total + per_page - 1) // per_page)
    page = min(max(1, page), pages)
    offset = (page - 1) * per_page

    start = max(1, page - 2)
    end = min(pages, page + 2)

    # 翻页链接要带上除 page 以外的所有筛选条件
    others = {k: v for k, v in request.args.items() if k != 'page'}

    pager = {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
        'has_prev': page > 1,
        'has_next': page < pages,
        'prev_page': page - 1,
        'next_page': page + 1,
        'window': list(range(start, end + 1)),
        'qs': urlencode(others),
    }
    return page, offset, pager


def like_keyword(raw):
    """把用户输入的关键词包装成 LIKE 参数；空关键词返回 None"""
    kw = (raw or '').strip()
    if not kw:
        return None
    # 转义 LIKE 通配符，避免用户输入 % 或 _ 时匹配到全部
    kw = kw.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return '%' + kw + '%'


# ---------------------------------------------------------------------------
# 跳转与冗余计数
# ---------------------------------------------------------------------------
def safe_next(default):
    """
    取站内跳转地址（用于「保存 / 删除后回到原来那一页筛选结果」）。
    只接受以单个 / 开头的站内路径，防止被构造成跳转到外部站点。
    """
    for source in (request.form, request.args):
        nxt = source.get('next') or ''
        if nxt.startswith('/') and not nxt.startswith('//'):
            return nxt
    return default


def refresh_counts():
    """
    重算冗余计数字段，保证与小程序端展示一致：
        category.count      <- 该分类题目数（首页分类宫格显示的就是它）
        bank.question_count <- 该题库挂载的题目数
        exam.total_count    <- 该考试挂载的题目数
    后台增删题目或改动挂载关系后必须调用，
    否则小程序端显示的数字会和实际题目对不上。
    """
    execute('UPDATE category SET count = '
            '(SELECT COUNT(*) FROM question WHERE question.category_id = category.id)')
    execute('UPDATE bank SET question_count = '
            '(SELECT COUNT(*) FROM bank_question WHERE bank_question.bank_id = bank.id)')
    execute('UPDATE exam SET total_count = '
            '(SELECT COUNT(*) FROM exam_question WHERE exam_question.exam_id = exam.id)')