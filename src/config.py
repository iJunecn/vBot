# -*- coding: utf-8 -*-
"""配置加载：.env 提供密钥，config.yaml 提供静态配置。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from env_loader import load_dotenv_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """从项目根目录读取 .env 文件（若存在）。"""
    load_dotenv_file(PROJECT_ROOT / ".env")


def load_yaml_config() -> Dict[str, Any]:
    """读取项目根目录的 config.yaml。"""
    config_path = PROJECT_ROOT / "config.yaml"
    if not config_path.is_file():
        return {}
    with config_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def get_appid() -> Optional[str]:
    """从环境变量读取机器人 APPID。"""
    return os.getenv("APPID")


def get_secret() -> Optional[str]:
    """从环境变量读取机器人 Secret。"""
    return os.getenv("SECRET")


def api_base_url() -> str:
    """vUSTB 公开 API 的 Base URL，可通过环境变量覆盖。"""
    return os.getenv("USTB_API_BASE", "https://www.ustb.world").rstrip("/")


def mcsearch_base_url() -> str:
    """MCSearch (tecostudio) 的 Base URL，可通过环境变量覆盖。"""
    return os.getenv("MCSEARCH_BASE", "https://search.tecostudio.cn").rstrip("/")
