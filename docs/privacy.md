# Privacy

HandleGuard analyses handling behaviour, not people.

- No face recognition
- No worker names or employee IDs
- Track IDs reset per video
- `store_worker_identity` must remain false
- Optional face blur when OpenCV is available; otherwise `blur_faces()` is a no-op passthrough
- Retention defaults: full video 7 days, incident clips 30 days
- Assistant refuses identity, confirmed-damage, and punitive prompts
- `redact_identity()` strips `worker_name`, `employee_id`, `face_id` and similar keys from reports
- Incident exports include an explicit "not confirmed damage / no worker identity" disclaimer
