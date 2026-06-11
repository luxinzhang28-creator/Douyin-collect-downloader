# 抖音收藏夹下载器 · 把收藏变成知识库

> 收藏了大量学习/创业视频却用不上？  
> 本工具帮你：**批量下载抖音收藏夹 → 提取口播文案 → 导出结构化日志**，方便导入 Obsidian 等笔记工具。

基于 [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader) 二次开发，参考 [Mu-L/douyin-downloader](https://github.com/Mu-L/douyin-downloader)。

## ✨ 核心功能（相比原版新增）

| 功能 | 说明 |
|------|------|
| 📁 收藏夹批量下载 | `download_collects.py` 支持按收藏夹、全部收藏、交互选择 |
| 🎙️ 口播文案提取 | `extract_transcript.py` 支持 Vosk / Faster-Whisper |
| 📊 结构化日志 | 自动生成 CSV + JSON，便于后续知识库整理 |
| 🍪 Cookie 工具 | 自动/手动获取 Cookie，附详细踩坑教程见 `USAGE.md` |

## 🚀 快速开始

### 环境要求

- Python 3.8+（Vosk）或 Python 3.9+（Whisper）
- Windows / macOS / Linux

### 安装

```bash
git clone https://github.com/luxinzhang28-creator/Douyin-collect-downloader.git
cd Douyin-collect-downloader
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 使用流程

```bash
# 1. 获取 Cookie（首次使用）
python cookie_extractor.py
# 或: python get_cookies_manual.py

# 2. 复制配置模板并填入 Cookie
cp config.example.yml config.yml

# 3. 下载收藏夹
python download_collects.py              # 交互选择
python download_collects.py --all        # 下载全部收藏夹

# 4. 提取口播文案（需额外安装 vosk 依赖）
pip install -r requirements-transcript-vosk.txt
python extract_transcript.py --backend vosk --path "./Downloaded/collects"
```

## 📋 脚本说明

| 脚本 | 用途 |
|------|------|
| `download_collects.py` | **收藏夹下载**（本项目核心） |
| `extract_transcript.py` | 口播转文字 |
| `DouYinCommand.py` | V1.0 稳定版（单视频/主页） |
| `downloader.py` | V2.0 增强版（异步/自动 Cookie） |
| `cookie_extractor.py` | Playwright 自动获取 Cookie |

## ⚠️ 免责声明

- 本项目仅供**学习交流**使用
- 请遵守相关法律法规及抖音平台服务条款
- 不得用于商业用途或侵犯他人版权
- 下载内容请尊重原作者权益

## 📄 许可证

MIT License

---

如果这个项目对你有帮助，请给个 ⭐ Star！
