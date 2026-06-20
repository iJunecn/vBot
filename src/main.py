# -*- coding: utf-8 -*-
"""vBot 入口文件。"""
from __future__ import annotations

import sys

import botpy

from client import VBotClient
from config import get_appid, get_secret, load_env


def main() -> None:
    # 先加载 .env，再读取 APPID/SECRET
    load_env()

    appid = get_appid()
    secret = get_secret()
    if not appid or not secret:
        print("错误: 缺少 APPID 或 SECRET 环境变量", file=sys.stderr)
        print("请先复制 .env.example 为 .env 并填写配置", file=sys.stderr)
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
