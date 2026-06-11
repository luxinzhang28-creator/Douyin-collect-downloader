<div align="center">

[![简体中文](https://img.shields.io/badge/README-简体中文-red?style=for-the-badge)](README.md)
[![English](https://img.shields.io/badge/README-English-blue?style=for-the-badge)](README_en.md)

# Douyin Collect Downloader

<h3>Saved 300 videos — but never reviewed a single one?</h3>

**Batch Download Favorites · Speech-to-Text · Structured Export**

Turn saved-but-never-watched favorites into searchable, analyzable local assets.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](requirements.txt)
[![Rich TUI](https://img.shields.io/badge/CLI-Rich_TUI-00C7B7)](download_collects.py)

[Quick Start](#-quick-start) · [Features](#-features) · [Preview](#-preview) · [Docs](USAGE.md)

</div>

---

## One-liner

> This is **not** just another video downloader — it's a **favorites-to-files pipeline**:
> pick folders interactively → batch download → extract spoken transcripts → export CSV/JSON for content ops or knowledge management.

It does **not** auto-build a knowledge base, but it makes the hardest first step — **getting scattered favorites onto your disk, structured** — dead simple.

---

<a id="preview"></a>

## Preview

### Workflow

![Workflow](./docs/screenshots/demo-workflow.png)

### Interactive Folder Picker (Rich TUI)

No memorizing flags — pick folders like a menu:

![Interactive UI](./docs/screenshots/demo-interactive-menu.png)

| Input | Effect |
|-------|--------|
| `0` | Download all folders |
| `2` | Download folder #2 only |
| `1,3,5` | Download multiple folders |

### Live Download Progress

Multi-threaded, skip existing files, live progress bar:

![Download progress](./docs/screenshots/demo-download-progress.png)

### Output Structure

Videos, covers, audio, metadata & transcripts organized by folder:

![Output structure](./docs/screenshots/demo-output-structure.png)

---

<a id="features"></a>

## Features

### 1. Three Download Sources

```bash
python download_collects.py                    # Interactive
python download_collects.py --all              # All folders
python download_collects.py --mode favorites   # Uncategorized favorites
python download_collects.py --mode both        # Both
```

| Mode | Who it's for |
|------|--------------|
| **Folders** | Themed collections: motivation, business, AI, etc. |
| **Favorites** | All saved videos without folder grouping |
| **Both** | Full backup in one run |

### 2. Beautiful CLI (Rich TUI)

Built with [Rich](https://github.com/Textualize/rich):

- Color tables with folder names & video counts
- Confirm panel before download
- Live progress bar with skip/success/fail status
- Chinese folder names · Windows / Linux / macOS

### 3. Speech-to-Text

```bash
python extract_transcript.py --backend vosk --path "./Downloaded/collects"
```

Exports `*_transcript.txt` and updates `*_result.json` with spoken content.

### 4. Structured Logs

Auto-generates `download_log_latest.csv` / `.json` — drop into Excel, Notion, or AI workflows for topic analysis.

### 5. Cookie Helpers

- `cookie_extractor.py` — Playwright auto browser login
- `get_cookies_manual.py` — Manual F12 step-by-step guide
- Saves to `config.yml` — same file as main workflow

---

## vs. Generic Downloaders

| | Generic douyin-downloader | This project |
|--|---------------------------|--------------|
| Favorites folders | ❌ | ✅ Core feature |
| Uncategorized favorites | ❌ | ✅ `--mode favorites` |
| Interactive folder picker | ❌ | ✅ Rich TUI |
| Transcription | ❌ | ✅ Vosk / Whisper |
| Download log CSV | ❌ | ✅ Auto |
| Folder-based output | ❌ | ✅ Default |

---

## Pipeline

```mermaid
flowchart LR
    A[📁 Douyin Favorites] --> B[download_collects.py]
    B --> C[Video / Cover / Audio / JSON]
    C --> D[extract_transcript.py]
    D --> E[CSV / JSON / TXT]
    E --> F[Obsidian / Excel / AI]
```

---

## Who It's For

| Who | Use case |
|-----|----------|
| Heavy savers | Full backup — never lose a saved video |
| Content ops | Batch extract scripts, study topics & hooks |
| Creators | Turn favorites into a searchable asset library |
| PKM users | Export structured data to Obsidian / Notion |
| Developers | Open source, fork-friendly, Cursor-ready |

---

## Requirements

| Scenario | Python |
|----------|--------|
| Download + Vosk | 3.8+ |
| Faster-Whisper | 3.9+ |
| **Recommended** | **3.10** |

---

<a id="quick-start"></a>

## Quick Start

```bash
# 1. Clone
git clone https://github.com/luxinzhang28-creator/Douyin-collect-downloader.git
cd Douyin-collect-downloader

# 2. Install (includes Playwright)
pip install -r requirements.txt
playwright install chromium

# 3. Cookie
python cookie_extractor.py
cp config.example.yml config.yml

# 4. Download (interactive — recommended first time)
python download_collects.py

# 5. Transcribe
pip install -r requirements-transcript-vosk.txt
python extract_transcript.py --backend vosk --path "./Downloaded/collects"
```

Full Cookie guide: **[USAGE.md](USAGE.md)**

---

## Output Layout

```
Downloaded/collects/
├── download_log_latest.csv
├── download_log_latest.json
├── Motivation/
│   └── author_title/
│       ├── *_video.mp4
│       ├── *_music.mp3
│       ├── *_cover.jpg
│       ├── *_result.json
│       └── *_transcript.txt
└── ...
```

---

## Scripts

| Script | Description |
|--------|-------------|
| `download_collects.py` | Main favorites downloader (Rich TUI) |
| `extract_transcript.py` | Video → spoken text |
| `cookie_extractor.py` | Auto cookie via browser |
| `get_cookies_manual.py` | Manual cookie paste |
| `downloader.py` / `DouYinCommand.py` | Bonus: single video / profile download |

---

## FAQ

<details>
<summary><b>Why Cookie?</b></summary>

Favorites require login. Cookie is your session credential, stored locally in `config.yml` only.
</details>

<details>
<summary><b>Will Cookie leak to GitHub?</b></summary>

No. Excluded in `.gitignore`. See [SECURITY.md](SECURITY.md).
</details>

<details>
<summary><b>Poor transcription quality?</b></summary>

Try Faster-Whisper: `pip install -r requirements-transcript.txt` then add `--backend whisper`.
</details>

---

## Roadmap

- [ ] `export_obsidian.py` — one-click Markdown export
- [ ] Auto topic tagging
- [ ] Batch AI summarization
- [ ] GUI
- [ ] Topic library CSV template

Ideas? [Open an Issue](https://github.com/luxinzhang28-creator/Douyin-collect-downloader/issues).

---

## Credits

Based on [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader) & [Mu-L/douyin-downloader](https://github.com/Mu-L/douyin-downloader).

## Disclaimer

For personal learning only. Respect copyright and platform Terms of Service.

## License

[MIT](LICENSE)

---

<div align="center">

**If this rescued your favorites from the void — please ⭐ Star the repo**

</div>
