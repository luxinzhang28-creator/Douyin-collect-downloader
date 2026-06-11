# Douyin Collect Downloader

**抖音收藏夹批量下载与视频转文字工具。**

本项目用于将抖音收藏夹、收藏视频保存到本地，并提取视频口播文案，生成结构化日志，方便后续进行**素材整理、内容运营分析、选题研究**或**个人知识库沉淀**。

> 它不是一个「自动生成知识库」的工具，而是一个面向资料整理的**前置处理工具**。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20recommended-blue.svg)](requirements.txt)

## 工作流程

```
抖音收藏夹 / 视频链接
    ↓
批量下载视频、封面、音乐、元数据
    ↓
提取视频口播文案
    ↓
生成 CSV / JSON / TXT
    ↓
导入 Obsidian / Notion / Excel / AI 工具继续整理
```

## 适用人群

- 想**备份和整理**抖音收藏夹的用户
- **短视频运营、内容运营、素材分析**人员
- 想研究爆款视频**标题、口播、选题结构**的人
- 想把视频内容**转成文字资料**的人
- 想把收藏内容**沉淀为个人知识库**的人

## 核心功能

| 功能 | 说明 |
|------|------|
| 收藏夹批量下载 | 支持下载收藏夹内容、收藏视频，并生成下载日志 |
| 视频转文字 | 支持 Vosk / Faster-Whisper 提取口播文案 |
| 结构化日志 | 自动生成 CSV / JSON，方便筛选、统计和整理 |
| Cookie 获取工具 | 支持自动获取和手动填写 Cookie |
| 本地资料整理 | 可作为 Obsidian、Notion、Excel、AI 总结工具的前置流程 |

## 推荐环境

**推荐使用 Python 3.10**

最低可用环境：

| 场景 | Python 版本 |
|------|------------|
| 仅下载 + Vosk 转写 | 3.8+ |
| Faster-Whisper 转写 | 3.9+ |
| **新手推荐** | **3.10** |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/luxinzhang28-creator/Douyin-collect-downloader.git
cd Douyin-collect-downloader
```

### 2. 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
playwright install chromium
```

### 3. 配置 Cookie 并下载

```bash
# 自动获取 Cookie（推荐）
python cookie_extractor.py

# 或手动获取
python get_cookies_manual.py

# 若尚未有 config.yml，从模板复制
cp config.example.yml config.yml

# 下载收藏夹
python download_collects.py --all
```

### 4. 提取口播文案

```bash
pip install -r requirements-transcript-vosk.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python extract_transcript.py --backend vosk --path "./Downloaded/collects"
```

详细步骤见 [USAGE.md](USAGE.md)，Cookie 教程占主要篇幅。

## 输出文件示例

```
Downloaded/collects/
├── download_log_latest.csv
├── download_log_latest.json
├── 激励/
│   ├── 作者名_视频标题/
│   │   ├── 作者名_视频标题_video.mp4
│   │   ├── 作者名_视频标题_music.mp3
│   │   ├── 作者名_视频标题_cover.jpg
│   │   ├── 作者名_视频标题_result.json
│   │   └── 作者名_视频标题_transcript.txt
│   └── ...
└── 创业/
    └── ...
```

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `download_collects.py` | **收藏夹下载**（主流程） |
| `extract_transcript.py` | 口播转文字 |
| `cookie_extractor.py` | Playwright 自动获取 Cookie |
| `get_cookies_manual.py` | 手动获取 Cookie |
| `DouYinCommand.py` | V1.0 稳定版（单视频/主页，附赠） |
| `downloader.py` | V2.0 增强版（用户主页，附赠） |

## FAQ

### 为什么需要 Cookie？

收藏夹属于登录后内容，需要通过 Cookie 识别当前账号。详见 [USAGE.md](USAGE.md#cookie-获取与填写教程)。

### Cookie 会上传到 GitHub 吗？

不会。`config.yml`、`cookies.txt` 等已在 `.gitignore` 中忽略。详见 [SECURITY.md](SECURITY.md)。

### 为什么转写效果不完美？

Vosk 轻量快速，适合本地使用。追求更高准确率可使用 Faster-Whisper（Python 3.9+）：

```bash
pip install -r requirements-transcript.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python extract_transcript.py --backend whisper --path "./Downloaded/collects"
```

## Roadmap

- [ ] 自动生成 Obsidian Markdown（`export_obsidian.py`）
- [ ] 自动按主题分类收藏视频
- [ ] 接入大模型批量总结
- [ ] 生成知识图谱节点
- [ ] 增加图形化界面
- [ ] 支持一键导出选题库

## Credits

本项目基于以下开源项目二次开发：

- [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader)
- [Mu-L/douyin-downloader](https://github.com/Mu-L/douyin-downloader)

感谢原作者与开源社区。

## 免责声明

- 本项目仅供**学习交流**使用
- 请遵守相关法律法规及抖音平台服务条款
- 不得用于商业用途或侵犯他人版权
- 下载内容请尊重原作者权益

## 许可证

[MIT License](LICENSE)

---

如果这个项目对你有帮助，请给个 ⭐ Star！
