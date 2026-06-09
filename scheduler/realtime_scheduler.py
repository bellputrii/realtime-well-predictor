# scheduler/realtime_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from well_client.fetch_api import fetch_wells_ops
from services.prediction_service import predict_batch_service, predict_batch_casing_service
from database.connection import SessionLocal
from database.models import ActivityPrediction, CasingPrediction
from well_client.mapping import ACTIVITY_FIELD_MAP, CASING_FIELD_MAP

# Default token bisa diganti via parameter
DEFAULT_WELL_TOKEN = "ea1210d9edd8f1d87258d809b4ba477c"

def sanitize_input(record: dict, field_map: dict) -> dict:
    """Mapping API ke schema FastAPI (Activity/Casing)"""
    return {fastapi_key: float(record.get(api_key, 0.0)) for api_key, fastapi_key in field_map.items()}

def get_realtime_scheduler(token: str = DEFAULT_WELL_TOKEN, interval_minutes: int = 5):
    scheduler = AsyncIOScheduler()

    async def scheduled_task():
        try:
            # Ambil data realtime 1 menit terakhir sebelum eksekusi
            data_list = await fetch_wells_ops(token=token, time_window_minutes=interval_minutes)
            if not data_list:
                print("[Scheduler] No data in this interval.")
                return

            db = SessionLocal()
            try:
                # ================= Activity Prediction =================
                sanitized_activity = [sanitize_input(r, ACTIVITY_FIELD_MAP) for r in data_list]
                results_activity = predict_batch_service(sanitized_activity)

                for idx, (inp, res) in enumerate(zip(sanitized_activity, results_activity), start=1):
                    record = ActivityPrediction(
                        **inp,
                        prediction_code=res["prediction_code"],
                        prediction_label=res["prediction_label"],
                        confidence=res["confidence"],
                        confidence_level=res["confidence_level"]
                    )
                    db.add(record)
                    print(f"[Activity #{idx}] {res['prediction_label']} Confidence: {res['confidence']:.4f}")

                # ================= Casing Prediction =================
                sanitized_casing = [sanitize_input(r, CASING_FIELD_MAP) for r in data_list]
                results_casing = predict_batch_casing_service(sanitized_casing)

                for idx, (inp, res) in enumerate(zip(sanitized_casing, results_casing), start=1):
                    record = CasingPrediction(
                        **inp,
                        prediction_code=res["prediction_code"],
                        prediction_label=res["prediction_label"],
                        confidence=res["confidence"],
                        confidence_level=res["confidence_level"]
                    )
                    db.add(record)
                    print(f"[Casing #{idx}] {res['prediction_label']} Confidence: {res['confidence']:.4f}")

                db.commit()
                print(f"[Scheduler] Batch complete. Activity: {len(results_activity)}, Casing: {len(results_casing)}")
            finally:
                db.close()

        except Exception as e:
            print("[Scheduler] Error:", e)

    scheduler.add_job(
        scheduled_task,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="realtime_task",
        name="Realtime Well Prediction"
    )

    return scheduler