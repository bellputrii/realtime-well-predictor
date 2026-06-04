from database.connection import engine, Base
from database import models
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.activity_route import router as activity_router

# Import scheduler
from scheduler.drilling_scheduler import get_scheduler

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

# ===============================
# Jalankan scheduler saat startup
# ===============================
scheduler = get_scheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()