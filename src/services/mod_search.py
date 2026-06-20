# -*- coding: utf-8 -*-
"""MCSearch Mod 聚合搜索接口封装。"""
from __future__ import annotations

from typing import Any, Dict, List

from config import mcsearch_base_url
from services.http_client import HttpClient


class ModSearchService:
    """调用 MCSearch (`https://search.tecostudio.cn`) 的 Mod 聚合搜索。"""

    def __init__(self, client: Optional[HttpClient] = None) -> None:
        self._client = client or HttpClient(base_url=mcsearch_base_url())

    async def search(
        self,
        query: str,
        *,
        source: str = "all",
        page: int = 1,
    ) -> Dict[str, Any]:
        """搜索 Mod。

        ``GET /api/v1/mod/search?q=<query>&source=<source>&page=<page>``
        """
        params = {"q": query, "source": source, "page": page}
        return await self._client.get_json("/api/v1/mod/search", params=params)

    @staticmethod
    def _format_item(item: Dict[str, Any], index: int) -> str:
        name = item.get("name") or "（无标题）"
        source_name = item.get("sourceName") or item.get("source") or "?"
        description = (item.get("description") or "").strip()
        url = item.get("url") or ""
        downloads = item.get("downloads")
        author = item.get("author")

        head = f"{index}. {name}  [{source_name}]"
        body: List[str] = []
        if description:
            # 截断过长的描述，避免单条消息超长
            body.append(f"   {description[:160]}{'…' if len(description) > 160 else ''}")
        meta_bits: List[str] = []
        if author:
            meta_bits.append(f"作者 {author}")
        if isinstance(downloads, int):
            meta_bits.append(f"下载 {downloads:,}")
        if meta_bits:
            body.append("   " + " · ".join(meta_bits))
        if url:
            body.append(f"   🔗 {url}")
        return "\n".join([head, *body])

    @classmethod
    def format_for_chat(
        cls,
        query: str,
        payload: Dict[str, Any],
        *,
        limit: int = 5,
    ) -> str:
        """把搜索结果格式化成可读文本（默认取前 5 条）。"""
        results: List[Dict[str, Any]] = (payload or {}).get("results") or []
        if not results:
            return f"🔍 没有找到与「{query}」相关的 Mod"

        source = (payload or {}).get("source") or "all"
        header = (
            f"🔍 Mod 搜索 · {query}  (source={source}, "
            f"命中 {len(results)} 条，显示前 {min(limit, len(results))} 条)"
        )
        body = [cls._format_item(item, idx) for idx, item in enumerate(results[:limit], start=1)]
        return "\n\n".join([header, *body])
