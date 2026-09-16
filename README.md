# Adaptive Timeline Organizer

Adaptive Timeline is a Streamlit + FastAPI task-planning application. It combines context prediction, Jira-style priority and coarse effort signals, explicit deadline parsing, transparent urgency rules, user-confirmed importance, and an adaptive scheduler.

The application is designed to be honest about what is predicted and what remains the user's decision:

- **Model A** predicts likely working time slots and location from the task title and list/context.
- **Model B** suggests Jira-style priority labels.
- **Effort model** predicts a coarse `S/M/L` bucket and a calibrated duration range.
- **Deadline** comes only from user input or an explicit date found in task text.
- **Urgency** is rule-based.
- **Importance** remains user-authoritative.
- **Duration precedence** is user override, explicit duration in text, calibrated effort estimate, then a labelled 30-minute planning block.

## Quick start

### 1. Requirements

- Python 3.11 or newer
- Git
- A machine with enough memory for the selected Hugging Face base models
- Internet access once if the base models are not already cached

Create an isolated environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-adaptive-timeline.txt
```

### 2. Download the released checkpoints

The checkpoints are distributed as GitHub Release assets rather than Git blobs because they are hundreds of megabytes each. Download them into `models/`:

```bash
mkdir -p models
curl -L --fail --retry 3 \
  https://github.com/alihamdy135/NLP-Project/releases/download/v1.0.0/best_model_A.pt \
  -o models/best_model_A.pt
curl -L --fail --retry 3 \
  https://github.com/alihamdy135/NLP-Project/releases/download/v1.0.0/best_model_B.pt \
  -o models/best_model_B.pt
curl -L --fail --retry 3 \
  https://github.com/alihamdy135/NLP-Project/releases/download/v1.0.0/best_model_effort.pt \
  -o models/best_model_effort.pt
curl -L --fail --retry 3 \
  https://github.com/alihamdy135/NLP-Project/releases/download/v1.0.0/effort_production_config.json \
  -o models/effort_production_config.json
```

The manifest expects exactly these four files. If you store them elsewhere, set:

```bash
export ADAPTIVE_MODEL_ROOT=/absolute/path/to/models
```

The repository does **not** include the raw Jira export or other training exports. The supplied Jira sample contains embedded credentials and connection strings in issue text, so it is intentionally excluded from the public repository. Do not publish raw exports without reviewing and redacting them.

### 3. Start the API

In one terminal:

```bash
source .venv/bin/activate
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8010
```

The API is available at `http://127.0.0.1:8010`.

### 4. Start Streamlit

In a second terminal:

```bash
source .venv/bin/activate
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Open `http://127.0.0.1:8501`.

The UI uses `ADAPTIVE_API_URL` for the API address. It defaults to `http://127.0.0.1:8010`:

```bash
export ADAPTIVE_API_URL=http://127.0.0.1:8010
```

### 5. Load Hugging Face base models

By default the API uses `ADAPTIVE_HF_LOCAL_ONLY=1` and never downloads a base model silently. If the base models are not already cached, approve the download explicitly before using model inference:

```bash
export ADAPTIVE_HF_LOCAL_ONLY=0
```

Restart the API after changing this variable. Set it back to `1` for an offline/local-only deployment after the cache is populated.

## API

- `GET /health` — process, checkpoint, and model-base status.
- `GET /api/v1/metadata` — manifest, labels, provenance, and limitations.
- `POST /api/v1/tasks/analyze` — task analysis, deadline, urgency, importance, quadrant, priority, context, and effort.
- `POST /api/v1/predict/task` — compatibility alias for task analysis.
- `POST /api/v1/schedule` — schedule tasks across the selected horizon.
- `GET /docs` — interactive Swagger documentation.

Example request:

```bash
curl -X POST http://127.0.0.1:8010/api/v1/tasks/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "task_title": "Finish the project report by Friday",
    "list_title": "university",
    "description": "Write the conclusion and proofread the references.",
    "importance": true,
    "deadline": null,
    "duration_override_minutes": null
  }'
```

## Model and data boundaries

Only two sources were used for the supplied training work:

1. **MS-LaTTE** for context labels such as time and location.
2. **Jira sample data** for priority and the effort proxy.

The effort model is not a personal-task ground-truth model. Its labels use positive `timeestimate_seconds` first and positive `timespent_seconds` as fallback. Zero or non-positive values are treated as missing. The production candidate was evaluated on 1,877 labelled Jira issues and predicts `S`, `M`, or `L`; its duration is a train-only calibrated median/range. Review the range or override it for a real task.

The raw effort regression was not used for scheduling because its test R² was negative. Scheduling uses the bucket calibration instead.

## Repository layout

```text
app/                 Streamlit presentation layer and API client
backend/app/         FastAPI routes, model runtime, rules, and scheduler
config/              Manifest, provenance, and urgency policy
models/              Downloaded release artifacts; ignored by Git
tests/               Unit and API-contract tests
```

Streamlit does not load models or duplicate preprocessing. FastAPI owns model loading, preprocessing, rules, and scheduling.

## Verification

```bash
python -m compileall -q backend app tests
python -m unittest discover -s tests -v
```

## Configuration

- `ADAPTIVE_API_URL` — Streamlit-to-FastAPI URL; default `http://127.0.0.1:8010`.
- `ADAPTIVE_MODEL_ROOT` — checkpoint directory; default `./models`.
- `ADAPTIVE_DEVICE` — PyTorch device; default `cpu`.
- `ADAPTIVE_HF_LOCAL_ONLY` — `1` by default; set to `0` only to approve a Hugging Face base-model download.

No passwords, API keys, access tokens, or credentials are required by this application. Keep any local `.env` files and downloaded private data outside Git.

## Usage rights

The repository does not include a license file. Use it according to the permissions and terms that apply to the included code, model artifacts, and their upstream dependencies.
