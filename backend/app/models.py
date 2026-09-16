from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModel, AutoTokenizer

from .config import DEVICE, HF_LOCAL_ONLY, MODEL_ROOT, load_manifest


class ModelNotReady(RuntimeError):
    pass


class MultiHeadModelA(torch.nn.Module):
    def __init__(self, model_name: str, num_time_classes: int, num_loc_classes: int):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name, local_files_only=HF_LOCAL_ONLY)
        hidden_size = self.encoder.config.hidden_size
        self.dropout = torch.nn.Dropout(0.2)
        self.time_head = torch.nn.Linear(hidden_size, num_time_classes)
        self.loc_head = torch.nn.Linear(hidden_size, num_loc_classes)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, **_: torch.Tensor):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        mask = attention_mask.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        pooled = (outputs.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
        pooled = self.dropout(pooled)
        return self.time_head(pooled), self.loc_head(pooled)


class ModelBClassifier(torch.nn.Module):
    def __init__(self, model_name: str, num_classes: int):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name, local_files_only=HF_LOCAL_ONLY)
        hidden_size = self.encoder.config.hidden_size
        self.dropout = torch.nn.Dropout(0.2)
        self.classifier = torch.nn.Linear(hidden_size, num_classes)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, **_: torch.Tensor):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        mask = attention_mask.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        pooled = (outputs.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
        return self.classifier(self.dropout(pooled))


class ModelBEffortBucketClassifier(torch.nn.Module):
    def __init__(self, model_name: str, num_classes: int):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name, local_files_only=HF_LOCAL_ONLY)
        hidden_size = self.encoder.config.hidden_size
        self.dropout = torch.nn.Dropout(0.2)
        self.classifier = torch.nn.Linear(hidden_size, num_classes)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, **_: torch.Tensor):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        mask = attention_mask.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        pooled = (outputs.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
        return self.classifier(self.dropout(pooled))


@dataclass
class RuntimeModelStatus:
    loaded: bool
    artifact: str
    base_model: str
    error: str | None = None


class ModelRuntime:
    def __init__(self, model_root: Path = MODEL_ROOT):
        self.model_root = Path(model_root)
        self.manifest = load_manifest()
        self.device = torch.device(DEVICE)
        self._model_a = None
        self._tokenizer_a = None
        self._model_b = None
        self._tokenizer_b = None
        self._model_effort = None
        self._tokenizer_effort = None
        self._effort_config: dict[str, Any] = {}
        self._errors: dict[str, str] = {}

    def _artifact(self, name: str) -> Path:
        return self.model_root / self.manifest['models'][name]['artifact']

    def status(self) -> dict[str, RuntimeModelStatus]:
        result = {}
        for name in ('context', 'priority', 'effort'):
            item = self.manifest['models'][name]
            error = self._errors.get(name)
            loaded = {
                'context': self._model_a is not None,
                'priority': self._model_b is not None,
                'effort': self._model_effort is not None,
            }[name]
            result[name] = RuntimeModelStatus(
                loaded=loaded,
                artifact=str(self._artifact(name)),
                base_model=item['base_model'],
                error=error or (None if self._artifact(name).is_file() else 'checkpoint file not found'),
            )
        return result

    def _load_context(self):
        if self._model_a is not None:
            return
        spec = self.manifest['models']['context']
        try:
            checkpoint_path = self._artifact('context')
            if not checkpoint_path.is_file():
                raise ModelNotReady(f'Model A checkpoint not found: {checkpoint_path}')
            self._tokenizer_a = AutoTokenizer.from_pretrained(spec['tokenizer'], local_files_only=HF_LOCAL_ONLY)
            checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=True)
            self._model_a = MultiHeadModelA(spec['base_model'], len(spec['time_labels']), len(spec['location_labels']))
            self._model_a.load_state_dict(checkpoint, strict=True)
            self._model_a.to(self.device).eval()
        except Exception as exc:
            self._errors['context'] = f'{type(exc).__name__}: {exc}'
            raise ModelNotReady(self._errors['context']) from exc

    def _load_priority(self):
        if self._model_b is not None:
            return
        spec = self.manifest['models']['priority']
        try:
            checkpoint_path = self._artifact('priority')
            if not checkpoint_path.is_file():
                raise ModelNotReady(f'Model B checkpoint not found: {checkpoint_path}')
            self._tokenizer_b = AutoTokenizer.from_pretrained(spec['tokenizer'], local_files_only=HF_LOCAL_ONLY)
            checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=True)
            self._model_b = ModelBClassifier(spec['base_model'], len(spec['labels']))
            self._model_b.load_state_dict(checkpoint, strict=True)
            self._model_b.to(self.device).eval()
        except Exception as exc:
            self._errors['priority'] = f'{type(exc).__name__}: {exc}'
            raise ModelNotReady(self._errors['priority']) from exc

    def _load_effort(self):
        if self._model_effort is not None:
            return
        spec = self.manifest['models']['effort']
        try:
            checkpoint_path = self._artifact('effort')
            config_path = self.model_root / spec['config_artifact']
            if not checkpoint_path.is_file():
                raise ModelNotReady(f'Effort checkpoint not found: {checkpoint_path}')
            if not config_path.is_file():
                raise ModelNotReady(f'Effort configuration not found: {config_path}')
            self._effort_config = json.loads(config_path.read_text(encoding='utf-8'))
            if self._effort_config.get('deployment_status') != 'candidate':
                raise ModelNotReady('Effort candidate is held by its deployment gate.')
            self._tokenizer_effort = AutoTokenizer.from_pretrained(spec['tokenizer'], local_files_only=HF_LOCAL_ONLY)
            checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
            self._model_effort = ModelBEffortBucketClassifier(spec['base_model'], len(spec['labels']))
            self._model_effort.load_state_dict(checkpoint['state_dict'], strict=True)
            self._model_effort.to(self.device).eval()
        except Exception as exc:
            self._errors['effort'] = f'{type(exc).__name__}: {exc}'
            raise ModelNotReady(self._errors['effort']) from exc

    def predict_effort(self, text: str) -> dict[str, Any]:
        self._load_effort()
        spec = self.manifest['models']['effort']
        encoding = self._tokenizer_effort(text, truncation=True, padding='max_length', max_length=spec.get('max_length', 64), return_tensors='pt')
        encoding = {key: value.to(self.device) for key, value in encoding.items()}
        with torch.inference_mode():
            logits = self._model_effort(**encoding)
            probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()
        items = [
            {'label': label, 'probability': round(float(prob), 6)}
            for label, prob in zip(spec['labels'], probabilities)
        ]
        items.sort(key=lambda item: item['probability'], reverse=True)
        label = items[0]['label']
        calibration = self._effort_config.get('duration_calibration', {}).get(label, {})
        median = calibration.get('median_minutes')
        if median is None:
            raise ModelNotReady(f'No duration calibration is available for effort bucket {label}.')
        return {
            'status': 'ready',
            'bucket': label,
            'difficulty': spec.get('difficulty_map', {}).get(label, {'S': 'easy', 'M': 'medium', 'L': 'hard'}[label]),
            'probability': items[0]['probability'],
            'probabilities': items,
            'estimated_minutes': int(round(median)),
            'estimated_range_minutes': {
                'low': int(round(calibration.get('p25_minutes', median))),
                'high': int(round(calibration.get('p75_minutes', median))),
            },
            'source': 'jira_effort_bucket_model',
            'proxy_domain': 'Jira software issues',
        }

    def predict_context(self, task_title: str, list_title: str) -> dict[str, Any]:
        self._load_context()
        spec = self.manifest['models']['context']
        input_text = f'{task_title} [SEP] {list_title}'
        encoding = self._tokenizer_a(input_text, truncation=True, padding='max_length', max_length=64, return_tensors='pt')
        encoding = {key: value.to(self.device) for key, value in encoding.items()}
        with torch.inference_mode():
            time_logits, location_logits = self._model_a(**encoding)
            time_probs = torch.sigmoid(time_logits).squeeze(0).cpu().tolist()
            location_probs = torch.softmax(location_logits, dim=1).squeeze(0).cpu().tolist()
        thresholds = spec.get('thresholds', [0.5] * len(spec['time_labels']))
        slots = [
            {'label': label, 'probability': round(float(prob), 6)}
            for label, prob, threshold in zip(spec['time_labels'], time_probs, thresholds)
            if prob >= threshold
        ]
        if not slots:
            best = max(zip(spec['time_labels'], time_probs), key=lambda pair: pair[1])
            slots = [{'label': best[0], 'probability': round(float(best[1]), 6)}]
        slots.sort(key=lambda item: item['probability'], reverse=True)
        best_location = max(enumerate(location_probs), key=lambda pair: pair[1])
        return {
            'input_text': input_text,
            'time_slots': slots[:5],
            'location': {'label': spec['location_labels'][best_location[0]], 'probability': round(float(best_location[1]), 6)},
        }

    def predict_priority(self, text: str) -> dict[str, Any]:
        self._load_priority()
        spec = self.manifest['models']['priority']
        encoding = self._tokenizer_b(text, truncation=True, padding='max_length', max_length=64, return_tensors='pt')
        encoding = {key: value.to(self.device) for key, value in encoding.items()}
        with torch.inference_mode():
            logits = self._model_b(**encoding)
            probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()
        items = [
            {'label': label, 'probability': round(float(prob), 6)}
            for label, prob in zip(spec['labels'], probabilities)
        ]
        items.sort(key=lambda item: item['probability'], reverse=True)
        return {'label': items[0]['label'], 'probability': items[0]['probability'], 'probabilities': items}
