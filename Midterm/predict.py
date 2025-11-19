import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class Row(BaseModel):
    # dynamic: accept arbitrary mapping by using dict; but pydantic requires fields
    # We'll accept list of dicts via request body
    pass

app = FastAPI(title="CatBoost prediction service")

# load model & preprocess artifacts
MODEL_PATH = os.environ.get("MODEL_PATH", "artifacts/model.cbm")
PREPROCESS_PATH = os.environ.get("PREPROCESS_PATH", "artifacts/preprocess.pkl")

print("Loading model...", MODEL_PATH)
from catboost import CatBoostRegressor
model = CatBoostRegressor()
model.load_model(MODEL_PATH)
prep = joblib.load(PREPROCESS_PATH)
scaler = prep["scaler"]
feature_cols = prep["features"]

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_PATH, "n_features": len(feature_cols)}

@app.post("/predict")
def predict_batch(records: List[dict]):
    """
    Accepts a JSON list of dicts, each dict maps feature_name -> value.
    Example:
    [
      {"feature_0": 1.2, "feature_1": 3.4, ...},
      {"feature_0": 0.7, "feature_1": 2.1, ...}
    ]
    """
    if not isinstance(records, list) or len(records) == 0:
        return {"error": "send a non-empty list of records"}

    # Build dataframe and align columns
    df = pd.DataFrame(records)
    # Ensure all feature columns exist; missing -> fillna(0)
    for c in feature_cols:
        if c not in df.columns:
            df[c] = 0.0
    df = df[feature_cols]  # ensure order

    X = scaler.transform(df.values.astype(float))
    preds = model.predict(X)
    return {"predictions": preds.tolist()}