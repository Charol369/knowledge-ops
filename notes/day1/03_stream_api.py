"""Day1 下午 - FastAPI SSE 流式接口
任务：把 LLM 流式输出包装成 HTTP 接口，前端能用 EventSource 接收
"""
import os
import sys

# Windows 控制台默认 GBK，需强制 UTF-8 才能正常输出 emoji 和中文
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()
app = FastAPI(title="Day1 - SSE Demo")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)


class ChatRequest(BaseModel):
    """请求体的 Pydantic 模型"""
    question: str


def stream_llm(question: str):
    """生成器：把 LLM chunk 转成 SSE 格式

    SSE 协议每条消息格式：
        data: <内容>\n\n
    """
    stream = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[{"role": "user", "content": question}],
        stream=True,
    )
    for chunk in stream:
        # 流式最后一个 chunk 可能 choices=[]（只带 usage），需防御
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield f"data: {delta}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/chat")
def chat(req: ChatRequest):
    """SSE 接口：返回流式响应"""
    return StreamingResponse(
        stream_llm(req.question),
        media_type="text/event-stream",
    )


@app.get("/health")
def health():
    """健康检查接口"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
