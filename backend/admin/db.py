# -*- coding: utf-8 -*-
"""
数据库访问层
================
直接复用小程序后端 app.py 里的 DB_PATH 与 get_db，好处是：
  1. 数据库路径只在 app.py 定义一处，后台不会走偏；
  2. 后台只 import，不修改 app.py 任何代码。

安全说明：app.py 的 init_db() 与 app.run() 都在 `if __name__ == "__main__"` 保护下，
因此被 import 时不会误启动小程序服务，也不会重置数据库。
"""

import os
import sys

# 把 backend/ 加入模块搜索路径，否则 `import app` 找不到（app.py 在上一级目录）
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import DB_PATH, get_db  # noqa: E402

__all__ = ['DB_PATH', 'get_db', 'query', 'query_one', 'scalar', 'execute', 'executemany']


def query(sql, params=()):
    """查多行，返回 sqlite3.Row 列表（可按列名取值）"""
    conn = get_db()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def query_one(sql, params=()):
    """查一行，没有则返回 None"""
    conn = get_db()
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()


def scalar(sql, params=(), default=0):
    """查单个值，例如 COUNT(*)；无结果时返回 default"""
    row = query_one(sql, params)
    if row is None or row[0] is None:
        return default
    return row[0]


def execute(sql, params=()):
    """单条写操作（INSERT/UPDATE/DELETE），自动提交，返回受影响行数"""
    conn = get_db()
    try:
        rowcount = conn.execute(sql, params).rowcount
        conn.commit()
        return rowcount
    finally:
        conn.close()


def executemany(sql, seq_of_params):
    """批量写操作，自动提交，返回受影响行数"""
    conn = get_db()
    try:
        rowcount = conn.executemany(sql, seq_of_params).rowcount
        conn.commit()
        return rowcount
    finally:
        conn.close()