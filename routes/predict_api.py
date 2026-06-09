# routes/predict_api_route.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from database.connection import get_db
from database.models import ActivityPrediction, CasingPrediction
from well_client.fetch_api import fetch_well_realtime
from services.prediction_service import predict_batch_service, predict_batch_casing_service
from well_client.mapping import ACTIVITY_FIELD_MAP, CASING_FIELD_MAP

router = APIRouter()

# -------------------
# Input Schema POST
# -------------------
class WellFetchInput(BaseModel):
    token: str = Field(..., description="API token well")
    start_time: str = Field(..., description="Start datetime, format YYYY-MM-DD HH:MM:SS")
    end_time: str = Field(..., description="End datetime, format YYYY-MM-DD HH:MM:SS")

# -------------------
# Activity POST endpoint
# -------------------
@router.post("/predict-activity-api")
async def predict_activity_api(
    input_data: WellFetchInput,
    db: Session = Depends(get_db)
):
    try:
        # Ambil data realtime dari API
        raw_data = await fetch_well_realtime(
            token=input_data.token,
            start_time=input_data.start_time,
            end_time=input_data.end_time
        )
        if not raw_data:
            return {"success": True, "total_rows": 0, "results": []}

        # Sanitasi input sesuai Activity schema
        sanitized = [
            {k: float(r.get(k, 0.0)) for k in ACTIVITY_FIELD_MAP.values()} for r in raw_data
        ]

        # Prediksi batch
        results = predict_batch_service(sanitized)

        saved_results = []
        for inp, res in zip(sanitized, results):
            record = ActivityPrediction(
                **inp,
                prediction_code=res["prediction_code"],
                prediction_label=res["prediction_label"],
                confidence=res["confidence"],
                confidence_level=res["confidence_level"]
            )
            db.add(record)
            db.flush()
            saved_results.append({
                "input_data": inp,
                "prediction_code": res["prediction_code"],
                "prediction_label": res["prediction_label"],
                "confidence": res["confidence"]
            })

        db.commit()
        return {"success": True, "total_rows": len(saved_results), "results": saved_results}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# -------------------
# Casing POST endpoint
# -------------------
@router.post("/predict-casing-api")
async def predict_casing_api(
    input_data: WellFetchInput,
    db: Session = Depends(get_db)
):
    try:
        raw_data = await fetch_well_realtime(
            token=input_data.token,
            start_time=input_data.start_time,
            end_time=input_data.end_time
        )
        if not raw_data:
            return {"success": True, "total_rows": 0, "results": []}

        sanitized = [
            {k: float(r.get(k, 0.0)) for k in CASING_FIELD_MAP.values()} for r in raw_data
        ]

        results = predict_batch_casing_service(sanitized)
        saved_results = []
        for inp, res in zip(sanitized, results):
            record = CasingPrediction(
                **inp,
                prediction_code=res["prediction_code"],
                prediction_label=res["prediction_label"],
                confidence=res["confidence"],
                confidence_level=res["confidence_level"]
            )
            db.add(record)
            db.flush()
            saved_results.append({
                "input_data": inp,
                "prediction_code": res["prediction_code"],
                "prediction_label": res["prediction_label"],
                "confidence": res["confidence"]
            })

        db.commit()
        return {"success": True, "total_rows": len(saved_results), "results": saved_results}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))