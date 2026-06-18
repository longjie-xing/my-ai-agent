"""
============================================
  我的第一个 AI Agent —— 个人知识助手
============================================

这个程序实现了一个命令行 AI 助手，你可以：
1️⃣ 直接提问（像 ChatGPT 一样聊天）
2️⃣ 加载本地知识文件（让 AI 基于你的文档回答）
3️⃣ 保存对话历史

运行方法：
  第一步：复制 .env.example 为 .env，填入你的 APIPassword
  第二步：pip install -r requirements.txt
  第三步：python agent.py

作者：跟着教程一步步学的 AI 新手 (微笑)
"""

# ============================================
# 第一步：导入需要用到的工具包
# ============================================

import os                    # 操作系统功能（读文件、路径等）
from pathlib import Path     # 更优雅的文件路径操作
from dotenv import load_dotenv  # 读取 .env 文件中的配置
from openai import OpenAI    # OpenAI 兼容的 API 客户端（讯飞星火也用这个）


# ============================================
# 第二步：加载配置
# ============================================

# 告诉程序去读取 .env 文件
# 这样你的 API Key 就不会直接写在代码里，更安全
load_dotenv()

# 从 .env 文件中获取 MaaS 配置
# 如果没找到，就给出友好的错误提示
API_KEY = os.getenv("MAAS_API_KEY")
API_BASE = os.getenv("MAAS_API_BASE", "https://maas-api.cn-huabei-1.xf-yun.com/v2")
MODEL_ID = os.getenv("MAAS_MODEL_ID")

if not API_KEY or API_KEY == "你的APIKey在这里":
    print("=" * 50)
    print("[警告]  还没配置 API Key 呢！")
    print()
    print("操作步骤：")
    print("  1. 打开 .env 文件（复制 .env.example 为 .env）")
    print("  2. 登录讯飞星辰 MaaS 平台：https://maas.xfyun.cn")
    print("  3. 开通/订阅模型服务")
    print('  4. 在"服务管控"->"模型服务列表"->"调用信息"中获取：')
    print("     - API Key")
    print("     - API Base URL")
    print("     - Model ID")
    print("  5. 把上面的值填到 .env 文件里")
    print("=" * 50)
    exit()  # 退出程序

if not MODEL_ID or MODEL_ID == "你的ModelID在这里":
    print("=" * 50)
    print("[警告]  还没配置 Model ID 呢！")
    print("   请在 .env 文件中填写 MAAS_MODEL_ID")
    print("   从服务管控 -> 调用信息中获取")
    print("=" * 50)
    exit()


# ============================================
# 第三步：创建 AI 客户端
# ============================================

# 讯飞星辰 MaaS 平台 API 是 OpenAI 兼容格式
# 所以我们用 OpenAI 的库，但把服务器地址和 Key 改成 MaaS 的
# 这样好处是：以后换其他 AI 平台，只需要改 base_url 和 api_key 两行！
client = OpenAI(
    api_key=API_KEY,       # 你的 MaaS API Key
    base_url=API_BASE      # MaaS 平台的服务地址
)


# ============================================
# 第四步：核心功能 ① —— 聊天
# ============================================

def chat(messages):
    """
    向 AI 发送消息并获取回复。

    参数 messages: 对话历史列表
    每个元素的格式：{"role": "...", "content": "..."}
      - role="system"  → 系统指令（设定 AI 的角色和行为）
      - role="user"    → 用户说的话
      - role="assistant" → AI 的回复

    返回值: AI 回复的文本内容
    """
    try:
        # 发送请求给 AI
        # 这就像你在网页上按了"发送"按钮
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.7,    # 0~2 之间的数：越小越保守，越大越有创意
            max_tokens=2048,    # AI 最多回复多少个字（约等于 token 数）
        )

        # 从返回结果中提取 AI 说的文本
        reply = response.choices[0].message.content
        return reply

    except Exception as e:
        # 如果出错了（比如网络问题、API Key 不对），
        # 返回错误信息，而不是让程序崩溃
        return f"哎呀，出错了：{e}"


# ============================================
# 第五步：核心功能 ② —— 加载知识文件
# ============================================

def load_knowledge(file_path):
    """
    读取一个本地文本文件，返回文件内容。

    参数 file_path: 文件路径（可以是 .txt、.md 等文本格式）

    返回值: (文件名, 文件内容) 如果出错返回 None
    """
    path = Path(file_path)

    # 检查文件是否存在
    if not path.exists():
        print(f"  [错误] 文件不存在：{file_path}")
        return None

    try:
        # 读取文件内容（with 语句会自动关闭文件，不用手动管）
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return (path.name, content)

    except Exception as e:
        # 如果读取出错（比如文件是二进制的），提示用户
        print(f"  [错误] 读取文件失败：{e}")
        return None


def load_multiple_files(file_paths):
    """
    同时加载多个知识文件。

    参数 file_paths: 文件路径列表

    返回值: 合并后的知识文本（带文件名标记），以及加载了多少个文件
    """
    combined = ""
    count = 0

    for fp in file_paths:
        result = load_knowledge(str(fp).strip())
        if result:
            name, content = result
            # 用文件名作为分隔标记，方便 AI 知道信息来自哪个文件
            combined += f"\n===== 文件：{name} =====\n{content}\n"
            print(f"  [OK] 已加载：{name}（{len(content)} 个字符）")
            count += 1

    return combined, count


def load_knowledge_directory(dir_path="knowledge"):
    """
    加载整个目录下的所有 .txt 和 .md 文件。

    参数 dir_path: 知识目录路径（默认 knowledge 文件夹）

    返回值: 合并后的知识文本，以及加载了多少个文件
    """
    path = Path(dir_path)

    if not path.exists() or not path.is_dir():
        print(f"  [错误] 目录不存在：{dir_path}")
        return "", 0

    # 查找目录下所有的 .txt 和 .md 文件
    files = sorted(list(path.glob("*.txt")) + list(path.glob("*.md")))

    if not files:
        print(f"  [错误] 目录 {dir_path} 中没有找到 .txt 或 .md 文件")
        return "", 0

    print(f"  [目录] 在 {dir_path}/ 目录下找到 {len(files)} 个知识文件：")
    return load_multiple_files(files)


# ============================================
# 第六步：核心功能 ③ —— 带知识库的问答
# ============================================

def ask_with_knowledge(question, knowledge_text):
    """
    基于本地知识内容回答问题。

    原理（这一步就是最简单的 RAG——检索增强生成）：
      把知识文本放在系统指令里，告诉 AI "请基于以下资料回答"，
      AI 就会根据你提供的资料来回答问题，不会自己瞎编。

    参数:
      question:      用户的问题
      knowledge_text: 本地知识文本内容

    返回值: AI 的回答
    """
    # 构建系统指令 —— 这是 AI 的行为准则
    system_prompt = f"""你是一个个人知识助手。
请基于以下提供的资料来回答用户的问题。
如果资料里没有相关信息，就诚实地告诉用户"资料中没有提到这一点"。
不要编造答案。

--- 以下是参考资料 ---
{knowledge_text}
--- 资料结束 ---"""

    # 把系统指令和用户问题组合成消息列表
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    # 调用聊天功能
    return chat(messages)


# ============================================
# 第七步：主界面 —— 命令行交互
# ============================================

def main():
    """
    程序的主入口。运行这个函数就启动了 AI 助手。
    """
    # 显示欢迎信息
    print()
    print("=" * 50)
    print("   个人知识助手 AI Agent  v1.0")
    print("=" * 50)
    print()
    print("[提示] 你可以这样跟我玩：")
    print("  直接输入问题 -> 像聊天一样问我")
    print("  /load 文件名  -> 加载一个本地知识文件")
    print("  /ask 问题     -> 基于已加载的知识来回答")
    print("  /clear        -> 清空对话历史")
    print("  /help         -> 显示帮助")
    print("  /quit         -> 退出程序")
    print()

    # ============================================
    # 对话历史
    # 这是一个列表，记录了所有说过的话
    # AI 就是根据这个"记住"上下文的
    # ============================================
    messages = [
        # 系统指令：告诉 AI 它的身份
        {"role": "system", "content": "你是一个友好的个人知识助手。回答简洁、准确、有条理。"}
    ]

    # 当前加载的知识文本和文件列表（初始为空）
    knowledge_text = None
    loaded_files = []

    # ============================================
    # 无限循环 —— 用户问一次，AI 答一次
    # 直到用户说 /quit 才退出
    # ============================================
    while True:
        # 获取用户输入（input 函数会在终端等待你打字）
        user_input = input("[你] ").strip()

        # ---------- 退出 ----------
        if user_input.lower() in ["/quit", "/exit", "再见", "拜拜"]:
            print("[助手] 拜拜！下次再来找我玩~")
            break

        # ---------- 帮助 ----------
        elif user_input == "/help":
            print()
            print("[帮助菜单]")
            print("  /load 文件1 文件2 ...  -> 加载一个或多个知识文件")
            print("  /loaddir [目录名]      -> 加载整个目录的知识文件")
            print("  /ask 你的问题          -> 基于知识库回答")
            print("  /list                 -> 查看已加载的知识文件")
            print("  /clear                -> 清空对话历史")
            print("  /help                 -> 显示这个帮助")
            print("  /quit                 -> 退出程序")
            print()

        # ---------- 清空对话 ----------
        elif user_input == "/clear":
            # 重置对话历史，但保留系统指令
            messages = [messages[0]]
            knowledge_text = None
            loaded_files = []
            print("[助手] 好的，对话历史已清空！重新开始吧~")
            print()

        # ---------- 查看已加载的知识文件 ----------
        elif user_input == "/list":
            if not loaded_files:
                print("[信息] 当前没有加载任何知识文件")
                print("   用 /load 文件名 或 /loaddir 来加载")
            else:
                print(f"[信息] 已加载 {len(loaded_files)} 个知识文件：")
                for i, f in enumerate(loaded_files, 1):
                    print(f"  {i}. {f}")
                total = len(knowledge_text) if knowledge_text else 0
                print(f"   共 {total} 个字符")
            print()

        # ---------- 加载知识文件（支持多个）----------
        elif user_input.startswith("/load "):
            # 提取文件名列表（/load 后面的部分，按空格分隔）
            parts = user_input[6:].strip().split()

            if not parts:
                print("  [错误] 请指定要加载的文件名")
                print("    示例：/load 我的笔记.txt")
                print("    示例：/load 知识1.txt 知识2.md 知识3.txt")
                print()
                continue

            print(f"  [信息] 正在加载 {len(parts)} 个文件...")
            combined, count = load_multiple_files(parts)

            if count > 0:
                knowledge_text = combined
                loaded_files = parts[:]
                print(f"[OK] 知识库已更新，共 {count} 个文件，{len(combined)} 个字符")
                print("   你可以用 /ask 来基于这些知识提问了")
            print()

        # ---------- 加载整个目录的知识文件 ----------
        elif user_input.startswith("/loaddir"):
            # 提取目录名（/loaddir 后面的部分，如果没有则默认 knowledge）
            parts = user_input[9:].strip().split()
            dir_path = parts[0] if parts else "knowledge"

            combined, count = load_knowledge_directory(dir_path)

            if count > 0:
                knowledge_text = combined
                loaded_files = [str(p) for p in Path(dir_path).glob("*") if p.suffix in (".txt", ".md")]
                print(f"[OK] 知识库已更新，共 {count} 个文件，{len(combined)} 个字符")
                print("   你可以用 /ask 来基于这些知识提问了")
            print()

        # ---------- 基于知识提问 ----------
        elif user_input.startswith("/ask "):
            # 提取问题（/ask 后面的部分）
            question = user_input[5:].strip()

            # 检查是否已经加载了知识文件
            if not knowledge_text:
                print("[助手] 助手：你还没加载知识文件呢！先用 /load 文件名.txt 加载一个吧~")
                print()
                continue

            # 带着知识回答问题
            print("[助手] 助手：让我看看资料...", end=" ", flush=True)
            reply = ask_with_knowledge(question, knowledge_text)
            print()
            print(f"[助手] 助手：{reply}")
            print()

        # ---------- 普通聊天 ----------
        else:
            # 把用户说的话加入对话历史
            messages.append({"role": "user", "content": user_input})

            # 显示"正在思考"的提示
            print("[助手] 助手：", end="", flush=True)

            # 调用 AI 获取回复
            reply = chat(messages)

            # 把 AI 的回复也加入对话历史（这样 AI 就能记住上下文）
            messages.append({"role": "assistant", "content": reply})

            # 显示 AI 的回复
            print(reply)
            print()


# ============================================
# 第八步：启动程序
# ============================================

# 这行代码的意思是：
# "如果这个文件是直接运行的，就执行 main() 函数"
# 以后你写更多 Python 程序都可以这样写
if __name__ == "__main__":
    main()
