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
└── database/        SQLite 数据库文件 smartquiz.db（首次启动自动生成）
```

## 题库维护（重点）
题目统一存放在 **`questions_data.py`**（独立数据文件），与后端逻辑分离，加题只需改这一个文件，不改代码。
- 每题一行 `(分类名, 题型key, 难度, 题干, 选项, 答案, 解析)`
- 分类名 ∈ `语文/数学/英语/理综`；题型key ∈ `single(单选)/multi(多选)/judge(判断)/fill(填空)`
- 选项格式 `A. x B. y C. z D. w`；判断题 `A. 正确 B. 错误`；填空题选项留空、答案直接填文本
- 难度 ∈ `简单/中等/困难`
- 加题后若数据库已存在，需删除 `database/smartquiz.db` 再启动才会重新灌入新题（旧答题记录会一并清空）；全新部署会自动全量注入。

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