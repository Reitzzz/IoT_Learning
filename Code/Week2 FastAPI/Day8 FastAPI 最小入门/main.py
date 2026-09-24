from fastapi import FastAPI, HTTPException

app = FastAPI()

DEVICE_ID = "001"
devices = {
    DEVICE_ID: {
        "device_id": DEVICE_ID,
        "temperature": 36.5,
        "rpm": 1500,
        "status": "RUNNING",
        "last_seen": None,
    }
}


@app.get("/devices")
def get_devices():
    return list(devices.values())
# 返回 devices 中所有设备信息组成的列表


@app.get("/devices/{device_id}")
def get_device(device_id: str):
    device = devices.get(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device
#查询特定device的信息
