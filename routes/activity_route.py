from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import ActivityPrediction, CasingPrediction
from schemas.activity_schema import ActivityInput, CasingInput
from services.prediction_service import predict_batch_service, predict_batch_casing_service

router = APIRouter()

@router.post("/predict-activity")
def predict_activity(data: List[ActivityInput], db: Session = Depends(get_db)):
    input_items = [item.model_dump() for item in data]
    results = predict_batch_service(input_items)
    saved_results = []
    for input_dict, result in zip(input_items, results):
        record = ActivityPrediction(
            **input_dict,
            prediction_code=result["prediction_code"],
            prediction_label=result["prediction_label"],
            confidence=result["confidence"],
            confidence_level=result["confidence_level"]
        )
        db.add(record)
        db.flush()
        saved_results.append({
            "id": record.id,
            "prediction_code": result["prediction_code"],
            "prediction_label": result["prediction_label"],
            "confidence": result["confidence"]
        })
    db.commit()
    return {"total_rows": len(saved_results), "results": saved_results}


@router.post("/predict-casing")
def predict_casing(data: List[CasingInput], db: Session = Depends(get_db)):
    input_items = [item.model_dump() for item in data]
    results = predict_batch_casing_service(input_items)
    saved_results = []
    for input_dict, result in zip(input_items, results):
        record = CasingPrediction(
            **input_dict,
            prediction_code=result["prediction_code"],
            prediction_label=result["prediction_label"],
            confidence=result["confidence"],
            confidence_level=result["confidence_level"]
        )
        db.add(record)
        db.flush()
        saved_results.append({
            "id": record.id,
            "prediction_code": result["prediction_code"],
            "prediction_label": result["prediction_label"],
            "confidence": result["confidence"]
        })
    db.commit()
    return {"total_rows": len(saved_results), "results": saved_results}