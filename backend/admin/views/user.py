# -*- coding: utf-8 -*-
"""用户与答题记录查询（只读）"""

from flask import Blueprint, flash, redirect, render_template, url_for

from db import query, query_one, scalar
from helpers import build_pager, request_page_args

user_bp = Blueprint('user', __name__)


def format_accuracy(correct, total):
    return ('%d%%' % round(correct / total * 100)) if total else '0%'


@user_bp.route('/users')
def index():
    total = scalar('SELECT COUNT(*) FROM user')
    page, per_page = request_page_args()
    _, offset, pager = build_pager(total, page, per_page)

    rows = query(
        'SELECT u.id, u.nickname, u.avatar, u.created_at, '
        '       COUNT(r.id) AS record_count, '
        '       COALESCE(SUM(r.total), 0) AS answer_total, '
        '       COALESCE(SUM(r.correct), 0) AS answer_correct, '
        '       (SELECT COUNT(*) FROM wrong_item w WHERE w.user_id = u.id) AS wrong_count '
        'FROM user u LEFT JOIN user_record r ON r.user_id = u.id '
        'GROUP BY u.id ORDER BY u.id LIMIT ? OFFSET ?',
        (per_page, offset)
    )

    users = [{
        'id': row['id'],
        'nickname': row['nickname'],
        'avatar': row['avatar'],
        'created_at': row['created_at'],
        'record_count': row['record_count'],
        'answer_total': row['answer_total'],
        'wrong_count': row['wrong_count'],
        'accuracy': format_accuracy(row['answer_correct'], row['answer_total']),
    } for row in rows]

    return render_template('user_list.html', users=users, pager=pager)


@user_bp.route('/users/<int:uid>')
def detail(uid):
    current = query_one('SELECT * FROM user WHERE id = ?', (uid,))
    if current is None:
        flash('用户不存在', 'error')
        return redirect(url_for('user.index'))

    records = query('SELECT * FROM user_record WHERE user_id = ? ORDER BY id DESC', (uid,))
    wrong_items = query('SELECT * FROM wrong_item WHERE user_id = ? ORDER BY created_at DESC', (uid,))

    answer_total = sum(r['total'] for r in records)
    answer_correct = sum(r['correct'] for r in records)
    summary = {
        'record_count': len(records),
        'answer_total': answer_total,
        'wrong_count': len(wrong_items),
        'accuracy': format_accuracy(answer_correct, answer_total),
        'active_days': len({r['date'] for r in records if r['date']}),
    }

    return render_template('user_detail.html', user=current, records=records,
                           wrong_items=wrong_items, summary=summary)