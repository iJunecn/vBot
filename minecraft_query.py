# -*- coding: utf-8 -*-
"""
Minecraft服务器状态查询模块
"""
import asyncio
from typing import Dict, Optional
from uapi import UapiClient
from uapi.errors import UapiError


class MinecraftServerQuery:
    """Minecraft服务器查询器"""
    
    def __init__(self, base_url: str = "https://uapis.cn", token: str = None):
        self.client = UapiClient(base_url, token=token)
    
    async def query_server(self, server_address: str) -> Optional[Dict]:
        """
        查询单个Minecraft服务器状态
        
        Args:
            server_address: 服务器地址，如 mc.ustb.world
            
        Returns:
            服务器状态信息字典，查询失败返回None
        """
        try:
            # uapi sdk是同步的，在异步环境中使用run_in_executor
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.client.game.get_game_minecraft_serverstatus(server=server_address)
            )
            return result
        except UapiError as exc:
            print(f"[MinecraftQuery] API error when querying {server_address}: {exc}")
            return None
        except Exception as exc:
            print(f"[MinecraftQuery] Unexpected error when querying {server_address}: {exc}")
            return None
    
    async def query_multiple_servers(self, server_list: list) -> Dict[str, Optional[Dict]]:
        """
        批量查询多个服务器状态
        
        Args:
            server_list: 服务器地址列表
            
        Returns:
            服务器地址到状态信息的映射字典
        """
        tasks = []
        for server in server_list:
            tasks.append(self.query_server(server))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            server: result if not isinstance(result, Exception) else None
            for server, result in zip(server_list, results)
        }
    
    def format_server_status(self, server_address: str, status: Optional[Dict], display_name: str = None) -> str:
        """
        格式化服务器状态为可读文本
        
        Args:
            server_address: 服务器地址
            status: 服务器状态信息
            display_name: 显示名称
            
        Returns:
            格式化后的状态文本
        """
        name = display_name or server_address
        
        if status is None:
            return f"❌ {name} ({server_address})\n  状态: 查询失败或服务器离线"
        
        try:
            # 检查是否是成功的响应
            if isinstance(status, dict):
                code = status.get('code', -1)
                if code != 200:
                    msg = status.get('msg', '未知错误')
                    return f"❌ {name} ({server_address})\n  状态: {msg}"
                
                data = status.get('data', {})
                online = data.get('online', False)
                
                if not online:
                    return f"❌ {name} ({server_address})\n  状态: 服务器离线"
                
                # 服务器在线，获取详细信息
                version = data.get('version', '未知版本')
                players_online = data.get('players_online', 0)
                players_max = data.get('players_max', 0)
                motd = data.get('motd', '无描述')
                
                # 获取玩家列表（如果有）
                player_list = data.get('players', [])
                player_names = []
                if isinstance(player_list, list) and len(player_list) > 0:
                    player_names = [p.get('name', '未知') for p in player_list if isinstance(p, dict)]
                
                status_text = f"✅ {name} ({server_address})\n"
                status_text += f"  版本: {version}\n"
                status_text += f"  在线人数: {players_online}/{players_max}"
                
                if player_names:
                    status_text += f"\n  在线玩家: {', '.join(player_names[:10])}"
                    if len(player_names) > 10:
                        status_text += f" 等共{len(player_names)}人"
                
                if motd and motd != '无描述':
                    status_text += f"\n  描述: {motd}"
                
                return status_text
            else:
                return f"❌ {name} ({server_address})\n  状态: 返回数据格式异常"
                
        except Exception as e:
            return f"❌ {name} ({server_address})\n  状态: 解析数据失败 - {str(e)}"
