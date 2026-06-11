#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from typing import Dict, List, Optional


def find_chrome_executable() -> Optional[str]:
    """Find installed Google Chrome on the current system."""
    candidates: List[str] = []
    env_path = os.environ.get('CHROME_PATH', '').strip()
    if env_path:
        candidates.append(env_path)

    if os.name == 'nt':
        candidates.extend([
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            os.path.join(
                os.environ.get('LOCALAPPDATA', ''),
                'Google', 'Chrome', 'Application', 'chrome.exe',
            ),
        ])
    elif sys.platform == 'darwin':
        candidates.append(
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        )
    else:
        candidates.extend([
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium-browser',
        ])

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def get_chromium_launch_kwargs(
    headless: bool = False,
    extra_args: Optional[List[str]] = None,
) -> Dict:
    """Build Playwright launch kwargs, preferring system Chrome over bundled Chromium."""
    args = ['--disable-blink-features=AutomationControlled']
    if extra_args:
        args.extend(extra_args)

    kwargs: Dict = {'headless': headless, 'args': args}
    chrome_path = find_chrome_executable()
    if chrome_path:
        kwargs['executable_path'] = chrome_path
    else:
        kwargs['channel'] = 'chrome'
    return kwargs
