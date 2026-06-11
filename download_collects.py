#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
下载抖音「我 → 收藏」下的视频，并生成结构化日志。

支持两种来源:
  - 收藏夹: 用户创建的收藏夹分类
  - 收藏的视频: 「收藏」页全部作品（不按收藏夹分类）

用法:
  python download_collects.py              # 交互选择来源与收藏夹
  python download_collects.py --all        # 下载全部收藏夹
  python download_collects.py --mode favorites
  python download_collects.py --mode both --all
  python download_collects.py --folder-index 3
  python download_collects.py --max-duration 3600
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from apiproxy.douyin import douyin_headers
from apiproxy.douyin.douyin import Douyin
from apiproxy.douyin.download import Download
from apiproxy.common import utils

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
)
logger = logging.getLogger('download_collects')
console = Console(highlight=False)

DEFAULT_MAX_DURATION_SEC = 3600  # 1 小时
FAVORITE_VIDEO_LABEL = '收藏的视频'
FAVORITE_VIDEO_ID = '__favorites__'
MODE_FOLDERS = 'folders'
MODE_FAVORITES = 'favorites'
MODE_BOTH = 'both'


def load_config(config_path: Path) -> dict:
    defaults = {
        'path': './Downloaded/collects/',
        'music': True,
        'cover': True,
        'avatar': False,
        'json': True,
        'folderstyle': True,
        'thread': 5,
        'max_duration_sec': DEFAULT_MAX_DURATION_SEC,
        'number': {'folders': 0, 'videos': 0},
        'cookies': {},
        'cookie': '',
    }
    if not config_path.exists():
        return defaults
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    for key, value in data.items():
        if key == 'number' and isinstance(value, dict):
            defaults['number'].update(value)
        else:
            defaults[key] = value
    return defaults


def apply_cookie(config: dict):
    cookie_str = config.get('cookie') or ''
    if not cookie_str and config.get('cookies'):
        cookie_str = '; '.join(f'{k}={v}' for k, v in config['cookies'].items())
    if cookie_str:
        douyin_headers['Cookie'] = cookie_str
        return True
    return False


def video_url(aweme_id) -> str:
    return f'https://www.douyin.com/video/{aweme_id}'


def format_duration(seconds: float) -> str:
    if seconds <= 0:
        return '未知'
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h:
        return f'{h}小时{m}分{s}秒'
    if m:
        return f'{m}分{s}秒'
    return f'{s}秒'


def get_duration_sec(aweme: dict) -> float:
    if aweme.get('duration_sec'):
        return float(aweme['duration_sec'])
    ms = aweme.get('duration_ms') or 0
    return float(ms) / 1000.0 if ms else 0.0


def save_logs(save_root: Path, summary: dict, entries: list):
    save_root.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')

    json_path = save_root / f'download_log_{ts}.json'
    csv_path = save_root / f'download_log_{ts}.csv'
    latest_json = save_root / 'download_log_latest.json'
    latest_csv = save_root / 'download_log_latest.csv'

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'entries': entries}, f, ensure_ascii=False, indent=2)
    with open(latest_json, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'entries': entries}, f, ensure_ascii=False, indent=2)

    fieldnames = [
        'source_type', 'folder_name', 'folder_id', 'aweme_id', 'url', 'desc', 'author',
        'duration_sec', 'duration_text', 'aweme_type', 'status', 'reason',
        'save_path', 'timestamp',
    ]
    for path in (csv_path, latest_csv):
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries)

    logger.info('日志已保存: %s', json_path)
    logger.info('日志已保存: %s', csv_path)
    return json_path, csv_path


def download_folder(dl: Download, videos: list, folder_path: Path) -> list:
    results = []
    for aweme in videos:
        try:
            dl.awemeDownload(awemeDict=aweme, savePath=folder_path)
            results.append(('success', aweme, ''))
        except Exception as e:
            logger.error('下载失败 aweme_id=%s: %s', aweme.get('aweme_id'), e)
            results.append(('failed', aweme, str(e)))
    return results


def filter_videos_by_duration(videos: list, max_duration_sec: float):
    kept, skipped = [], []
    for aweme in videos:
        dur = get_duration_sec(aweme)
        if max_duration_sec > 0 and dur > max_duration_sec:
            skipped.append((aweme, dur))
        else:
            kept.append(aweme)
    return kept, skipped


def make_entry(folder_name, folder_id, aweme, folder_path, status, reason='', source_type='folder'):
    dur = get_duration_sec(aweme)
    aweme_type = 'video' if aweme.get('awemeType') == 0 else 'images'
    return {
        'source_type': source_type,
        'folder_name': folder_name,
        'folder_id': folder_id,
        'aweme_id': aweme.get('aweme_id', ''),
        'url': video_url(aweme.get('aweme_id', '')),
        'desc': (aweme.get('desc') or '')[:200],
        'author': aweme.get('author', {}).get('nickname', ''),
        'duration_sec': dur,
        'duration_text': format_duration(dur),
        'aweme_type': aweme_type,
        'status': status,
        'reason': reason,
        'save_path': str(folder_path) if status == 'success' else '',
        'timestamp': datetime.now().isoformat(),
    }


def folder_display_name(folder: dict) -> str:
    return folder.get('collects_name') or folder.get('name') or f'收藏夹_{folder.get("collects_id")}'


def parse_folder_choice(choice: str, folders: list):
    """解析用户输入，返回选中的收藏夹列表；无效则返回 None。"""
    normalized = choice.strip().lower()
    if normalized in ('', '0', 'all', 'a', '全部', '全'):
        return list(folders)

    parts = re.split(r'[,，\s]+', normalized)
    indices = []
    for part in parts:
        if not part:
            continue
        if not part.isdigit():
            return None
        idx = int(part)
        if idx < 1 or idx > len(folders):
            return None
        if idx not in indices:
            indices.append(idx)

    if not indices:
        return None
    return [folders[i - 1] for i in indices]


def folder_count(folder: dict) -> str:
    total = folder.get('total_number') or folder.get('collects_count')
    return str(total) if total is not None else '—'


def mode_label(mode: str) -> str:
    return {
        MODE_FOLDERS: '仅收藏夹',
        MODE_FAVORITES: '仅收藏的视频',
        MODE_BOTH: '收藏夹 + 收藏的视频',
    }.get(mode, mode)


def render_mode_menu():
    console.print()
    console.print(Panel(
        '[bold white]抖音收藏下载[/bold white]\n'
        '[dim]请选择要下载的内容来源[/dim]',
        border_style='bright_blue',
        padding=(1, 2),
        expand=False,
    ))
    table = Table(
        show_header=True,
        header_style='bold bright_white',
        border_style='bright_black',
        box=box.ROUNDED,
        padding=(0, 1),
        expand=False,
        title='[bold]下载来源[/bold]',
        title_style='bright_cyan',
    )
    table.add_column('序号', style='bold cyan', justify='center', width=6)
    table.add_column('来源', style='white', min_width=28)
    table.add_column('说明', style='dim', min_width=24)
    table.add_row('1', '收藏夹作品', '按你创建的收藏夹分类下载')
    table.add_row('2', '收藏的视频', '「我 → 收藏」全部作品，不按收藏夹')
    table.add_row('3', '两者都要', '先下收藏的视频，再下所选收藏夹')
    console.print(table)
    console.print()


def prompt_download_mode() -> str:
    render_mode_menu()
    mapping = {'1': MODE_FOLDERS, '2': MODE_FAVORITES, '3': MODE_BOTH}

    while True:
        try:
            choice = Prompt.ask(
                '[bold bright_white]请选择下载来源 (1/2/3)[/bold bright_white]',
                console=console,
            ).strip()
        except (EOFError, KeyboardInterrupt):
            console.print('\n[yellow]已取消[/yellow]')
            sys.exit(0)

        if choice in mapping:
            mode = mapping[choice]
            logger.info('已选择下载来源: %s', mode_label(mode))
            return mode

        console.print('[red]✗[/red] 输入无效，请输入 [cyan]1[/cyan]、[cyan]2[/cyan] 或 [cyan]3[/cyan]')


def build_target(folder: dict, save_root: Path) -> dict:
    folder_id = str(folder.get('collects_id', ''))
    folder_name = folder_display_name(folder)
    safe_name = utils.replaceStr(folder_name) or folder_id
    return {
        'type': MODE_FOLDERS,
        'name': folder_name,
        'id': folder_id,
        'path': save_root / safe_name,
    }


def build_favorite_target(save_root: Path) -> dict:
    safe_name = utils.replaceStr(FAVORITE_VIDEO_LABEL) or FAVORITE_VIDEO_ID
    return {
        'type': MODE_FAVORITES,
        'name': FAVORITE_VIDEO_LABEL,
        'id': FAVORITE_VIDEO_ID,
        'path': save_root / safe_name,
    }


def fetch_videos_for_target(dy: Douyin, target: dict, max_videos: int) -> list:
    if target['type'] == MODE_FAVORITES:
        return dy.getFavoriteVideoList(number=max_videos) or []
    return dy.getCollectsVideoList(target['id'], number=max_videos) or []


def process_download_target(
    dy: Douyin,
    dl: Download,
    target: dict,
    max_videos: int,
    max_duration: float,
    entries: list,
) -> tuple:
    folder_name = target['name']
    folder_id = target['id']
    folder_path = target['path']
    source_type = target['type']
    folder_path.mkdir(parents=True, exist_ok=True)

    all_videos = fetch_videos_for_target(dy, target, max_videos)
    videos, skipped = filter_videos_by_duration(all_videos, max_duration)
    total_skipped_duration = 0

    for aweme, dur in skipped:
        total_skipped_duration += 1
        logger.warning(
            '跳过(超长): %s | 时长 %s > 限制 %s | %s',
            (aweme.get('desc') or '')[:40],
            format_duration(dur),
            format_duration(max_duration),
            video_url(aweme.get('aweme_id', '')),
        )
        entries.append(make_entry(
            folder_name, folder_id, aweme, folder_path,
            'skipped', f'duration>{max_duration}s', source_type,
        ))

    success, failed = 0, 0
    if videos:
        dl_results = download_folder(dl, videos, folder_path)
        for status, aweme, reason in dl_results:
            if status == 'success':
                success += 1
            else:
                failed += 1
            entries.append(make_entry(
                folder_name, folder_id, aweme, folder_path, status, reason, source_type,
            ))
    elif not skipped:
        logger.warning('[%s] 内没有获取到视频', folder_name)

    return {
        'source_type': source_type,
        'folder_name': folder_name,
        'folder_id': folder_id,
        'video_total': len(all_videos),
        'video_downloaded': len(videos),
        'video_skipped_duration': len(skipped),
        'success': success,
        'failed': failed,
        'save_path': str(folder_path),
    }, total_skipped_duration


def render_folder_menu(folders: list):
    console.print()
    console.print(Panel(
        '[bold white]收藏夹选择[/bold white]\n'
        f'[dim]已扫描[/dim] [bold cyan]{len(folders)}[/bold cyan] [dim]个收藏夹 · 请选择要下载的项目[/dim]',
        border_style='bright_blue',
        padding=(1, 2),
        expand=False,
    ))

    table = Table(
        show_header=True,
        header_style='bold bright_white',
        border_style='bright_black',
        box=box.ROUNDED,
        padding=(0, 1),
        expand=False,
        title='[bold]收藏夹列表[/bold]',
        title_style='bright_cyan',
    )
    table.add_column('序号', style='bold cyan', justify='center', width=6, no_wrap=True)
    table.add_column('收藏夹名称', style='white', min_width=24, no_wrap=False)
    table.add_column('作品数', style='bold green', justify='right', width=8, no_wrap=True)

    table.add_row(
        '[bold yellow]0[/bold yellow]',
        '[bold yellow]★  全部下载[/bold yellow]',
        '[dim]全部[/dim]',
    )
    for i, folder in enumerate(folders, 1):
        table.add_row(str(i), folder_display_name(folder), folder_count(folder))

    console.print(table)
    console.print(
        Panel(
            '[dim]输入示例[/dim]  '
            '[cyan]0[/cyan] [dim]→ 全部[/dim]   '
            '[cyan]2[/cyan] [dim]→ 单个[/dim]   '
            '[cyan]1,3,5[/cyan] [dim]→ 多个（逗号或空格分隔）[/dim]',
            border_style='dim',
            padding=(0, 2),
            expand=False,
        ),
        '',
    )


def render_targets_confirm(targets: list):
    lines = []
    for i, target in enumerate(targets, 1):
        kind = '收藏视频' if target['type'] == MODE_FAVORITES else '收藏夹'
        extra = ''
        if target['type'] == MODE_FOLDERS:
            folder = target.get('folder_meta') or {}
            extra = f'  [dim]({folder_count(folder)} 个作品)[/dim]'
        lines.append(f'[cyan]{i:>2}[/cyan]  [{kind}] {target["name"]}{extra}')
    console.print(Panel(
        '\n'.join(lines),
        title=f'[bold green]即将下载 {len(targets)} 项[/bold green]',
        border_style='green',
        padding=(1, 2),
        expand=False,
    ))
    console.print()


def log_folder_selection(selected: list, total: int):
    if len(selected) == total:
        logger.info('已选择: 全部收藏夹 (%d 个)', total)
    elif len(selected) == 1:
        logger.info('已选择: %s', folder_display_name(selected[0]))
    else:
        names = '、'.join(folder_display_name(f) for f in selected)
        logger.info('已选择 %d 个收藏夹: %s', len(selected), names)


def prompt_folder_selection(folders: list) -> list:
    render_folder_menu(folders)

    while True:
        try:
            choice = Prompt.ask(
                '[bold bright_white]请输入序号[/bold bright_white]',
                console=console,
            ).strip()
        except (EOFError, KeyboardInterrupt):
            console.print('\n[yellow]已取消[/yellow]')
            sys.exit(0)

        selected = parse_folder_choice(choice, folders)
        if selected is None:
            console.print(
                f'[red]✗[/red] 输入无效，请输入 [cyan]0[/cyan]、[cyan]1[/cyan]-[cyan]{len(folders)}[/cyan] '
                f'或逗号分隔的多个序号',
            )
            continue

        log_folder_selection(selected, len(folders))
        return selected


def build_download_targets(mode: str, folders: list, save_root: Path) -> list:
    targets = []
    if mode in (MODE_FAVORITES, MODE_BOTH):
        targets.append(build_favorite_target(save_root))
    if mode in (MODE_FOLDERS, MODE_BOTH):
        for folder in folders:
            target = build_target(folder, save_root)
            target['folder_meta'] = folder
            targets.append(target)
    return targets


def ensure_utf8_console():
    if sys.platform == 'win32':
        for stream in (sys.stdout, sys.stderr):
            reconfigure = getattr(stream, 'reconfigure', None)
            if reconfigure:
                try:
                    reconfigure(encoding='utf-8')
                except Exception:
                    pass


def main():
    ensure_utf8_console()
    parser = argparse.ArgumentParser(description='下载抖音收藏/收藏夹视频并生成日志')
    parser.add_argument('--config', '-F', default='config.yml', help='配置文件路径')
    parser.add_argument('--path', '-p', help='保存目录（覆盖配置文件）')
    parser.add_argument('--number', '-n', type=int, default=0,
                        help='每个来源最多下载视频数，0 表示全部')
    parser.add_argument('--folders', type=int, default=0,
                        help='最多处理收藏夹数量，0 表示全部')
    parser.add_argument('--max-duration', type=int, default=0,
                        help=f'跳过超过此时长的视频(秒)，0 用配置或默认 {DEFAULT_MAX_DURATION_SEC}')
    parser.add_argument('--mode', choices=[MODE_FOLDERS, MODE_FAVORITES, MODE_BOTH], default='',
                        help='下载来源: folders=收藏夹, favorites=收藏视频, both=两者')
    parser.add_argument('--favorites-only', action='store_true',
                        help='仅下载「收藏的视频」，等同 --mode favorites --no-interactive')
    parser.add_argument('--all', action='store_true', help='下载全部收藏夹，跳过收藏夹交互选择')
    parser.add_argument('--folder-index', type=int, default=0,
                        help='直接指定收藏夹序号(1-based)，跳过交互')
    parser.add_argument('--no-interactive', action='store_true', help='不显示交互菜单')
    args = parser.parse_args()

    config = load_config(Path(args.config))
    if args.path:
        config['path'] = args.path
    if args.number:
        config['number']['videos'] = args.number
    if args.folders:
        config['number']['folders'] = args.folders

    max_duration = args.max_duration or config.get('max_duration_sec', DEFAULT_MAX_DURATION_SEC)

    if not apply_cookie(config):
        logger.error('未配置 Cookie。请先运行 python cookie_extractor.py 或编辑 config.yml')
        sys.exit(1)

    save_root = Path(os.path.abspath(config['path']))
    save_root.mkdir(parents=True, exist_ok=True)

    dy = Douyin(database=False)
    dl = Download(
        thread=config.get('thread', 5),
        music=config.get('music', True),
        cover=config.get('cover', True),
        avatar=config.get('avatar', False),
        resjson=config.get('json', True),
        folderstyle=config.get('folderstyle', True),
    )

    skip_interactive = bool(
        args.no_interactive or args.favorites_only or args.folder_index or args.mode or args.all
    )
    if args.favorites_only:
        mode = MODE_FAVORITES
    elif args.mode:
        mode = args.mode
    elif not skip_interactive:
        mode = prompt_download_mode()
    else:
        mode = MODE_FOLDERS

    selected_folders = []
    if mode in (MODE_FOLDERS, MODE_BOTH):
        logger.info('=' * 60)
        logger.info('开始获取收藏夹列表...')
        all_folders = dy.getCollectsList(number=config['number'].get('folders', 0))
        if not all_folders:
            if mode == MODE_FOLDERS:
                logger.error('未获取到任何收藏夹。请确认: 1) Cookie 有效  2) 账号下有收藏夹')
                sys.exit(1)
            logger.warning('未获取到收藏夹，将仅下载「收藏的视频」')
            mode = MODE_FAVORITES
        else:
            logger.info('共获取 %d 个收藏夹', len(all_folders))
            if args.folder_index:
                if 1 <= args.folder_index <= len(all_folders):
                    selected_folders = [all_folders[args.folder_index - 1]]
                    name = folder_display_name(selected_folders[0])
                    logger.info('命令行指定收藏夹: [%d] %s', args.folder_index, name)
                else:
                    logger.error('folder-index 无效，范围 1-%d', len(all_folders))
                    sys.exit(1)
            elif args.all or skip_interactive:
                selected_folders = all_folders
                logger.info('共 %d 个收藏夹，将全部下载', len(selected_folders))
            else:
                selected_folders = prompt_folder_selection(all_folders)

    targets = build_download_targets(mode, selected_folders, save_root)
    if not targets:
        logger.error('没有可下载的目标，请检查参数或 Cookie')
        sys.exit(1)

    if not skip_interactive and not args.folder_index:
        render_targets_confirm(targets)

    start = time.time()
    started_at = datetime.now().isoformat()
    entries = []
    folder_summaries = []
    total_skipped_duration = 0
    max_videos = config['number'].get('videos', 0)

    logger.info('=' * 60)
    logger.info('下载来源: %s', mode_label(mode))
    logger.info('时长过滤: 跳过 > %s 的视频', format_duration(max_duration))

    for idx, target in enumerate(targets, 1):
        kind = '收藏视频' if target['type'] == MODE_FAVORITES else '收藏夹'
        logger.info('-' * 60)
        logger.info('[%d/%d] %s: %s (id=%s)', idx, len(targets), kind, target['name'], target['id'])

        summary, skipped_count = process_download_target(
            dy, dl, target, max_videos, max_duration, entries,
        )
        folder_summaries.append(summary)
        total_skipped_duration += skipped_count

        logger.info(
            '[%s] 完成: 下载 %d, 跳过超长 %d, 失败 %d',
            target['name'], summary['success'], summary['video_skipped_duration'], summary['failed'],
        )

    duration = time.time() - start
    summary = {
        'started_at': started_at,
        'finished_at': datetime.now().isoformat(),
        'duration_seconds': round(duration, 1),
        'source_mode': mode,
        'max_duration_sec': max_duration,
        'total_targets': len(targets),
        'total_videos': len(entries),
        'skipped_duration_count': total_skipped_duration,
        'save_root': str(save_root),
        'folders': folder_summaries,
    }

    save_logs(save_root, summary, entries)

    logger.info('=' * 60)
    logger.info(
        '全部完成: %d 个下载项, 记录 %d 条, 跳过超长 %d 条, 耗时 %.0f 秒',
        len(targets), len(entries), total_skipped_duration, duration,
    )
    logger.info('文件保存目录: %s', save_root)


if __name__ == '__main__':
    main()
