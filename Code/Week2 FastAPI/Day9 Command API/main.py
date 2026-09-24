from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import publisher
# 优先导入模块、函数或常量，避免依赖跨模块共享的可变全局变量
# main.py 导入 publisher 模块并调用其发送函数
# 由 publisher.py 读取发送参数，避免反向导入 main.py 中的可变状态

app=FastAPI()

class CommandRequest(BaseModel):
    command: str

@app.post("/devices/{device_id}/command")
def send_command(device_id:str,req:CommandRequest): # device_id 来自路径参数；req 是经 CommandRequest 校验后的请求体
  if device_id != "001":
     raise HTTPException(status_code=404,detail="设备号错误") # 使用 FastAPI 的 HTTPException 返回 HTTP 错误

  if req.command != "STOP":
     raise HTTPException(status_code=400,detail="暂时不支持该操作") # 同上

  publisher.publish_command(req.command)
  
  return{
    "device_id": device_id,
    "command": req.command,
    "status": "命令已发送",
  }
# 构造响应字典，并调用 publisher.publish_command 发送 MQTT 命令

