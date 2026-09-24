from fastapi import APIRouter, HTTPException

from app.models.device import CommandRequest
from app.services import device_service

# APIRouter 是“路由分组容器”，不是另一个 FastAPI 应用。
# 这里按业务/资源分组：GET 和 POST 都围绕“设备”这一类资源，
# 所以放在同一个 devices 路由组，而不是按 HTTP 方法拆成 get_router / post_router。
#
# prefix="/devices" 是这一组路由的统一 URL 前缀。
# 完整路径 = prefix + @router 装饰器里的 path，因此：
#   @router.get("")                      -> GET /devices
#   @router.get("/{device_id}")          -> GET /devices/{device_id}
#   @router.post("/{device_id}/command") -> POST /devices/{device_id}/command


# tags=["devices"] 只是 Swagger/OpenAPI 文档的分组标签，
# 只影响 /docs 页面中的归类，不改变 URL、HTTP 方法或业务逻辑。
router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("")
def get_devices():
    return device_service.list_devices()


@router.get("/{device_id}")
def get_device(device_id: str):
    device = device_service.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device


@router.post("/{device_id}/command")
def send_command(device_id: str, req: CommandRequest):
    if device_service.get_device(device_id) is None:
        raise HTTPException(status_code=404, detail="设备号错误")

    if not device_service.command_is_supported(req.command):
        raise HTTPException(status_code=400, detail="暂时不支持该操作")

    device_service.send_command(req.command)

    return {
        "device_id": device_id,
        "command": req.command,
        "status": "命令已发送",
    }
