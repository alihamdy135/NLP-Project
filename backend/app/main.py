from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import load_manifest, load_provenance
from .models import ModelRuntime
from .scheduler import Scheduler
from .schemas import AnalysisResponse, ScheduleRequest, ScheduleResponse, TaskAnalysisRequest
from .service import AnalysisService

manifest = load_manifest()
provenance = load_provenance()
runtime = ModelRuntime()
service = AnalysisService(runtime)
scheduler = Scheduler(service)

app = FastAPI(
    title='Adaptive Timeline Organizer API',
    version='1.0.0',
    description='Context-aware task analysis and transparent scheduling for the Adaptive Timeline Organizer.',
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8501', 'http://127.0.0.1:8501'],
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)


def _status_payload() -> dict:
    payload = {}
    for name, status in runtime.status().items():
        payload[name] = {
            'loaded': status.loaded,
            'artifact': status.artifact,
            'base_model': status.base_model,
            'error': status.error,
        }
    return payload


@app.get('/health')
def health() -> dict:
    statuses = _status_payload()
    artifact_ok = all(item['error'] is None for item in statuses.values())
    return {'status': 'ok' if artifact_ok else 'degraded', 'service': 'adaptive-timeline-api', 'models': statuses}


@app.get('/api/v1/metadata')
def metadata() -> dict:
    return {
        'service': 'Adaptive Timeline Organizer',
        'api_version': '1.0.0',
        'manifest_version': manifest['manifest_version'],
        'feature_schema_version': manifest['feature_schema_version'],
        'models': manifest['models'],
        'known_limitations': manifest['known_limitations'],
        'provenance': provenance,
        'runtime': _status_payload(),
    }


@app.post('/api/v1/tasks/analyze', response_model=AnalysisResponse)
def analyze_task(request: TaskAnalysisRequest) -> AnalysisResponse:
    return service.analyze(request)


@app.post('/api/v1/predict/task', response_model=AnalysisResponse)
def predict_task(request: TaskAnalysisRequest) -> AnalysisResponse:
    return service.analyze(request)


@app.post('/api/v1/schedule', response_model=ScheduleResponse)
def schedule_tasks(request: ScheduleRequest) -> ScheduleResponse:
    return scheduler.schedule(request)


@app.get('/')
def root() -> dict:
    return {'name': 'Adaptive Timeline Organizer API', 'docs': '/docs', 'health': '/health'}
