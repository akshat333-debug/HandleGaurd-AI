# Risk model

Risk and confidence are separate.

```
risk = 100 * clip(
  0.35 * behaviour_severity
  + 0.20 * intensity
  + 0.15 * product_fragility
  + 0.10 * duration
  + 0.10 * repeat_frequency
  + 0.10 * location_risk
)
```

Bands: 0–24 Low, 25–49 Medium, 50–74 High, 75–100 Critical.

Confidence is `clip(0.35 + 0.65 * evidence.raw_score)` and is displayed independently.

Weights: `configs/risk_weights.yaml`. Product priors: `configs/products.yaml`.
