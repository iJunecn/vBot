# -*- coding: utf-8 -*-
"""配置加载：机器人凭据从 ``secrets`` 模块读取，外部 API Base 可由环境变量覆盖。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

import secrets as _secrets
from env_loader import load_dotenv_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """兼容旧用法：仍允许从 ``.env`` 覆盖默认值，但不强制要求该文件存在。

    凭据的权威来源是 ``src/secrets.py``，这里的 ``.env`` 加载仅用于覆盖
    ``USTB_API_BASE`` / ``MCSEARCH_BASE`` 等可调参数。
    """
    load_dotenv_file(PROJECT_ROOT / ".env")


def load_yaml_config() -> Dict[str, Any]:
    """读取项目根目录的 config.yaml。"""
    config_path = PROJECT_ROOT / "config.yaml"
    if not config_path.is_file():
        return {}
    with config_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def get_appid() -> str:
    """机器人 APPID：从混淆常量解码得到。"""
    return _secrets.get_appid()


def get_secret() -> str:
    """机器人 SECRET：从混淆常量解码得到。"""
    return _secrets.get_secret()


def get_token() -> Optional[str]:
    """机器人 Token（如 botpy 在你的场景下需要可由 ``secrets`` 提供）。"""
    try:
        return _secrets.get_token()
    except Exception:
        return None


def api_base_url() -> str:
    """vUSTB 公开 API 的 Base URL，可通过环境变量覆盖。"""
    return os.getenv("USTB_API_BASE", "https://www.ustb.world").rstrip("/")


def mcsearch_base_url() -> str:
    """MCSearch (tecostudio) 的 Base URL，可通过环境变量覆盖。"""
    return os.getenv("MCSEARCH_BASE", "https://search.tecostudio.cn").rstrip("/")
