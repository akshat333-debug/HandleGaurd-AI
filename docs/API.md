# API

Base path: `/api`

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness |
| GET | `/camera/guidance` | Fixed-camera capture rules + webcam/RTSP stubs |
| GET | `/demo/annotations` | Deterministic demo behaviour JSON pack |
| GET | `/demo/clips` | Offline 12-clip catalog (filenames only; no encoded mp4s) |
| POST | `/videos` | Register video metadata |
| POST | `/videos/upload` | Upload file |
| GET | `/videos` | List |
| GET | `/videos/{id}` | Detail |
| POST | `/videos/{id}/process` | Run pipeline |
| GET | `/incidents` | Filterable list (`behaviour`, `risk_level`, `status`, `loading_bay`, `camera_id`, `start`, `end`) |
| GET | `/incidents/{id}` | Detail |
| PATCH | `/incidents/{id}` | Review workflow |
| GET | `/incidents/{id}/clip` | Clip metadata |
| GET | `/incidents/{id}/report` | JSON or `?fmt=markdown` export |
| GET | `/observability` | FPS, latency, incident/error counts |
| GET | `/metrics/ablation` | Full vs no-tracking vs no-event-graph F1 |
| GET | `/metrics/feedback` | Supervisor confirm / false-positive precision |
| GET | `/metrics/impact` | Assumed avoided-loss opportunity (labelled) |
| GET | `/metrics/errors` | False-positive error cards |
| GET | `/metrics/assistant` | Predetermined-query factuality (grounding / unsupported rates) |
| GET | `/analytics/summary` | Counts |
| GET | `/analytics/behaviours` | Behaviour histogram |
| GET | `/analytics/risk` | Risk bands |
| GET | `/analytics/bays` | Bay histogram |
| GET | `/analytics/shift` | Shift KPIs (high-risk rate, FP rate) |
| POST | `/assistant/query` | Grounded question |
| GET | `/behaviours/cards` | Behaviour model cards |
| GET/PATCH | `/config/behaviours` | Thresholds |
| GET/POST/PATCH/DELETE | `/zones` | Zone polygons |

Incident JSON always includes `risk_score`, `risk_level`, `confidence`, `explanation`, and `recommendation`.
