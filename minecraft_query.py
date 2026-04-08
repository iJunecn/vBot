# -*- coding: utf-8 -*-
"""
Minecraft服务器状态查询模块
"""
import asyncio
import json
from typing import Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class MinecraftServerQuery:
    """Minecraft服务器查询器"""
    
    def __init__(self, base_url: str = "https://motd.minebbs.com", timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    async def query_server(self, server_address: str) -> Optional[Dict]:
        """
        查询单个Minecraft服务器状态
        
        Args:
            server_address: 服务器地址，如 mc.ustb.world
            
        Returns:
            服务器状态信息字典，查询失败返回None
        """
        try:
            raw_response = await asyncio.to_thread(self._fetch_status, server_address)
            return self._normalize_response(raw_response, server_address)
        except (URLError, TimeoutError) as exc:
            print(f"[MinecraftQuery] Network error when querying {server_address}: {exc}")
            return None
        except Exception as exc:
            print(f"[MinecraftQuery] Unexpected error when querying {server_address}: {exc}")
            return None

    def _build_query_url(self, server_address: str) -> str:
        """构造 MineBBS 查询 URL。"""
        params: Dict[str, str] = {}

        if server_address.count(':') == 1:
            params['host'] = server_address
        else:
            params['ip'] = server_address

        params['stype'] = 'auto'
        return f"{self.base_url}/api/status?{urlencode(params)}"

    def _fetch_status(self, server_address: str) -> Dict:
        """同步请求 MineBBS 状态接口。"""
        url = self._build_query_url(server_address)
        request = Request(url, headers={'User-Agent': 'vBot/1.0'})

        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode('utf-8', errors='replace')
        except HTTPError as exc:
            body = exc.read().decode('utf-8', errors='replace')
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {
                    'code': exc.code,
                    'msg': body or exc.reason,
                    'data': None,
                }

        return json.loads(body)

    def _normalize_response(self, payload: Dict, server_address: str) -> Dict:
        """把 MineBBS 返回值规范化成 bot 侧容易处理的结构。"""
        if not isinstance(payload, dict):
            return {
                'code': 500,
                'msg': '返回数据格式异常',
                'data': {
                    'online': False,
                    'raw': payload,
                    'server_address': server_address,
                },
            }

        data = payload.get('data')
        if not isinstance(data, dict):
            data = payload

        status_data = self._extract_status_data(data, server_address)

        code = payload.get('code')
        if code is None:
            code = 200
        else:
            code = self._to_int(code)

        msg = payload.get('msg') or payload.get('message') or 'success'

        return {
            'code': code,
            'msg': msg,
            'data': {
                **status_data,
                'raw': payload,
                'server_address': server_address,
            },
        }

    def _extract_status_data(self, data: Dict, server_address: str) -> Dict:
        """尽量兼容不同返回结构，提取核心状态字段。"""
        online = data.get('online')
        if online is None:
            status_value = data.get('status')
            if isinstance(status_value, bool):
                online = status_value
            elif isinstance(status_value, str):
                online = status_value.lower() in {'online', 'true', '1', 'yes', 'up'}
            else:
                online = bool(data)

        version_value = data.get('version') or data.get('mc_version') or data.get('protocol_version')
        version = self._stringify_version(version_value)

        players_online, players_max, player_names = self._extract_players(data)
        motd = self._stringify_text(data.get('motd') or data.get('description') or data.get('text'))

        return {
            'online': online,
            'version': version,
            'players_online': players_online,
            'players_max': players_max,
            'motd': motd,
            'players': [{'name': name} for name in player_names],
        }

    def _extract_players(self, data: Dict) -> tuple[int, int, list[str]]:
        """提取在线人数、总人数和玩家列表。"""
        players_online = self._to_int(data.get('players_online'))
        players_max = self._to_int(data.get('players_max'))
        player_names: list[str] = []

        players_value = data.get('players')
        if isinstance(players_value, dict):
            if players_online == 0:
                players_online = self._to_int(players_value.get('online') or players_value.get('count') or players_value.get('online_count'))
            if players_max == 0:
                players_max = self._to_int(players_value.get('max') or players_value.get('limit') or players_value.get('max_count'))

            players_list = players_value.get('list') or players_value.get('sample') or players_value.get('names')
            player_names = self._extract_player_names(players_list)
        else:
            player_names = self._extract_player_names(players_value)

        if players_online == 0 and player_names:
            players_online = len(player_names)

        if players_max == 0 and player_names:
            players_max = max(players_online, len(player_names))

        return players_online, players_max, player_names

    def _extract_player_names(self, players_value) -> list[str]:
        """从各种可能的玩家列表结构里提取玩家名。"""
        if not players_value:
            return []

        names: list[str] = []
        if isinstance(players_value, list):
            for player in players_value:
                if isinstance(player, dict):
                    name = player.get('name') or player.get('username') or player.get('nick')
                    if name:
                        names.append(str(name))
                elif isinstance(player, str):
                    names.append(player)
        elif isinstance(players_value, dict):
            for key in ('name', 'username', 'nick'):
                value = players_value.get(key)
                if isinstance(value, str):
                    names.append(value)

        return names

    def _stringify_version(self, value) -> str:
        """把版本信息统一转成字符串，兼容整数和字典。"""
        if value is None:
            return '未知版本'
        if isinstance(value, dict):
            for key in ('name', 'text', 'value', 'version'):
                nested = value.get(key)
                if nested is not None:
                    return str(nested)
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _stringify_text(self, value) -> str:
        """把文本类字段统一转成字符串。"""
        if value is None:
            return '无描述'
        if isinstance(value, dict):
            for key in ('text', 'name', 'value', 'raw'):
                nested = value.get(key)
                if nested is not None:
                    return str(nested)
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, dict):
                    parts.append(str(item.get('text') or item.get('value') or item.get('name') or ''))
                else:
                    parts.append(str(item))
            return ''.join(parts) if parts else '无描述'
        return str(value)

    def _to_int(self, value) -> int:
        """安全转成整数。"""
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
    
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
        name = display_name or "Minecraft服务器"
        
        if status is None:
            return f"❌ {name}\n  状态: 查询失败或服务器离线"
        
        try:
            # 检查是否是成功的响应
            if isinstance(status, dict):
                code = self._to_int(status.get('code', -1))
                if code not in (0, 200):
                    msg = status.get('msg', '未知错误')
                    return f"❌ {name}\n  状态: {msg}"
                
                data = status.get('data', {})
                online = data.get('online', False)
                
                if not online:
                    return f"❌ {name}\n  状态: 服务器离线"
                
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
                
                status_text = f"✅ {name}\n"
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
                return f"❌ {name}\n  状态: 返回数据格式异常"
                
        except Exception as e:
            return f"❌ {name}\n  状态: 解析数据失败 - {str(e)}"
