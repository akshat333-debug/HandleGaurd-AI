# HandleGuard AI — Next Tasks Plan

> **For agentic workers:** Execute task-by-task with TDD. Commit and push after each batch.

**Goal:** Close remaining P0/P1 prototype gaps: evidence clips, evaluation metrics, structured logging, upload security, observability, and exportable incident reports.

**Architecture:** Keep perception injectable. Clip planning, metrics, and reports are pure functions so tests never need OpenCV/GPU.

**Tech Stack:** Python 3.11, FastAPI, pytest, existing HandleGuard packages.

## Global Constraints

- No worker identity, no face recognition, no confirmed-damage claims
- Thresholds remain in YAML
- Risk and confidence stay separate
- Tests must not require YOLO or OpenCV
- FastAPI prefix `/api`

## Remaining backlog (priority)

### Batch A — Evidence + sampling (P0)
1. Frame sampler (`inference_fps`, skip closed source)
2. Clip window planner (pre 3s / post 4s) + filename
3. Attach `clip_path` on incident create

### Batch B — Evaluation metrics (P0)
4. Detection precision/recall/F1
5. Behaviour event-level TP/FP/FN with temporal overlap
6. Latency mean / p50 / p95

### Batch C — Hardening (P1)
7. Structured logger
8. Upload validation (type, size, sanitized name)
9. Observability snapshot endpoint
10. Typed pipeline errors (unsupported video, empty detections)

### Batch D — Reports + privacy hooks (P1) — done
11. Incident JSON/Markdown report export
12. Identity-redaction helper
13. Docs + checklist update

### Batch E — Ablation + adapters (P1) — done
14. Ablation runner: full vs no-tracking vs no-event-graph
15. YOLO box mapper (`YOLODetector` unbound by default)
16. Clip sidecar JSON writer + retention expiry helper

---
