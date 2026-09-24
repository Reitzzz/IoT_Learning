from fastapi import FastAPI

from app.api.devices import router as devices_router

app = FastAPI(title="IoT Device API")

# APIRouter 只负责定义和分组路由，本身不能启动服务。
# 只有 include_router 把它注册到 app 后，接口才真正生效；
# 如果漏掉这一行，Swagger 里不会出现 /devices 接口。
app.include_router(devices_router)
