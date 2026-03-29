# -*- coding: utf-8 -*-
"""
vBot - QQ机器人主程序
功能：
1. Minecraft服务器在线状态查询
2. GUGUBot传声筒服务
"""
import os
import sys
import asyncio
import traceback

# 添加父目录到路径，以便导入botpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import botpy
from botpy import logging, BotAPI
from botpy.message import Message, GroupMessage, C2CMessage
from botpy.ext.cog_yaml import read

from minecraft_query import MinecraftServerQuery
from gugubot_server import GugubotServer

# 读取配置
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = read(config_path)

# 日志
_log = logging.get_logger()

# 全局状态
_target_group_id: str = None  # 用于转发MC消息的QQ群ID


class vBotClient(botpy.Client):
    """vBot主客户端"""
    
    def __init__(self, intents: botpy.Intents, **kwargs):
        super().__init__(intents=intents, **kwargs)
        
        # 初始化Minecraft查询器
        self.mc_query = MinecraftServerQuery(
            base_url=config.get('uapi_base_url', 'https://uapis.cn'),
            token=config.get('uapi_token')
        )
        
        # 初始化Gugubot HTTP服务器
        self.gugubot = GugubotServer(port=config.get('gugubot_port', 8000))
        self.gugubot.set_mc_message_handler(self.handle_mc_message)
        
    async def on_ready(self):
        """机器人准备就绪"""
        _log.info(f"🤖 机器人 [{self.robot.name}] 已上线!")
        _log.info(f"📡 Gugubot HTTP服务器将在端口 {config.get('gugubot_port', 8000)} 启动")
        
        # 启动Gugubot HTTP服务器
        await self.gugubot.start()
    
    async def close(self):
        """关闭机器人"""
        await self.gugubot.stop()
        await super().close()
    
    async def handle_mc_message(self, player: str, message: str):
        """
        处理来自MC服务器的消息，转发到QQ群
        
        Args:
            player: 玩家名
            message: 消息内容
        """
        global _target_group_id
        
        if not _target_group_id:
            _log.warning("[vBot] 未设置目标QQ群，无法转发MC消息")
            return
        
        try:
            formatted_msg = f"💬 [MC] {player}: {message}"
            await self.api.post_group_message(
                group_openid=_target_group_id,
                msg_type=0,
                content=formatted_msg
            )
            _log.info(f"[vBot] MC消息已转发到QQ群: {player}: {message}")
        except Exception as e:
            _log.error(f"[vBot] 转发MC消息失败: {e}")
    
    # ==================== 群消息处理 ====================
    
    async def on_group_at_message_create(self, message: GroupMessage):
        """处理群@消息"""
        content = message.content.strip()
        _log.info(f"[vBot] 收到群@消息: {content}")
        
        # 处理命令
        response = await self.process_command(content, message)
        if response:
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=response
            )
    
    async def on_group_message_create(self, message: GroupMessage):
        """处理普通群消息（非@）"""
        # 可以在这里处理普通群消息
        pass
    
    # ==================== 频道消息处理 ====================
    
    async def on_at_message_create(self, message: Message):
        """处理频道@消息"""
        content = message.content.strip()
        _log.info(f"[vBot] 收到频道@消息: {content}")
        
        response = await self.process_command(content, message)
        if response:
            await message.reply(content=response)
    
    # ==================== 私聊消息处理 ====================
    
    async def on_c2c_message_create(self, message: C2CMessage):
        """处理私聊消息"""
        content = message.content.strip()
        _log.info(f"[vBot] 收到私聊消息: {content}")
        
        response = await self.process_command(content, message)
        if response:
            await message._api.post_c2c_message(
                openid=message.author.user_openid,
                msg_type=0,
                msg_id=message.id,
                content=response
            )
    
    # ==================== 命令处理 ====================
    
    async def process_command(self, content: str, message) -> str:
        """
        处理用户命令
        
        支持的命令:
        - 帮助/help: 显示帮助信息
        - 状态/status: 查询Minecraft服务器状态
        - 绑定/bind: 绑定当前群为MC消息转发目标
        """
        global _target_group_id
        
        content_lower = content.lower()
        
        # 帮助命令
        if content_lower in ['帮助', 'help', '菜单', 'menu']:
            return self.get_help_text()
        
        # 服务器状态查询
        if content_lower in ['状态', 'status', '服务器状态', 'mc', 'minecraft']:
            return await self.query_mc_servers()
        
        # 绑定群为MC消息转发目标
        if content_lower in ['绑定', 'bind']:
            if hasattr(message, 'group_openid'):
                _target_group_id = message.group_openid
                return f"✅ 已将本群绑定为MC消息转发目标\n当前绑定群ID: {_target_group_id}"
            else:
                return "❌ 该命令只能在QQ群中使用"
        
        # 解绑
        if content_lower in ['解绑', 'unbind']:
            if _target_group_id:
                old_id = _target_group_id
                _target_group_id = None
                return f"✅ 已解绑MC消息转发\n原绑定群ID: {old_id}"
            else:
                return "ℹ️ 当前没有绑定任何群"
        
        # 检查转发状态
        if content_lower in ['转发状态', 'forward status']:
            if _target_group_id:
                return f"✅ MC消息转发已启用\n目标群ID: {_target_group_id}"
            else:
                return "ℹ️ MC消息转发未启用，请在目标群发送「绑定」开启"
        
        # 未知命令，返回帮助提示
        if content:  # 如果用户确实发了内容
            return f"未知命令: {content}\n发送「帮助」查看可用命令"
        
        return None
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        return """🤖 vBot 使用帮助

【Minecraft服务器查询】
📌 状态/status - 查询服务器在线状态

【传声筒功能】
📌 绑定/bind - 将当前群设为MC消息转发目标
📌 解绑/unbind - 取消MC消息转发
📌 转发状态 - 查看当前转发状态

【其他】
📌 帮助/help - 显示本帮助信息

服务器列表:
• mc.ustb.world - USTB主服务器
• mod.ustb.world - USTB模组服务器"""
    
    async def query_mc_servers(self) -> str:
        """查询所有Minecraft服务器状态"""
        servers = config.get('minecraft_servers', [])
        
        if not servers:
            return "❌ 未配置Minecraft服务器"
        
        server_addresses = [s['name'] for s in servers]
        results = await self.mc_query.query_multiple_servers(server_addresses)
        
        lines = ["🎮 Minecraft服务器状态"]
        lines.append("=" * 30)
        
        for server_config in servers:
            addr = server_config['name']
            display = server_config.get('display_name', addr)
            status = results.get(addr)
            formatted = self.mc_query.format_server_status(addr, status, display)
            lines.append(formatted)
            lines.append("")  # 空行分隔
        
        return "\n".join(lines)


def main():
    """主函数"""
    # 设置意图
    intents = botpy.Intents(
        public_messages=True,      # 群消息
        public_guild_messages=True, # 频道消息
        direct_message=True         # 私信
    )
    
    # 创建客户端
    client = vBotClient(intents=intents)
    
    # 运行机器人 (run是阻塞方法，内部处理了事件循环)
    client.run(
        appid=config['appid'],
        secret=config['secret']
    )


if __name__ == "__main__":
    # 检查依赖
    try:
        import uapi
    except ImportError:
        print("错误: 缺少 uapi-sdk-python 依赖")
        print("请运行: pip install uapi-sdk-python")
        sys.exit(1)
    
    try:
        import aiohttp
    except ImportError:
        print("错误: 缺少 aiohttp 依赖")
        print("请运行: pip install aiohttp")
        sys.exit(1)
    
    # Windows上的事件循环策略设置
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n[vBot] 收到退出信号，正在关闭...")
    except Exception as e:
        print(f"[vBot] 发生错误: {e}")
        traceback.print_exc()
