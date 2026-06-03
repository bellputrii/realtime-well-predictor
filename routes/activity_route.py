from typing import List

from fastapi import APIRouter, HTTPException

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
            "model": "Random Forest",
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


@router.get("/model-info")
def model_info():
    return {
        "success": True,
        "message": "Model information retrieved successfully",
        "data": {
            "model": "Random Forest",
            "total_features": len(feature_columns),
            "features": feature_columns,
            "classes": inverse_class_mapping
        }
    }


@router.get("/features")
def get_features():
    return {
        "success": True,
        "message": "Feature columns retrieved successfully",
        "data": {
            "total_features": len(feature_columns),
            "feature_columns": feature_columns
        }
    }


@router.get("/classes")
def get_classes():
    return {
        "success": True,
        "message": "Classes retrieved successfully",
        "data": {
            "classes": inverse_class_mapping
        }
    }


@router.post("/predict")
def predict_activity(data: ActivityInput):
    try:
        result = predict_activity_service(data.model_dump())

        return {
            "success": True,
            "message": "Prediction successful",
            "data": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Prediction failed",
                "error": str(error)
            }
        )


@router.post("/predict-batch")
def predict_batch(data: List[ActivityInput]):
    try:
        input_items = [
            item.model_dump()
            for item in data
        ]

        results = predict_batch_service(input_items)

        return {
            "success": True,
            "message": "Batch prediction successful",
            "data": {
                "total_rows": len(results),
                "results": results
            }
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Batch prediction failed",
                "error": str(error)
            }
        )