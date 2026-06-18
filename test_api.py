"""测试 Agnes AI API 是否可用"""
import os, sys
from dotenv import load_dotenv
load_dotenv()

# 兼容旧的 MAAS_* 环境变量名，优先使用 AGNES_* 新变量
api_key = os.getenv("AGNES_API_KEY") or os.getenv("MAAS_API_KEY")
api_base = os.getenv("AGNES_API_BASE") or os.getenv("MAAS_API_BASE", "https://apihub.agnes-ai.com/v1")
model_id = os.getenv("AGNES_MODEL_ID") or os.getenv("MAAS_MODEL_ID", "agnes-2.0-flash")

# 检查配置
if not api_key or api_key == "YOUR_API_KEY" or api_key == "你的APIKey在这里":
    print("[错误] AGNES_API_KEY 未配置或还是默认值")
    print("请先到 https://platform.agnes-ai.com/settings/apiKeys 创建 API Key")
    sys.exit(1)
if not model_id:
    print("[错误] AGNES_MODEL_ID 未配置")
    sys.exit(1)

print(f"[OK] API Key: {api_key[:8]}...")
print(f"[OK] API Base: {api_base}")
print(f"[OK] Model ID: {model_id}")

from openai import OpenAI
client = OpenAI(api_key=api_key, base_url=api_base)

print("[..] 正在调用 Agnes AI API...")
response = client.chat.completions.create(
    model=model_id,
    messages=[{"role": "user", "content": "你好，请用一句话介绍你自己"}],
    max_tokens=100
)

reply = response.choices[0].message.content
print(f"[OK] 调用成功！")
print(f"[AI] {reply}")
