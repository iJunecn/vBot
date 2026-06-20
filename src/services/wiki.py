# -*- coding: utf-8 -*-
"""MCSearch Wiki 词条摘要接口封装。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from config import mcsearch_base_url
from services.http_client import HttpClient


class WikiService:
    """调用 MCSearch (`https://search.tecostudio.cn`) 的 Wiki 摘要接口。"""

    def __init__(self, client: Optional[HttpClient] = None) -> None:
        self._client = client or HttpClient(base_url=mcsearch_base_url())

    async def get_page(self, title: str) -> Optional[Dict[str, Any]]:
        """获取指定词条的摘要。

        ``GET /api/v1/wiki/page?title=<title>``。

        词条不存在时服务端返回 ``null``，按约定返回 ``None``。
        """
        params = {"title": title}
        data = await self._client.get_json("/api/v1/wiki/page", params=params)
        if data is None:
            return None
        return data

    @staticmethod
    def format_for_chat(title: str, page: Optional[Dict[str, Any]]) -> str:
        """把词条摘要格式化成可读文本。"""
        if not page:
            return f"📚 找不到 Wiki 词条「{title}」"

        real_title = page.get("title") or title
        extract = (page.get("extract") or "").strip()
        url = page.get("url") or ""

        text = f"📚 Wiki · {real_title}\n{extract}"
        if url:
            text += f"\n🔗 {url}"
        return text
