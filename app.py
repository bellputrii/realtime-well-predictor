from database.connection import engine, Base
from database import models
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.activity_route import router as activity_router
from routes.predict_api import router as fetch_predict_router

# Import scheduler
from scheduler.casing_scheduler import get_casing_scheduler
from scheduler.drilling_scheduler import get_scheduler
from scheduler.realtime_scheduler import get_realtime_scheduler

app = FastAPI(
    title="Activity Classifier API",
    description="API untuk prediksi activity drilling menggunakan Random Forest ONNX",
    version="1.0.0"
)

# Buat table DB otomatis
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity_router)
app.include_router(fetch_predict_router)
realtime_scheduler = get_realtime_scheduler()

scheduler = get_scheduler()
casing_scheduler = get_casing_scheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()
    casing_scheduler.start()
    realtime_scheduler.start()