# Architecture

HandleGuard is a layered monorepo. Each package has one job and talks through typed dataclasses.

## Runtime flow

1. `apps.api` accepts a video row (upload or metadata).
2. `HandleGuardPipeline` pulls detections from a `Detector` implementation.
3. `IoUTracker` assigns stable IDs and bounded history.
4. `build_event_graph` records handling / support / stack relations.
5. Twelve `BehaviourDetector` implementations emit `BehaviourEvidence`.
6. `IncidentEngine` scores risk, deduplicates, explains, and stores SOP actions.
7. SQLAlchemy repositories persist to SQLite.
8. React dashboard and the assistant read only stored incidents.

## Module map

| Path | Responsibility |
|---|---|
| `handleguard/config` | YAML loaders |
| `handleguard/features` | Geometry, kinematics, zones |
| `handleguard/perception` | Detector protocol + stub |
| `handleguard/tracking` | Greedy IoU tracker |
| `handleguard/events` | Temporal event graph |
| `handleguard/behaviours` | 12 detectors |
| `handleguard/risk` | Separate risk vs confidence |
| `handleguard/incidents` | Dedup, explain, recommend |
| `handleguard/pipeline` | Orchestration |
| `handleguard/db` | Models + repositories |
| `handleguard/assistant` | Grounded Q&A + guardrails |
| `apps/api` | FastAPI |
| `apps/web` | Supervisor UI |

## Design rules

- Thresholds live in `configs/*.yaml`
- Tests inject `StubDetector`; they do not download weights
- Risk and confidence are never collapsed into one number
- Assistant answers cite incident IDs or refuse
