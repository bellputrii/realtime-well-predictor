from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import json
import importlib.util
from pathlib import Path


# =====================================================
# PATH
# =====================================================

ARTIFACT_DIR = Path("artifacts")

MODEL_PATH = ARTIFACT_DIR / "random_forest_model.pkl"
SCALER_PATH = ARTIFACT_DIR / "minmax_scaler.pkl"
FEATURE_COLUMNS_PATH = ARTIFACT_DIR / "feature_columns.json"
CLASS_MAPPING_PATH = ARTIFACT_DIR / "class_mapping.json"
FEATURE_ENGINEERING_PATH = ARTIFACT_DIR / "feature_engineering.py"


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def load_json(path: Path):
    with open(path, "r") as f:
        return json.load(f)


def build_inverse_class_mapping(class_mapping):
    if isinstance(class_mapping, dict) and "classes" in class_mapping:
        return {i: label for i, label in enumerate(class_mapping["classes"])}

    if isinstance(class_mapping, list):
        return {i: label for i, label in enumerate(class_mapping)}

    if isinstance(class_mapping, dict):
        sample_key = next(iter(class_mapping.keys()))
        sample_value = next(iter(class_mapping.values()))

        if isinstance(sample_value, int):
            return {int(v): str(k) for k, v in class_mapping.items()}

        if str(sample_key).isdigit():
            return {int(k): str(v) for k, v in class_mapping.items()}

    raise ValueError("Format class_mapping.json tidak dikenali.")


def load_feature_engineering_module(path: Path):
    spec = importlib.util.spec_from_file_location("feature_engineering", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# =====================================================
# LOAD ARTIFACTS
# =====================================================

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

feature_columns = load_json(FEATURE_COLUMNS_PATH)
class_mapping = load_json(CLASS_MAPPING_PATH)
inverse_class_mapping = build_inverse_class_mapping(class_mapping)

feature_engineering = load_feature_engineering_module(FEATURE_ENGINEERING_PATH)


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="Activity Classifier API",
    description="API untuk prediksi activity drilling menggunakan Random Forest",
    version="1.0.0"
)


# =====================================================
# INPUT SCHEMA
# Sesuai kolom pada feature_engineering.py
# =====================================================

class ActivityInput(BaseModel):
    bitdepth: float
    md: float
    Hookload: float
    mudflowin: float
    rpm: float
    torqa: float
    woba: float
    blockpos: float


# =====================================================
# ROUTES
# =====================================================

@app.get("/")
def home():
    return {
        "message": "Activity Classifier API is running",
        "model": "Random Forest",
        "endpoint": "/predict",
        "total_features": len(feature_columns),
        "classes": inverse_class_mapping
    }


@app.get("/features")
def get_features():
    return {
        "total_features": len(feature_columns),
        "feature_columns": feature_columns
    }


@app.get("/classes")
def get_classes():
    return {
        "classes": inverse_class_mapping
    }


@app.post("/predict")
def predict_activity(data: ActivityInput):
    try:
        input_df = pd.DataFrame([data.model_dump()])

        if not hasattr(feature_engineering, "preprocess_drilling_activity"):
            raise HTTPException(
                status_code=500,
                detail="Fungsi preprocess_drilling_activity tidak ditemukan di feature_engineering.py"
            )

        X_scaled, processed_df = feature_engineering.preprocess_drilling_activity(
            input_df,
            scaler,
            feature_columns
        )

        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]

        prediction_code = int(prediction)
        predicted_label = inverse_class_mapping.get(
            prediction_code,
            str(prediction_code)
        )

        confidence = float(max(probability))

        probabilities = {
            inverse_class_mapping.get(i, str(i)): float(probability[i])
            for i in range(len(probability))
        }

        return {
            "prediction_code": prediction_code,
            "prediction_label": predicted_label,
            "confidence": confidence,
            "probabilities": probabilities
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )