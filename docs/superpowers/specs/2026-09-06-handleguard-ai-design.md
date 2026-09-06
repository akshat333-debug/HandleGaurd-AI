# HandleGuard AI — Prototype Design Spec

**Date:** 2026-09-06  
**Status:** Approved for implementation (source: `HandleGuard_AI_Complete_Project_Master_Plan.md`)  
**Product:** Warehouse handling video intelligence — a damage-prevention decision system, not a CCTV demo.

## 1. Goal

Convert warehouse video (upload) into explainable, reviewable, preventive operational intelligence:

1. What happened, involving whom/what, where, when
2. Why it was scored as risky, with evidence and confidence
3. Recommended corrective action (SOP-backed)
4. Supervisor replay, conversational query, false-positive correction
5. Privacy: analyse behaviour, never identity
6. At least 10 (target 12) behaviours

## 2. Architecture

Layered pipeline with injected perception (no GPU required for tests):

```text
VideoSource -> FrameSampler -> Detector(Protocol) -> Tracker
  -> TemporalFeatures -> EventGraph -> BehaviourDetectors
  -> RiskScorer -> IncidentEngine (dedup, explanation, SOP action)
  -> SQLite + FastAPI -> React Dashboard + Assistant
```

Perception is a Protocol. Production can use YOLO; tests use `StubDetector` and synthetic tracks. Core reasoning never depends on a specific model vendor.

## 3. Modules (one responsibility each)

| Package | Responsibility |
|---|---|
| `handleguard.config` | Load YAML configs (`behaviours`, `products`, `zones`, `risk_weights`, `sop_rules`) |
| `handleguard.video` | Open/read/timestamp/close; sample frames; write evidence clips |
| `handleguard.perception` | Detection types + Detector protocol + stub |
| `handleguard.tracking` | IoU greedy tracker, `TrackState` with history |
| `handleguard.features` | Geometry, velocity, acceleration, spatial relations |
| `handleguard.events` | Temporal event graph of entities and interactions |
| `handleguard.behaviours` | 12 detectors behind `BehaviourDetector.update(context)` |
| `handleguard.risk` | Separate risk 0–100 and confidence; Low/Medium/High/Critical |
| `handleguard.incidents` | Create, dedup, explain, recommend |
| `handleguard.pipeline` | Orchestrate one video into incidents |
| `handleguard.db` | SQLAlchemy models + repositories |
| `handleguard.assistant` | Tool-grounded queries + guardrails (no identity, no damage claims) |
| `handleguard.privacy` | Face-blur hook, retention policy, no worker identity |
| `apps.api` | FastAPI routes matching master-plan endpoints |
| `apps.web` | Supervisor dashboard (React + Vite + Tailwind) |

## 4. Behaviours (B01–B12)

`drop`, `throw`, `drag`, `rough_handling`, `improper_stack`, `unstable_stack`, `zone_violation`, `pallet_overhang`, `stepping`, `improper_manual_handling`, `unsafe_sequence`, `unsafe_surface`.

Thresholds live in `configs/behaviours.yaml`. Detectors return `BehaviourEvidence`; they do not persist incidents.

## 5. Risk

```text
risk = 100 * clip(
  0.35*behaviour_severity + 0.20*intensity + 0.15*fragility
  + 0.10*duration + 0.10*repeat_frequency + 0.10*location_risk
)
```

Bands: 0–24 Low, 25–49 Medium, 50–74 High, 75–100 Critical. Confidence is independent.

## 6. API

`POST/GET /api/videos`, `POST /api/videos/{id}/process`, incident CRUD + clip, analytics, assistant query, behaviour config, zones.

## 7. Testing contract

Every core function has expected input → expected output unit tests. Integration tests run synthetic detections through tracker → behaviours → risk → incident → DB → API. Regression: drop sequence must produce ≥1 DROP; gentle placement must not produce Critical.

## 8. Out of scope (prototype)

Face recognition, worker identity, punitive automation, WMS/ERP, multi-site, custom foundation-model training, claiming confirmed physical damage from video alone.

## 9. UI

Data-dense operations dashboard. Industrial slate + safety orange (`#EA580C`). Fira Sans / Fira Code. Dark+light. No emoji icons. WCAG AA contrast. Filters, KPI cards, incident table, review workflow, assistant panel.
