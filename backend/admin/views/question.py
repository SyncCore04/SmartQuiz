# -*- coding: utf-8 -*-
"""
题目管理（后台核心模块）
================
列表（分类 / 题型 / 难度 / 关键词筛选 + 分页）、新增、编辑、删除、批量导入。

数据一致性说明：
  后台直接改的就是小程序读取的那张 question 表，因此保存后小程序端刷新即可生效，
  既不用重启后端，也不用删库重建。
"""

import ast

from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import execute, executemany, query, query_one, scalar
from helpers import (DIFFICULTIES, JUDGE_OPTIONS, OPTION_LETTERS, PER_PAGE_CHOICES,
                     TYPE_DISPLAY, build_pager, join_options, like_keyword,
                     refresh_counts, request_page_args, safe_next, split_options)

question_bp = Blueprint('question', __name__)

INSERT_SQL = ('INSERT INTO question(category_id, type, type_key, difficulty, title, options_text, answer, analysis) '
              'VALUES(:category_id, :type, :type_key, :difficulty, :title, :options_text, :answer, :analysis)')

UPDATE_SQL = ('UPDATE question SET category_id = :category_id, type = :type, type_key = :type_key, '
              'difficulty = :difficulty, title = :title, options_text = :options_text, '
              'answer = :answer, analysis = :analysis WHERE id = :id')


# ---------------------------------------------------------------------------
# 表单快照 / 校验
# ---------------------------------------------------------------------------
def load_categories():
    return query('SELECT id, name FROM category ORDER BY id')


def snapshot_from_form(form):
    """把表单原样读成快照，既用于校验落库，也用于出错时回填表单"""
    snap = {
        'category_id': form.get('category_id', type=int) or '',
        'type_key': (form.get('type_key') or '').strip(),
        'difficulty': (form.get('difficulty') or '').strip(),
        'title': (form.get('title') or '').strip(),
        'answer': (form.get('answer') or '').strip(),
        'analysis': (form.get('analysis') or '').strip(),
        'options': {},
    }
    for letter in OPTION_LETTERS:
        snap['options'][letter] = (form.get('option_' + letter) or '').strip()
    return snap


def snapshot_from_row(row):
    """把数据库一行读成快照，用于编辑页回填"""
    return {
        'category_id': row['category_id'] or '',
        'type_key': row['type_key'] or 'single',
        'difficulty': row['difficulty'] or '中等',
        'title': row['title'] or '',
        'answer': row['answer'] or '',
        'analysis': row['analysis'] or '',
        'options': split_options(row['options_text']),
    }


def validate(snap):
    """
    校验并归一化，返回 (row, errors)。
    row 为可直接落库的字典；errors 非空时 row 为 None。
    """
    errors = []

    category_id = snap['category_id']
    type_key = snap['type_key']
    difficulty = snap['difficulty']

    if not category_id:
        errors.append('请选择学科分类')
    elif not scalar('SELECT COUNT(*) FROM category WHERE id = ?', (category_id,)):
        errors.append('所选学科分类不存在')

    if type_key not in TYPE_DISPLAY:
        errors.append('请选择题型')
    if difficulty not in DIFFICULTIES:
        errors.append('请选择难度')
    if not snap['title']:
        errors.append('题干不能为空')

    # ---------- 选项 ----------
    if type_key == 'judge':
        letters = ['A', 'B']
    elif type_key in ('single', 'multi'):
        letters = list(OPTION_LETTERS)
    else:
        letters = []

    options = {letter: snap['options'].get(letter, '') for letter in letters}

    if type_key == 'judge':
        # 判断题的选项在语义上固定就是「正确 / 错误」，
        # 直接覆盖提交值，避免存入不符合约定的选项文本
        options = dict(JUDGE_OPTIONS)
    elif type_key in ('single', 'multi'):
        filled = [letter for letter in letters if options[letter]]
        if len(filled) < 2:
            errors.append('选择题至少填写 2 个选项')
        elif filled != letters[:len(filled)]:
            errors.append('选项需从 A 开始连续填写，不能跳过中间字母')

    # ---------- 答案 ----------
    answer = snap['answer']
    if type_key == 'fill':
        if not answer:
            errors.append('填空题答案不能为空')
    else:
        available = [letter for letter in letters if options.get(letter)] or letters
        if not answer:
            errors.append('请设置正确答案')
        else:
            answer = answer.upper()
            bad = [ch for ch in answer if ch not in available]
            if bad:
                errors.append('答案只能是 %s 中的字母' % '、'.join(available))
            else:
                # 去重并排序，与小程序端「选中项字母排序后拼接」的比对规则一致
                answer = ''.join(sorted(set(answer)))
                if type_key in ('single', 'judge') and len(answer) != 1:
                    errors.append('单选题 / 判断题的答案只能是一个字母')

    if errors:
        return None, errors

    return {
        'category_id': category_id,
        'type': TYPE_DISPLAY[type_key],
        'type_key': type_key,
        'difficulty': difficulty,
        'title': snap['title'],
        'options_text': join_options(options),
        'answer': answer,
        'analysis': snap['analysis'],
    }, []


def form_context(snap, errors, question=None):
    return {
        'form': snap,
        'errors': errors,
        'question': question,
        'categories': load_categories(),
        'type_display': TYPE_DISPLAY,
        'difficulties': DIFFICULTIES,
        'option_letters': OPTION_LETTERS,
        'back_url': url_for('question.index'),
    }


# ---------------------------------------------------------------------------
# 列表
# ---------------------------------------------------------------------------
@question_bp.route('/questions')
def index():
    category_id = request.args.get('category_id', type=int)
    type_key = (request.args.get('type_key') or '').strip()
    difficulty = (request.args.get('difficulty') or '').strip()
    keyword = request.args.get('keyword')

    where = ['1 = 1']
    params = []
    if category_id:
        where.append('q.category_id = ?')
        params.append(category_id)
    if type_key in TYPE_DISPLAY:
        where.append('q.type_key = ?')
        params.append(type_key)
    if difficulty in DIFFICULTIES:
        where.append('q.difficulty = ?')
        params.append(difficulty)

    like = like_keyword(keyword)
    if like:
        where.append("q.title LIKE ? ESCAPE '\\'")
        params.append(like)

    where_sql = ' AND '.join(where)

    total = scalar('SELECT COUNT(*) FROM question q WHERE ' + where_sql, params)
    page, per_page = request_page_args()
    _, offset, pager = build_pager(total, page, per_page)

    questions = query(
        'SELECT q.*, c.name AS category_name FROM question q '
        'LEFT JOIN category c ON c.id = q.category_id '
        'WHERE ' + where_sql + ' ORDER BY q.id DESC LIMIT ? OFFSET ?',
        params + [per_page, offset]
    )

    return render_template(
        'question_list.html',
        questions=questions,
        pager=pager,
        categories=load_categories(),
        type_display=TYPE_DISPLAY,
        difficulties=DIFFICULTIES,
        per_page_choices=PER_PAGE_CHOICES,
        filters={
            'category_id': category_id or '',
            'type_key': type_key,
            'difficulty': difficulty,
            'keyword': keyword or '',
        },
    )


# ---------------------------------------------------------------------------
# 新增 / 编辑
# ---------------------------------------------------------------------------
@question_bp.route('/questions/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        snap = snapshot_from_form(request.form)
        row, errors = validate(snap)
        if errors:
            return render_template('question_form.html', **form_context(snap, errors))
        execute(INSERT_SQL, row)
        refresh_counts()
        flash('题目已新增，小程序端刷新即可看到', 'success')
        return redirect(url_for('question.index'))

    blank = {'category_id': '', 'type_key': 'single', 'difficulty': '中等',
             'title': '', 'answer': '', 'analysis': '', 'options': {}}
    return render_template('question_form.html', **form_context(blank, []))


@question_bp.route('/questions/<int:qid>/edit', methods=['GET', 'POST'])
def edit(qid):
    current = query_one('SELECT * FROM question WHERE id = ?', (qid,))
    if current is None:
        flash('题目不存在或已被删除', 'error')
        return redirect(url_for('question.index'))

    if request.method == 'POST':
        snap = snapshot_from_form(request.form)
        row, errors = validate(snap)
        if errors:
            return render_template('question_form.html', **form_context(snap, errors, question=current))
        row['id'] = qid
        execute(UPDATE_SQL, row)
        refresh_counts()
        flash('题目已保存', 'success')
        return redirect(safe_next(url_for('question.index')))

    return render_template('question_form.html',
                           **form_context(snapshot_from_row(current), [], question=current))


# ---------------------------------------------------------------------------
# 删除
# ---------------------------------------------------------------------------
@question_bp.route('/questions/<int:qid>/delete', methods=['POST'])
def delete(qid):
    current = query_one('SELECT id FROM question WHERE id = ?', (qid,))
    if current is None:
        flash('题目不存在或已被删除', 'error')
        return redirect(url_for('question.index'))

    # SQLite 默认不启用外键级联，这里手动清理两张中间表，避免留下脏关联
    execute('DELETE FROM bank_question WHERE question_id = ?', (qid,))
    execute('DELETE FROM exam_question WHERE question_id = ?', (qid,))
    execute('DELETE FROM question WHERE id = ?', (qid,))
    refresh_counts()

    flash('题目已删除', 'success')
    return redirect(safe_next(url_for('question.index')))


# ---------------------------------------------------------------------------
# 批量导入
# ---------------------------------------------------------------------------
def parse_import_lines(text):
    """
    逐行解析题库文本，格式与 questions_data.py 里的元组完全一致：
        ("分类名", "题型key", "难度", "题干", "选项文本", "答案", "解析")
    用 ast.literal_eval 解析，只认字面量、不会执行任何代码。
    返回 (rows, errors)。
    """
    category_map = {row['name']: row['id'] for row in load_categories()}
    rows = []
    errors = []

    for lineno, raw in enumerate((text or '').splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        # 从 questions_data.py 复制出来的行常带结尾逗号，容错处理
        if line.endswith(','):
            line = line[:-1]

        try:
            item = ast.literal_eval(line)
        except (ValueError, SyntaxError):
            errors.append('第 %d 行：无法解析，需为 (分类, 题型, 难度, 题干, 选项, 答案, 解析) 形式的元组' % lineno)
            continue

        if not isinstance(item, (list, tuple)) or len(item) != 7:
            length = len(item) if isinstance(item, (list, tuple)) else 0
            errors.append('第 %d 行：需要 7 个字段，实际 %d 个' % (lineno, length))
            continue

        cat_name, type_key, difficulty, title, options_text, answer, analysis = [
            '' if value is None else str(value).strip() for value in item
        ]

        if cat_name not in category_map:
            errors.append('第 %d 行：分类「%s」不存在，请先在「学科分类」中创建' % (lineno, cat_name))
            continue
        if type_key not in TYPE_DISPLAY:
            errors.append('第 %d 行：题型 key「%s」无效，只能是 single / multi / judge / fill' % (lineno, type_key))
            continue
        if difficulty not in DIFFICULTIES:
            errors.append('第 %d 行：难度「%s」无效，只能是 简单 / 中等 / 困难' % (lineno, difficulty))
            continue
        if not title:
            errors.append('第 %d 行：题干为空' % lineno)
            continue
        if not answer:
            errors.append('第 %d 行：答案为空' % lineno)
            continue

        rows.append({
            'category_id': category_map[cat_name],
            'type': TYPE_DISPLAY[type_key],
            'type_key': type_key,
            'difficulty': difficulty,
            'title': title,
            'options_text': options_text,
            'answer': answer.upper() if type_key != 'fill' else answer,
            'analysis': analysis,
        })

    return rows, errors


@question_bp.route('/questions/import', methods=['GET', 'POST'])
def import_questions():
    result = None
    if request.method == 'POST':
        rows, errors = parse_import_lines(request.form.get('content') or '')
        if rows:
            executemany(INSERT_SQL, rows)
            refresh_counts()
        result = {'imported': len(rows), 'errors': errors}
    return render_template('question_import.html', result=result,
                           type_display=TYPE_DISPLAY, difficulties=DIFFICULTIES)