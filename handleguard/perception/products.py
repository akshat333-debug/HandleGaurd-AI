from __future__ import annotations

ALIASES = {
    "box": "carton",
    "carton": "carton",
    "package": "carton",
    "large_carton": "carton",
    "fragile_package": "electronics",
    "electronics": "electronics",
    "glass": "glass",
    "mattress": "mattress",
    "pallet": "pallet",
    "pallet_truck": "pallet_jack",
    "pallet_jack": "pallet_jack",
    "trolley": "trolley",
    "forklift": "forklift",
    "person": "person",
    "human": "person",
}


def classify_product(class_name: str) -> str:
    key = class_name.lower().strip().replace("-", "_").replace(" ", "_")
    return ALIASES.get(key, "default")
