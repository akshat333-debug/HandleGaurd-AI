# HandleGuard AI

AI video intelligence for warehouse handling. This is a **damage-prevention decision system**, not a CCTV analytics demo.

The prototype converts warehouse video into explainable, reviewable operational intelligence: what happened, which objects were involved, where and when, why it was scored as risky, what evidence supports that conclusion, how confident the system is, and which SOP-backed corrective action to take.

## Problem

Loading and unloading damage is usually discovered after the fact. Supervisors need sequence-level handling risk, not single-frame object boxes.

## Solution

HandleGuard observes product, person, pallet, and equipment tracks over time, classifies 12 handling behaviours, scores **risk and confidence separately**, stores incidents with evidence, and supports human review plus a grounded supervisor assistant.

## Architecture

```text
Video upload / synthetic timeline
        ↓
Detector (Protocol: YOLO or StubDetector)
        ↓
IoU tracker → temporal features → event graph
        ↓
12 behaviour detectors (YAML thresholds)
        ↓
Risk engine → incident engine (dedup, explanation, SOP action)
        ↓
SQLite + FastAPI `/api` → React supervisor dashboard
```

Perception is injected. Unit and integration tests never require a GPU or YOLO weights.

## Features

- Video register + process pipeline
- 12 behaviour detectors (drop, throw, drag, rough handling, improper stack, unstable stack, zone violation, pallet overhang, stepping, improper manual handling, unsafe sequence, unsafe surface)
- Risk 0–100 and independent confidence
- Incident deduplication, explanations, SOP recommendations
- Review workflow: confirm, false positive, note, resolve
- Analytics by behaviour, risk band, and loading bay
- Tool-grounded assistant with identity / damage / punitive guardrails
- Privacy-by-design: no worker identity, no face recognition
- Evidence clip planner (3s pre / 4s post) and exportable incident reports
- Structured logs, upload validation, observability snapshot
- Ablation study (full vs no-tracking vs no-event-graph)
- YOLO box mapper behind the same Detector protocol (unbound in tests)

## Behaviours

| ID | Behaviour | Notes |
|---|---|---|
| B01 | drop | Rapid downward motion + impact/stop |
| B02 | throw | High horizontal unsupported velocity |
| B03 | drag | Floor-level horizontal translation |
| B04 | rough_handling | Acceleration / impact spike |
| B05 | improper_stack | Larger item on smaller support |
| B06 | unstable_stack | Low support ratio |
| B07 | zone_violation | Persistent restricted-zone dwell |
| B08 | pallet_overhang | Low product∩pallet fraction |
| B09 | stepping | Person footprint on product |
| B10 | improper_manual_handling | Large item, too few people, no equipment |
| B11 | unsafe_sequence | Large item moved before equipment |
| B12 | unsafe_surface | Movement through wet-floor zone |

## Technology stack

- Python 3.11, FastAPI, Pydantic, SQLAlchemy, PyYAML, pytest
- React 18, Vite, Tailwind CSS, Recharts, Lucide
- SQLite for the prototype (PostgreSQL optional)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Frontend:

```bash
cd apps/web
npm install
```

## Run

```bash
# API
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# seed synthetic incidents
python scripts/seed_demo.py

# web (proxies /api to :8000)
cd apps/web
npm run dev
```

Docker:

```bash
docker compose up --build
```

## Tests

```bash
python -m pytest tests -q
```

Unit tests cover geometry, kinematics, config, tracker, 12 behaviours, risk bands, dedup, explanations, reports, identity redaction, and assistant guardrails. Integration tests cover drop vs gentle placement, the demo timeline, and the API path `video → process → incident → review → report → analytics → assistant`.

## Dataset

This prototype ships a **synthetic detection timeline** (`handleguard/demo.py`) so the full reasoning stack can be demonstrated without annotated warehouse video. Replace `StubDetector` with a YOLO detector when camera footage is available.

## Model information

Default perception is `StubDetector` (deterministic). Production can bind Ultralytics YOLO + ByteTrack behind the same `Detector` protocol. No custom foundation model is trained.

## Evaluation

Behaviour detectors are tested with expected input/output fixtures (true drop vs gentle placement, drag vs carry, persistent vs transient zone dwell, assistant refusal cases). Risk and confidence are asserted as separate numbers. Metrics helpers compute detection P/R/F1, mAP@0.50, event temporal IoU, latency mean/p50/p95, ablation F1, and labelled avoided-loss opportunity.

## Responsible AI

- Analyses behaviour and track IDs, never worker identity
- Risk events are decision support, not proof of damage or misconduct
- Alerts require human review
- No disciplinary recommendations
- Confidence and evidence are always shown

## Limitations

- Image-space kinematics, not metric 3D
- Synthetic perception in the default demo
- Fragility is a class prior, not a measured material property
- Clip encoding requires OpenCV in production

## Roadmap

Live RTSP, fine-tuned warehouse detector, calibrated metric drop height, multi-bay deployment, and WMS hooks.

## License

MIT
