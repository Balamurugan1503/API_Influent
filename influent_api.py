# influent_api.py
# ----------------------------------------------------------
# Influent Generator API - FastAPI service for realistic
# influent (raw wastewater) water quality parameter simulation
# ----------------------------------------------------------

from fastapi import FastAPI, Response, Query
from pydantic import BaseModel
from typing import List
import random

# Initialize the FastAPI application
app = FastAPI(
    title="Influent Generator API",
    description="Generates realistic influent water quality parameters for use in ML-based wastewater treatment simulations",
    version="1.0.0",
)

# ----------------------------------------------------------
# Realistic parameter ranges (you can adjust anytime)
# ----------------------------------------------------------

INFLUENT_RANGES = {
    "flow_m3_h": (20, 500),         # m3/h
    "temp_C": (10, 35),             # Celsius
    "pH": (6.0, 8.5),               # unitless
    "TSS_in_mgL": (80, 800),        # mg/L - Total Suspended Solids
    "BOD_in_mgL": (100, 500),       # mg/L - Biochemical Oxygen Demand
    "COD_in_mgL": (200, 1000),      # mg/L - Chemical Oxygen Demand
    "oil_grease_in_mgL": (1, 50),   # mg/L
    "turbidity_in_NTU": (20, 500),  # NTU
}


# ----------------------------------------------------------
# Pydantic models for clean API input/output
# ----------------------------------------------------------

class Influent(BaseModel):
    """Model for a single set of influent parameters."""
    flow_m3_h: float
    temp_C: float
    pH: float
    TSS_in_mgL: float
    BOD_in_mgL: float
    COD_in_mgL: float
    oil_grease_in_mgL: float
    turbidity_in_NTU: float


class InfluentBatch(BaseModel):
    """Model for a list (batch) of influent parameters."""
    count: int
    influents: List[Influent]


# ----------------------------------------------------------
# Helper to generate a single influent sample
# ----------------------------------------------------------

def generate_influent() -> Influent:
    """Generate one realistic influent sample within defined bounds."""
    def rand(low, high, decimals=1):
        value = random.uniform(low, high)
        # Use round(value) for integers (decimals=0), otherwise round to specified decimals
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
    """Returns a health status message."""
    return {
        "status": "ok",
        "message": "Influent Generator API is running."
    }

# Added HEAD handler to prevent 405 errors from health checks
@app.head("/", tags=["health"], status_code=200)
def head_root(response: Response):
    """Responds to HEAD requests for health checks."""
    # Since HEAD requests only ask for headers, we just set a 200 status
    # and return, preventing the 405 error you saw.
    return response


@app.get("/influent", response_model=Influent, tags=["influent"])
def get_single_influent():
    """
    Returns one random, realistic influent profile.
    Suitable for single-step ML model inputs.
    """
    return generate_influent()


@app.get("/influent/batch", response_model=InfluentBatch, tags=["influent"])
def get_batch_influent(
    n: int = Query(
        default=5, 
        ge=1, 
        le=100, 
        description="The number of influent samples to generate."
    )
):
    """
    Returns a batch of random influents.
    Query: /influent/batch?n=10
    Limit: 1–100
    """
    samples = [generate_influent() for _ in range(n)]
    return InfluentBatch(count=n, influents=samples)
