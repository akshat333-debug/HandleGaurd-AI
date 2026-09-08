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

### Batch F — Feedback + privacy hooks (P1) — done
17. Review-label precision (`GET /api/metrics/feedback`)
18. Face-blur passthrough hook
19. Write clip sidecar on video process

### Batch G — Evaluation extras (P1) — done
20. mAP@0.50 from IoU-matched boxes
21. Leakage-safe session split (70/15/15 by recording session)
22. Overlay plan + false-positive error cards + labelled avoided-loss

### Batch H — Annotations + model cards (P1) — done
23. Behaviour annotation JSON parse/serialize
24. Product-class aliases (`box`→`carton`, `pallet_truck`→`pallet_jack`)
25. Behaviour model cards + labelled image-space calibration

### Batch I — Camera + empty video (P1) — done
26. Camera guidance document/API
27. Empty detections raise `EmptyDetectionsError`
28. WebcamSource stub (not bound in tests)

### Batch J — Filters + shift KPIs (P1) — done
29. Filter incidents by loading bay and created-at range
30. Shift KPI: high-risk per 100 handling actions + FP rate

### Batch K — Cards + RTSP stub (P1/P2) — done
31. Specific model cards for all 12 behaviours
32. RtspSource stub (not bound in tests)
33. Dashboard shift KPI panel

---
