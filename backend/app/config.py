from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = Path(os.getenv('ADAPTIVE_MODEL_ROOT', str(PROJECT_ROOT / 'models')))
MANIFEST_PATH = PROJECT_ROOT / 'config' / 'model_manifest.json'
POLICY_PATH = PROJECT_ROOT / 'config' / 'urgency_policy.json'
PROVENANCE_PATH = PROJECT_ROOT / 'config' / 'artifact_provenance.json'
DEVICE = os.getenv('ADAPTIVE_DEVICE', 'cpu')
HF_LOCAL_ONLY = os.getenv('ADAPTIVE_HF_LOCAL_ONLY', '1').lower() not in {'0', 'false', 'no'}


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding='utf-8'))


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))


def load_provenance() -> dict:
    return json.loads(PROVENANCE_PATH.read_text(encoding='utf-8'))
