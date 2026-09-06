from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config {path} must be a mapping")
    return data


@dataclass
class AppConfig:
    behaviours: dict[str, Any]
    products: dict[str, Any]
    zones: dict[str, Any]
    risk_weights: dict[str, Any]
    sop_rules: dict[str, Any]
    video: dict[str, Any] = field(default_factory=dict)
    config_dir: Path = DEFAULT_CONFIG_DIR

    def behaviour(self, name: str) -> dict[str, Any]:
        cfg = self.behaviours.get(name)
        if not isinstance(cfg, dict):
            raise KeyError(f"Unknown behaviour config: {name}")
        return cfg

    def product_meta(self, class_name: str) -> dict[str, Any]:
        catalog = self.products.get("products", self.products)
        default = catalog.get("default", {"fragility": 0.4, "large": False})
        return catalog.get(class_name.lower(), default)

    def sop(self, behaviour: str) -> dict[str, str]:
        rule = self.sop_rules.get(behaviour, {})
        return {
            "rule_text": str(rule.get("rule_text", "")).strip(),
            "recommendation": str(rule.get("recommendation", "")).strip(),
        }

    def dedup_window(self, behaviour: str) -> float:
        table = self.behaviours.get("dedup", {})
        return float(table.get(behaviour, 4))


def load_config(config_dir: Path | str | None = None) -> AppConfig:
    root = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
    video_cfg = _read_yaml(root / "video.yaml") if (root / "video.yaml").exists() else {}
    return AppConfig(
        behaviours=_read_yaml(root / "behaviours.yaml"),
        products=_read_yaml(root / "products.yaml"),
        zones=_read_yaml(root / "zones.yaml"),
        risk_weights=_read_yaml(root / "risk_weights.yaml"),
        sop_rules=_read_yaml(root / "sop_rules.yaml"),
        video=video_cfg,
        config_dir=root,
    )
