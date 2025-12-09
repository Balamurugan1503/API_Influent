# influent_api.py
# ----------------------------------------------------------
# Influent Generator API - FastAPI service for realistic
# influent (raw wastewater) water quality parameter simulation
# ----------------------------------------------------------

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import random

app = FastAPI(
    title="Influent Generator API",
    description="Generates realistic influent water quality parameters for use in ML-based wastewater treatment simulations",
    version="1.0.0",
)

# ----------------------------------------------------------
# Realistic parameter ranges (you can adjust anytime)
# ----------------------------------------------------------

INFLUENT_RANGES = {
    "flow_m3_h": (20, 500),            # m3/h
    "temp_C": (10, 35),                # Celsius
    "pH": (6.0, 8.5),                  # unitless
    "TSS_in_mgL": (80, 800),           # mg/L
    "BOD_in_mgL": (100, 500),          # mg/L
    "COD_in_mgL": (200, 1000),         # mg/L
    "oil_grease_in_mgL": (1, 50),      # mg/L
    "turbidity_in_NTU": (20, 500),     # NTU
}


# ----------------------------------------------------------
# Pydantic models for clean API output
# ----------------------------------------------------------

class Influent(BaseModel):
    flow_m3_h: float
    temp_C: float
    pH: float
    TSS_in_mgL: float
    BOD_in_mgL: float
    COD_in_mgL: float
    oil_grease_in_mgL: float
    turbidity_in_NTU: float


class InfluentBatch(BaseModel):
    count: int
    influents: List[Influent]


# ----------------------------------------------------------
# Helper to generate a single influent sample
# ----------------------------------------------------------

def generate_influent() -> Influent:
    """Generate one realistic influent sample within defined bounds."""
    def rand(low, high, decimals=1):
        value = random.uniform(low, high)
        if decimals == 0:
            return round(value)
        return round(value, decimals)

    return Influent(
        flow_m3_h=rand(*INFLUENT_RANGES["flow_m3_h"], decimals=0),
        temp_C=rand(*INFLUENT_RANGES["temp_C"]),
        pH=rand(*INFLUENT_RANGES["pH"]),
        TSS_in_mgL=rand(*INFLUENT_RANGES["TSS_in_mgL"]),
        BOD_in_mgL=rand(*INFLUENT_RANGES["BOD_in_mgL"]),
        COD_in_mgL=rand(*INFLUENT_RANGES["COD_in_mgL"]),
        oil_grease_in_mgL=rand(*INFLUENT_RANGES["oil_grease_in_mgL"]),
        turbidity_in_NTU=rand(*INFLUENT_RANGES["turbidity_in_NTU"]),
    )


# ----------------------------------------------------------
# API Endpoints
# ----------------------------------------------------------

@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "message": "Influent Generator API is running."
    }


@app.get("/influent", response_model=Influent, tags=["influent"])
def get_single_influent():
    """
    Returns one random influent profile.
    Suitable for primary/biological/tertiary ML model inputs.
    """
    return generate_influent()


@app.get("/influent/batch", response_model=InfluentBatch, tags=["influent"])
def get_batch_influent(n: int = 5):
    """
    Returns a batch of random influents.
    Query: /influent/batch?n=10
    Limit: 1–100
    """
    n = max(1, min(n, 100))
    samples = [generate_influent() for _ in range(n)]
    return InfluentBatch(count=n, influents=samples)
