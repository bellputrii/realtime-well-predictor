from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import ActivityPrediction

from schemas.activity_schema import ActivityInput
from services.prediction_service import (
    predict_activity_service,
    predict_batch_service
)
from core.loader import (
    feature_columns,
    inverse_class_mapping
)

router = APIRouter()

@router.get("/")
def home():
    return {
        "success": True,
        "message": "Activity Classifier API is running",
        "data": {
            "model": "Random Forest ONNX",
            "endpoint": "/predict",
            "docs": "/docs"
        }
    }


@router.get("/health")
def health_check():
    return {
        "success": True,
        "message": "API is healthy",
        "data": {
            "status": "ok"
        }
    }


# @router.get("/model-info")
# def model_info():
#     return {
#         "success": True,
#         "message": "Model information retrieved successfully",
#         "data": {
#             "model": "Random Forest ONNX",
#             "total_features": len(feature_columns),
#             "features": feature_columns,
#             "classes": inverse_class_mapping
#         }
#     }


# @router.get("/features")
# def get_features():
#     return {
#         "success": True,
#         "message": "Feature columns retrieved successfully",
#         "data": {
#             "total_features": len(feature_columns),
#             "feature_columns": feature_columns
#         }
#     }


# @router.get("/classes")
# def get_classes():
#     return {
#         "success": True,
#         "message": "Classes retrieved successfully",
#         "data": {
#             "classes": inverse_class_mapping
#         }
#     }


@router.get("/prediction-history")
def get_prediction_history(db: Session = Depends(get_db)):
    records = (
        db.query(ActivityPrediction)
        .order_by(ActivityPrediction.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "message": "Prediction history retrieved successfully",
        "data": [
            {
                "id": record.id,
                "bitdepth": record.bitdepth,
                "md": record.md,
                "Hookload": record.Hookload,
                "mudflowin": record.mudflowin,
                "rpm": record.rpm,
                "torqa": record.torqa,
                "woba": record.woba,
                "blockpos": record.blockpos,
                "prediction_code": record.prediction_code,
                "prediction_label": record.prediction_label,
                "confidence": record.confidence,
                # "confidence_level": record.confidence_level,
                # "probabilities": record.probabilities,
                # "rule_signals": record.rule_signals,
                "created_at": record.created_at
            }
            for record in records
        ]
    }


# @router.post("/predict")
# def predict_activity(data: ActivityInput, db: Session = Depends(get_db)):
#     try:
#         input_dict = data.model_dump()
#         result = predict_activity_service(input_dict)

#         prediction_record = ActivityPrediction(
#             **input_dict,
#             prediction_code=result["prediction_code"],
#             prediction_label=result["prediction_label"],
#             confidence=result["confidence"],
#             confidence_level=result["confidence_level"],
#             probabilities=result["probabilities"],
#             rule_signals=result["rule_signals"]
#         )

#         db.add(prediction_record)
#         db.commit()
#         db.refresh(prediction_record)

#         return {
#             "success": True,
#             "message": "Prediction successful and saved to database",
#             "data": {
#                 "id": prediction_record.id,
#                 **result
#             }
#         }

#     except Exception as error:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "success": False,
#                 "message": "Prediction failed",
#                 "error": str(error)
#             }
#         )

@router.post("/predict")
def predict_activity(data: ActivityInput, db: Session = Depends(get_db)):
    try:
        input_dict = data.model_dump()
        result = predict_activity_service(input_dict)

        # Simpan ke DB (SQLite/MySQL)
        prediction_record = ActivityPrediction(
            **input_dict,
            prediction_code=result["prediction_code"],
            prediction_label=result["prediction_label"],
            confidence=result["confidence"],
            confidence_level=result["confidence_level"]  # wajib untuk NOT NULL
        )

        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        # Response minimal
        return {
            "id": prediction_record.id,
            "prediction_code": result["prediction_code"],
            "prediction_label": result["prediction_label"],
            "confidence": result["confidence"]
        }

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Prediction failed",
                "error": str(error)
            }
        )


# @router.post("/predict-batch")
# def predict_batch(data: List[ActivityInput], db: Session = Depends(get_db)):
#     try:
#         input_items = [
#             item.model_dump()
#             for item in data
#         ]

#         results = predict_batch_service(input_items)

#         saved_results = []

#         for input_dict, result in zip(input_items, results):
#             prediction_record = ActivityPrediction(
#                 **input_dict,
#                 prediction_code=result["prediction_code"],
#                 prediction_label=result["prediction_label"],
#                 confidence=result["confidence"],
#                 confidence_level=result["confidence_level"],
#                 probabilities=result["probabilities"],
#                 rule_signals=result["rule_signals"]
#             )

#             db.add(prediction_record)
#             db.flush()

#             saved_results.append({
#                 "id": prediction_record.id,
#                 **result
#             })

#         db.commit()

#         return {
#             "success": True,
#             "message": "Batch prediction successful and saved to database",
#             "data": {
#                 "total_rows": len(saved_results),
#                 "results": saved_results
#             }
#         }

#     except Exception as error:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "success": False,
#                 "message": "Batch prediction failed",
#                 "error": str(error)
#             }
#         )

@router.post("/predict-batch")
def predict_batch(data: List[ActivityInput], db: Session = Depends(get_db)):
    try:
        input_items = [item.model_dump() for item in data]
        results = predict_batch_service(input_items)
        saved_results = []

        for input_dict, result in zip(input_items, results):
            prediction_record = ActivityPrediction(
                **input_dict,
                prediction_code=result["prediction_code"],
                prediction_label=result["prediction_label"],
                confidence=result["confidence"],
                confidence_level=result["confidence_level"]
            )
            db.add(prediction_record)
            db.flush()

            saved_results.append({
                "id": prediction_record.id,
                "prediction_code": result["prediction_code"],
                "prediction_label": result["prediction_label"],
                "confidence": result["confidence"]
            })

        db.commit()

        return {
            "total_rows": len(saved_results),
            "results": saved_results
        }

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Batch prediction failed",
                "error": str(error)
            }
        )
    
    
@router.get("/latest-scheduler-results")
def latest_scheduler_results(limit: int = 10, db: Session = Depends(get_db)):
    """
    Mengembalikan hasil prediksi terbaru dari scheduler.
    limit = jumlah record terbaru yang ingin ditampilkan
    Response minimal: id, prediction_code, prediction_label, confidence
    """
    try:
        records = (
            db.query(ActivityPrediction)
            .order_by(ActivityPrediction.created_at.desc())
            .limit(limit)
            .all()
        )

        results = [
            {
                "id": record.id,
                "prediction_code": record.prediction_code,
                "prediction_label": record.prediction_label,
                "confidence": record.confidence
            }
            for record in records
        ]

        return {
            "success": True,
            "message": f"{len(results)} latest scheduler predictions retrieved",
            "data": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to retrieve latest scheduler results",
                "error": str(e)
            }
        )