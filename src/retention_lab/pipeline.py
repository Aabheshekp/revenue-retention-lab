from pathlib import Path
import csv
from datetime import date
import pandas as pd

REQUIRED = {"account_id", "cohort_month", "snapshot_month", "active", "mrr_usd", "plan", "channel"}

def read_snapshots(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing: raise ValueError(f"Missing fields: {', '.join(sorted(missing))}")
    if df[sorted(REQUIRED)].isna().any().any(): raise ValueError("Rows contain missing values")
    for col in ("cohort_month", "snapshot_month"):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.to_period("M")
    df["active"] = df.active.astype(str).str.lower().isin({"1", "true", "yes"})
    df["mrr_usd"] = pd.to_numeric(df.mrr_usd, errors="coerce")
    if df[list(REQUIRED)].isna().any().any(): raise ValueError("Rows contain missing or invalid values")
    if (df.mrr_usd < 0).any(): raise ValueError("MRR cannot be negative")
    if (df.loc[~df.active, "mrr_usd"] > 0).any(): raise ValueError("Inactive accounts must have zero MRR")
    dup = df.duplicated(["account_id", "snapshot_month"])
    if dup.any(): raise ValueError("Each account may have only one snapshot per month")
    return df

def generate_demo(path: str | Path, months: int = 18, accounts: int = 260) -> Path:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    today = date.today().replace(day=1)
    plans = [("starter", 39), ("growth", 119), ("scale", 349)]
    channels = ["content", "partner", "paid-search", "community"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(sorted(REQUIRED))
        for customer in range(accounts):
            cohort_offset = customer % months
            cohort = (pd.Period(today, freq="M") - (months - 1 - cohort_offset))
            plan, base = plans[(customer * 7) % len(plans)]
            channel = channels[(customer * 3) % len(channels)]
            churn_after = 2 + (customer * 17 % months) if customer % 5 == 0 else months + 1
            for age in range(min(months - cohort_offset, months)):
                period = cohort + age
                if period > pd.Period(today, freq="M"): break
                active = age < churn_after
                mrr = base * (1 + (age // 6) * .12) if active else 0
                w.writerow([f"ACC-{customer:04}", str(cohort), str(period), int(active), round(mrr, 2), plan, channel])
    return path
