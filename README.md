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
├── src/                          # 全部 Python 源码
│   ├── __init__.py
│   ├── main.py                   # 入口（python -m main, PYTHONPATH=src）
│   ├── client.py                 # VBotClient，路由群/频道/私聊消息
│   ├── config.py                 # .env + config.yaml 加载（凭据从 secrets 取）
│   ├── secrets.py                # 机器人凭据（XOR+base64 混淆后的常量）
│   ├── env_loader.py             # 零依赖的 .env 解析器（兼容旧用法）
│   └── services/
│       ├── http_client.py        # 复用 httpx.AsyncClient + 重试
│       ├── mc_servers.py         # vUSTB MC 服务器 API
│       ├── printers.py           # vUSTB 打印机 API
│       ├── wiki.py               # MCSearch Wiki 词条 API
│       └── mod_search.py         # MCSearch Mod 搜索 API
├── config.yaml                   # 静态配置（占位，全部数据走 API 实时拉取）
├── Dockerfile                    # vBot 镜像构建
├── docker-compose.yml            # 一键启动
├── start.bat                     # Windows 一键启动
├── requirements.txt              # Python 依赖
├── LICENSE
└── README.md
```

## 关于凭据（重要）

机器人凭据 **不再通过 `.env` 注入**，而是**硬编码在 [src/secrets.py](src/secrets.py) 里**，并做了一个简单的 `XOR + base64` 混淆（仅防 `grep`，不是真正的安全保护）。

为什么这么做：
- 单文件部署，省去挂卷 / 传 env_file 的麻烦；
- 仓库本身应是私有的；
- 如果将来要轮换凭据，按 [src/secrets.py](src/secrets.py) 顶部的生成脚本替换三个 `*_ENC` 常量即可。

> ⚠️ 安全提示：拿到源码就能还原出原始凭据。**请勿将本仓库公开 / 上传到公网 / 推送到公开镜像仓库**，否则机器人账号有被盗用风险。

如果以后想换回 `.env`，把 `src/config.py` 里 `get_appid()` / `get_secret()` 改成 `os.getenv("APPID")` 即可，并恢复 [docker-compose.yml](docker-compose.yml) 的 `env_file: [.env]` 段。

## 配置（可选环境变量）

```env
# 覆盖 vUSTB 公开 API 的 Base URL
USTB_API_BASE=https://www.ustb.world
# 覆盖 MCSearch 的 Base URL
MCSEARCH_BASE=https://search.tecostudio.cn
```

可以通过 `docker-compose.yml` 的 `environment` 段、或本地 shell 注入。

## 运行方式

### 方式一：本地直接运行

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m main
```

Windows 用户可直接双击 `start.bat`。

### 方式二：Docker Compose

```bash
docker compose up -d --build
docker compose logs -f vbot
```

## 注意事项

- 机器人需要**出网**访问 QQ 官方 API 以及 `ustb.world` / `search.tecostudio.cn`。
- vUSTB 与 MCSearch 接口均为公开接口，但请遵守各自的服务条款和限流（参见上游响应头 `X-RateLimit-*`）。
- 单条 QQ 文本消息上限约 4500 字；若返回过长会被服务端拒绝，后续可按需改为分段/消息合并转发。
- 旧版的 MineBBS 第三方 ping、`/api/mc-servers` 直连方案、`botpy.log`、`.env` 配置方式均已移除。

## License

MIT，详见 [LICENSE](LICENSE)。
