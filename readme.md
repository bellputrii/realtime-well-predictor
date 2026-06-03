# Activity Classifier API

API untuk prediksi aktivitas drilling secara real-time menggunakan model Machine Learning Random Forest yang telah dilatih menggunakan data operasi pengeboran.

## Overview

Project ini menyediakan REST API berbasis FastAPI untuk melakukan klasifikasi aktivitas drilling berdasarkan parameter operasional rig.

Model yang digunakan adalah Random Forest Classifier yang telah dilatih dan diekspor menjadi artifact sehingga dapat digunakan untuk inferensi secara real-time tanpa perlu melakukan training ulang.

---

## Features

* Real-time activity prediction
* Batch prediction
* Automatic feature engineering
* Probability score untuk setiap kelas
* Confidence level prediction
* Health check endpoint
* Model information endpoint
* Modular FastAPI architecture
* Swagger UI documentation

---

## Project Structure

```text
api-activity-drilling/
│
├── app.py
│
├── artifacts/
│   ├── random_forest_model.pkl
│   ├── minmax_scaler.pkl
│   ├── feature_columns.json
│   ├── class_mapping.json
│   └── feature_engineering.py
│
├── core/
│   ├── config.py
│   └── loader.py
│
├── routes/
│   └── activity_route.py
│
├── schemas/
│   └── activity_schema.py
│
├── services/
│   └── prediction_service.py
│
├── requirements.txt
└── README.md
```

---

## Machine Learning Pipeline

### Input Features

Model menggunakan parameter drilling berikut:

| Feature   |
| --------- |
| mudflowin |
| rpm       |
| woba      |
| Hookload  |
| torqa     |
| blockpos  |
| bitdepth  |
| md        |

### Feature Engineering

Beberapa fitur tambahan dibuat secara otomatis:

* rotary_drilling_signal
* slide_drilling_signal
* other_activity_signal

### Model

Algorithm:

```text
Random Forest Classifier
```

Preprocessing:

```text
MinMaxScaler
```

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

---

## Run API

Development mode:

```bash
python -m uvicorn app:app --reload
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

Response:

```json
{
  "success": true,
  "message": "API is healthy",
  "data": {
    "status": "ok"
  }
}
```

---

### Model Information

```http
GET /model-info
```

---

### Feature List

```http
GET /features
```

---

### Available Classes

```http
GET /classes
```

---

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
  "message": "Prediction successful",
  "data": {
    "prediction_code": 0,
    "prediction_label": "ROTARY DRILLING",
    "confidence": 0.94,
    "confidence_level": "High",
    "probabilities": {
      "ROTARY DRILLING": 0.94,
      "SLIDE DRILLING": 0.04,
      "OTHER": 0.02
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

### Machine Learning

* Scikit-Learn
* Random Forest Classifier
* MinMaxScaler

### Data Processing

* Pandas
* NumPy

---

## Future Improvements

* Docker deployment
* Authentication & API key
* Prediction logging
* Monitoring dashboard
* Model versioning
* CI/CD pipeline
* Cloud deployment

---

## Author

Developed for drilling activity classification and real-time prediction deployment using FastAPI and Machine Learning.
