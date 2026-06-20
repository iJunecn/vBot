# -*- coding: utf-8 -*-
"""vBot 入口文件。"""
from __future__ import annotations

import sys

import botpy

from client import VBotClient
from config import get_appid, get_secret, load_env


def main() -> None:
    # 仅用于加载 USTB_API_BASE / MCSEARCH_BASE 等可调环境变量；
    # 机器人凭据来自 src/secrets.py，不再依赖 .env。
    load_env()

    appid = get_appid()
    secret = get_secret()
    if not appid or not secret:
        print("错误: 无法获取 APPID 或 SECRET", file=sys.stderr)
        print("请检查 src/secrets.py 中的混淆常量是否完整", file=sys.stderr)
        sys.exit(1)

    intents = botpy.Intents(
        public_messages=True,
        public_guild_messages=True,
        direct_message=True,
    )

    client = VBotClient(intents=intents)
    # botpy 的 run 是阻塞调用，内部负责事件循环与资源回收
    client.run(appid=appid, secret=secret)


if __name__ == "__main__":
    main()
