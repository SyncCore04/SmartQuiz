# -*- coding: utf-8 -*-
"""
在线答题系统 —— Flask + SQLite 后端
用于「在线答题系统」微信小程序（期末设计作业）
启动：python app.py  （首次运行会自动建库、建表并灌入种子数据）
数据库文件：SmartQuiz/database/smartquiz.db

题库扩充：题目统一维护在 questions_data.py（独立数据文件），
          seed_data() 从此文件读取灌库，如需加题只需改数据文件。
"""
import os
import sqlite3
import random
from datetime import datetime, date, timedelta

from flask import Flask, request, jsonify

from questions_data import QUESTIONS

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 数据库路径约定：固定写入 SmartQuiz/database/smartquiz.db（相对 backend/ 上一级的 database/）
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'smartquiz.db')


def get_db():
    """获取数据库连接（每行返回可按键名访问的 Row 对象）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# 建表
# ---------------------------------------------------------------------------
SCHEMA = """
DROP TABLE IF EXISTS bank_question;
DROP TABLE IF EXISTS exam_question;
DROP TABLE IF EXISTS wrong_item;
DROP TABLE IF EXISTS user_record;
DROP TABLE IF EXISTS exam;
DROP TABLE IF EXISTS bank;
DROP TABLE IF EXISTS question;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS swiper;
DROP TABLE IF EXISTS user;

CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    avatar TEXT,
    created_at TEXT
);

CREATE TABLE swiper(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    image TEXT
);

CREATE TABLE category(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    icon TEXT,
    color TEXT,
    bg_color TEXT,
    count INTEGER DEFAULT 0
);

CREATE TABLE question(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    type TEXT,
    type_key TEXT,
    difficulty TEXT,
    title TEXT,
    options_text TEXT,
    answer TEXT,
    analysis TEXT
);

CREATE TABLE bank(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    desc TEXT,
    cover TEXT,
    question_count INTEGER DEFAULT 0,
    joined INTEGER DEFAULT 0,
    tag TEXT
);

CREATE TABLE bank_question(
    bank_id INTEGER,
    question_id INTEGER
);

CREATE TABLE exam(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    cover TEXT,
    date TEXT,
    duration TEXT,
    total_count INTEGER DEFAULT 0,
    joined INTEGER DEFAULT 0,
    status TEXT,
    status_color TEXT
);

CREATE TABLE exam_question(
    exam_id INTEGER,
    question_id INTEGER
);

CREATE TABLE user_record(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    score REAL,
    total INTEGER,
    correct INTEGER,
    wrong INTEGER,
    date TEXT
);

CREATE TABLE wrong_item(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    num INTEGER,
    title TEXT,
    my_answer TEXT,
    correct_answer TEXT,
    analysis TEXT,
    created_at TEXT
);
"""


# ---------------------------------------------------------------------------
# 种子数据（与小程序前端展示一致，便于演示）
# ---------------------------------------------------------------------------
def seed_data():
    """首次启动时灌入示例数据。类别/题库已存在则跳过，避免重复插入。"""
    conn = get_db()
    c = conn.cursor()
    if c.execute("SELECT COUNT(*) AS n FROM category").fetchone()["n"] > 0:
        conn.close()
        return

    # 学科分类
    categories = [
        ("语文", "notes-o", "#4F46E5", "#ede9fe"),
        ("数学", "chart-trending-o", "#EC4899", "#fce7f3"),
        ("英语", "comment-o", "#F59E0B", "#fef3c7"),
        ("理综", "points", "#10B981", "#d1fae5"),
    ]
    for name, icon, color, bg in categories:
        c.execute("INSERT INTO category(name, icon, color, bg_color) VALUES(?,?,?,?)", (name, icon, color, bg))
    cat_map = {row["id"]: row for row in c.execute("SELECT * FROM category").fetchall()}
    cat_by_name = {r["name"]: r["id"] for r in cat_map.values()}

    # 题目来源：统一从独立题库 questions_data.py 读取（见文件顶部说明）
    # 每题：(分类名, 题型key, 难度, 题干, 选项, 答案, 解析)
    # 分类名 -> 分类id、题型key -> 中文题型 在此映射
    type_display = {"single": "单选", "multi": "多选", "judge": "判断", "fill": "填空"}
    qid_by_ord = {}
    for ord_no, (cat_name, tk, diff, title, opt, ans, ana) in enumerate(QUESTIONS, start=1):
        cid = cat_by_name.get(cat_name)
        cur = c.execute(
            "INSERT INTO question(category_id,type,type_key,difficulty,title,options_text,answer,analysis) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (cid, type_display[tk], tk, diff, title, opt, ans, ana))
        qid_by_ord[ord_no] = cur.lastrowid

    # 更新每个分类的题目数量 count
    # 注意：先把 SELECT 结果 fetchall 取完，再执行 UPDATE；
    #       否则同一个游标在迭代中执行 UPDATE 会打断遍历，只更新第一行。
    for ci, cn in c.execute("SELECT category_id, COUNT(*) AS n FROM question GROUP BY category_id").fetchall():
        c.execute("UPDATE category SET count=? WHERE id=?", (cn, ci))

    # 热门题库（复用前端首页 hotBanks）
    banks = [
        ("2024高考语文真题精选", "涵盖近五年高考语文真题，精选阅读理解与作文素材", "/images/photo-1685287731216-a7a0fae7a41a_w400.jpg", 3280, "热门"),
        ("数学压轴题专项突破", "针对高考数学最后两道大题的专项训练", "/images/photo-1495465798138-718f86d1a4bc_w400.jpg", 2156, "推荐"),
        ("英语完形填空强化训练", "高频词汇与经典题型，快速提升完形填空得分", "/images/photo-1617239098289-ad0ee436361e_w400.jpg", 1890, "新课"),
    ]
    bid = []
    for title, desc, cover, joined, tag in banks:
        cur = c.execute("INSERT INTO bank(title,desc,cover,question_count,joined,tag) VALUES(?,?,?,?,?,?)",
                        (title, desc, cover, 0, joined, tag))
        bid.append(cur.lastrowid)
    # 给题库 1 挂语文题，题库 2 挂数学题，题库 3 挂英语题
    qs_all = c.execute("SELECT id, category_id FROM question").fetchall()
    for b_idx, cid in enumerate([cat_by_name["语文"], cat_by_name["数学"], cat_by_name["英语"]], start=0):
        picked = [q["id"] for q in qs_all if q["category_id"] == cid]
        for qid in picked:
            c.execute("INSERT INTO bank_question(bank_id, question_id) VALUES(?,?)", (bid[b_idx], qid))
        c.execute("UPDATE bank SET question_count=? WHERE id=?", (len(picked), bid[b_idx]))

    # 考试列表（复用前端 exam-list）
    exams = [
        ("2024年高考语文模拟考试", "/images/photo-1685287731216-a7a0fae7a41a_w400.jpg", "2024-03-15", "120分钟", 1256, "进行中", "#4F46E5"),
        ("数学函数与导数专项考试", "/images/photo-1495465798138-718f86d1a4bc_w400.jpg", "2024-03-20", "90分钟", 890, "未开始", "#FFD166"),
        ("英语综合能力测评", "/images/photo-1617239098289-ad0ee436361e_w400.jpg", "2024-03-10", "100分钟", 2100, "已结束", "#999999"),
        ("理综全真模拟考试", "/images/photo-1617529497832-5ad49d9b5928_w400.jpg", "2024-04-01", "150分钟", 680, "未开始", "#FFD166"),
    ]
    eid = []
    q_ord = list(qid_by_ord.values())
    for title, cover, d, dur, joined, status, sc in exams:
        total = random.randint(10, len(q_ord))
        cur = c.execute("INSERT INTO exam(title,cover,date,duration,total_count,joined,status,status_color) "
                        "VALUES(?,?,?,?,?,?,?,?)", (title, cover, d, dur, total, joined, status, sc))
        eid.append(cur.lastrowid)
        # 给每场考试随机挂题，近似题量
        pool = random.sample(q_ord, min(total, len(q_ord)))
        for qid in pool:
            c.execute("INSERT INTO exam_question(exam_id, question_id) VALUES(?,?)", (cur.lastrowid, qid))

    # 轮播图（复用前端首页 swiperList）
    swipers = [
        ("每日刷题挑战", "/images/photo-1517673132405-a56a62b18caf_w1080.jpg"),
        ("模拟考试上线", "/images/photo-1564609116494-380be7238d7d_w1080.jpg"),
    ]
    c.executemany("INSERT INTO swiper(title, image) VALUES(?,?)", swipers)

    conn.commit()
    conn.close()


def init_db():
    """建库建表并灌种子数据（仅在全新库时执行，重启保留已有答题记录）"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='question'").fetchone()
    if not exists:
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()
        seed_data()
    else:
        conn.close()


# ---------------------------------------------------------------------------
# 统一响应 + 跨域
# ---------------------------------------------------------------------------
def ok(data=None, msg="ok"):
    return jsonify({"code": 0, "data": data if data is not None else {}, "msg": msg})


def fail(msg, code=1):
    return jsonify({"code": code, "data": {}, "msg": msg})


@app.after_request
def add_cors_headers(resp):
    """允许小程序端跨域访问（练手项目简化处理）"""
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


# ---------------------------------------------------------------------------
# 接口实现
# ---------------------------------------------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    """游客/假账号登录：不存在则创建"""
    data = request.get_json(silent=True) or {}
    nickname = (data.get("nickname") or "清和学长").strip()
    conn = get_db()
    row = conn.execute("SELECT * FROM user WHERE nickname=?", (nickname,)).fetchone()
    if row is None:
        avatar = "/images/photo-1517673132405-a56a62b18caf_w200.jpg"
        cur = conn.execute("INSERT INTO user(nickname, avatar, created_at) VALUES(?,?,?)",
                           (nickname, avatar, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        user_id = cur.lastrowid
        conn.commit()
    else:
        user_id = row["id"]
    conn.close()
    return ok({"user_id": user_id, "nickname": nickname})


@app.route("/api/swipers", methods=["GET"])
def swipers():
    conn = get_db()
    rows = conn.execute("SELECT * FROM swiper").fetchall()
    conn.close()
    return ok([{"id": r["id"], "image": r["image"], "title": r["title"]} for r in rows])


@app.route("/api/categories", methods=["GET"])
def categories():
    conn = get_db()
    rows = conn.execute("SELECT * FROM category").fetchall()
    conn.close()
    return ok([{"id": r["id"], "name": r["name"], "icon": r["icon"],
                "count": r["count"], "color": r["color"], "bgColor": r["bg_color"]} for r in rows])


@app.route("/api/banks", methods=["GET"])
def banks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM bank").fetchall()
    conn.close()
    return ok([{"id": r["id"], "title": r["title"], "desc": r["desc"], "cover": r["cover"],
                "count": r["question_count"], "joined": r["joined"], "tag": r["tag"]} for r in rows])


@app.route("/api/questions", methods=["GET"])
def questions():
    """题目列表，支持 category_id / type_key / bank_id 筛选；返回不含答案与解析"""
    category_id = request.args.get("category_id", type=int)
    type_key = request.args.get("type_key", "").strip()
    bank_id = request.args.get("bank_id", type=int)

    sql = ("SELECT q.* FROM question q WHERE 1=1 ")
    params = []
    if category_id:
        sql += "AND q.category_id=? "
        params.append(category_id)
    if type_key:
        sql += "AND q.type_key=? "
        params.append(type_key)
    if bank_id:
        sql += "AND q.id IN (SELECT question_id FROM bank_question WHERE bank_id=?) "
        params.append(bank_id)

    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    # 只返回前端需要的字段，绝不带 answer / analysis
    li = []
    for i, r in enumerate(rows, start=1):
        li.append({"id": r["id"], "num": i, "type": r["type"], "typeKey": r["type_key"],
                   "difficulty": r["difficulty"], "title": r["title"], "options": r["options_text"]})
    return ok(li)


@app.route("/api/exams", methods=["GET"])
def exams():
    conn = get_db()
    rows = conn.execute("SELECT * FROM exam").fetchall()
    conn.close()
    return ok([{"id": r["id"], "title": r["title"], "cover": r["cover"], "date": r["date"],
                "duration": r["duration"], "totalCount": r["total_count"], "joined": r["joined"],
                "status": r["status"], "statusColor": r["status_color"]} for r in rows])


@app.route("/api/exams/<int:eid>", methods=["GET"])
def exam_detail(eid):
    conn = get_db()
    row = conn.execute("SELECT * FROM exam WHERE id=?", (eid,)).fetchone()
    if row is None:
        conn.close()
        return fail("考试不存在")
    qs = conn.execute("SELECT question_id FROM exam_question WHERE exam_id=?", (eid,)).fetchall()
    total = conn.execute("SELECT COUNT(*) AS n FROM exam_question WHERE exam_id=?", (eid,)).fetchone()["n"]
    conn.close()
    return ok({"id": row["id"], "title": row["title"], "cover": row["cover"], "date": row["date"],
               "duration": row["duration"], "totalCount": total, "joined": row["joined"],
               "status": row["status"], "statusColor": row["status_color"],
               "questionIds": [q["question_id"] for q in qs]})


@app.route("/api/submit", methods=["POST"])
def submit():
    """提交作答并判分：写答题记录、自动收集错题"""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    title = data.get("title") or "在线练习"
    time_used = data.get("time_used") or "0分钟"
    answers = data.get("answers") or []

    if not user_id:
        return fail("缺少 user_id")

    conn = get_db()
    results = []
    wrong_items = []
    correct = 0
    for i, a in enumerate(answers, start=1):
        qid = a.get("question_id")
        my_ans = (a.get("my_answer") or "").strip()
        q = conn.execute("SELECT * FROM question WHERE id=?", (qid,)).fetchone()
        if q is None:
            continue
        is_correct = my_ans.upper() == (q["answer"] or "").strip().upper()
        if is_correct:
            correct += 1
        else:
            wrong_items.append((user_id, i, q["title"], my_ans, q["answer"], q["analysis"],
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        results.append({"num": i, "isCorrect": is_correct, "myAnswer": my_ans,
                        "correctAnswer": q["answer"], "title": q["title"]})

    total = len(results)
    wrong = total - correct
    score = round(correct / total * 100) if total else 0
    accuracy = f"{round(correct / max(total, 1) * 100)}%"

    conn.execute("INSERT INTO user_record(user_id,title,score,total,correct,wrong,date) "
                 "VALUES(?,?,?,?,?,?,?)",
                 (user_id, title, score, total, correct, wrong,
                  datetime.now().strftime("%Y-%m-%d")))

    # 错题写入/更新（同一题已存在则更新）
    for uid, num, t, mya, ca, ana, ts in wrong_items:
        qid_of = answers[num - 1].get("question_id")
        exist = conn.execute("SELECT id FROM wrong_item WHERE user_id=? AND title=?",
                             (uid, t)).fetchone()
        if exist:
            conn.execute("UPDATE wrong_item SET my_answer=?, correct_answer=?, analysis=?, created_at=? "
                         "WHERE id=?", (mya, ca, ana, ts, exist["id"]))
        else:
            conn.execute("INSERT INTO wrong_item(user_id,num,title,my_answer,correct_answer,analysis,created_at) "
                         "VALUES(?,?,?,?,?,?,?)", (uid, num, t, mya, ca, ana, ts))

    conn.commit()
    conn.close()
    return ok({"score": score, "total": total, "correct": correct, "wrong": wrong,
               "accuracy": accuracy, "timeUsed": time_used, "results": results})


@app.route("/api/records", methods=["GET"])
def records():
    """答题记录，date 返回 MM-DD"""
    user_id = request.args.get("user_id", type=int)
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM user_record WHERE user_id=? ORDER BY date DESC, id DESC LIMIT 20",
        (user_id,)).fetchall()
    conn.close()
    return ok([{"id": r["id"], "title": r["title"], "score": r["score"], "total": r["total"] * 10,
                "date": r["date"][5:], "correct": r["correct"], "wrong": r["wrong"]} for r in rows])


@app.route("/api/stats/overview", methods=["GET"])
def stats_overview():
    """学习统计汇总：总数、正确率、连续天数、本周数据"""
    user_id = request.args.get("user_id", type=int)
    conn = get_db()
    rows = conn.execute("SELECT * FROM user_record WHERE user_id=? ORDER BY date",
                        (user_id,)).fetchall()

    total_questions = sum(r["total"] for r in rows)
    total_correct = sum(r["correct"] for r in rows)
    total_all = sum(r["total"] for r in rows)
    accuracy = f"{round(total_correct / total_all * 100)}%" if total_all else "0%"

    # 连续答题天数：按出现的日期去重后，统计从最近有记录那天往前连续的天数
    days = sorted({r["date"] for r in rows})
    streak = 0
    if days:
        streak = 1
        cur = datetime.strptime(days[-1], "%Y-%m-%d").date()
        idx = len(days) - 2
        while idx >= 0:
            prev = datetime.strptime(days[idx], "%Y-%m-%d").date()
            if (cur - prev).days == 1:
                streak += 1
                cur = prev
                idx -= 1
            else:
                break

    # 本周（周一~周日）每天的答题数
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_days = [monday + timedelta(days=i) for i in range(7)]
    day_vals = {}
    for r in rows:
        d = datetime.strptime(r["date"], "%Y-%m-%d").date()
        if d in week_days:
            day_vals[d.isoformat()] = day_vals.get(d.isoformat(), 0) + r["total"]
    names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekly = []
    max_v = max(day_vals.values()) if day_vals else 0
    for i, d in enumerate(week_days):
        v = day_vals.get(d.isoformat(), 0)
        height = int(v / max_v * 100) if max_v else 0
        weekly.append({"day": names[i], "value": v, "height": height})

    conn.close()
    return ok({"totalQuestions": total_questions, "accuracy": accuracy, "streakDays": streak,
               "weeklyData": weekly})


@app.route("/api/wrong-book", methods=["GET"])
def wrong_book():
    user_id = request.args.get("user_id", type=int)
    conn = get_db()
    rows = conn.execute("SELECT * FROM wrong_item WHERE user_id=? ORDER BY created_at DESC",
                        (user_id,)).fetchall()
    conn.close()
    return ok([{"id": r["id"], "num": r["num"], "title": r["title"], "myAnswer": r["my_answer"],
                "correctAnswer": r["correct_answer"], "analysis": r["analysis"]} for r in rows])


@app.route("/api/wrong-book/<int:wid>", methods=["DELETE"])
def wrong_book_delete(wid):
    conn = get_db()
    cur = conn.execute("DELETE FROM wrong_item WHERE id=?", (wid,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return fail("错题不存在")
    return ok(msg="已删除")


@app.route("/api/profile", methods=["GET"])
def profile():
    user_id = request.args.get("user_id", type=int)
    conn = get_db()
    u = conn.execute("SELECT * FROM user WHERE id=?", (user_id,)).fetchone()
    if u is None:
        conn.close()
        return fail("用户不存在")
    rows = conn.execute("SELECT * FROM user_record WHERE user_id=?", (user_id,)).fetchall()
    total_all = sum(r["total"] for r in rows)
    total_correct = sum(r["correct"] for r in rows)
    day_count = len({r["date"] for r in rows})
    accuracy = f"{round(total_correct / total_all * 100)}%" if total_all else "0%"
    conn.close()
    return ok({
        "userInfo": {"nickName": u["nickname"], "avatar": u["avatar"]},
        "stats": [{"label": "答题数", "value": total_all},
                  {"label": "正确率", "value": accuracy},
                  {"label": "连续天数", "value": day_count}],
    })


if __name__ == "__main__":
    init_db()
    print("数据库文件：", DB_PATH)
    print("服务启动：http://127.0.0.1:5000")
    # debug=False：避免 Flask reloader 常驻双进程、残留多个实例导致端口/缓存错乱
    app.run(host="0.0.0.0", port=5000, debug=False)