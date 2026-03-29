# -*- coding: utf-8 -*-
"""
GUGUBot 传声筒HTTP服务器模块
为MC服务器的GUGUBot插件提供消息转发服务
"""
import asyncio
import json
from typing import Callable, Optional
from aiohttp import web


class GugubotServer:
    """
    GUGUBot传声筒服务器
    监听指定端口，接收来自MC服务器的消息并转发到QQ
    """
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        # 消息回调函数
        self.on_mc_message: Optional[Callable[[str, str], asyncio.Coroutine]] = None
        self.on_qq_message: Optional[Callable[[str], asyncio.Coroutine]] = None
        
        # 设置路由
        self.app.router.add_post('/message', self.handle_message)
        self.app.router.add_get('/health', self.handle_health)
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """健康检查接口"""
        return web.json_response({
            "status": "ok",
            "service": "vBot-gugubot",
            "port": self.port
        })
    
    async def handle_message(self, request: web.Request) -> web.Response:
        """
        处理来自MC服务器的消息
        
        GUGUBot会发送POST请求到这个端点，包含以下字段:
        - type: 消息类型 ('mc_to_qq' 或 'qq_to_mc')
        - player: 玩家名 (mc_to_qq时)
        - message: 消息内容
        - sender: 发送者 (qq_to_mc时)
        """
        try:
            data = await request.json()
            msg_type = data.get('type', '')
            
            if msg_type == 'mc_to_qq':
                # MC消息转发到QQ
                player = data.get('player', '未知玩家')
                message = data.get('message', '')
                
                if self.on_mc_message:
                    await self.on_mc_message(player, message)
                
                return web.json_response({
                    "code": 0,
                    "msg": "success",
                    "data": None
                })
            
            elif msg_type == 'qq_to_mc':
                # QQ消息转发到MC (通过HTTP响应返回)
                sender = data.get('sender', '未知用户')
                message = data.get('message', '')
                
                # 这里可以添加对QQ消息的处理逻辑
                return web.json_response({
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "broadcast": True,
                        "message": f"[QQ] {sender}: {message}"
                    }
                })
            
            else:
                return web.json_response({
                    "code": 400,
                    "msg": f"unknown type: {msg_type}",
                    "data": None
                }, status=400)
                
        except json.JSONDecodeError:
            return web.json_response({
                "code": 400,
                "msg": "invalid json",
                "data": None
            }, status=400)
        except Exception as e:
            return web.json_response({
                "code": 500,
                "msg": str(e),
                "data": None
            }, status=500)
    
    async def start(self):
        """启动HTTP服务器"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await self.site.start()
        print(f"[GugubotServer] HTTP服务器已启动，端口: {self.port}")
    
    async def stop(self):
        """停止HTTP服务器"""
        if self.runner:
            await self.runner.cleanup()
            print("[GugubotServer] HTTP服务器已停止")
    
    def set_mc_message_handler(self, handler: Callable[[str, str], asyncio.Coroutine]):
        """设置MC消息处理器"""
        self.on_mc_message = handler
    
    def set_qq_message_handler(self, handler: Callable[[str], asyncio.Coroutine]):
        """设置QQ消息处理器"""
        self.on_qq_message = handler
