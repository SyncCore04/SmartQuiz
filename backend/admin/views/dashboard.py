# -*- coding: utf-8 -*-
"""数据看板：全站统计概览"""

from flask import Blueprint, render_template

from db import query, scalar

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    # ---------- 统计卡片 ----------
    user_count = scalar('SELECT COUNT(*) FROM user')
    question_count = scalar('SELECT COUNT(*) FROM question')
    answer_total = scalar('SELECT COALESCE(SUM(total), 0) FROM user_record')
    answer_correct = scalar('SELECT COALESCE(SUM(correct), 0) FROM user_record')
    accuracy = ('%d%%' % round(answer_correct / answer_total * 100)) if answer_total else '0%'

    stats = {
        'user_count': user_count,
        'question_count': question_count,
        'answer_total': answer_total,
        'accuracy': accuracy,
        'record_count': scalar('SELECT COUNT(*) FROM user_record'),
        'wrong_count': scalar('SELECT COUNT(*) FROM wrong_item'),
        'bank_count': scalar('SELECT COUNT(*) FROM bank'),
        'exam_count': scalar('SELECT COUNT(*) FROM exam'),
        'category_count': scalar('SELECT COUNT(*) FROM category'),
    }

    # ---------- 各分类题目数（柱状图，高度按最大值归一到 100） ----------
    rows = query(
        'SELECT c.name AS name, COUNT(q.id) AS n '
        'FROM category c LEFT JOIN question q ON q.category_id = c.id '
        'GROUP BY c.id ORDER BY n DESC, c.id'
    )
    max_n = max([r['n'] for r in rows], default=0)
    category_bars = [
        {'name': r['name'], 'n': r['n'], 'height': int(r['n'] / max_n * 100) if max_n else 0}
        for r in rows
    ]

    # ---------- 各题型数量 ----------
    type_rows = query('SELECT type, COUNT(*) AS n FROM question GROUP BY type_key ORDER BY n DESC')

    # ---------- 最近答题记录 ----------
    recent_records = query(
        'SELECT r.id, r.title, r.score, r.total, r.correct, r.wrong, r.date, u.nickname '
        'FROM user_record r LEFT JOIN user u ON u.id = r.user_id '
        'ORDER BY r.id DESC LIMIT 8'
    )

    return render_template(
        'dashboard.html',
        stats=stats,
        category_bars=category_bars,
        type_rows=type_rows,
        recent_records=recent_records,
    )