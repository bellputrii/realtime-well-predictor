from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from well_client.fetch_api import fetch_wells_ops
from services.prediction_service import predict_batch_service, predict_batch_casing_service
from database.connection import SessionLocal
from database.models import ActivityPrediction, CasingPrediction

WELL_TOKEN = "ea1210d9edd8f1d87258d809b4ba477c"

def sanitize_input(record, field_map):
    """Mapping field API ke schema FastAPI (Activity/Casing)"""
    return {k: float(record.get(k, 0.0)) for k in field_map}

def get_realtime_scheduler():
    scheduler = AsyncIOScheduler()

    async def scheduled_task():
        try:
            data_list = await fetch_wells_ops(token=WELL_TOKEN, time_window_minutes=5)
            if not data_list:
                print("[Scheduler] No data")
                return

            db = SessionLocal()
            try:
                # Activity
                sanitized_activity = [sanitize_input(r, ["md","bitdepth","hklda","mudflowin","rpm","torqa","woba","blockpos"]) for r in data_list]
                results_activity = predict_batch_service(sanitized_activity)
                for i, (inp, res) in enumerate(zip(sanitized_activity, results_activity), 1):
                    record = ActivityPrediction(
                        **inp,
                        prediction_code=res["prediction_code"],
                        prediction_label=res["prediction_label"],
                        confidence=res["confidence"],
                        confidence_level=res["confidence_level"]
                    )
                    db.add(record)
                    print(f"[Activity #{i}] {res['prediction_label']} Confidence: {res['confidence']:.4f}")

                # Casing
                sanitized_casing = [sanitize_input(r, ["blockpos","bitdepth","speeddown","md","hklda","mudflowin","speedup","stppress"]) for r in data_list]
                results_casing = predict_batch_casing_service(sanitized_casing)
                for i, (inp, res) in enumerate(zip(sanitized_casing, results_casing), 1):
                    record = CasingPrediction(
                        **inp,
                        prediction_code=res["prediction_code"],
                        prediction_label=res["prediction_label"],
                        confidence=res["confidence"],
                        confidence_level=res["confidence_level"]
                    )
                    db.add(record)
                    print(f"[Casing #{i}] {res['prediction_label']} Confidence: {res['confidence']:.4f}")

                db.commit()
                print(f"[Scheduler] Batch complete. Activity: {len(results_activity)}, Casing: {len(results_casing)}")
            finally:
                db.close()
        except Exception as e:
            print("[Scheduler] Error:", e)

    scheduler.add_job(
        scheduled_task,
        trigger=IntervalTrigger(minutes=5),
        id="realtime_task",
        name="Realtime Well Prediction"
    )
    return scheduler