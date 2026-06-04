from pathlib import Path

ARTIFACT_DIR = Path("artifacts")

MODEL_PATH = ARTIFACT_DIR / "random_forest_activity.onnx"
FEATURE_COLUMNS_PATH = ARTIFACT_DIR / "feature_columns.json"
CLASS_MAPPING_PATH = ARTIFACT_DIR / "class_mapping.json"
FEATURE_ENGINEERING_PATH = ARTIFACT_DIR / "feature_engineering.py"