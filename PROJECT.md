# 个人知识助手 AI Agent - 项目文档

## 项目位置
D:\Program Files\atomcode\my-ai-agent

## 启动方式
cd /d "D:\Program Files\atomcode\my-ai-agent" && python web_app.py
浏览器打开 http://localhost:5000

## 项目文件

### 核心文件
- web_app.py          — Flask 后端（API、Token统计、知识库加载）
- templates/chat.html — 前端界面（DeepSeek风格、对话管理、文件上传）
- .env                — API配置（AGNES_API_KEY / AGNES_API_BASE / AGNES_MODEL_ID）
  - 也兼容旧的 MAAS_API_KEY / MAAS_API_BASE / MAAS_MODEL_ID
- requirements.txt    — Python依赖（flask, openai, python-dotenv）

### 知识库目录
- knowledge/AI概念入门.md
- knowledge/python入门.md
- knowledge/我的笔记.txt

### 旧文件（命令行版，Web版完善后可删除）
- agent.py            — 命令行版知识助手
- test_api.py         — API连通性测试

## 已实现功能

### 界面
- [x] DeepSeek风格UI（左侧栏 + 中央聊天区 + 输入框）
- [x] 欢迎页面（首次打开时显示）
- [x] 聊天气泡（用户蓝色/助手白色）

### 对话管理
- [x] 多对话（左侧列表）
- [x] 新建对话（+ 按钮）
- [x] 切换对话（单击）
- [x] 重命名（双击 或 ⋮菜单）
- [x] 置顶（⋮菜单 → 置顶）
- [x] 删除（⋮菜单 → 删除 / x按钮）
- [x] 按时间分组（7天内/30天内/月份）
- [x] 本地持久化（localStorage，刷新不丢失）

### 文件上传
- [x] 图片上传（自动显示缩略图）
- [x] 图片点击放大查看（全屏遮罩）
- [x] 文本文件上传（自动读取内容到输入框）
- [x] 支持格式：图片、PDF、Word、Excel、PPT、TXT、MD、CSV

### AI对话
- [x] 文字聊天
- [x] 图片理解识别
- [x] 知识库问答（基于 knowledge/ 目录内容）
- [x] Token消耗统计（输入/输出/总计）

### 设置面板
- [x] Token消耗统计
- [x] API信息显示（模型名称、API地址）
- [x] 知识库文件列表

## API 接口
- GET  /              — 首页
- POST /api/chat      — 聊天（支持文字+图片），返回reply+usage
- GET  /api/knowledge — 知识库信息
- GET  /api/stats     — Token累计统计

## 已知问题
- 历史消息中的图片仅保存标记，刷新后不保留实际图片数据（前端 localStorage 限制）

## 开发环境
- Python 3.12
- Flask 3.1.3
- OpenAI Python SDK
- Agnes AI 平台（模型: agnes-2.0-flash / API: apihub.agnes-ai.com/v1）

## 变更记录

### 2026-06-17 — 模型切换（讯飞星辰 MaaS → Agnes AI）
- **API 提供商切换**：从讯飞星辰 MaaS 切换到 Agnes AI（OpenAI 兼容格式）
- **新模型**：`xopqwen36v35b` → `agnes-2.0-flash`
- **新 API 地址**：`https://maas-api.cn-huabei-1.xf-yun.com/v2` → `https://apihub.agnes-ai.com/v1`
- **环境变量重命名**：`MAAS_API_KEY/MAAS_API_BASE/MAAS_MODEL_ID` → `AGNES_API_KEY/AGNES_API_BASE/AGNES_MODEL_ID`
- **向后兼容**：代码仍支持旧的 `MAAS_*` 变量名作为回退
- **已验证**：API 连通性测试通过，Web 应用正常加载
