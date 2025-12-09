
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import eth_info
import adb_info

# --- 4. FastAPI 应用 ---
app = FastAPI()


adb_info.setup_routes(app)
eth_info.setup_routes(app)


# --- 5. 静态文件挂载 ---
py_dir = Path(__file__).absolute().parents[1]
dist_dir = py_dir / "dist"
app.mount("", StaticFiles(directory=dist_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9001)
    # uvicorn.exe index:app --port 9001 --reload