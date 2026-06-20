# -*- coding: utf-8 -*-
"""简单的 .env 文件加载器，避免引入额外依赖。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Union


def load_dotenv_file(file_path: Union[str, "os.PathLike[str]"]) -> None:
    """从 .env 文件加载环境变量（若尚未设置）。

    注释行以 ``#`` 开头，格式为 ``KEY=VALUE``，引号会被自动剥离。
    已存在的环境变量不会被覆盖。
    """
    path = Path(file_path)
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
