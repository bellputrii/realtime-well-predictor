import pandas as pd

from core.loader import (
    model,
    scaler,
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


def predict_activity_service(input_data: dict) -> dict:
    input_df = pd.DataFrame([input_data])

    X_scaled, processed_df = feature_engineering.preprocess_drilling_activity(
        input_df,
        scaler,
        feature_columns
    )

    prediction = model.predict(X_scaled)[0]
    probability = model.predict_proba(X_scaled)[0]

    prediction_code = int(prediction)
    prediction_label = inverse_class_mapping.get(
        prediction_code,
        str(prediction_code)
    )

    confidence = float(max(probability))

    probabilities = {
        inverse_class_mapping.get(i, str(i)): float(probability[i])
        for i in range(len(probability))
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