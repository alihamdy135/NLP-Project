from __future__ import annotations

import os
from typing import Any

import httpx

API_URL = os.getenv('ADAPTIVE_API_URL', 'http://127.0.0.1:8010').rstrip('/')


class APIError(RuntimeError):
    pass


def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        with httpx.Client(base_url=API_URL, timeout=90.0) as client:
            response = client.request(method, path, json=payload)
        if response.status_code >= 400:
            try:
                detail = response.json().get('detail', response.text)
            except Exception:
                detail = response.text
            raise APIError(f'{response.status_code}: {detail}')
        return response.json()
    except httpx.HTTPError as exc:
        raise APIError(f'API is unreachable at {API_URL}: {exc}') from exc


def get_health() -> dict[str, Any]:
    return _request('GET', '/health')


def get_metadata() -> dict[str, Any]:
    return _request('GET', '/api/v1/metadata')


def analyze_task(payload: dict[str, Any]) -> dict[str, Any]:
    return _request('POST', '/api/v1/tasks/analyze', payload)


def schedule_tasks(payload: dict[str, Any]) -> dict[str, Any]:
    return _request('POST', '/api/v1/schedule', payload)
