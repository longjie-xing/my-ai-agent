# 🤖 个人知识助手 AI Agent

一个功能全面的 AI 对话助手 Web 应用，基于 **Agnes AI API**（OpenAI 兼容格式），支持文字对话、图片生成、视频生成、知识库问答。

## ✨ 功能一览

| 功能 | 说明 |
|------|------|
| 💬 **AI 对话** | 流式输出，逐字显示回复，支持 Markdown 渲染 |
| 🎨 **图片生成** | 输入描述，调用 `agnes-image-2.1-flash` 生成图片 |
| 🎬 **视频生成** | 异步任务，自动轮询完成状态，完成后嵌入播放器 |
| 📚 **知识库问答** | 基于 `knowledge/` 目录文件内容进行 RAG 问答 |
| 🔀 **多模型切换** | 可在 `agnes-2.0-flash` / `agnes-1.5-flash` 间切换 |
| 🌙 **深色模式** | 一键切换，偏好自动保存 |
| 📁 **对话管理** | 多对话、重命名、置顶、搜索、按时间分组 |
| 📎 **文件上传** | 图片自动缩略图 + AI 理解，文本文件自动读取内容 |
| ✏️ **编辑消息** | 双击自己发的消息可编辑后重新发送 |
| 🛑 **停止生成** | AI 回复时可随时中断 |
| 📋 **代码复制** | 代码块右上角一键复制 |
| 📤 **对话导出** | 导出为 JSON 或 TXT 格式 |
| 📱 **移动端适配** | 窄屏侧栏可滑出，响应式布局 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
copy .env.example .env
```

打开 `.env`，将 `YOUR_API_KEY` 替换为你的 Key（从 [platform.agnes-ai.com](https://platform.agnes-ai.com/settings/apiKeys) 获取）。

### 3. 运行

```bash
python web_app.py
```

浏览器打开 **http://localhost:5000**

## 📁 项目结构

```
my-ai-agent/
├── web_app.py              # Flask 后端
├── templates/
│   └── chat.html           # 前端界面（单页）
├── knowledge/              # 知识库目录
│   ├── AI概念入门.md
│   ├── python入门.md
│   └── 我的笔记.txt
├── .env                    # API 配置（不提交）
├── .env.example            # 配置模板
├── requirements.txt        # 依赖
├── start.bat               # Windows 启动脚本
└── agent.py                # 命令行版（旧）
```

## 🧠 技术栈

- **后端**: Python Flask
- **前端**: 原生 HTML + CSS + JavaScript
- **AI API**: Agnes AI（OpenAI 兼容格式）
- **Markdown**: marked.js
- **模型**: agnes-2.0-flash / agnes-1.5-flash / agnes-image-2.1-flash / agnes-video-v2.0
