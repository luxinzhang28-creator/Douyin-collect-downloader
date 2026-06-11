# 使用说明

本文档以**收藏夹下载 + 口播转写**为主流程。Cookie 配置是新手最容易卡住的地方，请仔细阅读。

## 目录

1. [推荐环境](#1-推荐环境)
2. [安装依赖](#2-安装依赖)
3. [Cookie 获取与填写教程](#3-cookie-获取与填写教程)
4. [下载收藏夹](#4-下载收藏夹)
5. [提取口播文字](#5-提取口播文字)
6. [查看输出结果](#6-查看输出结果)
7. [常见问题](#7-常见问题)
8. [附：V1/V2 下载器（可选）](#8-附v1v2-下载器可选)

---

## 1. 推荐环境

| 场景 | Python 版本 |
|------|------------|
| 仅下载 + Vosk 转写 | 3.8+ |
| Faster-Whisper 转写 | 3.9+ |
| **新手推荐** | **3.10** |

操作系统：Windows / macOS / Linux 均可。

---

## 2. 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
playwright install chromium
```

若只需转写功能，额外安装：

```bash
# Vosk（Python 3.8+，轻量）
pip install -r requirements-transcript-vosk.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Faster-Whisper（Python 3.9+，更准确）
pip install -r requirements-transcript.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 3. Cookie 获取与填写教程

抖音收藏夹属于**登录后内容**，首次使用前必须配置 Cookie。

Cookie 相当于网页登录状态，**请勿分享给他人，也不要上传到 GitHub**。详见 [SECURITY.md](SECURITY.md)。

### 准备工作

若还没有 `config.yml`，先从模板复制：

```bash
cp config.example.yml config.yml
```

Cookie 工具会把解析结果保存到 **`config.yml`**（与 `download_collects.py` 读取的文件一致）。

---

### 方式一：自动获取 Cookie（推荐）

**第 1 步：确认 Playwright 已安装**

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
playwright install chromium
```

**第 2 步：运行自动获取工具**

```bash
python cookie_extractor.py
```

程序会自动打开浏览器，你需要在浏览器中**登录抖音网页版**。

登录成功后，程序会读取 Cookie 并保存到 `config.yml`。

**第 3 步：验证**

```bash
python download_collects.py
```

若能看到收藏夹列表，说明 Cookie 有效。

**浏览器打不开？** 尝试：

```bash
playwright install chromium
```

仍失败则改用下面的手动方式。

---

### 方式二：手动获取 Cookie

**第 1 步：打开抖音网页版**

用 Chrome 或 Edge 打开 [https://www.douyin.com](https://www.douyin.com)，并登录账号。

**第 2 步：打开开发者工具**

按 `F12`，或右键页面选择「检查」。

**第 3 步：方法一 — 从「应用」面板获取（推荐，最稳定）**

1. 切换到顶部的 **Application / 应用** 标签
2. 左侧展开 **Storage → Cookies → https://www.douyin.com**
3. 在右侧找到并复制以下字段的值：
   - `sessionid`
   - `ttwid`
   - `msToken`
   - `odin_tt`

**第 3 步：方法二 — 从「网络」面板获取（备用）**

1. 切换到 **Network / 网络** 标签
2. 勾选 **Preserve log / 保留日志**
3. 过滤框输入 `www.douyin.com`，类型选 **Fetch/XHR**
4. 点击任意收藏夹或滚动收藏列表，触发请求
5. 点击某个 `www.douyin.com` 请求
6. 在 **Request Headers / 请求标头** 中找到 `Cookie`，复制完整内容

**第 4 步：运行手动 Cookie 工具**

```bash
python get_cookies_manual.py
```

选择 `1. 获取新的 Cookie`，粘贴复制的内容，确认保存。

程序会解析 Cookie 并保存到 **`config.yml`**。

---

### Cookie 填写格式

**推荐：键值对方式**（保存在 `config.yml`）

```yaml
cookies:
  sessionid: YOUR_SESSIONID
  ttwid: YOUR_TTWID
  msToken: YOUR_MSTOKEN
  odin_tt: YOUR_ODIN_TT
```

**备选：整串 Cookie**

```yaml
cookie: "sessionid=xxx; ttwid=xxx; msToken=xxx; odin_tt=xxx;"
```

注意：`cookies` 和 `cookie` 二选一即可，不要同时填写。

---

### Cookie 安全提醒

以下文件必须保持本地私有，**不要提交到 Git**：

- `config.yml`
- `cookies.txt`
- `cookies_backup_*.json`
- `Downloaded/`
- `logs/`

若不小心把 Cookie 上传到 GitHub，请立即退出抖音网页版并重新登录，使旧 Cookie 失效。

---

## 4. 下载收藏夹

确保 `config.yml` 中 Cookie 已填写。

```bash
# 交互选择收藏夹
python download_collects.py

# 下载全部收藏夹
python download_collects.py --all

# 只下载「收藏的视频」（不按收藏夹分类）
python download_collects.py --mode favorites

# 下载指定收藏夹（从 1 开始编号）
python download_collects.py --folder-index 3
```

默认保存路径：`./Downloaded/collects/`

---

## 5. 提取口播文字

```bash
# Vosk（推荐新手，Python 3.8+）
pip install -r requirements-transcript-vosk.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python extract_transcript.py --backend vosk --path "./Downloaded/collects"

# Faster-Whisper（更准确，Python 3.9+）
pip install -r requirements-transcript.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python extract_transcript.py --backend whisper --path "./Downloaded/collects"

# 强制重新识别
python extract_transcript.py --backend vosk --path "./Downloaded/collects" --force
```

每个视频会生成 `*_transcript.txt`，同时更新 `*_result.json` 中的 `spoken_transcript` 字段。

---

## 6. 查看输出结果

```
Downloaded/collects/
├── download_log_latest.csv      # 总表，可用 Excel 打开
├── download_log_latest.json
├── 收藏夹名称/
│   └── 作者_标题/
│       ├── *_video.mp4
│       ├── *_music.mp3
│       ├── *_cover.jpg
│       ├── *_result.json        # 元数据
│       └── *_transcript.txt     # 口播全文
```

---

## 7. 常见问题

### Cookie 过期怎么办？

重新运行 `python cookie_extractor.py` 或 `python get_cookies_manual.py` 获取新 Cookie。

### 下载失败 / 收藏夹列表为空？

1. 确认 Cookie 有效（重新登录抖音网页版测试）
2. 确认 `config.yml` 中至少有 `sessionid`、`ttwid`、`msToken`
3. 查看 `download_log_latest.json` 中的错误信息

### 转写结果乱码或为空？

1. 确认视频有口播（纯音乐视频无法转写）
2. 尝试 `--force` 重新识别
3. 换用 Faster-Whisper 引擎

### 获取帮助

- 详细文档：[README.md](README.md)
- 安全问题：[SECURITY.md](SECURITY.md)
- 报告问题：[GitHub Issues](https://github.com/luxinzhang28-creator/Douyin-collect-downloader/issues)

---

## 8. 附：V1/V2 下载器（可选）

本项目还保留了原项目的单视频/主页下载能力，非主流程：

| 脚本 | 适用场景 |
|------|---------|
| `DouYinCommand.py` | V1.0 稳定版，单视频下载 |
| `downloader.py` | V2.0 增强版，用户主页批量下载 |

```bash
# V1.0 示例
python DouYinCommand.py

# V2.0 示例
python downloader.py -u "https://www.douyin.com/user/xxxxx"
```
