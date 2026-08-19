# -*- coding: utf-8 -*-
"""vUSTB 二手书问答接口封装。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from config import api_base_url
from services.http_client import HttpClient


class BookService:
    """调用 ``POST /api/book/ask/text``，仅返回接口的 answer 字段。"""

    def __init__(self, client: Optional[HttpClient] = None) -> None:
        self._client = client or HttpClient(base_url=api_base_url())

    async def ask(self, question: str) -> str:
        """提交二手书问题并提取文本回答。"""
        payload: Dict[str, Any] = await self._client.post_json(
            "/api/book/ask/text",
            json={"question": question},
        )
        answer = payload.get("answer") if isinstance(payload, dict) else None
        if isinstance(answer, str) and answer.strip():
            return answer.strip()
        return "🟦 二手书问答服务暂未返回答案。"
