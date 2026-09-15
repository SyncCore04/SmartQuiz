# 在线答题系统 · 微信小程序 + Flask 后端

一个前后端联动的在线答题小程序，用于本科课程期末设计作业演示。前端为微信小程序，后端基于 Flask + SQLite，答题判分、错题本、学习统计均真实落地。

## 技术栈
- **前端**：微信小程序（原生 + Vant Weapp 组件库）
- **后端**：Python 3 + Flask + SQLite（标准库 `sqlite3`，无 ORM）

## 目录结构
```
SmartQuiz/
├── front/          微信小程序前端（微信开发者工具导入此目录）
├── backend/         Flask 后端（app.py / requirements.txt / 接口说明见 backend/README.md）
├── database/       SQLite 数据库（首次启动后端时自动生成 smartquiz.db，勿手动上传）
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
- 首次运行会在 `../database/smartquiz.db` 自动建库、建表并灌入演示数据（题库 19 题、分类、考试等）。
- 服务默认监听 `http://127.0.0.1:5000`，**重启不会丢失答题记录**。

### 2. 打开前端
1. 打开**微信开发者工具 → 导入项目 → 选择 `front/` 目录**。
2. 在「详情 → 本地设置」勾选 **不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**（否则无法访问本地后端）。
3. 编译运行。

> 真机预览：把 `front/utils/api.js` 顶部的 `BASE_URL` 从 `127.0.0.1` 改为电脑局域网 IP，手机与电脑同一 Wi-Fi 即可访问。

## 功能闭环演示路径
首页 → 题库分类/热门题库 → 答题 → 提交判分 → 查看结果 → 错题自动进错题本 → 学习统计实时更新 → 我的信息。

## 接口概览
全部接口及字段约定见 [`backend/README.md`](backend/README.md)。统一前缀 `/api`，返回 `{"code":0,"data":...,"msg":"ok"}`。

## 常见问题
- **数据库需要上传吗？** 不需要。后端首启自动生成 `smartquiz.db`，已通过 `.gitignore` 忽略。
- **想重新演示干净数据？** 删除 `database/smartquiz.db` 后重启后端即可重建。
- **没有 Python 环境的评审场景？** 建议录一份演示视频/截图。