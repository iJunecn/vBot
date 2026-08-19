# -*- coding: utf-8 -*-
"""vBot QQ 机器人客户端：接收消息并路由命令。"""
from __future__ import annotations

import shlex
from typing import Awaitable, Callable, Optional

import botpy
from botpy import logging
from botpy.message import C2CMessage, GroupMessage, Message

from services.ask import AskService
from services.mod_search import ModSearchService
from services.mc_servers import MinecraftServerService
from services.printers import PrinterService
from services.wiki import WikiService


_log = logging.get_logger()


# 命令处理函数签名：async def handler(args: str) -> str
CommandHandler = Callable[[str], Awaitable[str]]


HELP_TEXT = """🟦 贝壳使用帮助

【Minecraft 服务器】
    🟦 /server - 查看 vUSTB 公开服务器列表（含 IP、版本、介绍、在线人数）
    🟦 /printers - 查看 3D 打印机实时状态

【Minecraft 资料查询】
    🟦 /wiki <词条> - 查询中文 Minecraft Wiki 词条摘要
    🟦 /mod <关键词> - 聚合搜索 Mod（Modrinth / BBSMC / CurseForge 等）
    🟦 /ask <问题> - 向像素北科知识库提问

【其他】
    🟦 /help - 显示本帮助信息
    🟦 /about - 查看机器人介绍
"""


ABOUT_TEXT = """你好，我是本群专属群 Bot 贝壳，欢迎来到 USTB Servers！
USTB Servers 是北科 Minecraft 交流群，是 Minecraft 高校联盟在北京的核心高校组织，
在校内以「元宇宙体素工作坊」形式作为社团部门存在，欢迎大家加入！
更多内容详见群内置顶公告，感谢配合！"""


class VBotClient(botpy.Client):
    """vBot 主客户端。"""

    def __init__(self, intents: botpy.Intents, **kwargs) -> None:
        super().__init__(intents=intents, **kwargs)

        self.mc_servers = MinecraftServerService()
        self.printers = PrinterService()
        self.wiki = WikiService()
        self.mod_search = ModSearchService()
        self.ask_service = AskService()

    async def on_ready(self) -> None:
        _log.info(f"🤖 机器人 [{self.robot.name}] 已上线!")

    # ---- 群 / 频道 / 私聊入口 -------------------------------------------

    async def on_group_at_message_create(self, message: GroupMessage) -> None:
        content = message.content.strip()
        _log.info(f"[vBot] 收到群@消息: {content}")
        response = await self._dispatch(content)
        if not response:
            return
        mention_name = getattr(getattr(message, "member", None), "nick", None) or ""
        mention_prefix = f"@{mention_name}\n" if mention_name else ""
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=f"{mention_prefix}{response}",
        )

    async def on_at_message_create(self, message: Message) -> None:
        content = message.content.strip()
        _log.info(f"[vBot] 收到频道@消息: {content}")
        response = await self._dispatch(content)
        if response:
            await message.reply(content=response)

    async def on_c2c_message_create(self, message: C2CMessage) -> None:
        content = message.content.strip()
        _log.info(f"[vBot] 收到私聊消息: {content}")
        response = await self._dispatch(content)
        if response:
            await message._api.post_c2c_message(
                openid=message.author.user_openid,
                msg_type=0,
                msg_id=message.id,
                content=response,
            )

    # ---- 命令路由 -------------------------------------------------------

    async def _dispatch(self, content: str) -> Optional[str]:
        """解析并执行命令，返回响应文本或 None。"""
        if not content:
            return None

        try:
            tokens = shlex.split(content)
        except ValueError:
            tokens = content.split()

        if not tokens:
            return None
        command = tokens[0].lower()
        # 把剩余部分用单空格拼接，方便下游按空格分词
        rest = " ".join(tokens[1:]).strip()

        try:
            if command in ("/help", "/?"):
                return HELP_TEXT
            if command == "/about":
                return ABOUT_TEXT
            if command in ("/server", "/status", "/servers"):
                return await self._cmd_server()
            if command in ("/printers", "/printer"):
                return await self._cmd_printers()
            if command == "/wiki":
                return await self._cmd_wiki(rest)
            if command == "/mod":
                return await self._cmd_mod(rest)
            if command == "/ask":
                return await self._cmd_ask(rest)
        except Exception as exc:  # 兜底，避免单条命令的异常让客户端崩溃
            _log.exception(f"[vBot] 命令 {command} 执行失败: {exc}")
            return f"🟥 命令执行出错：{exc}"

        return f"未知命令: {command}\n发送 /help 查看可用命令"

    # ---- 命令实现 -------------------------------------------------------

    async def _cmd_server(self) -> str:
        servers = await self.mc_servers.list_with_status()
        return self.mc_servers.format_list(servers)

    async def _cmd_printers(self) -> str:
        printers = await self.printers.list_with_status()
        return self.printers.format_list(printers)

    async def _cmd_wiki(self, query: str) -> str:
        if not query:
            return "用法：/wiki <词条>\n例如：/wiki 红石"
        page = await self.wiki.get_page(query)
        return self.wiki.format_for_chat(query, page)

    async def _cmd_mod(self, query: str) -> str:
        if not query:
            return "用法：/mod <关键词>\n例如：/mod 工业时代"
        payload = await self.mod_search.search(query)
        return self.mod_search.format_for_chat(query, payload)

    async def _cmd_ask(self, question: str) -> str:
        if not question:
            return "用法：/ask <问题>\n例如：/ask 像素北科跟服务器有什么关系？"
        return await self.ask_service.ask(question)
