# -*- coding: utf-8 -*-
"""
vBot - QQ机器人主程序
功能：
1. Minecraft服务器在线状态查询
"""
import os
import sys

# 添加父目录到路径，以便导入botpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import botpy
from botpy import logging
from botpy.message import Message, GroupMessage, C2CMessage
from botpy.ext.cog_yaml import read

from minecraft_query import MinecraftServerQuery


def load_dotenv_file(file_path: str) -> None:
    """从 .env 文件加载环境变量。"""
    if not os.path.exists(file_path):
        return

    with open(file_path, encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


# 读取环境变量和配置
project_dir = os.path.dirname(__file__)
load_dotenv_file(os.path.join(project_dir, ".env"))

# 读取配置
config_path = os.path.join(project_dir, "config.yaml")
config = read(config_path)

# 日志
_log = logging.get_logger()


class vBotClient(botpy.Client):
    """vBot主客户端"""
    
    def __init__(self, intents: botpy.Intents, **kwargs):
        super().__init__(intents=intents, **kwargs)
        
        # 初始化Minecraft查询器
        self.mc_query = MinecraftServerQuery()
        
    async def on_ready(self):
        """机器人准备就绪"""
        _log.info(f"🤖 机器人 [{self.robot.name}] 已上线!")
    
    # ==================== 群消息处理 ====================
    
    async def on_group_at_message_create(self, message: GroupMessage):
        """处理群@消息"""
        content = message.content.strip()
        _log.info(f"[vBot] 收到群@消息: {content}")
        
        # 处理命令
        response = await self.process_command(content, message)
        if response:
            mention_name = getattr(getattr(message, "member", None), "nick", None) or ""
            mention_prefix = f"@{mention_name}\n" if mention_name else ""
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"{mention_prefix}{response}"
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
        - /help: 显示帮助信息
        - /server: 查询Minecraft服务器状态
        - /about: 介绍本群
        """
        content_lower = content.lower()
        
        # 帮助命令
        if content_lower == '/help':
            return self.get_help_text()
        
        # 服务器状态查询
        if content_lower == '/server':
            return await self.query_mc_servers()

        # 机器人介绍
        if content_lower == '/about':
            return self.get_about_text()
        
        # 未知命令，返回帮助提示
        if content:  # 如果用户确实发了内容
            return f"未知命令: {content}\n发送 /help 查看可用命令"
        
        return None
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        return """🤖 贝壳使用帮助

【Minecraft服务器查询】
    📌 /server - 查询服务器在线状态

【其他】
    📌 /help - 显示本帮助信息
    📌 /about - 查看本群介绍
"""

    def get_about_text(self) -> str:
        """获取机器人介绍文本"""
        return """你好，我是本群专属群Bot贝壳，欢迎来到 USTB Servers ！
USTB Servers 是北科 Minecraft 交流群，是 Minecraft 高校联盟在北京的核心高校组织，在校内以“元宇宙体素工作坊”形式作为社团部门存在，欢迎大家加入！
更多内容详见群内置顶公告，感谢配合！"""
    
    async def query_mc_servers(self) -> str:
        """查询所有Minecraft服务器状态"""
        servers = config.get('minecraft_servers', [])
        
        if not servers:
            return "❌ 未配置Minecraft服务器"
        
        server_addresses = [s['name'] for s in servers]
        results = await self.mc_query.query_multiple_servers(server_addresses)
        
        lines = ["🎮 Minecraft服务器状态"]
        lines.append("=" * 27)
        
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
    appid = os.getenv('APPID') or config.get('appid')
    secret = os.getenv('SECRET') or config.get('secret')

    if not appid or not secret:
        print("错误: 缺少 APPID 或 SECRET 环境变量")
        print("请先复制 .env.example 为 .env 并填写配置")
        sys.exit(1)

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
        appid=appid,
        secret=secret
    )


if __name__ == "__main__":
    main()
