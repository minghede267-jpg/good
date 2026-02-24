from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import openai

# Railway 环境变量中设置 OPENAI_API_KEY
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = FastAPI()

# 允许跨域访问前端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简单伪 free 用户次数控制（可拓展）
FREE_LIMIT = 20
user_free_counts = {}  # 记录每个 session/ip 当天次数

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    session_id = data.get("session_id", "default")
    message = data.get("message")
    affection = data.get("affection", 50)
    intimacy = data.get("intimacy", 30)
    mood = data.get("mood", "neutral")

    # 免费次数检测
    count = user_free_counts.get(session_id, 0)
    if count >= FREE_LIMIT:
        return {"reply": "今天免费次数用完啦！开通会员解锁更多对话哦～",
                "affection": affection,
                "intimacy": intimacy,
                "mood": mood}

    # Prompt 构建
    prompt = f"""
你是星野澪，一个二次元暧昧型女主。
性格: 傲娇, 暧昧, 会拉扯。
当前好感度: {affection}
当前亲密度: {intimacy}
当前情绪: {mood}

用户说: {message}
请用不超过120字回复。
"""

    # 调用 OpenAI API
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": prompt}],
        max_tokens=200
    )
    reply = resp.choices[0].message.content

    # 简单好感度/亲密度逻辑
    if any(word in message for word in ["喜欢","可爱","爱"]):
        affection += 2
        intimacy += 1
    elif any(word in message for word in ["讨厌","烦"]):
        affection -= 3

    # 限制范围
    affection = max(0, min(100, affection))
    intimacy = max(0, min(100, intimacy))

    # 更新免费次数
    user_free_counts[session_id] = count + 1

    return {
        "reply": reply,
        "affection": affection,
        "intimacy": intimacy,
        "mood": mood
    }
