from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI() # app 是 FastAPI/ASGI 应用对象，约定俗成命名为 app

class AnalyzeRequest(BaseModel):
    text: str
# req 是 AnalyzeRequest 实例，req.text 是 str 类型属性
# text 缺失或类型错误时，FastAPI/Pydantic 返回 422

@app.post("/api/analyze") # 处理函数的 req 参数接收经过 AnalyzeRequest 校验并转换后的数据
def analyze(req: AnalyzeRequest):
    return {
        "text": req.text,
        "score": 0.5,
        "label": "偏平静",
        "pinyin": "（模块 6 再说）",
    }

profile = {
    "heroTitle": "关于我",
    "heroSubtitle": "项目，创意，灵感，心得，我的作品",
}

@app.get("/api/profile") # 将 /api/profile 的 GET 请求交给 get_profile 处理
def get_profile():
    return profile
