#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从已下载的抖音视频中提取口播文案（语音转文字）。

两种引擎:
  whisper  - 需 Python 3.9+，pip install -r requirements-transcript.txt
  vosk     - 支持 Python 3.8，pip install -r requirements-transcript-vosk.txt

两种文案:
  desc              - 发布标题（下载时已在 *_result.json 里）
  spoken_transcript - 口播全文（本脚本从音频识别后写入 JSON 和 *_transcript.txt）

用法:
  # 处理全部收藏夹（推荐）
  python extract_transcript.py --backend vosk --path "./Downloaded/collects"

  # 只处理某个收藏夹
  python extract_transcript.py --backend vosk --path "./Downloaded/collects/视频"

  # 强制重新识别所有视频
  python extract_transcript.py --backend vosk --path "./Downloaded/collects" --force
"""

import argparse
import csv
import json
import logging
import re
import shutil
import subprocess
import sys
import time
import wave
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import urlretrieve

import yaml

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('extract_transcript')

VOSK_MODEL_NAME = 'vosk-model-small-cn-0.22'
# 优先国内镜像，官方源放最后
VOSK_MODEL_URLS = [
    'https://ghproxy.net/https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip',
    'https://mirror.ghproxy.com/https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip',
    'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip',
]
MIN_TRANSCRIPT_LEN = 20


def load_default_path(config_path: Path) -> Path:
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
        return Path(cfg.get('path', './Downloaded/collects/'))
    return Path('./Downloaded/collects/')


def default_backend(requested: Optional[str]) -> str:
    if requested:
        return requested
    return 'vosk' if sys.version_info < (3, 9) else 'whisper'


def resolve_media_targets(path: Path) -> Tuple[Path, List[Path]]:
    path = path.resolve()
    if path.is_file():
        if path.suffix.lower() not in {'.mp4', '.mp3', '.wav', '.m4a'}:
            return path.parent, []
        csv_root = path.parent.parent.parent if path.parent.parent.parent.exists() else path.parent.parent
        return csv_root, [path]
    if not path.is_dir():
        return path, []
    videos = sorted(path.rglob('*_video.mp4'))
    if videos:
        return path, videos
    return path, sorted(path.rglob('*.mp4'))


def find_audio_fallback(video_path: Path) -> Optional[Path]:
    for mp3 in sorted(video_path.parent.glob('*_music_*.mp3')):
        return mp3
    return None


def load_metadata(video_path: Path) -> Dict:
    meta = {
        'aweme_id': '', 'author': '', 'caption': '',
        'create_time': '', 'url': '',
    }
    for json_path in sorted(video_path.parent.glob('*_result.json')):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            meta['aweme_id'] = str(data.get('aweme_id', ''))
            meta['author'] = data.get('author', {}).get('nickname', '')
            meta['caption'] = data.get('desc', '')
            meta['create_time'] = data.get('create_time', '')
            if meta['aweme_id']:
                meta['url'] = f"https://www.douyin.com/video/{meta['aweme_id']}"
        except Exception:
            pass
        break
    return meta


def collect_folder_name(video_path: Path, root: Path) -> str:
    try:
        rel = video_path.parent.relative_to(root)
        return rel.parts[0] if rel.parts else ''
    except ValueError:
        return ''


def format_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds % 1) * 1000))
    return f'{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}'


def normalize_transcript(text: str) -> str:
    """Fix vosk Chinese output (spaces between characters)."""
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', line)
        lines.append(line)
    return '\n'.join(lines)


def find_result_json(video_path: Path) -> Optional[Path]:
    for json_path in sorted(video_path.parent.glob('*_result.json')):
        return json_path
    return None


def read_spoken_from_json(json_path: Optional[Path]) -> str:
    if not json_path or not json_path.exists():
        return ''
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return (data.get('spoken_transcript') or '').strip()
    except Exception:
        return ''


def update_result_json(json_path: Path, transcript: str, backend: str):
    """Write spoken transcript into result.json (desc remains post caption)."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['spoken_transcript'] = transcript
    data['transcript_engine'] = backend
    data['transcript_updated_at'] = datetime.now().isoformat()
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def should_skip(json_path: Optional[Path], txt_path: Path, force: bool) -> bool:
    if force:
        return False
    spoken = read_spoken_from_json(json_path)
    if len(spoken) >= MIN_TRANSCRIPT_LEN:
        return True
    if txt_path.exists():
        try:
            if len(txt_path.read_text(encoding='utf-8').strip()) >= MIN_TRANSCRIPT_LEN:
                return False  # has txt but json missing -> sync or re-run
        except Exception:
            pass
    return False


def save_transcript_outputs(
    video_path: Path, stem: str, transcript: str, backend: str,
    segments, srt_path: Path, no_srt: bool,
):
    txt_path = video_path.parent / f'{stem}_transcript.txt'
    txt_path.write_text(transcript, encoding='utf-8')
    if not no_srt and segments:
        write_srt_from_segments(segments, srt_path)
    json_path = find_result_json(video_path)
    if json_path:
        update_result_json(json_path, transcript, backend)
        logger.info('已写入 JSON: %s (字段 spoken_transcript)', json_path.name)
    return txt_path


def write_srt_from_segments(segments, path: Path):
    with open(path, 'w', encoding='utf-8') as f:
        for idx, seg in enumerate(segments, 1):
            text = (getattr(seg, 'text', None) or seg.get('text', '')).strip()
            if not text:
                continue
            start = getattr(seg, 'start', seg.get('start', 0))
            end = getattr(seg, 'end', seg.get('end', start + 1))
            f.write(f'{idx}\n')
            f.write(f'{format_srt_time(start)} --> {format_srt_time(end)}\n')
            f.write(f'{text}\n\n')


def save_summary_csv(root: Path, rows: List[Dict]):
    if not rows:
        return
    fieldnames = [
        'folder', 'aweme_id', 'create_time', 'author', 'caption',
        'transcript', 'transcript_file', 'srt_file', 'media_file', 'url', 'processed_at',
    ]
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    for name in (f'all_transcripts_{ts}.csv', 'all_transcripts_latest.csv'):
        out = root / name
        with open(out, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        logger.info('汇总已保存: %s', out)


def find_ffmpeg() -> str:
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        return ffmpeg
    raise RuntimeError('未找到 ffmpeg，请确认已安装并加入 PATH')


def ffprobe_duration(media_path: Path) -> float:
    ffprobe = shutil.which('ffprobe')
    if not ffprobe:
        return 0.0
    cmd = [
        ffprobe, '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(media_path),
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            return float(out.stdout.strip())
    except Exception:
        pass
    return 0.0


def pick_media_source(video_path: Path) -> Path:
    """Prefer mp3 (smaller, faster decode) over full mp4."""
    mp3 = find_audio_fallback(video_path)
    return mp3 if mp3 else video_path


def get_media_duration_sec(video_path: Path, json_path: Optional[Path]) -> float:
    if json_path and json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('duration_sec'):
                return float(data['duration_sec'])
            if data.get('duration_ms'):
                return float(data['duration_ms']) / 1000.0
        except Exception:
            pass
    media = pick_media_source(video_path)
    return ffprobe_duration(media)


def media_to_wav(media_path: Path, wav_path: Path):
    cmd = [
        find_ffmpeg(), '-y', '-loglevel', 'error', '-nostats',
        '-threads', '0', '-i', str(media_path),
        '-vn', '-ac', '1', '-ar', '16000', '-f', 'wav', str(wav_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-500:] if result.stderr else 'ffmpeg 转换失败')


def ensure_vosk_model(model_dir: Path) -> Path:
    target = model_dir / VOSK_MODEL_NAME
    if target.exists() and any(target.iterdir()):
        return target

    model_dir.mkdir(parents=True, exist_ok=True)
    zip_path = model_dir / f'{VOSK_MODEL_NAME}.zip'
    logger.info('首次使用需下载中文语音模型（约 42MB）...')

    for url in VOSK_MODEL_URLS:
        try:
            logger.info('下载: %s', url)
            urlretrieve(url, str(zip_path))
            break
        except Exception as e:
            logger.warning('下载失败: %s', e)
    else:
        raise RuntimeError(
            '模型下载失败。请手动下载解压到 models 目录:\n'
            f'  {VOSK_MODEL_URLS[-1]}\n'
            f'  解压后路径应为: {target}'
        )

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(model_dir)
    zip_path.unlink(missing_ok=True)
    logger.info('模型已就绪: %s', target)
    return target


class VoskEngine:
    def __init__(self, model_path: Path, need_words: bool = False):
        from vosk import Model, KaldiRecognizer
        self._Model = Model
        self._KaldiRecognizer = KaldiRecognizer
        self.need_words = need_words
        self.model = Model(str(model_path))

    def transcribe(self, media_path: Path, language: str = 'zh'):
        wav_path = media_path.parent / f'._{media_path.stem}_16k.wav'
        try:
            media_to_wav(media_path, wav_path)
            with wave.open(str(wav_path), 'rb') as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                    raise RuntimeError('wav 格式异常')
                rec = self._KaldiRecognizer(self.model, wf.getframerate())
                if self.need_words:
                    rec.SetWords(True)
                parts = []
                segments = []
                # 1 秒块读取，减少 Python 循环次数
                chunk = wf.getframerate()
                while True:
                    data = wf.readframes(chunk)
                    if not data:
                        break
                    if rec.AcceptWaveform(data):
                        r = json.loads(rec.Result())
                        t = (r.get('text') or '').strip()
                        if t:
                            parts.append(t)
                            if self.need_words:
                                for w in r.get('result', []):
                                    segments.append({
                                        'text': w.get('word', ''),
                                        'start': w.get('start', 0),
                                        'end': w.get('end', 0),
                                    })
                r = json.loads(rec.FinalResult())
                t = (r.get('text') or '').strip()
                if t:
                    parts.append(t)
                text = normalize_transcript('\n'.join(parts))
                duration = wf.getnframes() / float(wf.getframerate())
                info = type('Info', (), {'language': language, 'duration': duration})()
                return text, segments, info
        finally:
            wav_path.unlink(missing_ok=True)


class WhisperEngine:
    def __init__(self, model_name: str, device: str, compute_type: str):
        from faster_whisper import WhisperModel
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)

    def transcribe(self, media_path: Path, language: str = 'zh'):
        segments_iter, info = self.model.transcribe(
            str(media_path),
            language=language,
            vad_filter=True,
            beam_size=3,
            best_of=1,
        )
        segment_list = list(segments_iter)
        text = '\n'.join((s.text or '').strip() for s in segment_list if (s.text or '').strip())
        return text, segment_list, info


def create_engine(args):
    backend = default_backend(args.backend)
    need_words = not args.no_srt
    if backend == 'vosk':
        try:
            import vosk  # noqa: F401
        except ImportError:
            logger.error('未安装 vosk，请执行:')
            logger.error('  pip install -r requirements-transcript-vosk.txt -i https://pypi.tuna.tsinghua.edu.cn/simple')
            sys.exit(1)
        model_path = ensure_vosk_model(Path('models'))
        logger.info('使用 Vosk 引擎 (优先 mp3, %s)', '含时间轴' if need_words else '纯文本加速')
        return VoskEngine(model_path, need_words=need_words), backend

    if sys.version_info < (3, 9):
        logger.error('whisper 引擎需要 Python 3.9+，请使用: --backend vosk')
        sys.exit(1)
    try:
        from faster_whisper import WhisperModel  # noqa: F401
    except ImportError:
        logger.error('未安装 faster-whisper，请执行:')
        logger.error('  pip install -r requirements-transcript.txt -i https://pypi.tuna.tsinghua.edu.cn/simple')
        logger.error('或使用: --backend vosk')
        sys.exit(1)

    device = args.device
    if device == 'auto':
        try:
            import ctranslate2
            device = 'cuda' if ctranslate2.get_cuda_device_count() > 0 else 'cpu'
        except Exception:
            device = 'cpu'
    compute = 'float16' if device == 'cuda' else 'int8'
    model_name = args.model or ('medium' if device == 'cuda' else 'small')
    logger.info('使用 Whisper 引擎: %s (%s)', model_name, device)
    return WhisperEngine(model_name, device, compute), backend


def main():
    parser = argparse.ArgumentParser(description='提取抖音视频口播文案')
    parser.add_argument('--path', '-p', help='已下载视频根目录（含空格请加双引号）')
    parser.add_argument('--file', '-f', help='只处理单个视频/音频文件')
    parser.add_argument('--config', '-F', default='config.yml')
    parser.add_argument('--backend', '-b', choices=['vosk', 'whisper'], help='识别引擎，默认 py38=vosk')
    parser.add_argument('--model', '-m', help='Whisper 模型名（仅 whisper）')
    parser.add_argument('--device', '-d', default='auto', choices=['auto', 'cpu', 'cuda'])
    parser.add_argument('--language', '-l', default='zh')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--no-srt', action='store_true', help='不生成 srt（Vosk 可明显加速）')
    parser.add_argument('--max-duration', type=int, default=0,
                        help='跳过超过此时长的视频(秒)，0 表示不限制，建议 7200')
    args = parser.parse_args()

    if args.file:
        target = Path(args.file)
    elif args.path:
        target = Path(args.path)
    else:
        target = load_default_path(Path(args.config))

    if not target.exists():
        logger.error('路径不存在: %s', target)
        sys.exit(1)

    root, media_files = resolve_media_targets(target)
    if not media_files:
        logger.error('未找到视频文件')
        sys.exit(1)

    engine, backend = create_engine(args)
    logger.info('待处理 %d 个文件', len(media_files))

    rows, skipped, success, failed = [], 0, 0, 0
    start = time.time()

    for idx, video_path in enumerate(media_files, 1):
        stem = video_path.stem
        if stem.endswith('_video'):
            stem = stem[:-6]
        txt_path = video_path.parent / f'{stem}_transcript.txt'
        srt_path = video_path.parent / f'{stem}_transcript.srt'
        meta = load_metadata(video_path)
        folder = collect_folder_name(video_path, root)

        json_path = find_result_json(video_path)

        if args.max_duration > 0:
            dur = get_media_duration_sec(video_path, json_path)
            if dur > args.max_duration:
                logger.warning(
                    '[%d/%d] 跳过(超长 %.0fs): %s',
                    idx, len(media_files), dur, video_path.name,
                )
                skipped += 1
                rows.append(_row(folder, meta, '', txt_path, srt_path, video_path, 'skipped_duration'))
                continue

        if should_skip(json_path, txt_path, args.force):
            logger.info('[%d/%d] 跳过（JSON 已有口播）: %s', idx, len(media_files), video_path.name)
            skipped += 1
            transcript = read_spoken_from_json(json_path)
            rows.append(_row(folder, meta, transcript, txt_path, srt_path, video_path, 'skipped'))
            continue

        # txt 已有但 JSON 未写入：仅同步，不重新识别
        if txt_path.exists() and not args.force and json_path:
            raw = txt_path.read_text(encoding='utf-8').strip()
            if len(raw) >= MIN_TRANSCRIPT_LEN and not read_spoken_from_json(json_path):
                transcript = normalize_transcript(raw)
                save_transcript_outputs(
                    video_path, stem, transcript, backend, [], srt_path, args.no_srt,
                )
                logger.info('[%d/%d] 已同步 txt -> JSON: %s', idx, len(media_files), video_path.name)
                success += 1
                rows.append(_row(folder, meta, transcript, txt_path, srt_path, video_path, 'synced'))
                continue

        media = pick_media_source(video_path)
        if media != video_path:
            logger.info('[%d/%d] 使用音频轨: %s', idx, len(media_files), media.name)
        logger.info('[%d/%d] 语音识别中: %s', idx, len(media_files), video_path.name)
        try:
            transcript, segments, info = engine.transcribe(media, args.language)
            if backend == 'vosk':
                transcript = normalize_transcript(transcript)
        except Exception as err:
            if media != video_path:
                logger.warning('音频识别失败，改用视频: %s', err)
                try:
                    transcript, segments, info = engine.transcribe(video_path, args.language)
                    if backend == 'vosk':
                        transcript = normalize_transcript(transcript)
                    media = video_path
                except Exception as e2:
                    logger.error('识别失败: %s', e2)
                    failed += 1
                    continue
            else:
                fallback = find_audio_fallback(video_path)
                if fallback:
                    logger.warning('改用音频: %s', fallback.name)
                    try:
                        transcript, segments, info = engine.transcribe(fallback, args.language)
                        if backend == 'vosk':
                            transcript = normalize_transcript(transcript)
                        media = fallback
                    except Exception as e2:
                        logger.error('识别失败: %s', e2)
                        failed += 1
                        continue
                else:
                    logger.error('识别失败: %s', err)
                    failed += 1
                    continue

        save_transcript_outputs(
            video_path, stem, transcript, backend, segments, srt_path, args.no_srt,
        )
        logger.info('完成 (字数=%d, 时长=%.0fs)', len(transcript), getattr(info, 'duration', 0) or 0)
        success += 1
        rows.append(_row(folder, meta, transcript, txt_path, srt_path, media, datetime.now().isoformat()))

    save_summary_csv(root, rows)
    logger.info('=' * 60)
    logger.info('处理完成: 成功 %d, 跳过 %d, 失败 %d, 耗时 %.0f 秒',
                success, skipped, failed, time.time() - start)


def _row(folder, meta, transcript, txt_path, srt_path, media, processed_at):
    return {
        'folder': folder,
        'aweme_id': meta['aweme_id'],
        'create_time': meta['create_time'],
        'author': meta['author'],
        'caption': meta['caption'],
        'transcript': transcript,
        'transcript_file': str(txt_path),
        'srt_file': str(srt_path) if srt_path.exists() else '',
        'media_file': str(media),
        'url': meta['url'],
        'processed_at': processed_at,
    }


if __name__ == '__main__':
    main()
