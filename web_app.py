"""
Web 版个人知识助手 AI Agent（多模型支持 + 图片/视频生成）
用法：python web_app.py
然后浏览器打开 http://localhost:5000
"""

import os, time, json, uuid
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from openai import OpenAI
import urllib.request, urllib.error

# 加载配置
load_dotenv()

# 兼容旧的 MAAS_* 环境变量名，优先使用 AGNES_* 新变量
API_KEY = os.getenv("AGNES_API_KEY") or os.getenv("MAAS_API_KEY")
API_BASE = os.getenv("AGNES_API_BASE") or os.getenv("MAAS_API_BASE", "https://apihub.agnes-ai.com/v1")
MODEL_ID = os.getenv("AGNES_MODEL_ID") or os.getenv("MAAS_MODEL_ID", "agnes-2.0-flash")

# 创建 Flask 应用，限制请求最大 20MB（图片生成会大一些）
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# 创建 AI 客户端
client = OpenAI(api_key=API_KEY, base_url=API_BASE, timeout=60.0, max_retries=1)

# ===== Token 统计（全局累计） =====
TOTAL_STATS = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

# ===== 缓存的模型列表 =====
CACHED_MODELS = []
CACHED_MODELS_TIME = 0


def fetch_models():
    """从 Agnes AI 获取可用模型列表（缓存 5 分钟）"""
    global CACHED_MODELS, CACHED_MODELS_TIME
    now = time.time()
    if CACHED_MODELS and now - CACHED_MODELS_TIME < 300:
        return CACHED_MODELS
    try:
        url = API_BASE.rstrip('/') + '/models'
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {API_KEY}'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        models = [{"id": m["id"], "owned_by": m.get("owned_by", "")} for m in data.get("data", [])]
        CACHED_MODELS = models
        CACHED_MODELS_TIME = now
        return models
    except Exception as e:
        # 返回当前的缓存或默认列表
        if CACHED_MODELS:
            return CACHED_MODELS
        return [
            {"id": "agnes-2.0-flash", "owned_by": "custom"},
            {"id": "agnes-1.5-flash", "owned_by": "custom"},
            {"id": "agnes-image-2.1-flash", "owned_by": "custom"},
            {"id": "agnes-image-2.0-flash", "owned_by": "custom"},
            {"id": "agnes-video-v2.0", "owned_by": "custom"},
        ]


def chat_with_ai(messages, model=None, temperature=0.7, max_tokens=2048):
    """调用 AI API，返回 (回复文本, token用量字典)"""
    try:
        response = client.chat.completions.create(
            model=model or MODEL_ID,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        reply = response.choices[0].message.content

        # 提取 token 用量
        usage = response.usage
        tokens = {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }
        # 累加到全局统计
        for k, v in tokens.items():
            TOTAL_STATS[k] += v

        return reply, tokens
    except Exception as e:
        return f"调用 AI 出错：{e}", None


def load_knowledge_files():
    """读取 knowledge 目录下所有知识文件"""
    knowledge_dir = Path("knowledge")
    combined = ""
    files_info = []

    if not knowledge_dir.exists() or not knowledge_dir.is_dir():
        return combined, files_info

    for fp in sorted(list(knowledge_dir.glob("*.txt")) + list(knowledge_dir.glob("*.md"))):
        try:
            content = fp.read_text(encoding="utf-8")
            combined += f"\n===== 文件：{fp.name} =====\n{content}\n"
            files_info.append({"name": fp.name, "size": len(content)})
        except Exception:
            pass

    return combined, files_info


KNOWLEDGE_TEXT, KNOWLEDGE_FILES = load_knowledge_files()


# ========== 路由 ==========

@app.route("/")
def index():
    models = fetch_models()
    return render_template("chat.html",
                           files=KNOWLEDGE_FILES,
                           total_chars=len(KNOWLEDGE_TEXT),
                           has_knowledge=len(KNOWLEDGE_FILES) > 0,
                           model_id=MODEL_ID,
                           models=models,
                           api_base=API_BASE)


@app.route("/api/models", methods=["GET"])
def api_models():
    """返回可用模型列表"""
    models = fetch_models()
    return jsonify({"models": models})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """聊天 API：支持模型选择 + 文字 + 图片理解 + 流式输出 + 参数调节"""
    data = request.get_json()
    user_message = data.get("message", "").strip()
    image_data = data.get("image", "")
    model = data.get("model", MODEL_ID)
    stream = data.get("stream", False)
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 2048)

    if not user_message and not image_data:
        return jsonify({"reply": "请输入消息或上传图片"})

    system_messages = []
    if KNOWLEDGE_TEXT:
        if image_data:
            kb_prompt = f"""你是一个个人知识助手，同时具备图片理解能力。
请结合以下参考资料和用户上传的图片来回答问题。
如果参考资料里有相关信息就用资料回答，如果资料里没有但图片里有信息就用图片回答。

--- 参考资料 ---
{KNOWLEDGE_TEXT}
--- 资料结束 ---"""
        else:
            kb_prompt = f"请基于以下参考资料回答问题。如果资料里没有相关信息，就如实说不知道。\n\n--- 参考资料 ---\n{KNOWLEDGE_TEXT}\n--- 资料结束 ---"
        system_messages.append({"role": "system", "content": kb_prompt})
    system_messages.append({"role": "system", "content": "你是一个友好的个人知识助手。回答简洁、准确、有条理。"})

    if image_data:
        user_content = []
        if user_message:
            user_content.append({"type": "text", "text": user_message})
        else:
            user_content.append({"type": "text", "text": "请描述这张图片"})
        user_content.append({"type": "image_url", "image_url": {"url": image_data}})
        messages = system_messages + [{"role": "user", "content": user_content}]
    else:
        messages = system_messages + [{"role": "user", "content": user_message}]

    if stream:
        def generate():
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                for chunk in response:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        data = json.dumps({"choices": [{"delta": {"content": delta.content}}]})
                        yield f"data: {data}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype="text/event-stream")

    reply, tokens = chat_with_ai(messages, model=model, temperature=temperature, max_tokens=max_tokens)

    result = {"reply": reply, "model": model}
    if tokens:
        result["usage"] = tokens
        result["total_usage"] = dict(TOTAL_STATS)
    return jsonify(result)


@app.route("/api/generate-image", methods=["POST"])
def api_generate_image():
    """图片生成 API（后端下载图片转 base64，避免外部 URL 失效）"""
    import base64 as b64

    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    model = data.get("model", "agnes-image-2.1-flash")
    size = data.get("size", "1024x1024")

    if not prompt:
        return jsonify({"error": "请输入图片描述"}), 400

    try:
        # 不带 response_format，获取 URL
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=1,
        )
        image_url = response.data[0].url if hasattr(response.data[0], 'url') else None
        revised_prompt = getattr(response.data[0], 'revised_prompt', None)

        result = {"model": model}
        if image_url:
            # 后端下载图片并转 base64
            try:
                req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                img_resp = urllib.request.urlopen(req, timeout=30)
                img_bytes = img_resp.read()
                img_b64 = b64.b64encode(img_bytes).decode('utf-8')
                result["image_data"] = img_b64
            except Exception:
                # 下载失败则直接返回 URL
                result["image_url"] = image_url
        if revised_prompt:
            result["revised_prompt"] = revised_prompt
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"图片生成失败：{e}"}), 500


@app.route("/api/generate-video", methods=["POST"])
def api_generate_video():
    """视频生成 API（异步任务）"""
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    model = data.get("model", "agnes-video-v2.0")

    if not prompt:
        return jsonify({"error": "请输入视频描述"}), 400

    try:
        # 视频 API 使用 /v1/video/generations
        api_base = API_BASE.rstrip('/v1').rstrip('/')
        url = f"{api_base}/v1/video/generations"
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "duration": 5,
        }).encode()
        req = urllib.request.Request(url, data=payload,
                                     headers={
                                         'Authorization': f'Bearer {API_KEY}',
                                         'Content-Type': 'application/json',
                                     })
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read().decode())
        return jsonify(result)
    except urllib.error.URLError as e:
        return jsonify({"error": f"视频生成超时（服务端繁忙），请稍后重试"}), 504
    except Exception as e:
        return jsonify({"error": f"视频生成失败：{e}"}), 500


@app.route("/api/video-status/<task_id>", methods=["GET"])
def api_video_status(task_id):
    """查询视频生成任务状态"""
    try:
        api_base = API_BASE.rstrip('/v1').rstrip('/')
        url = f"{api_base}/v1/video/generations/{task_id}"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {API_KEY}'})
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read().decode())

        # 解包嵌套结构，提取视频信息
        video_url = None
        status = "unknown"
        # 尝试多种路径取视频 URL
        if isinstance(result, dict):
            inner = result.get("data") or result
            if isinstance(inner, dict):
                status = inner.get("status", inner.get("state", "unknown"))
                data_inner = inner.get("data") or inner
                if isinstance(data_inner, dict):
                    video_url = data_inner.get("remixed_from_video_id") or data_inner.get("url") or data_inner.get("output")
                    if data_inner.get("status"):
                        status = data_inner["status"]
                video_url = video_url or inner.get("result_url") or inner.get("video_url") or inner.get("url") or inner.get("output")

        return jsonify({
            "task_id": task_id,
            "status": status,
            "video_url": video_url,
            "url": video_url,
            "output": video_url,
        })
    except Exception as e:
        return jsonify({"error": f"查询失败：{e}"}), 500


@app.route("/api/knowledge", methods=["GET"])
def api_knowledge():
    return jsonify({
        "files": KNOWLEDGE_FILES,
        "total_chars": len(KNOWLEDGE_TEXT),
        "file_count": len(KNOWLEDGE_FILES)
    })


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """返回全局 token 统计"""
    return jsonify(dict(TOTAL_STATS))


@app.route("/api/upload-knowledge", methods=["POST"])
def api_upload_knowledge():
    """上传文件到知识库"""
    if "file" not in request.files:
        return jsonify({"error": "请选择文件"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "文件名不能为空"}), 400
    # 只允许文本文件
    allowed = {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".xml", ".py", ".js", ".html", ".css"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        return jsonify({"error": f"不支持的文件格式: {ext}"}), 400

    knowledge_dir = Path("knowledge")
    knowledge_dir.mkdir(exist_ok=True)
    save_path = knowledge_dir / file.filename

    try:
        content = file.read().decode("utf-8")
        save_path.write_text(content, encoding="utf-8")
        # 重新加载知识库
        global KNOWLEDGE_TEXT, KNOWLEDGE_FILES
        KNOWLEDGE_TEXT, KNOWLEDGE_FILES = load_knowledge_files()
        return jsonify({"success": True, "name": file.filename, "size": len(content)})
    except Exception as e:
        return jsonify({"error": f"上传失败：{e}"}), 500


@app.route("/api/delete-knowledge/<filename>", methods=["DELETE"])
def api_delete_knowledge(filename):
    """删除知识库文件"""
    try:
        file_path = Path("knowledge") / filename
        if file_path.exists():
            file_path.unlink()
            global KNOWLEDGE_TEXT, KNOWLEDGE_FILES
            KNOWLEDGE_TEXT, KNOWLEDGE_FILES = load_knowledge_files()
            return jsonify({"success": True})
        return jsonify({"error": "文件不存在"}), 404
    except Exception as e:
        return jsonify({"error": f"删除失败：{e}"}), 500


# ========== 启动 ==========

if __name__ == "__main__":
    models = fetch_models()
    print("=" * 50)
    print("  知识助手 Web 版已启动！")
    print("  浏览器打开：http://localhost:5000")
    print("=" * 50)
    print(f"  已加载 {len(KNOWLEDGE_FILES)} 个知识文件")
    for f in KNOWLEDGE_FILES:
        print(f"    - {f['name']} ({f['size']} 字符)")
    print(f"  默认模型: {MODEL_ID}")
    print(f"  可用模型: {', '.join(m['id'] for m in models)}")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
