# -*- coding: utf-8 -*-
"""
分类 / 热门题库 / 模拟考试 管理
================
三者的共同点：
  - category 是题目的归属，count 由 refresh_counts() 自动维护；
  - bank / exam 与题目是多对多关系，各自靠中间表（bank_question / exam_question）挂载，
    挂载页把「全量题目」列出来勾选，保存时整体替换该实体的关联记录。
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import execute, executemany, query, query_one, scalar
from helpers import refresh_counts

taxonomy_bp = Blueprint('taxonomy', __name__)

EXAM_STATUSES = ['进行中', '未开始', '已结束']
STATUS_COLORS = {'进行中': '#4F46E5', '未开始': '#FFD166', '已结束': '#999999'}

DEFAULT_CATEGORY_COLOR = '#4F46E5'
DEFAULT_CATEGORY_BG = '#ede9fe'


# ---------------------------------------------------------------------------
# 公用小工具
# ---------------------------------------------------------------------------
def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def valid_question_ids(raw_ids):
    """只保留真实存在的题目 id，防止手工构造表单塞进无效 id"""
    ids = []
    for raw in raw_ids:
        qid = to_int(raw, None)
        if qid is not None and qid not in ids:
            ids.append(qid)
    if not ids:
        return []
    placeholders = ','.join('?' * len(ids))
    rows = query('SELECT id FROM question WHERE id IN (%s)' % placeholders, ids)
    existing = {row['id'] for row in rows}
    return [qid for qid in ids if qid in existing]


def all_questions_for_mount():
    return query(
        'SELECT q.id, q.title, q.type, q.difficulty, c.name AS category_name '
        'FROM question q LEFT JOIN category c ON c.id = q.category_id '
        'ORDER BY q.id'
    )


def selected_ids(table, id_column, entity_id):
    rows = query('SELECT question_id FROM %s WHERE %s = ?' % (table, id_column), (entity_id,))
    return {row['question_id'] for row in rows}


# ===========================================================================
# 学科分类
# ===========================================================================
@taxonomy_bp.route('/categories')
def category_list():
    edit_id = request.args.get('edit', type=int)
    editing = query_one('SELECT * FROM category WHERE id = ?', (edit_id,)) if edit_id else None
    categories = query('SELECT * FROM category ORDER BY id')
    return render_template('category_list.html', categories=categories, editing=editing)


@taxonomy_bp.route('/categories/save', methods=['POST'])
def category_save():
    cid = request.form.get('id', type=int)
    name = (request.form.get('name') or '').strip()
    icon = (request.form.get('icon') or '').strip()
    color = (request.form.get('color') or '').strip() or DEFAULT_CATEGORY_COLOR
    bg_color = (request.form.get('bg_color') or '').strip() or DEFAULT_CATEGORY_BG

    if not name:
        flash('分类名称不能为空', 'error')
        return redirect(url_for('taxonomy.category_list'))

    duplicate = query_one('SELECT id FROM category WHERE name = ? AND id <> ?', (name, cid or 0))
    if duplicate:
        flash('分类名称「%s」已存在' % name, 'error')
        return redirect(url_for('taxonomy.category_list'))

    if cid:
        execute('UPDATE category SET name = ?, icon = ?, color = ?, bg_color = ? WHERE id = ?',
                (name, icon, color, bg_color, cid))
        flash('分类「%s」已保存' % name, 'success')
    else:
        execute('INSERT INTO category(name, icon, color, bg_color) VALUES(?,?,?,?)',
                (name, icon, color, bg_color))
        flash('分类「%s」已新增' % name, 'success')

    refresh_counts()
    return redirect(url_for('taxonomy.category_list'))


@taxonomy_bp.route('/categories/<int:cid>/delete', methods=['POST'])
def category_delete(cid):
    used = scalar('SELECT COUNT(*) FROM question WHERE category_id = ?', (cid,))
    if used:
        flash('该分类下还有 %d 道题目，请先把它们改到其他分类或删除后再删分类' % used, 'error')
    else:
        execute('DELETE FROM category WHERE id = ?', (cid,))
        flash('分类已删除', 'success')
    return redirect(url_for('taxonomy.category_list'))


# ===========================================================================
# 热门题库
# ===========================================================================
@taxonomy_bp.route('/banks')
def bank_list():
    banks = query('SELECT id, title, "desc", cover, question_count, joined, tag FROM bank ORDER BY id')
    return render_template('bank_list.html', banks=banks)


@taxonomy_bp.route('/banks/new', methods=['GET', 'POST'])
def bank_create():
    return _bank_form()


@taxonomy_bp.route('/banks/<int:bid>/edit', methods=['GET', 'POST'])
def bank_edit(bid):
    return _bank_form(bid)


def _bank_form(bid=None):
    current = None
    if bid is not None:
        current = query_one('SELECT id, title, "desc", cover, question_count, joined, tag FROM bank WHERE id = ?', (bid,))
        if current is None:
            flash('题库不存在或已被删除', 'error')
            return redirect(url_for('taxonomy.bank_list'))

    if request.method == 'POST':
        snap = {
            'title': (request.form.get('title') or '').strip(),
            'desc': (request.form.get('desc') or '').strip(),
            'cover': (request.form.get('cover') or '').strip(),
            'tag': (request.form.get('tag') or '').strip(),
            'joined': to_int(request.form.get('joined'), 0),
        }
        if not snap['title']:
            flash('题库名称不能为空', 'error')
        elif snap['joined'] < 0:
            flash('已加入人数不能为负数', 'error')
        else:
            if bid is None:
                execute('INSERT INTO bank(title, "desc", cover, tag, joined) VALUES(?,?,?,?,?)',
                        (snap['title'], snap['desc'], snap['cover'], snap['tag'], snap['joined']))
                flash('题库已新增', 'success')
            else:
                execute('UPDATE bank SET title = ?, "desc" = ?, cover = ?, tag = ?, joined = ? WHERE id = ?',
                        (snap['title'], snap['desc'], snap['cover'], snap['tag'], snap['joined'], bid))
                flash('题库已保存', 'success')
            return redirect(url_for('taxonomy.bank_list'))

        # 校验失败：回填错误时用户填过的内容
        current = snap

    if current is None:
        current = {'title': '', 'desc': '', 'cover': '', 'tag': '', 'joined': 0}

    return render_template('bank_form.html', bank=current, is_new=(bid is None))


@taxonomy_bp.route('/banks/<int:bid>/delete', methods=['POST'])
def bank_delete(bid):
    execute('DELETE FROM bank_question WHERE bank_id = ?', (bid,))
    execute('DELETE FROM bank WHERE id = ?', (bid,))
    flash('题库已删除', 'success')
    return redirect(url_for('taxonomy.bank_list'))


@taxonomy_bp.route('/banks/<int:bid>/questions', methods=['GET', 'POST'])
def bank_questions(bid):
    bank = query_one('SELECT id, title FROM bank WHERE id = ?', (bid,))
    if bank is None:
        flash('题库不存在或已被删除', 'error')
        return redirect(url_for('taxonomy.bank_list'))

    if request.method == 'POST':
        chosen = valid_question_ids(request.form.getlist('question_ids'))
        execute('DELETE FROM bank_question WHERE bank_id = ?', (bid,))
        if chosen:
            executemany('INSERT INTO bank_question(bank_id, question_id) VALUES(?,?)',
                        [(bid, qid) for qid in chosen])
        refresh_counts()
        flash('「%s」已挂载 %d 道题目' % (bank['title'], len(chosen)), 'success')
        return redirect(url_for('taxonomy.bank_list'))

    return render_template(
        '_mount.html',
        entity_label='题库挂载题目',
        entity_title='正在为题库「%s」挂载题目' % bank['title'],
        action_url=url_for('taxonomy.bank_questions', bid=bid),
        back_url=url_for('taxonomy.bank_list'),
        questions=all_questions_for_mount(),
        selected=selected_ids('bank_question', 'bank_id', bid),
    )


# ===========================================================================
# 模拟考试
# ===========================================================================
@taxonomy_bp.route('/exams')
def exam_list():
    exams = query('SELECT * FROM exam ORDER BY id')
    return render_template('exam_list.html', exams=exams, statuses=EXAM_STATUSES)


@taxonomy_bp.route('/exams/new', methods=['GET', 'POST'])
def exam_create():
    return _exam_form()


@taxonomy_bp.route('/exams/<int:eid>/edit', methods=['GET', 'POST'])
def exam_edit(eid):
    return _exam_form(eid)


def _exam_form(eid=None):
    current = None
    if eid is not None:
        current = query_one('SELECT * FROM exam WHERE id = ?', (eid,))
        if current is None:
            flash('考试不存在或已被删除', 'error')
            return redirect(url_for('taxonomy.exam_list'))

    if request.method == 'POST':
        status = (request.form.get('status') or '').strip()
        snap = {
            'title': (request.form.get('title') or '').strip(),
            'cover': (request.form.get('cover') or '').strip(),
            'date': (request.form.get('date') or '').strip(),
            'duration': (request.form.get('duration') or '').strip(),
            'joined': to_int(request.form.get('joined'), 0),
            'status': status,
            # 状态色留空时按状态取默认色，省得每次手填
            'status_color': (request.form.get('status_color') or '').strip()
                            or STATUS_COLORS.get(status, '#4F46E5'),
        }
        if not snap['title']:
            flash('考试名称不能为空', 'error')
        elif status not in EXAM_STATUSES:
            flash('请选择合法的考试状态', 'error')
        elif snap['joined'] < 0:
            flash('已参加人数不能为负数', 'error')
        else:
            if eid is None:
                execute('INSERT INTO exam(title, cover, date, duration, total_count, joined, status, status_color) '
                        'VALUES(?,?,?,?,0,?,?,?)',
                        (snap['title'], snap['cover'], snap['date'], snap['duration'],
                         snap['joined'], snap['status'], snap['status_color']))
                flash('考试已新增，可继续为它挂载题目', 'success')
            else:
                execute('UPDATE exam SET title = ?, cover = ?, date = ?, duration = ?, joined = ?, '
                        'status = ?, status_color = ? WHERE id = ?',
                        (snap['title'], snap['cover'], snap['date'], snap['duration'],
                         snap['joined'], snap['status'], snap['status_color'], eid))
                flash('考试已保存', 'success')
            return redirect(url_for('taxonomy.exam_list'))

        current = snap

    if current is None:
        current = {'title': '', 'cover': '', 'date': '', 'duration': '',
                   'joined': 0, 'status': '进行中', 'status_color': STATUS_COLORS['进行中']}

    return render_template('exam_form.html', exam=current, is_new=(eid is None), statuses=EXAM_STATUSES)


@taxonomy_bp.route('/exams/<int:eid>/delete', methods=['POST'])
def exam_delete(eid):
    execute('DELETE FROM exam_question WHERE exam_id = ?', (eid,))
    execute('DELETE FROM exam WHERE id = ?', (eid,))
    flash('考试已删除', 'success')
    return redirect(url_for('taxonomy.exam_list'))


@taxonomy_bp.route('/exams/<int:eid>/questions', methods=['GET', 'POST'])
def exam_questions(eid):
    exam = query_one('SELECT id, title FROM exam WHERE id = ?', (eid,))
    if exam is None:
        flash('考试不存在或已被删除', 'error')
        return redirect(url_for('taxonomy.exam_list'))

    if request.method == 'POST':
        chosen = valid_question_ids(request.form.getlist('question_ids'))
        execute('DELETE FROM exam_question WHERE exam_id = ?', (eid,))
        if chosen:
            executemany('INSERT INTO exam_question(exam_id, question_id) VALUES(?,?)',
                        [(eid, qid) for qid in chosen])
        refresh_counts()
        flash('「%s」已挂载 %d 道题目' % (exam['title'], len(chosen)), 'success')
        return redirect(url_for('taxonomy.exam_list'))

    return render_template(
        '_mount.html',
        entity_label='考试挂载题目',
        entity_title='正在为考试「%s」挂载题目' % exam['title'],
        action_url=url_for('taxonomy.exam_questions', eid=eid),
        back_url=url_for('taxonomy.exam_list'),
        questions=all_questions_for_mount(),
        selected=selected_ids('exam_question', 'exam_id', eid),
    )