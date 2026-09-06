# Behaviour taxonomy

See `HandleGuard_AI_Complete_Project_Master_Plan.md` §3 for full definitions. Detectors implement B01–B12 with YAML thresholds in `configs/behaviours.yaml`.

Detectors return `BehaviourEvidence`. They do not persist incidents and they do not assign worker identity.
