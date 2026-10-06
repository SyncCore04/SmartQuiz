# 在线答题系统 · 微信小程序 + Flask 后端

一个前后端联动的在线答题小程序，用于本科课程期末设计作业演示。前端为微信小程序，后端基于 Flask + SQLite，答题判分、错题本、学习统计均真实落地。

## 技术栈
- **前端**：微信小程序（原生 + Vant Weapp 组件库）
- **后端**：Python 3 + Flask + SQLite（标准库 `sqlite3`，无 ORM）
- **管理后台**：Flask + Jinja2 服务端渲染（手写 HTML/CSS/JS，无前端框架，无新增依赖）

## 目录结构
```
SmartQuiz/
├── front/          微信小程序前端（微信开发者工具导入此目录）
├── backend/         Flask 后端（app.py / questions_data.py / requirements.txt）
│   └── admin/       管理后台（独立端口 5001，不修改 app.py）
├── database/       SQLite 数据库（首次启动后端时自动生成 smartquiz.db，勿手动上传）
├── docs/           项目文档（PRD、答辩学习文档等）
├── start-backend.bat  一键启动小程序后端（端口 5000）
├── start-admin.bat    一键启动管理后台（端口 5001）
├── .gitignore
└── README.md
```

## 快速开始

### 1. 启动后端
```bash
cd backend
pip install -r requirements.txt   # 已装 Flask 可跳过
python app.py
```
- 首次运行会在 `../database/smartquiz.db` 自动建库、建表并灌入演示数据（题库 60 题、4 个学科分类、热门题库与模拟考试等）。
- 服务默认监听 `http://127.0.0.1:5000`，**重启不会丢失答题记录**。

**一键启动**：运行根目录下的`start-backend.bat`

### 2. 打开前端
1. 打开**微信开发者工具 → 导入项目 → 选择 `front/` 目录**。
2. 在「详情 → 本地设置」勾选 **不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**（否则无法访问本地后端）。
3. 编译运行。

> 真机预览：把 `front/utils/api.js` 顶部的 `BASE_URL` 从 `127.0.0.1` 改为电脑局域网 IP，手机与电脑同一 Wi-Fi 即可访问。

### 3. 启动管理后台（可选）
双击根目录 `start-admin.bat`（或 `cd backend/admin && python admin.py`）。
- 地址 `http://127.0.0.1:5001`，默认账号 `admin` / `admin123`（改密码见 `backend/admin/config.py`）。
- 功能：数据看板、题目增删改查与批量导入、学科分类、热门题库与模拟考试（含题目挂载）、用户与答题记录查询、首页轮播图。
- 与小程序端**共用同一个 `smartquiz.db`**：后台改完题目，小程序端**刷新即可生效**，无需重启后端、无需删库。
- 管理后台与小程序接口互不干扰：前者是独立进程、独立端口，且不修改 `app.py` 一行代码。

## 功能闭环演示路径
首页 → 题库分类/热门题库 → 答题 → 提交判分 → 查看结果 → 错题自动进错题本 → 学习统计实时更新 → 我的信息。

## 接口概览
全部接口及字段约定见 [`backend/README.md`](backend/README.md)。统一前缀 `/api`，返回 `{"code":0,"data":...,"msg":"ok"}`。

## 常见问题
- **数据库需要上传吗？** 不需要。后端首启自动生成 `smartquiz.db`，已通过 `.gitignore` 忽略。
- **想重新演示干净数据？** 删除 `database/smartquiz.db` 后重启后端即可重建。
- **加题还要改代码 + 删库重建吗？** 不用了。用管理后台加题，小程序端刷新即生效。`questions_data.py` 现在只在全新环境首次建库时使用。
- **管理后台能上传图片吗？** 不能。封面/轮播图仍需手动把图片放进 `front/images/`，后台只负责填 `/images/文件名` 并支持预览核对。
- **没有 Python 环境的评审场景？** 建议录一份演示视频/截图。