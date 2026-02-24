import random
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse

app = FastAPI()

# 首页
@app.get("/")
def home():
    return FileResponse("index.html")

# 伪 AI 聊天
responses = [
    "哼，你又来了呀~",
    "你在说什么呀？真是的",
    "啊…你怎么又想起我了~",
    "嗯…好像有点喜欢你呢",
    "讨厌啦，你这么说我害羞了"
]

FREE_LIMIT = 20
user_free_counts = {}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    session_id = data.get("session_id", "default")
    message = data.get("message")
    affection = data.get("affection", 50)
    intimacy = data.get("intimacy", 30)
    
    count = user_free_counts.get(session_id, 0)
    if count >= FREE_LIMIT:
        return {"reply": "今天免费次数用完啦！", "affection": affection, "intimacy": intimacy, "mood": "neutral"}

    reply = random.choice(responses)

    # 简单好感度规则
    if "喜欢" in message or "可爱" in message:
        affection += 2
        intimacy += 1
    elif "讨厌" in message:
        affection -= 3

    affection = max(0, min(100, affection))
    intimacy = max(0, min(100, intimacy))
    user_free_counts[session_id] = count + 1

    return {"reply": reply, "affection": affection, "intimacy": intimacy, "mood": "neutral"}
