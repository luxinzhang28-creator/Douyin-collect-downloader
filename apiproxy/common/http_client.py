#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

_session = None


def get_http_session() -> requests.Session:
    """Shared session that ignores broken system proxy env vars."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.trust_env = False
    return _session


def http_get(*args, **kwargs):
    return get_http_session().get(*args, **kwargs)


def http_post(*args, **kwargs):
    return get_http_session().post(*args, **kwargs)
