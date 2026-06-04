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
        return {
            int(class_code): float(probability)
            for class_code, probability in probability_raw.items()
        }

    probability_array = np.array(probability_raw)

    return {
        i: float(probability_array[i])
        for i in range(len(probability_array))
    }


def predict_activity_service(input_data: dict) -> dict:
    input_df = pd.DataFrame([input_data])

    X_raw, processed_df = feature_engineering.preprocess_drilling_activity(
        input_df,
        feature_columns
    )

    X_input = X_raw.to_numpy(dtype=np.float32)

    outputs = model.run(
        None,
        {
            onnx_input_name: X_input
        }
    )

    prediction_code = int(outputs[0][0])

    probability_raw = outputs[1][0]
    probability_dict = normalize_probability_output(probability_raw)

    prediction_label = inverse_class_mapping.get(
        prediction_code,
        str(prediction_code)
    )

    confidence = float(max(probability_dict.values()))

    probabilities = {
        inverse_class_mapping.get(int(class_code), str(class_code)): float(probability)
        for class_code, probability in probability_dict.items()
    }

    rule_signals = {
        "rotary_drilling_signal": int(processed_df["rotary_drilling_signal"].iloc[0]),
        "slide_drilling_signal": int(processed_df["slide_drilling_signal"].iloc[0]),
        "other_activity_signal": int(processed_df["other_activity_signal"].iloc[0])
    }

    return {
        "prediction_code": prediction_code,
        "prediction_label": prediction_label,
        "confidence": confidence,
        "confidence_level": get_confidence_level(confidence),
        "probabilities": probabilities,
        "rule_signals": rule_signals
    }


def predict_batch_service(input_items: list) -> list:
    results = []

    for index, item in enumerate(input_items):
        result = predict_activity_service(item)

        results.append({
            "row": index + 1,
            **result
        })

    return results