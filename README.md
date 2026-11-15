# Revenue Retention Lab

A subscription analytics workspace built around monthly account snapshots. It calculates MRR, logo and revenue churn, expansion, cohort retention, net revenue retention, segment comparisons, and an optional logistic churn propensity model. The default data is synthetic.

## Capabilities
- Validated monthly subscription snapshots with explicit cohort and month fields.
- MRR bridge: new, expansion, contraction, churn, and ending MRR.
- Account and revenue cohort curves by plan and acquisition channel.
- API, CLI reports, Streamlit explorer, CSV export, and Docker deployment.
- Churn model is an interpretable baseline and reports its features and operating threshold.

## Quick start
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m retention_lab.cli demo --output data/snapshots.csv
uvicorn retention_lab.api:app --reload
```
Dashboard: `streamlit run dashboard/app.py`; API docs: `/docs`. CSV contract: `account_id, cohort_month, snapshot_month, active, mrr_usd, plan, channel`. Set `RETENTION_DATA_PATH` to select a normalized snapshot file. See [metrics](docs/metrics.md). MIT license.
