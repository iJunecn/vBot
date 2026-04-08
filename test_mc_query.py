# -*- coding: utf-8 -*-
"""
Minecraft服务器查询测试脚本
"""
import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from minecraft_query import MinecraftServerQuery
from botpy.ext.cog_yaml import read


async def test_query():
    """测试Minecraft服务器查询"""
    print("=" * 50)
    print("Minecraft服务器查询测试")
    print("=" * 50)
    
    # 读取配置
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    config = read(config_path)
    
    # 创建查询器
    query = MinecraftServerQuery()
    
    # 测试单个服务器查询
    servers = config.get('minecraft_servers', [])
    
    if not servers:
        print("错误: 未配置Minecraft服务器")
        return
    
    print(f"\n开始查询 {len(servers)} 个服务器...\n")
    
    for server_config in servers:
        addr = server_config['name']
        display = server_config.get('display_name', addr)
        
        print(f"查询中: {display} ({addr})...")
        result = await query.query_server(addr)
        
        if result:
            print(f"原始响应: {result}")
            print()
            formatted = query.format_server_status(addr, result, display)
            print(formatted)
        else:
            print(f"❌ 查询失败: {addr}\n")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_query())
