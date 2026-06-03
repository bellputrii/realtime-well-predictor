from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.activity_route import router as activity_router

app = FastAPI(
    title="Activity Classifier API",
    description="API untuk prediksi activity drilling menggunakan Random Forest",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity_router)