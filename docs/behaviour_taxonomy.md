# Behaviour taxonomy

See `HandleGuard_AI_Complete_Project_Master_Plan.md` §3 for full definitions. Detectors implement B01–B12 with YAML thresholds in `configs/behaviours.yaml`.

Detectors return `BehaviourEvidence`. They do not persist incidents and they do not assign worker identity.

Each behaviour has a model card at `GET /api/behaviours/cards` covering what it detects, what it does not, failure conditions, camera view, minimum visibility, and calibration status.
