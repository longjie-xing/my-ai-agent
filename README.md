# 🤖 个人知识助手 AI Agent

一个适合新手的 Python AI 项目，基于 **讯飞星火大模型 API**。

## 你能学到什么？

| 知识点 | 说人话版 |
|--------|---------|
| 调用 AI API | 让程序和 AI "打电话" |
| Prompt 工程 | 怎么写指令让 AI 听你的 |
| RAG 入门 | 让 AI 基于你自己的资料回答问题 |
| 环境变量管理 | 把密码藏好，不泄露 |
| 对话历史管理 | 让 AI 记住上下文 |

## 准备工作

1. **安装 Python 3.12+** ✅ 你已装好
2. **安装 VS Code**（如果没装，去 code.visualstudio.com 下载）
3. **VS Code 装 Python 插件**（左侧扩展 → 搜 Python → 安装）
4. **注册讯飞星火账号** → https://console.xfyun.cn/app/myapp
5. **拿到 APIPassword**（在控制台 → 应用 → 服务接口认证信息）

## 快速开始

### 第 1 步：在 VS Code 中打开项目

```bash
# 打开 VS Code，按 Ctrl+K Ctrl+O
# 选择文件夹：D:\Program Files\atomcode\my-ai-agent
```

或者打开终端（cmd）运行：
```bash
code "D:\Program Files\atomcode\my-ai-agent"
```

### 第 2 步：配置 API Key

```bash
# 复制模板文件
copy .env.example .env
```

然后打开 `.env` 文件，把 `你的APIPassword在这里` 改成你在讯飞拿到的密码。

### 第 3 步：安装依赖

在 VS Code 的终端（Ctrl+`）里运行：
```bash
pip install -r requirements.txt
```

### 第 4 步：运行！

```bash
python agent.py
```

## 使用示例

### 💬 普通聊天
```
👤 你：你好，你是谁？
🤖 助手：你好！我是你的个人知识助手，你可以问我任何问题...
```

### 📄 基于本地知识问答
先创建一个知识文件（比如 `我的笔记.txt`），然后：
```
👤 你：/load 我的笔记.txt
📚 知识库已更新！

👤 你：/ask 我的笔记里提到了哪些技术？
🤖 助手：让我看看资料...根据你的笔记，提到了 Python、JavaScript...
```

## 进阶玩法（自己尝试！）

- [ ] 支持多个知识文件
- [ ] 支持 PDF/Word 文档
- [ ] 保存聊天记录到文件
- [ ] 用 Flask 做个网页界面
- [ ] 接入更多功能（天气查询、待办事项...）
