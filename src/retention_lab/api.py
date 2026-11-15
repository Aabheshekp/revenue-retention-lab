from fastapi import FastAPI, HTTPException
from .pipeline import read_snapshots
from .metrics import cohort_retention, mrr_bridge, churn_by_segment, churn_propensity
from .settings import DATA_PATH

app = FastAPI(title="Revenue Retention Lab", version="1.0.0")
def load():
    try: return read_snapshots(DATA_PATH)
    except (OSError, ValueError) as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/mrr-bridge")
def bridge(): return mrr_bridge(load()).to_dict(orient="records")

@app.get("/api/v1/cohorts/accounts")
def accounts(): return cohort_retention(load()).to_dict()

@app.get("/api/v1/cohorts/revenue")
def revenue(): return cohort_retention(load(), revenue=True).to_dict()

@app.get("/api/v1/churn-by-plan")
def churn(): return churn_by_segment(load()).to_dict(orient="records")

@app.get("/api/v1/churn-propensity")
def propensity(): return churn_propensity(load())
