import json
import joblib
import importlib.util
from pathlib import Path

from core.config import (
    MODEL_PATH,
    SCALER_PATH,
    FEATURE_COLUMNS_PATH,
    CLASS_MAPPING_PATH,
    FEATURE_ENGINEERING_PATH
)


def load_json(path: Path):
    with open(path, "r") as file:
        return json.load(file)


def build_inverse_class_mapping(class_mapping):
    if isinstance(class_mapping, dict) and "classes" in class_mapping:
        return {
            i: label for i, label in enumerate(class_mapping["classes"])
        }

    if isinstance(class_mapping, list):
        return {
            i: label for i, label in enumerate(class_mapping)
        }

    if isinstance(class_mapping, dict):
        sample_key = next(iter(class_mapping.keys()))
        sample_value = next(iter(class_mapping.values()))

        if isinstance(sample_value, int):
            return {
                int(v): str(k) for k, v in class_mapping.items()
            }

        if str(sample_key).isdigit():
            return {
                int(k): str(v) for k, v in class_mapping.items()
            }

    raise ValueError("Format class_mapping.json tidak dikenali.")


def load_feature_engineering_module(path: Path):
    spec = importlib.util.spec_from_file_location(
        "feature_engineering",
        path
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

feature_columns = load_json(FEATURE_COLUMNS_PATH)
class_mapping = load_json(CLASS_MAPPING_PATH)

inverse_class_mapping = build_inverse_class_mapping(class_mapping)

feature_engineering = load_feature_engineering_module(
    FEATURE_ENGINEERING_PATH
)