import numpy as np
import pandas as pd

from core.loader import (
    model,
    onnx_input_name,
    feature_columns,
    inverse_class_mapping,
    feature_engineering
)


def get_confidence_level(confidence: float) -> str:
    if confidence >= 0.80:
        return "High"
    if confidence >= 0.60:
        return "Medium"
    return "Low"


def normalize_probability_output(probability_raw):
    if isinstance(probability_raw, dict):
        return {int(k): float(v) for k, v in probability_raw.items()}
    arr = np.array(probability_raw)
    return {i: float(arr[i]) for i in range(len(arr))}


def predict_activity_service(input_data: dict) -> dict:
    # Preprocessing
    input_df = pd.DataFrame([input_data])
    X_raw, processed_df = feature_engineering.preprocess_drilling_activity(
        input_df, feature_columns
    )

    # Convert ke numpy float32 untuk ONNX
    X_input = X_raw.to_numpy(dtype=np.float32)

    # Prediksi
    outputs = model.run(None, {onnx_input_name: X_input})
    prediction_code = int(outputs[0][0])
    probability_raw = outputs[1][0]
    probability_dict = normalize_probability_output(probability_raw)
    prediction_label = inverse_class_mapping.get(prediction_code, str(prediction_code))
    confidence = float(max(probability_dict.values()))
    confidence_level = get_confidence_level(confidence)

    # Return minimal
    return {
        "prediction_code": prediction_code,
        "prediction_label": prediction_label,
        "confidence": confidence,
        "confidence_level": confidence_level
    }


def predict_batch_service(input_items: list) -> list:
    results = []
    for item in input_items:
        result = predict_activity_service(item)
        results.append(result)
    return results