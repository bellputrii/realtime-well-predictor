from pathlib import Path

ARTIFACT_DIR = Path("artifacts")

# ACTIVITY CLASSIFIER
MODEL_PATH = ARTIFACT_DIR / "random_forest_activity.onnx"
FEATURE_COLUMNS_PATH = ARTIFACT_DIR / "feature_columns.json"
CLASS_MAPPING_PATH = ARTIFACT_DIR / "class_mapping.json"
FEATURE_ENGINEERING_PATH = ARTIFACT_DIR / "feature_engineering.py"


ARTIFACT_DIR_CT = Path("artifacts-ct")
# CASING TRIP CLASSIFIER
MODEL_CASING_PATH = ARTIFACT_DIR_CT / "casing_trip_rf.onnx"
FEATURE_COLUMNS_CASING_PATH = ARTIFACT_DIR_CT / "feature_casing.json"
CLASS_MAPPING_CASING_PATH = ARTIFACT_DIR_CT / "class_casing_trip.json"
FEATURE_ENGINEERING_CASING_PATH = ARTIFACT_DIR_CT / "feature_engineering_casing.py"
