# -*- coding: utf-8 -*-
"""首页轮播图管理"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import execute, query, query_one

swiper_bp = Blueprint('swiper', __name__)


@swiper_bp.route('/swipers')
def index():
    edit_id = request.args.get('edit', type=int)
    editing = query_one('SELECT * FROM swiper WHERE id = ?', (edit_id,)) if edit_id else None
    swipers = query('SELECT * FROM swiper ORDER BY id')
    return render_template('swiper_list.html', swipers=swipers, editing=editing)


@swiper_bp.route('/swipers/save', methods=['POST'])
def save():
    sid = request.form.get('id', type=int)
    title = (request.form.get('title') or '').strip()
    image = (request.form.get('image') or '').strip()

    if not title:
        flash('轮播图标题不能为空', 'error')
        return redirect(url_for('swiper.index'))
    if not image:
        flash('轮播图图片路径不能为空', 'error')
        return redirect(url_for('swiper.index'))

    if sid:
        execute('UPDATE swiper SET title = ?, image = ? WHERE id = ?', (title, image, sid))
        flash('轮播图已保存', 'success')
    else:
        execute('INSERT INTO swiper(title, image) VALUES(?,?)', (title, image))
        flash('轮播图已新增', 'success')

    return redirect(url_for('swiper.index'))


@swiper_bp.route('/swipers/<int:sid>/delete', methods=['POST'])
def delete(sid):
    execute('DELETE FROM swiper WHERE id = ?', (sid,))
    flash('轮播图已删除', 'success')
    return redirect(url_for('swiper.index'))