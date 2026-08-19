# -*- coding: utf-8 -*-
"""异步 HTTP 客户端封装，复用一个全局 httpx.AsyncClient。"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx


_DEFAULT_TIMEOUT = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)
_DEFAULT_HEADERS = {
    "User-Agent": "vBot/2.0 (+https://github.com/LYOfficial/vBot)",
    "Accept": "application/json",
}


class HttpClient:
    """带简单重试的异步 HTTP 客户端封装。"""

    def __init__(
        self,
        base_url: str = "",
        timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
        max_retries: int = 2,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=_DEFAULT_HEADERS,
            follow_redirects=True,
        )
        self._max_retries = max_retries

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_json(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """发起 GET 请求并解析 JSON，失败抛出 httpx.HTTPError。"""
        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.get(path, params=params)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    # 指数退避：0.5s, 1s
                    await asyncio.sleep(0.5 * (attempt + 1))
        # 三次都失败，抛出最后一次的异常
        assert last_exc is not None
        raise last_exc

    async def post_json(
        self,
        path: str,
        json: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """发起 POST 请求并解析 JSON，失败时按 GET 相同策略重试。"""
        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.post(path, json=json, headers=headers)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
        assert last_exc is not None
        raise last_exc
