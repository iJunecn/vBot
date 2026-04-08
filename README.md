# vBot - QQ机器人

基于腾讯官方 botpy SDK 开发的QQ机器人，支持Minecraft服务器状态查询。

## 功能介绍

### Minecraft服务器状态查询
- 支持查询多个Minecraft服务器的在线状态
- 显示服务器版本、在线人数、在线玩家列表等信息

## 配置说明

复制 `.env.example` 为 `.env` 并填写你的机器人配置，然后编辑 `config.yaml` 文件：

```bash
copy .env.example .env
```

`.env` 示例：

```env
APPID=你的QQ机器人APPID
SECRET=你的QQ机器人Secret
TOKEN=你的QQ机器人Token
```

`config.yaml` 只保留 Minecraft 服务器列表：

```yaml
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
| /help | 显示帮助信息 |
| /server | 查询Minecraft服务器状态 |
| /about | 查看机器人介绍 |

## 目录结构

```
vBot/
├── bot.py              # 主程序
├── minecraft_query.py  # Minecraft服务器查询模块
├── .env.example        # 环境变量示例
├── config.yaml         # 配置文件
├── requirements.txt    # 依赖列表
└── README.md          # 本文档
```

## 注意事项

1. 首次运行前请确保已安装所有依赖
2. 机器人需要能够访问外网（连接QQ Bot API）
3. 如果不需要 Minecraft 状态查询，可以从 `config.yaml` 中移除 `minecraft_servers`
