# vBot - QQ机器人

基于腾讯官方 botpy SDK 开发的QQ机器人，支持Minecraft服务器状态查询和GUGUBot传声筒功能。

## 功能介绍

### 1. Minecraft服务器状态查询
- 支持查询多个Minecraft服务器的在线状态
- 显示服务器版本、在线人数、在线玩家列表等信息

### 2. GUGUBot传声筒
- 作为GUGUBot的服务端，监听8000端口
- 接收MC服务器的消息并转发到QQ群
- 支持QQ群消息转发到MC服务器

## 配置说明

编辑 `config.yaml` 文件：

```yaml
# QQ机器人配置（已预填）
appid: "102809514"
secret: "Ven6Pj3Oj5RoKrPxW5fFqR3fIvZDsXDt"
token: "S6aq0qzozPtJXgHYN7mPXb4ZE8cjMdkb"

# UAPI配置（已预填）
uapi_token: "uapi-kbxpfcmkWEn91QEYN2Y-CYlNB70AiDLyIq0ie1FD"
uapi_base_url: "https://uapis.cn"

# GUGUBot配置
gugubot_port: 8000

# Minecraft服务器列表
minecraft_servers:
  - name: "mc.ustb.world"
    display_name: "USTB主服务器"
  - name: "mod.ustb.world"
    display_name: "USTB模组服务器"
```

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行机器人

```bash
python bot.py
```

### 机器人命令

在QQ群或频道中@机器人发送以下命令：

| 命令 | 说明 |
|------|------|
| 帮助 / help | 显示帮助信息 |
| 状态 / status | 查询Minecraft服务器状态 |
| 绑定 / bind | 将当前群设为MC消息转发目标 |
| 解绑 / unbind | 取消MC消息转发 |
| 转发状态 | 查看当前转发状态 |

## GUGUBot配置

在MC服务器的GUGUBot配置中，设置QQ机器人地址为：

```
http://<你的服务器IP>:8000/message
```

例如：
```
http://192.168.1.100:8000/message
```

确保防火墙允许8000端口的访问。

## 目录结构

```
vBot/
├── bot.py              # 主程序
├── minecraft_query.py  # Minecraft服务器查询模块
├── gugubot_server.py   # GUGUBot HTTP服务器
├── config.yaml         # 配置文件
├── requirements.txt    # 依赖列表
└── README.md          # 本文档
```

## 注意事项

1. 首次运行前请确保已安装所有依赖
2. 机器人需要能够访问外网（连接QQ Bot API）
3. GUGUBot的HTTP服务器默认监听0.0.0.0:8000，确保端口未被占用
4. 如果需要修改端口，请编辑 `config.yaml` 中的 `gugubot_port`
