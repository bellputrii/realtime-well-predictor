from pathlib import Path

ARTIFACT_DIR = Path("artifacts")

MODEL_PATH = ARTIFACT_DIR / "random_forest_model.pkl"
SCALER_PATH = ARTIFACT_DIR / "minmax_scaler.pkl"
FEATURE_COLUMNS_PATH = ARTIFACT_DIR / "feature_columns.json"
CLASS_MAPPING_PATH = ARTIFACT_DIR / "class_mapping.json"
FEATURE_ENGINEERING_PATH = ARTIFACT_DIR / "feature_engineering.py"