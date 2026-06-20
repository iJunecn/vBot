# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
from typing import Final

# 与上面 docstring 中的生成脚本保持一致；只用于简单的 XOR 混淆，不是真正的密钥。
_OBFUSCATION_KEY: Final[bytes] = b"vBot-ustb-key-2026"

# base64( XOR(plaintext_utf8, _OBFUSCATION_KEY 循环) )
APPID_ENC: Final[str] = "R3JdTB1MRkVW"
SECRET_ENC: Final[str] = "ICcBQn0fQDsIGDkKMl9iSGUDEAQeJh4TOgI4aRg9PVk="
TOKEN_ENC: Final[str] = "JXQOBR0ECRsYfR8vIUp6aXwBGxI3FhkvNkwBRyYBEk8="


def _decode(encoded: str) -> str:
    """把 ``base64(XOR(plaintext))`` 还原成原始字符串。"""
    raw = base64.b64decode(encoded.encode("ascii"))
    key = _OBFUSCATION_KEY
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(raw)).decode("utf-8")


def get_appid() -> str:
    """返回机器人 APPID。"""
    return _decode(APPID_ENC)


def get_secret() -> str:
    """返回机器人 SECRET。"""
    return _decode(SECRET_ENC)


def get_token() -> str:
    """返回机器人 Token（若 botpy 在你的场景下不需要可忽略）。"""
    return _decode(TOKEN_ENC)


__all__ = ["get_appid", "get_secret", "get_token"]
