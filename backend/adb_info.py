import re
import os
import json
import subprocess


from fastapi import FastAPI, APIRouter, HTTPException

# 创建路由
router = APIRouter()


def hutxt_to_json(txt):
        # 解析输出
    result = {}
    lines = txt.splitlines()
    
    for line in lines:
        # 匹配键值对（例如 "AC powered: false"）
        match = re.match(r'\s*([^:]+):\s*(.*)', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # 尝试转换数值类型
            if value.isdigit():
                value = int(value)
            elif re.match(r'^-?\d+\.\d+$', value):
                value = float(value)
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
                
            result[key] = value
    
    return result


@router.get("/", summary="Termux-API 信息中心", tags=["Termux-API"])
def termux_info():
    """返回可用的 Termux-API 功能列表"""
    return {
        "available_endpoints": [
            "/battery", 
            "/device", 
            "/sensors", 
            "/location",
            "/storage",
            "/notify"
        ],
        "description": "Termux-API 功能接口"
    }

@router.get("/battery", summary="获取电池状态", tags=["Termux-API"])
def get_battery_status():
    """
    获取设备电池状态信息
    """
    try:
        result = subprocess.run("adb shell dumpsys battery", 
                              capture_output=True, shell=True, text=True, timeout=10)
        
        if result.returncode == 0:
            res_txt = result.stdout
            return hutxt_to_json(res_txt)
        else:
            raise HTTPException(status_code=500, detail="无法获取电池信息")
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="请求超时")
    except FileNotFoundError:
        raise HTTPException(
            status_code=501, 
            detail="adb 未安装，请先安装: android-tools"
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="数据解析错误")

@router.get("/device", summary="获取设备信息", tags=["Termux-API"])
def get_device_info():
    """
    获取设备基本信息和传感器数据
    """
    try:
        # 获取设备信息
        device_result = subprocess.run(["termux-telephony-deviceinfo"], 
                                     capture_output=True, text=True, timeout=10)
        
        # 获取传感器列表
        sensor_result = subprocess.run(["termux-sensor", "-l"], 
                                     capture_output=True, text=True, timeout=10)
        
        response_data = {}
        
        if device_result.returncode == 0:
            response_data["device_info"] = json.loads(device_result.stdout)
        else:
            response_data["device_info"] = {"error": "无法获取设备信息"}
            
        if sensor_result.returncode == 0:
            response_data["available_sensors"] = sensor_result.stdout.strip().split('\n')
        else:
            response_data["available_sensors"] = []
        
        return response_data
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="请求超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备信息失败: {str(e)}")

@router.get("/sensors", summary="获取传感器数据", tags=["Termux-API"])
def get_sensor_data(sensor_name: str = None, limit: int = 5):
    """
    获取传感器数据，可指定特定传感器
    """
    try:
        if sensor_name:
            # 获取特定传感器数据
            cmd = ["termux-sensor", "-s", sensor_name, "-n", str(limit)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        else:
            # 获取所有传感器数据（限制数量避免数据过大）
            result = subprocess.run(["termux-sensor", "-n", "3"], 
                                  capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw_data": result.stdout}
        else:
            raise HTTPException(status_code=404, detail="未找到传感器数据")
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="传感器数据获取超时")

@router.get("/location", summary="获取设备位置", tags=["Termux-API"])
def get_location(provider: str = "gps"):
    """
    获取设备地理位置信息
    """
    try:
        result = subprocess.run(["termux-location"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            location_data = json.loads(result.stdout)
            return {
                "location": location_data,
                "provider": provider,
                "timestamp": "2025-12-06T00:00:00Z"  # 实际使用时应该用当前时间
            }
        else:
            raise HTTPException(status_code=404, detail="无法获取位置信息")
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="位置获取超时，请检查GPS是否开启")

@router.get("/storage", summary="获取存储信息", tags=["Termux-API"])
def get_storage_info():
    """
    获取设备存储空间信息
    """
    try:
        # 使用 termux-storage-getinfo 获取存储信息
        result = subprocess.run(["termux-storage-getinfo"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            # 如果 termux-storage-getinfo 不可用，使用 df 命令
            df_result = subprocess.run(["df", "-h"], 
                                     capture_output=True, text=True, timeout=10)
            return {"storage_info": df_result.stdout.split('\n')}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取存储信息失败: {str(e)}")

@router.post("/notify", summary="发送通知", tags=["Termux-API"])
def send_notification(title: str, content: str):
    """
    向设备发送通知
    """
    try:
        # 使用 termux-notification 发送通知
        result = subprocess.run(["termux-notification", "-t", title, "-c", content], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return {"status": "success", "message": "通知发送成功"}
        else:
            raise HTTPException(status_code=500, detail="通知发送失败")
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="通知发送超时")

@router.get("/system", summary="获取系统信息", tags=["Termux-API"])
def get_system_info():
    """
    获取 Termux 系统信息
    """
    try:
        # 获取系统信息
        uname_result = subprocess.run(["uname", "-a"], 
                                    capture_output=True, text=True, timeout=5)
        memory_result = subprocess.run(["free", "-m"], 
                                     capture_output=True, text=True, timeout=5)
        
        return {
            "system_info": uname_result.stdout.strip(),
            "memory_usage": memory_result.stdout,
            "termux_version": "1.0.0",  # 实际应该从系统获取
            "python_version": "3.11.0"  # 实际应该从系统获取
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")

# 主应用集成示例
def setup_routes(app: FastAPI):
    """
    将 Termux-API 路由挂载到主应用
    """
    app.include_router(router, prefix="/api/adb", tags=["Termux-API"])

