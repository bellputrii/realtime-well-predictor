import numpy as np
import pandas as pd

from core.loader import (
    model,
    onnx_input_name,
    feature_columns,
    inverse_class_mapping,
    feature_engineering,
    model_casing,
    onnx_input_name_casing,
    feature_columns_casing,
    inverse_class_mapping_casing
)


def get_confidence_level(confidence: float) -> str:
    if confidence >= 0.80: return "High"
    if confidence >= 0.60: return "Medium"
    return "Low"


def normalize_probability_output(probability_raw):
    if isinstance(probability_raw, dict):
        return {int(k): float(v) for k, v in probability_raw.items()}
    arr = np.array(probability_raw)
    return {i: float(arr[i]) for i in range(len(arr))}


# ================= Activity Classifier =================
def predict_activity_service(input_data: dict) -> dict:
    input_df = pd.DataFrame([input_data])
    X_raw, _ = feature_engineering.preprocess_drilling_activity(input_df, feature_columns)
    X_input = X_raw.to_numpy(dtype=np.float32)

    outputs = model.run(None, {onnx_input_name: X_input})
    prediction_code = int(outputs[0][0])
    probability_raw = outputs[1][0]
    prediction_label = inverse_class_mapping.get(prediction_code, str(prediction_code))
    confidence = float(max(probability_raw.values()))
    confidence_level = get_confidence_level(confidence)

    return {
        "prediction_code": prediction_code,
        "prediction_label": prediction_label,
        "confidence": confidence,
        "confidence_level": confidence_level
    }


def predict_batch_service(input_items: list) -> list:
    return [predict_activity_service(item) for item in input_items]


# ================= Casing Trip Classifier =================

def predict_casing_service(input_data: dict) -> dict:
    input_df = pd.DataFrame([input_data])
    X_input = input_df[feature_columns_casing].to_numpy(dtype=np.float32)
    outputs = model_casing.run(None, {onnx_input_name_casing: X_input})
    prediction_code = int(outputs[0][0])
    probability_raw = outputs[1][0]
    prediction_label = inverse_class_mapping_casing.get(prediction_code, str(prediction_code))
    confidence = float(max(probability_raw.values()))
    confidence_level = get_confidence_level(confidence)

    return {
        "prediction_code": prediction_code,
        "prediction_label": prediction_label,
        "confidence": confidence,
        "confidence_level": confidence_level
    }

def predict_batch_casing_service(input_items: list) -> list:
    return [predict_casing_service(item) for item in input_items]