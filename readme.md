# Activity Classifier API

API untuk prediksi aktivitas drilling secara real-time menggunakan model Machine Learning Random Forest. API ini mendukung single prediction, batch prediction, penyimpanan riwayat prediksi ke database MySQL, serta dokumentasi otomatis melalui Swagger UI.

## Overview

Project ini menyediakan REST API berbasis FastAPI untuk melakukan klasifikasi aktivitas drilling berdasarkan parameter operasional rig.

Model yang digunakan adalah Random Forest Classifier yang telah dilatih dan diekspor menjadi artifact sehingga dapat digunakan untuk inferensi tanpa melakukan training ulang.

Selain melakukan prediksi, API ini juga dapat menyimpan input dan hasil prediksi ke database MySQL agar dapat digunakan kembali untuk kebutuhan dashboard, riwayat prediksi, monitoring, dan integrasi frontend.

---

## Features

* Real-time activity prediction
* Batch prediction
* Automatic feature engineering
* Probability score untuk setiap kelas
* Confidence level prediction
* Prediction history logging to MySQL
* Health check endpoint
* Model information endpoint
* Modular FastAPI architecture
* Swagger UI documentation
* Ready for frontend integration

---

## Project Structure

```text
api-activity-drilling/
│
├── app.py
├── .env
├── requirements.txt
├── README.md
│
├── artifacts/
│   ├── random_forest_model.pkl
│   ├── minmax_scaler.pkl
│   ├── feature_columns.json
│   ├── class_mapping.json
│   └── feature_engineering.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── loader.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── models.py
│
├── routes/
│   ├── __init__.py
│   └── activity_route.py
│
├── schemas/
│   ├── __init__.py
│   └── activity_schema.py
│
└── services/
    ├── __init__.py
    └── prediction_service.py
```

---

## Machine Learning Pipeline

```text
Input Data
    ↓
Feature Engineering
    ↓
MinMaxScaler
    ↓
Random Forest Classifier
    ↓
Prediction Result
    ↓
Save to MySQL Database
```

---

## Input Features

| Feature   |
| --------- |
| bitdepth  |
| md        |
| Hookload  |
| mudflowin |
| rpm       |
| torqa     |
| woba      |
| blockpos  |

---

## Feature Engineering

Beberapa fitur tambahan dibuat otomatis sebelum prediksi:

* rotary_drilling_signal
* slide_drilling_signal
* other_activity_signal

---

## Model

Algorithm:

```text
Random Forest Classifier
```

Preprocessing:

```text
MinMaxScaler
```

---

## Database

API ini menggunakan MySQL untuk menyimpan riwayat hasil prediksi.

### Database Name

```text
activity_drilling_db
```

### Table

```text
activity_predictions
```

### Stored Data

Data yang disimpan meliputi:

* input drilling parameters
* prediction code
* prediction label
* confidence
* confidence level
* probabilities
* rule signals
* created_at

---

## Environment Variables

Buat file `.env` di root project:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=activity_drilling_db
```

Jika MySQL menggunakan password, isi `DB_PASSWORD`.

---

## Installation

Clone repository:

```bash
git clone https://github.com/your-username/activity-classifier-api.git
cd activity-classifier-api
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Jika package database belum tersedia, install:

```bash
pip install sqlalchemy pymysql python-dotenv
```

---

## Run API

Pastikan MySQL sudah berjalan melalui XAMPP/Laragon.

Development mode:

```bash
python -m uvicorn app:app --reload
```

Jika terjadi error memory pada Windows, jalankan tanpa reload:

```bash
python -m uvicorn app:app
```

Server:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc Documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## API Endpoints

### Health Check

```http
GET /health
```

### Model Information

```http
GET /model-info
```

### Feature List

```http
GET /features
```

### Available Classes

```http
GET /classes
```

### Single Prediction

```http
POST /predict
```

Request:

```json
{
  "bitdepth": 335.46,
  "md": 335.46,
  "Hookload": 88.75,
  "mudflowin": 1088.36,
  "rpm": 14,
  "torqa": 0.73,
  "woba": 0,
  "blockpos": 0
}
```

Response:

```json
{
  "success": true,
  "message": "Prediction successful and saved to database",
  "data": {
    "id": 1,
    "prediction_code": 0,
    "prediction_label": "ROTARY DRILLING",
    "confidence": 0.94,
    "confidence_level": "High",
    "probabilities": {
      "ROTARY DRILLING": 0.94,
      "SLIDE DRILLING": 0.04,
      "OTHER": 0.02
    },
    "rule_signals": {
      "rotary_drilling_signal": 1,
      "slide_drilling_signal": 0,
      "other_activity_signal": 1
    }
  }
}
```

---

### Batch Prediction

```http
POST /predict-batch
```

Request:

```json
[
  {
    "bitdepth": 335.46,
    "md": 335.46,
    "Hookload": 88.75,
    "mudflowin": 1088.36,
    "rpm": 14,
    "torqa": 0.73,
    "woba": 0,
    "blockpos": 0
  },
  {
    "bitdepth": 340.12,
    "md": 342.50,
    "Hookload": 90.10,
    "mudflowin": 950.25,
    "rpm": 0,
    "torqa": 0.40,
    "woba": 2.50,
    "blockpos": 12.70
  }
]
```

---

### Prediction History

```http
GET /prediction-history
```

Endpoint ini digunakan untuk mengambil seluruh riwayat prediksi yang sudah tersimpan di database.

Response:

```json
{
  "success": true,
  "message": "Prediction history retrieved successfully",
  "data": [
    {
      "id": 1,
      "bitdepth": 335.46,
      "md": 335.46,
      "Hookload": 88.75,
      "mudflowin": 1088.36,
      "rpm": 14,
      "torqa": 0.73,
      "woba": 0,
      "blockpos": 0,
      "prediction_code": 0,
      "prediction_label": "ROTARY DRILLING",
      "confidence": 0.94,
      "confidence_level": "High",
      "probabilities": {
        "ROTARY DRILLING": 0.94,
        "SLIDE DRILLING": 0.04,
        "OTHER": 0.02
      },
      "rule_signals": {
        "rotary_drilling_signal": 1,
        "slide_drilling_signal": 0,
        "other_activity_signal": 1
      },
      "created_at": "2026-02-18T11:23:11"
    }
  ]
}
```

---

## Confidence Interpretation

| Confidence  | Level  |
| ----------- | ------ |
| ≥ 0.80      | High   |
| 0.60 - 0.79 | Medium |
| < 0.60      | Low    |

---

## Technology Stack

### Backend

* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy

### Database

* MySQL
* phpMyAdmin
* PyMySQL

### Machine Learning

* Scikit-Learn
* Random Forest Classifier
* MinMaxScaler

### Data Processing

* Pandas
* NumPy

---

## Frontend Integration Plan

API ini dapat digunakan oleh frontend seperti Next.js untuk membuat dashboard monitoring aktivitas drilling.

Contoh integrasi:

```text
Next.js Frontend
      ↓
FastAPI Backend
      ↓
Machine Learning Prediction
      ↓
MySQL Database
      ↓
Dashboard / History / Export Data
```

---

## Future Improvements

* Docker deployment
* Authentication & API key
* CSV upload for batch prediction
* Prediction logging dashboard
* Real-time streaming integration
* Model versioning
* CI/CD pipeline
* Cloud deployment

---

## Author

Developed for drilling activity classification, real-time prediction deployment, and prediction history monitoring using FastAPI, MySQL, and Machine Learning.
