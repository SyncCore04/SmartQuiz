# Vibe Coding 提示词：为「在线答题系统」微信小程序生成 Flask + SQLite 后端

把下面从「【提示词开始】」到「【提示词结束】」之间的全部内容，原样粘贴给任意一个编码 AI，用于一次性生成项目后端。

---

【提示词开始】

## 角色与目标
你是一名 Python 后端开发工程师。请为一个已存在的**微信小程序「在线答题系统」**生成一个**最小可用、练手级别**的后端服务，技术栈为 **Flask + SQLite**，让小程序前端与这个后端实现真实数据交互，形成一个能演示闭环的完整小项目（用于本科课程期末设计作业）。

## 硬性约束（务必遵守）
1. **越简单越好**：不引入 ORM（不用 SQLAlchemy），直接用 Python 标准库 `sqlite3`；不用 JWT、不用 OAuth。用户体系用**游客/假账号模式**。
2. **单文件优先**：尽量把所有后端逻辑放在一个 `app.py` 里（可附一个 `seed.py` 或启动时自动建表+灌入种子数据），方便老师查看和运行。
3. **中文注释**：关键代码需有简洁中文注释，方便本科生答辩时讲解。
4. **无第三方框架**：除 Flask 外不引入 pytest、flask_cors 等额外依赖（跨域需求可用 Flask 内置的 `@app.after_request` 加响应头实现）。
5. **数据可持久化**：成绩、错题、答题记录必须真正写入 SQLite 文件（如 `smartquiz.db`），重启不丢失。
6. **提供种子数据**：首次启动自动建表，并灌入与前端展示一致的示例数据（分类、题目、考试等，见下文）。

## 文件落点与项目结构（必须严格遵守）
项目的最终目录结构如下，前端已按此整理好放在 `front/` 下。你生成的后端代码与数据库文件必须写到**对应路径**，不要再新建其他目录：

```
SmartQuiz/            ← 项目根目录
├── front/           （现有微信小程序前端，已存在，不要动它）
├── backend/         （后端代码目录：在此生成 app.py、requirements.txt、README.md）
├── database/        （数据库目录：SQLite 的 .db 文件必须生成到此处）
└── backend_vibe_prompt.md
```

路径约定（写死在代码里）：
- 所有后端源码（`app.py`、`requirements.txt`、`README.md`）一律放在 `backend/` 目录下，即 `SmartQuiz/backend/`。
- 数据库文件路径固定为 `SmartQuiz/database/smartquiz.db`。在 `app.py` 里用相对路径引用：`DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'smartquiz.db')`，并确保 `database/` 存在（不存在则自动 `os.makedirs`）。
- 绝对不允许把 `.db` 文件和源码混在同一个目录，也不允许建新的顶层文件夹。

## 项目背景与前端结构
小程序前端位于 `front/pages/` 下，全部数据目前是**硬编码在页面 .js 里**的演示数据。后端需要把这些数据变成接口，前端改用它。前端页面及各页用到的字段如下（后端字段需与之一一对应）：

- **首页 index**：
  - 轮播 `swiperList`: `[{id, image, title}]`
  - 学科分类 `categories`: `[{id, name, icon, count, color, bgColor}]`
  - 热门题库 `hotBanks`: `[{id, title, desc, count, joined, tag, image}]`
  - 近期练习 `recentPractices`: `[{id, title, score, total, date, icon, bgColor, iconColor}]`
- **分类页 category**：按学科浏览分类（复用 `categories`）
- **题库页 question-list**：题型筛选 `filters`: `[{key:'all'|'single'|'multi'|'judge'|'fill', label}]`；题目列表 `questions`: `[{id, num, type, typeKey, difficulty, title, options}]`（options 为文本字符串，如 `"A. xx B. xx "`）
- **答题页 answer**：一套题目 `questions`: `[{id, type, title, options:[{key:'A',text,selected}]}]`
- **结果页 result**：判分结果 `{score, totalQuestions, correctCount, wrongCount, accuracy, timeUsed, results:[{num, isCorrect, myAnswer, correctAnswer, title}]}`
- **考试列表 exam-list**：`exams`: `[{id, title, cover, date, duration, totalCount, joined, status, statusColor}]`
- **错题本 wrong-book**：`wrongList`: `[{id, num, title, myAnswer, correctAnswer, analysis}]`（analysis 为解析）
- **统计页 stats**：`{totalQuestions, accuracy, streakDays, weeklyData:[{day,value,height}], recentRecords:[{id,title,score,total,date,correct,wrong}]}`
- **我的 profile**：`userInfo:{nickName, avatar}`，统计卡 `stats`，菜单 `menuList`

## 建议的数据库表结构
- `user(id INTEGER PK, nickname TEXT, avatar TEXT, created_at TEXT)`
- `category(id INTEGER PK, name TEXT, icon TEXT, color TEXT, bg_color TEXT, count INTEGER)`
- `question(id INTEGER PK, category_id INTEGER, type TEXT, type_key TEXT, difficulty TEXT, title TEXT, options_text TEXT, answer TEXT, analysis TEXT)`
  - `type_key` ∈ `single/multi/judge/fill`；`options_text` 存选项文本字符串；`answer` 存正确答案（如 `"B"`）
- `bank(id INTEGER PK, title TEXT, desc TEXT, cover TEXT, question_count INTEGER, joined INTEGER, tag TEXT)`，热门题库
- `bank_question(bank_id INTEGER, question_id INTEGER)`，题库与题目多对多
- `exam(id INTEGER PK, title TEXT, cover TEXT, date TEXT, duration TEXT, total_count INTEGER, joined INTEGER, status TEXT, status_color TEXT)`，考试列表
- `exam_question(exam_id INTEGER, question_id INTEGER)`
- `user_record(id INTEGER PK, user_id INTEGER, title TEXT, score REAL, total INTEGER, correct INTEGER, wrong INTEGER, date TEXT)`，每次答题的成绩记录
- `wrong_item(id INTEGER PK, user_id INTEGER, num INTEGER, title TEXT, my_answer TEXT, correct_answer TEXT, analysis TEXT, created_at TEXT)`，自动收集的错题

## 需要实现的接口清单（请实现并可测试）
统一前缀 `/api`，返回 JSON（`{"code":0,"data":...,"msg":"ok"}`），`code=0` 表示成功。

1. `POST /api/login` — 游客/假账号登录。请求 `{"nickname":"清和学长"}`；若该用户不存在则创建，返回 `{user_id, nickname, avatar}`。演示即拿这个 `user_id` 当身份凭证，后续接口可直接带 `user_id`。
2. `GET /api/swipers` — 轮播图列表。
3. `GET /api/categories` — 学科分类列表。
4. `GET /api/banks` — 热门题库列表（含各库题目数）。
5. `GET /api/questions?category_id=&type_key=&bank_id=` — 题目列表，支持按分类/题型/题库筛选。**返回内容必须不含 answer/analysis 字段**（防止前端直接看到答案）。
6. `GET /api/exams` — 考试列表。
7. `GET /api/exams/<id>` — 考试详情（含该考试题量、题目 id 列表）。
8. `POST /api/submit` — 提交一次作答并判分。请求 `{user_id, title, time_used, answers:[{question_id, my_answer}]}`。后端逐题比对 `question.answer` 判对错，写入 `user_record`，并把答错的题写入 `wrong_item`（去重，同一题已存在则更新）。返回 `{score,total,correct,wrong,accuracy,results:[{num,isCorrect,myAnswer,correctAnswer,title}]}`。
9. `GET /api/records?user_id=` — 该用户的答题记录（对应 stats 的 `recentRecords`，date 返回 `MM-DD`）。
10. `GET /api/stats/overview?user_id=` — 统计汇总 `{totalQuestions, accuracy, streakDays, weeklyData}`（正确率、总数按 user_record 聚合；weeklyData 给出周一到周日每天的答题数 `{day, value, height}`，height 可由前端按 value 换算，后端给 scale 即可）。
11. `GET /api/wrong-book?user_id=` — 错题列表。
12. `DELETE /api/wrong-book/<id>?user_id=` — 从错题本移除某题。
13. `GET /api/profile?user_id=` — 用户信息与统计卡 `{userInfo, stats:[{label,value}]}`。

## 种子数据要求
- 至少 4 个学科分类（语文/数学/英语/理综），颜色沿用前端 `index.js` 里已有值（如语文 `#4F46E5`）。
- 至少 10 道单选题把 `pages/answer/answer.js` 里的题目搬进来（保留题干、4 个选项、并补充正确答案 answer 与解析 analysis）。
- 额外补充几道多选题、判断题、填空题，使 `question-list` 的题型筛选生效。
- 至少 3 个热门题库、4 场考试，复用前端 `index.js` / `exam-list.js` 已有的标题与 `cover` 图片路径（保持 `/images/xxx.jpg` 相对路径即可）。

## 与小程序前端对接的说明（写入 README 或代码顶部注释）
1. 启动命令：`python app.py`，默认运行在 `http://127.0.0.1:5000`。
2. 小程序在「详情 → 本地设置 → 勾选『不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书』」后才能访问本地/局域网接口。
3. 演示时若前端没有改接口，可只先让后端这一切接口能独立用浏览器或 Postman 调通；前端改造做成下一步即可。

## 验收标准（完成这些即视为合格）
- `python app.py` 一条命令即可启动，首启自动建库建表并灌种子数据。
- 上面 13 个接口全部能通过浏览器/Postman 调通，返回结构符合字段约定。
- 做一次 `POST /api/submit`：能算出分数、写一条答题记录、自动产生错题；再查 `GET /api/records`、`GET /api/stats/overview`、`GET /api/wrong-book` 能看到对应的真实数据变化。
- `DELETE /api/wrong-book/<id>` 能真正删除错题。
- 无多余依赖、无复杂架构，代码有中文注释，适合本科答辩讲解。

## 文件输出要求（严格遵守，与上文《文件落点与项目结构》一致）
- 生成完整、可运行的代码（主要是 `app.py`，可含 `requirements.txt`、`README.md`），**所有源码文件一律写入 `SmartQuiz/backend/` 目录下**，不要写错位置。
- 数据持久化写入 `SmartQuiz/database/smartquiz.db`：请用 `os.path` 相对路径在代码里定位（以 `backend/app.py` 为基准向上取 `../database/smartquiz.db`），首次运行自动 `os.makedirs` 确保 `database/` 目录存在。
- 输出时按如下结构落盘，不得新建其他顶层文件夹：
  - `SmartQuiz/backend/app.py`
  - `SmartQuiz/backend/requirements.txt`
  - `SmartQuiz/backend/README.md`
  - `SmartQuiz/database/`（存放自动生成的 `smartquiz.db`）

【提示词结束】