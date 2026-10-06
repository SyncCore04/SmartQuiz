# 在线答题系统 · 后端

微信小程序「在线答题系统」的 Flask + SQLite 后端，用于本科期末设计作业的功能闭环演示。

## 技术栈
- Python 3 + Flask
- SQLite（Python 标准库 `sqlite3`，不引 ORM）

## 目录结构
```
SmartQuiz/
├── front/           微信小程序前端（本项目不改动）
├── backend/         本后端代码：app.py / questions_data.py / requirements.txt / README.md
│   └── admin/       管理后台（独立端口 5001，只复用 DB_PATH，不修改 app.py）
└── database/        SQLite 数据库文件 smartquiz.db（首次启动自动生成）
```

## 题库维护（重点）

**推荐方式：用管理后台改题**（根目录 `start-admin.bat`，或 `cd backend/admin && python admin.py`）。
后台直接写 `question` 表，而 `/api/questions` 每次请求都实时查库，
所以**改完小程序端刷新即生效，不用重启后端，也不用删库**。

**`questions_data.py` 的角色**：现在只是「初始数据快照」，仅在全新环境首次启动（数据库文件不存在）时用于灌库。
- 每题一行 `(分类名, 题型key, 难度, 题干, 选项, 答案, 解析)`
- 分类名 ∈ `语文/数学/英语/理综`；题型key ∈ `single(单选)/multi(多选)/judge(判断)/fill(填空)`
- 选项格式 `A. x B. y C. z D. w`；判断题 `A. 正确 B. 错误`；填空题选项留空、答案直接填文本
- 难度 ∈ `简单/中等/困难`

> 注意：数据库已存在时改这个文件**不会生效**（`init_db()` 只在空库时灌数据）。
> 该格式同时是管理后台「批量导入」支持的行格式，可直接复制粘贴导入。

## 快速开始
1. 安装依赖（已装 Flask 可跳过）：
   ```bash
   pip install -r requirements.txt
   ```
2. 启动服务：
   ```bash
   python app.py
   ```
   - 首次运行会自动在 `../database/smartquiz.db` 建库、建表并灌入演示数据。
   - 服务默认运行在 `http://127.0.0.1:5000`（监听 `0.0.0.0`，可用局域网 IP 供真机访问）。

## 与小程序前端对接
小程序开发者工具中：**详情 → 本地设置 → 勾选「不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书」**，即可访问本地/局域网接口。

## 管理后台
独立于小程序接口的 Flask 应用，默认 `http://127.0.0.1:5001`，账号 `admin` / `admin123`（见 `admin/config.py`）。

```bash
cd backend/admin
python admin.py
```

| 模块 | 说明 |
|------|------|
| 数据看板 | 用户数、题目数、答题题次、总体正确率、分类分布柱状图、最近答题记录 |
| 题目管理 | 列表筛选（分类/题型/难度/关键词）+ 分页、增删改、批量导入 |
| 学科分类 | 分类增删改（含图标与配色）；仍有题目的分类禁止删除 |
| 热门题库 | 题库增删改 + 题目挂载（多对多中间表 `bank_question`） |
| 模拟考试 | 考试增删改 + 题目挂载（`exam_question`）、状态与状态标签色 |
| 用户与记录 | 用户列表、单个用户的答题记录与错题本（只读查询） |
| 首页轮播图 | 轮播图增删改，含图片路径预览 |

设计要点：
- **零侵入**：只 `from app import DB_PATH, get_db` 复用数据库路径，不改 `app.py` 一行；
- **零新增依赖**：Jinja2 随 Flask 自带，密码哈希用 werkzeug（Flask 依赖），前端为手写 HTML/CSS/JS；
- **鉴权**：Flask session + 全局 `before_request` 拦截，默认所有页面都需登录；
- **计数一致性**：增删题目后自动重算 `category.count` / `bank.question_count` / `exam.total_count`，
  保证小程序端显示的数字与实际题目一致。

## 接口一览
统一前缀 `/api`，返回 `{"code":0,"data":...,"msg":"ok"}`，`code=0` 表示成功。

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/login` | 游客登录，请求 `{nickname}`，返回 `{user_id,...}` |
| GET | `/api/swipers` | 首页轮播 |
| GET | `/api/categories` | 学科分类 |
| GET | `/api/banks` | 热门题库 |
| GET | `/api/questions` | 题目列表（支持 `category_id/type_key/bank_id` 筛选，不含答案） |
| GET | `/api/exams` | 考试列表 |
| GET | `/api/exams/<id>` | 考试详情 |
| POST | `/api/submit` | 提交作答判分，写答题记录并自动收集错题 |
| GET | `/api/records` | 答题记录 |
| GET | `/api/stats/overview` | 学习统计汇总 |
| GET | `/api/wrong-book` | 错题列表 |
| DELETE | `/api/wrong-book/<id>` | 删除错题 |
| GET | `/api/profile` | 用户信息与统计卡 |

## 验收自测
跑通以下流程即视为功能闭环：
1. `POST /api/login` 拿 `user_id`；
2. `POST /api/submit` 提交 `answers:[{question_id, my_answer}]` → 能算分、写答题记录、自动出错题；
3. 查 `/api/records`、`/api/stats/overview`、`/api/wrong-book` 能看到真实变化；
4. `DELETE /api/wrong-book/<id>` 能真正删除错题。

管理后台自测：
1. 启动后台并登录 → 看板能看到真实统计数据；
2. 在「题目管理」新增一道题 → 小程序端刷新题库即可看到；
3. 删除该题 → 题库/考试中的关联自动清理，分类题数同步刷新；
4. 「批量导入」粘贴 `questions_data.py` 里的若干行 → 能导入并给出被跳过行的原因。