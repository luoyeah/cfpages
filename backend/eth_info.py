import platform
from typing import List, Dict


if platform.system() == "Windows":
    import winreg  # Windows标准库，无需额外安装


import netifaces

def _get_windows_friendly_names() -> Dict[str, str]:
    """
    Windows系统：从注册表读取「适配器GUID（无花括号）」→「友好名称」的映射。
    返回示例：{"37720383-C904-49A1-B76C-1632D18906C6": "以太网"}
    """
    friendly_map = {}
    # 注册表路径：所有网络适配器的根键（微软定义的固定路径）
    reg_root = r"SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}"
    
    try:
        # 打开注册表根键（HKEY_LOCAL_MACHINE）
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_root) as key:
            # 遍历所有子键（每个子键对应一个网络适配器，名为GUID带花括号）
            for i in range(winreg.QueryInfoKey(key)[0]):  # [0]是子键数量
                guid_with_braces = winreg.EnumKey(key, i)  # 获取子键名（如"{xxx}"）
                clean_guid = guid_with_braces.strip("{}")  # 去除花括号
                
                # 打开该适配器的Connection子键（存储友好名称）
                conn_key_path = fr"{reg_root}\{guid_with_braces}\Connection"
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, conn_key_path) as conn_key:
                        # 读取Name值（即友好名称，如“以太网”）
                        name, _ = winreg.QueryValueEx(conn_key, "Name")
                        friendly_map[clean_guid] = name
                except FileNotFoundError:
                    # 无Connection子键（无效适配器），跳过
                    continue
                except OSError as e:
                    print(f"警告：读取适配器{clean_guid}失败 → {str(e)}")
                    continue
    except FileNotFoundError:
        print("错误：找不到网络适配器注册表路径！")
    except OSError as e:
        print(f"错误：打开注册表失败 → {str(e)}")
    
    return friendly_map


def get_network_interfaces() -> List[Dict]:
    """
    获取所有网络接口的信息（跨平台）：
    - friendly_name：友好名称（Windows来自注册表，Linux用原生名）
    - original_name：原始名称（netifaces返回的GUID或Linux名）
    - ipv4：IPv4地址列表
    - ipv6：IPv6地址列表
    """
    system = platform.system()
    friendly_map = _get_windows_friendly_names() if system == "Windows" else {}
    interfaces = netifaces.interfaces()


    result = []
    
    for iface in interfaces:
        # 1. 处理友好名称
        if system == "Windows":
            clean_guid = iface.strip("{}")
            friendly_name = friendly_map.get(clean_guid, iface)  # 找不到则用原始GUID
        else:
            friendly_name = iface  # Linux原生名已友好
            
            
        if not _is_valid_eth_name(friendly_name):
            continue
        
        # 2. 提取IP地址（IPv4/IPv6）
        try:
            addr_info = netifaces.ifaddresses(iface)
        except ValueError:
            continue  # 忽略无效接口
        
        ipv4 = [info["addr"] for info in addr_info.get(netifaces.AF_INET, [])]
        ipv6 = [info["addr"] for info in addr_info.get(netifaces.AF_INET6, [])]
        
        # 3. 过滤无IP的接口（可选，保留可删除）
        if not ipv4 and not ipv6:
            continue
        
        # 自定义过滤
        if not _is_valid_ipv4(ipv4):
            continue

        ipv6 = _filter_ipv6(ipv6)

        result.append({
            "eth": friendly_name,
            "ipv4": ipv4,
            "ipv6": ipv6
        })
    
    return result
    
def _is_valid_eth_name(eth_name):
    # 黑名单模式
    block_list = ['tun']
    
    # 判断是否在黑名单内
    for _ in block_list:
        if eth_name.startswith(_):
            return False
            
    return True


def _is_valid_ipv4(ipv4):
    # 过滤没有ipv4的。
    if not ipv4:
        return False
    
    # 过滤本地回环
    for ip in ipv4:
        if ip.startswith("127."):
            return False
            
    return True

def _filter_ipv6(ipv6):
    result = []
    for ip in ipv6:
        if not ip.startswith("fe80::"):
            result.append(ip)

    return result

        
def _print_interfaces(interfaces: List[Dict]):
    """打印结果（友好格式）"""
    if not interfaces:
        print("未找到有IP地址的网卡！")
        return
    
    for idx, info in enumerate(interfaces, 1):
        print(f"【网卡 {idx}】")
        print(f"  网卡名称：{info['eth']}")
        # print(f"  原始名称：{info['original_name']}")
        print(f"  IPv4地址：{', '.join(info['ipv4']) if info['ipv4'] else '无'}")
        print(f"  IPv6地址：{', '.join(info['ipv6']) if info['ipv6'] else '无'}")
        # print(f"  system: {info['system']}")
        print("-" * 50)


if __name__ == "__main__":
    # 获取接口信息
    interfaces = get_network_interfaces()
    # 打印结果
    _print_interfaces(interfaces)