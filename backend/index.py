import sys
from pathlib import Path

import netifaces
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Any, Optional
from enum import Enum
import re # 引入 re 模块用于 GUID 识别

# --- 1. 定义数据结构 (Pydantic 模型) ---

# 使用 Enum 来限制 interface_type 的可选值
class InterfaceType(str, Enum):
    wired = "wired"
    wireless = "wireless"
    both = "both"

# --- 2. 核心逻辑函数 (增强跨平台支持) ---

def get_specific_interfaces(interface_type: InterfaceType) -> Dict[str, Dict[str, Any]]:
    """
    获取特定类型的网络接口及其地址信息，支持 Windows 和 Linux 平台。
    
    通过检测操作系统 (sys.platform) 来应用不同的接口名称模式进行有线/无线判断。
    
    :param interface_type: 'wired', 'wireless', 或 'both'
    :return: 包含接口名称和地址信息的字典。
    """
    
    # 确定操作系统，以便使用正确的名称模式
    current_os = sys.platform
    
    # --- 平台特定的网卡名称模式 ---
    if current_os.startswith('win'):
        # Windows (win32/win64) 模式
        # 注意: netifaces 在 Windows 上返回 GUID，这些名称模式只对少数非 GUID 虚拟接口有效。
        wired_patterns = ['ethernet', 'local area connection', '以太网', 'eth', 'vpn']
        wireless_patterns = ['wi-fi', 'wireless', 'wlan', '无线网络']
        # 在 Windows 上，通常需要过滤掉 Loopback, Teredo, ISATAP 等虚拟/隧道接口。
        exclude_patterns = ['loopback', 'teredo', 'isatap', 'pseudo']
    else:
        # Linux/macOS/Unix-like 模式 (默认)
        wired_patterns = ['eth', 'en', 'em', 'p1p', 'eno', 'ens'] # eth0, en0, ens33, etc.
        wireless_patterns = ['wlan', 'wlp', 'wifi', 'wi-fi', 'ath', 'wlo'] # wlan0, wlp2s0, etc.
        # 在 Linux 上通常只需过滤 lo (Loopback)
        exclude_patterns = ['lo', 'vbox', 'docker', 'virbr', 'br-'] # 排除 loopback 和虚拟桥接
        
    # GUID 正则表达式模式，用于识别 Windows 接口名
    guid_pattern = re.compile(r"\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}")

    try:
        # 获取所有接口名称
        interfaces = netifaces.interfaces()
    except Exception as e:
        print(f"Error getting interfaces: {e}")
        raise HTTPException(
            status_code=500, 
            detail="无法获取网络接口信息，请确保运行环境权限正确。"
        )

    result = {}
    
    for interface in interfaces:
        interface_lower = interface.lower()
        
        # 1. 排除不相关的虚拟/系统接口
        if any(pattern in interface_lower for pattern in exclude_patterns):
            continue
            
        # 检查是否为 Windows GUID 接口
        is_guid_interface = False
        if current_os.startswith('win') and guid_pattern.fullmatch(interface):
            is_guid_interface = True
            # **注意:** GUID 接口无法通过名称分类。在 'wired' 或 'wireless' 模式下，
            # 它们将被过滤。只有在 'both' 模式下才会显示。
            # 如果需要可靠的分类，请使用 Windows WMI 或 psutil 库进行 GUID 到友好名称的映射。

        # 2. 判断网卡类型 (基于平台特定模式)
        is_wired = False
        is_wireless = False
        
        # 仅对非 GUID 接口名进行模式匹配
        if not is_guid_interface:
            is_wired = any(pattern in interface_lower for pattern in wired_patterns)
            is_wireless = any(pattern in interface_lower for pattern in wireless_patterns)
        
        # 3. 根据请求类型筛选
        if interface_type == InterfaceType.wired and not is_wired:
            continue
        elif interface_type == InterfaceType.wireless and not is_wireless:
            continue
        elif interface_type == InterfaceType.both:
            # 'both' 模式下，允许 GUID 接口和被识别的 wired/wireless 接口通过
            if not is_guid_interface and not (is_wired or is_wireless):
                # 如果不是 GUID 接口，但未被识别为 wired/wireless，则跳过
                continue
        elif is_guid_interface:
            # 如果不是 'both' 模式，并且是无法分类的 GUID 接口，则跳过
            continue
                
        # 4. 获取该接口的地址信息
        try:
            addrs = netifaces.ifaddresses(interface)
        except ValueError:
            # 接口可能已被删除或状态改变，跳过
            continue
            
        interface_info: Dict[str, Any] = {}
        
        # IPv4 地址
        if netifaces.AF_INET in addrs:
            interface_info['IPv4'] = addrs[netifaces.AF_INET]
        
        # IPv6 地址
        if netifaces.AF_INET6 in addrs:
            interface_info['IPv6'] = addrs[netifaces.AF_INET6]
            
        # MAC 地址 (AF_LINK / AF_PACKET)
        # Windows 使用 AF_LINK，Linux 也使用 AF_PACKET 或 AF_LINK
        # 我们检查 AF_LINK 并尝试获取 MAC
        if netifaces.AF_LINK in addrs and addrs[netifaces.AF_LINK]:
            # 取第一个地址的 'addr' 字段作为 MAC 地址
            interface_info['MAC'] = addrs[netifaces.AF_LINK][0].get('addr')

        # 只有在获取到地址信息时才加入结果
        if interface_info:
            # 如果是 GUID 接口，我们可以尝试在结果中保留 GUID 接口名，或者如果能获取到更好的名称则替换（本例中无法直接获取，故保留 GUID）
            result[interface] = interface_info
    
    return result

# --- 3. 创建 FastAPI 实例和路由 ---

app = FastAPI(
    title="跨平台网络接口信息API",
    description="提供获取有线、无线或所有网络接口及其地址信息的功能，支持 Windows 和 Linux。"
)

# 挂载static

@app.get("/api/interfaces", 
         summary="获取网络接口信息",
         response_description="返回指定类型的网络接口及其地址信息")
def read_interfaces(
    interface_type: InterfaceType = Query(
        InterfaceType.both, 
        description="选择要显示的接口类型。",
        example="wired"
    )
) -> Dict[str, Dict[str, Any]]:
    """
    根据 `interface_type` 参数获取特定的网络接口信息。
    
    - **wired**: 只显示有线网卡 (在 Windows 上可能无法识别 GUID 接口)。
    - **wireless**: 只显示无线网卡 (在 Windows 上可能无法识别 GUID 接口)。
    - **both**: 显示所有被识别的有线和无线网卡，以及无法分类的 GUID 接口 (默认)。
    """
    
    return get_specific_interfaces(interface_type)

# --- 4. 运行应用 ---
py_dir = Path(__file__).absolute().parents[1]
dist_dir = py_dir / "dist"
app.mount("", StaticFiles(directory=dist_dir), name="static")

# 启动命令: uvicorn app:app --reload