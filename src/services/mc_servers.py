# -*- coding: utf-8 -*-
"""vUSTB 公开 Minecraft 服务器 API 封装。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import api_base_url
from services.http_client import HttpClient


# 状态展示文案
_STATUS_DISPLAY = {
    "online": ("🟩 在线", "ON"),
    "offline": ("🟥 离线", "OFF"),
}


class MinecraftServerService:
    """调用 vUSTB 公开 MC 服务器接口。"""

    def __init__(self, client: Optional[HttpClient] = None) -> None:
        self._client = client or HttpClient(base_url=api_base_url())

    async def list_with_status(self) -> List[Dict[str, Any]]:
        """获取服务器列表及实时状态（`GET /api/mc-servers/statuses`）。"""
        return await self._client.get_json("/api/mc-servers/statuses")

    @staticmethod
    def format_for_chat(server: Dict[str, Any]) -> str:
        """把单条服务器状态格式化成可读文本。"""
        name = server.get("name") or "未知服务器"
        address = server.get("address") or "地址未公开"
        description = (server.get("description") or "").strip() or "（暂无介绍）"
        version_hint = server.get("version_hint") or server.get("version") or "未知版本"
        theme = server.get("theme") or ""

        raw_status = (server.get("server_status") or "").lower()
        status_label, _ = _STATUS_DISPLAY.get(raw_status, ("⬜ 未知", "?"))

        online = server.get("players_online")
        max_online = server.get("players_max")
        if isinstance(online, int) and isinstance(max_online, int):
            player_text = f"在线 {online}/{max_online}"
        else:
            player_text = "在线人数未知"

        lines = [
            f"{status_label} {name}",
            f"  IP: {address}",
            f"  版本: {version_hint}",
        ]
        if theme:
            lines.append(f"  主题: {theme}")
        lines.append(f"  {player_text}")
        lines.append(f"  介绍: {description}")
        return "\n".join(lines)

    @classmethod
    def format_list(cls, servers: List[Dict[str, Any]]) -> str:
        """格式化整张服务器列表。"""
        if not servers:
            return "暂无公开的 Minecraft 服务器"

        header = ["🟦 Minecraft 服务器列表", "=" * 27]
        body = [cls.format_for_chat(s) for s in servers]
        return "\n\n".join(header + body)
