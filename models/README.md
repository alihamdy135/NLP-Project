# Model artifacts

This directory is intentionally ignored by Git. Download the four runtime artifacts from the `v1.0.0` GitHub Release and place them here:

- `best_model_A.pt`
- `best_model_B.pt`
- `best_model_effort.pt`
- `effort_production_config.json`

The runtime manifest and `backend/app/config.py` use this directory by default. Override it with `ADAPTIVE_MODEL_ROOT` if needed.
