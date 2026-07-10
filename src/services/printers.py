# -*- coding: utf-8 -*-
"""vUSTB 3D 打印机状态 API 封装。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import api_base_url
from services.http_client import HttpClient


# status_class -> 视觉图标
_STATUS_ICON = {
    "running": "🟩",
    "reserved": "🟨",
    "idle": "⬜",
    "paused": "🟥",
}


class PrinterService:
    """调用 vUSTB 公开打印机状态接口。"""

    def __init__(self, client: Optional[HttpClient] = None) -> None:
        self._client = client or HttpClient(base_url=api_base_url())

    async def list_with_status(self) -> List[Dict[str, Any]]:
        """获取全部打印机的实时状态（`GET /api/print/printers/statuses`）。"""
        return await self._client.get_json("/api/print/printers/statuses")

    @staticmethod
    def _humanize(printer: Dict[str, Any]) -> str:
        icon = _STATUS_ICON.get(printer.get("status_class", ""), "⬜")
        name = printer.get("name") or "未知打印机"
        location = printer.get("location") or "位置未知"
        model = printer.get("model") or "型号未知"
        status = printer.get("status") or "未知"
        booking_id = printer.get("current_booking_id")
        suffix = f"  (预约 #{booking_id})" if booking_id else ""
        return f"{icon} {name} · {status}{suffix}\n   位置：{location} · 型号：{model}"

    @classmethod
    def format_list(cls, printers: List[Dict[str, Any]]) -> str:
        """格式化整张打印机状态表。"""
        if not printers:
            return "暂无打印机信息"

        # 简单汇总
        counts = {"running": 0, "reserved": 0, "idle": 0, "paused": 0}
        for p in printers:
            cls_key = p.get("status_class")
            if cls_key in counts:
                counts[cls_key] += 1

        header = (
            "🟦 3D 打印机状态\n"
            + "=" * 27
            + "\n"
            + f"运行中 {counts['running']} · 已预约 {counts['reserved']} · "
            f"空闲 {counts['idle']} · 暂停 {counts['paused']}"
        )
        body = [cls._humanize(p) for p in printers]
        return "\n\n".join([header, *body])
