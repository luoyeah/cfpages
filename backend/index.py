
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import eth_info


# --- 4. FastAPI 应用 ---
app = FastAPI(
    title="网络接口有效IP查询API",
    description="返回内网或公网可访问的IP地址，支持Windows/Linux"
)

@app.get("/api/interfaces")
def read_interfaces():
    return eth_info.get_network_interfaces()

# --- 5. 静态文件挂载 ---
py_dir = Path(__file__).absolute().parents[1]
dist_dir = py_dir / "dist"
app.mount("", StaticFiles(directory=dist_dir), name="static")


# uvicorn.exe index:app --port 9001 --reload