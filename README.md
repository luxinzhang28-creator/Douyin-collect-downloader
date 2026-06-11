<div align="center">

# Douyin Collect Downloader

<h3>
  收藏了 300 条视频，却一条都没复盘过？<br/>
  Saved 300 videos — but never reviewed a single one?
</h3>

<p>
  <strong>抖音收藏夹批量下载 · 口播转文字 · 结构化整理</strong><br/>
  <strong>Batch Download Favorites · Speech-to-Text · Structured Export</strong>
</p>

<p>
  把「只收藏、不看」的内容，变成可搜索、可统计、可分析的本地资料。<br/>
  Turn saved-but-never-watched favorites into searchable, analyzable local assets.
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](requirements.txt)
[![Rich TUI](https://img.shields.io/badge/CLI-Rich_TUI-00C7B7)](download_collects.py)

[中文](#中文) · [English](#english) · [快速开始 / Quick Start](#-快速开始--quick-start) · [效果预览 / Preview](#-效果预览--preview) · [文档 / Docs](USAGE.md)

</div>

---

<a id="中文"></a>

## 一句话说清楚

> 这不是又一个「视频下载器」，而是一套 **收藏夹资料整理流水线**：
> 交互式选择收藏夹 → 批量下载 → 提取口播文案 → 输出 CSV/JSON，供运营分析或知识库沉淀。

它**不会**自动帮你生成知识库，但会把最难的第一步——**把收藏夹里的碎片内容搬到本地并结构化**——做到足够简单。

<a id="english"></a>

## One-liner

> This is **not** just another video downloader — it's a **favorites-to-files pipeline**:
> pick folders interactively → batch download → extract spoken transcripts → export CSV/JSON for content ops or knowledge management.

It does **not** auto-build a knowledge base, but it makes the hardest first step — **getting scattered favorites onto your disk, structured** — dead simple.

---

<a id="效果预览--preview"></a>

## 效果预览 · Preview

### 整体流程 · Workflow

![工作流程 Workflow](./docs/screenshots/demo-workflow.png)

### 交互式收藏夹选择 · Interactive Folder Picker (Rich TUI)

不用记命令，运行后像菜单一样点选收藏夹 · No memorizing flags — pick folders like a menu:

![交互界面 Interactive UI](./docs/screenshots/demo-interactive-menu.png)

| 输入 Input | 效果 Effect |
|------------|-------------|
| `0` | 下载全部收藏夹 · Download all folders |
| `2` | 只下载第 2 个 · Download folder #2 only |
| `1,3,5` | 下载多个 · Download multiple folders |

### 真实下载进度 · Live Download Progress

多线程下载、跳过已存在、实时进度条 · Multi-threaded, skip existing, live progress bar:

![下载进度 Download progress](./docs/screenshots/demo-download-progress.png)

### 本地输出目录 · Output Structure

视频、封面、音频、元数据、口播文案，按收藏夹分类 · Videos, covers, audio, metadata & transcripts by folder:

![输出结构 Output structure](./docs/screenshots/demo-output-structure.png)

---

## 功能亮点 · Features

### 1. 三种下载来源 · Three Download Sources

```bash
python download_collects.py                    # 交互式 · Interactive
python download_collects.py --all              # 全部收藏夹 · All folders
python download_collects.py --mode favorites   # 收藏的视频 · Uncategorized favorites
python download_collects.py --mode both        # 两者都要 · Both
```

| 模式 Mode | 适合 Who it's for |
|-----------|-------------------|
| **收藏夹 Folders** | 按主题分类：激励、创业、AI 等 · Themed folders |
| **收藏的视频 Favorites** | 随手收藏、未分类 · Uncategorized saves |
| **两者都要 Both** | 一次性全量备份 · Full backup |

### 2. 好看的终端交互 · Beautiful CLI (Rich TUI)

- 彩色表格展示收藏夹和作品数 · Color tables with folder names & counts
- 下载前确认面板 · Confirm panel before download
- 实时进度条 · Live progress bar
- 支持中文收藏夹名 · Chinese folder names supported

### 3. 口播转文字 · Speech-to-Text

```bash
python extract_transcript.py --backend vosk --path "./Downloaded/collects"
```

输出 `*_transcript.txt` + 更新 `*_result.json` · Exports transcript TXT & updates JSON metadata.

### 4. 结构化日志 · Structured Logs

自动生成 `download_log_latest.csv` / `.json` — 直接丢进 Excel 做选题分析 · Auto CSV/JSON for Excel, Notion, or AI workflows.

### 5. Cookie 工具 · Cookie Helpers

- `cookie_extractor.py` — Playwright 自动登录 · Auto browser login
- `get_cookies_manual.py` — F12 手动复制 · Manual F12 guide
- 统一保存到 `config.yml` · Saves to `config.yml`

---

## 和普通下载器的区别 · vs. Generic Downloaders

| | 普通 douyin-downloader | 本项目 This project |
|--|------------------------|---------------------|
| 收藏夹下载 Favorites folders | ❌ | ✅ 核心 Core |
| 收藏视频 Uncategorized | ❌ | ✅ `--mode favorites` |
| 交互选文件夹 Interactive picker | ❌ | ✅ Rich TUI |
| 口播转文字 Transcription | ❌ | ✅ Vosk / Whisper |
| 下载日志 CSV Download log | ❌ | ✅ Auto |
| 按收藏夹分目录 Folder structure | ❌ | ✅ Default |

---

## 工作流程 · Pipeline (Mermaid)

```mermaid
flowchart LR
    A["📁 收藏夹 Favorites"] --> B["download_collects.py"]
    B --> C["视频/封面/音频/JSON Media + JSON"]
    C --> D["extract_transcript.py"]
    D --> E["CSV / JSON / TXT"]
    E --> F["Obsidian / Excel / AI"]
```

---

## 适用人群 · Who It's For

| 你是谁 Who | 用途 Use case |
|------------|---------------|
| 收藏党 Savers | 全量备份，不怕视频被删 · Full backup |
| 短视频运营 Creators / Ops | 批量提取口播，研究选题话术 · Script & topic research |
| 内容创作者 Content makers | 收藏变素材库 · Favorites as asset library |
| 知识管理 PKM users | 导入 Obsidian / Notion · Import to notes |
| 开发者 Devs | 开源可改，Cursor 友好 · Fork & extend |

---

## 推荐环境 · Requirements

| 场景 Scenario | Python |
|---------------|--------|
| 下载 + Vosk Download + Vosk | 3.8+ |
| Faster-Whisper | 3.9+ |
| **新手推荐 Recommended** | **3.10** |

---

<a id="快速开始--quick-start"></a>

## 快速开始 · Quick Start

```bash
# 1. Clone 克隆
git clone https://github.com/luxinzhang28-creator/Douyin-collect-downloader.git
cd Douyin-collect-downloader

# 2. Install 安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
playwright install chromium

# 3. Cookie
python cookie_extractor.py
cp config.example.yml config.yml

# 4. Download 下载（interactive 交互式）
python download_collects.py

# 5. Transcribe 转写
pip install -r requirements-transcript-vosk.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python extract_transcript.py --backend vosk --path "./Downloaded/collects"
```

Cookie 详细教程 · Full Cookie guide: **[USAGE.md](USAGE.md)**

---

## 输出目录 · Output Layout

```
Downloaded/collects/
├── download_log_latest.csv
├── 激励/ Motivation/
│   └── author_title/
│       ├── *_video.mp4
│       ├── *_result.json
│       └── *_transcript.txt
└── ...
```

---

## 脚本一览 · Scripts

| 脚本 Script | 说明 Description |
|-------------|------------------|
| `download_collects.py` | 收藏夹下载主程序 · Main favorites downloader |
| `extract_transcript.py` | 口播转文字 · Speech-to-text |
| `cookie_extractor.py` | 自动 Cookie · Auto cookie |
| `get_cookies_manual.py` | 手动 Cookie · Manual cookie |

---

## FAQ

<details>
<summary><b>为什么需要 Cookie？ / Why Cookie?</b></summary>

收藏夹需登录后才能访问，Cookie 仅保存在本地 `config.yml`。<br/>
Favorites require login. Cookie stays local in `config.yml` only.
</details>

<details>
<summary><b>Cookie 会上传 GitHub 吗？ / Will Cookie leak to GitHub?</b></summary>

不会，已在 `.gitignore` 排除。详见 [SECURITY.md](SECURITY.md)。<br/>
No. See [SECURITY.md](SECURITY.md).
</details>

<details>
<summary><b>转写不准怎么办？ / Poor transcription?</b></summary>

换 Faster-Whisper：`pip install -r requirements-transcript.txt` 后加 `--backend whisper`。<br/>
Try `--backend whisper` with `requirements-transcript.txt`.
</details>

---

## Roadmap

- [ ] `export_obsidian.py` — Markdown 导出 · Markdown export
- [ ] 自动标签 · Auto tagging
- [ ] AI 批量总结 · Batch AI summaries
- [ ] GUI 图形界面 · GUI
- [ ] 选题库模板 · Topic library template

[提 Issue / Open Issue](https://github.com/luxinzhang28-creator/Douyin-collect-downloader/issues)

---

## Credits

基于 · Based on [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader) & [Mu-L/douyin-downloader](https://github.com/Mu-L/douyin-downloader).

## 免责声明 · Disclaimer

仅供学习交流 · For personal learning only. Respect copyright and platform ToS.

## License

[MIT](LICENSE)

---

<div align="center">

**如果这个项目帮你把收藏夹「救」了出来，请点个 ⭐ Star**<br/>
**If this rescued your favorites from the void — please ⭐ Star the repo**

</div>
