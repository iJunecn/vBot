# -*- coding: utf-8 -*-
"""
GUGUBot HTTP服务器测试脚本
"""
import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gugubot_server import GugubotServer


async def test_server():
    """测试Gugubot服务器"""
    print("=" * 50)
    print("GUGUBot HTTP服务器测试")
    print("=" * 50)
    
    server = GugubotServer(port=8000)
    
    # 设置消息处理器
    async def handle_mc_message(player: str, message: str):
        print(f"\n[收到MC消息] {player}: {message}")
    
    server.set_mc_message_handler(handle_mc_message)
    
    # 启动服务器
    await server.start()
    
    print(f"\n服务器已启动在 http://localhost:8000")
    print("测试接口: http://localhost:8000/health")
    print("\n按 Ctrl+C 停止服务器\n")
    
    try:
        # 保持运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        await server.stop()


if __name__ == "__main__":
    try:
        import aiohttp
    except ImportError:
        print("错误: 缺少 aiohttp 依赖")
        print("请运行: pip install aiohttp")
        sys.exit(1)
    
    asyncio.run(test_server())
