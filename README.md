# vBot - QQ 机器人

基于腾讯官方 [botpy](https://github.com/tencent-connect/botpy) SDK 的 QQ 机器人，为 **vUSTB（像素北科）** 群聊提供 Minecraft 服务器 / 3D 打印机状态查询，以及 Minecraft Wiki 与 Mod 聚合搜索。

## 功能一览

| 命令 | 数据来源 | 说明 |
| --- | --- | --- |
| `/server`（含别名 `/status`、`/servers`） | `GET https://www.ustb.world/api/mc-servers/statuses` | 列出全部公开 MC 服务器的实时状态：在线/离线、IP、版本、主题、在线人数、服务器介绍 |
| `/printers`（含别名 `/printer`） | `GET https://www.ustb.world/api/print/printers/statuses` | 查看 3D 打印机实时状态，含名称、位置、型号、运行/已预约/空闲/暂停 |
| `/wiki <词条>` | `GET https://search.tecostudio.cn/api/v1/wiki/page` | 拉取中文 Minecraft Wiki 词条摘要（≤300 字）+ 原文链接 |
| `/mod <关键词>` | `GET https://search.tecostudio.cn/api/v1/mod/search` | 聚合搜索 Modrinth / BBSMC / CurseForge 等来源的 Mod |
| `/help` / `/about` | — | 内置帮助与机器人自我介绍 |

## 项目结构

```
vBot/
├── src/                  # 全部 Python 源码
│   ├── __init__.py
│   ├── main.py           # 入口（python -m src.main）
│   ├── client.py         # VBotClient，路由群/频道/私聊消息
│   ├── config.py         # .env + config.yaml 加载
│   ├── env_loader.py     # 零依赖的 .env 解析
│   └── services/
│       ├── http_client.py     # 复用 httpx.AsyncClient + 重试
│       ├── mc_servers.py      # vUSTB MC 服务器 API
│       ├── printers.py        # vUSTB 打印机 API
│       ├── wiki.py            # MCSearch Wiki 词条 API
│       └── mod_search.py      # MCSearch Mod 搜索 API
├── config.yaml           # 静态配置（当前为空，预留扩展位）
├── .env.example          # 环境变量示例
├── Dockerfile            # vBot 镜像构建
├── docker-compose.yml    # 一键启动
├── start.bat             # Windows 一键启动
├── requirements.txt      # Python 依赖
├── LICENSE
└── README.md
```

## 配置说明

1. 复制 `.env.example` 为 `.env`，填入机器人凭据：

   ```bash
   cp .env.example .env   # Windows: copy .env.example .env
   ```

   ```env
   APPID=你的QQ机器人APPID
   SECRET=你的QQ机器人Secret
   ```

2. （可选）通过环境变量覆盖 API 地址：

   ```env
   USTB_API_BASE=https://www.ustb.world
   MCSEARCH_BASE=https://search.tecostudio.cn
   ```

## 运行方式

### 方式一：本地直接运行

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m main
```

Windows 用户可直接双击 `start.bat`。

### 方式二：Docker Compose

```bash
cp .env.example .env  # 填好 APPID / SECRET
docker compose up -d --build
docker compose logs -f vbot
```

## 注意事项

- 机器人需要**出网**访问 QQ 官方 API 以及 `ustb.world` / `search.tecostudio.cn`。
- vUSTB 与 MCSearch 接口均为公开接口，但请遵守各自的服务条款和限流（参见上游响应头 `X-RateLimit-*`）。
- 单条 QQ 文本消息上限约 4500 字；若返回过长会被服务端拒绝，后续可按需改为分段/消息合并转发。
- 旧版的 MineBBS 第三方 ping、`/api/mc-servers` 直连方案与 `botpy.log` 已移除，全部数据改走 vUSTB / MCSearch。

## License

MIT，详见 [LICENSE](LICENSE)。
