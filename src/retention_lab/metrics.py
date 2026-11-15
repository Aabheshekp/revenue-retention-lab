import pandas as pd

def cohort_retention(df: pd.DataFrame, revenue: bool = False) -> pd.DataFrame:
    active = df.loc[df.active].copy()
    active["age_month"] = active.snapshot_month.astype("int64") - active.cohort_month.astype("int64")
    if revenue:
        values = active.groupby(["cohort_month", "age_month"]).mrr_usd.sum().rename("value")
        base = active.loc[active.age_month == 0].groupby("cohort_month").mrr_usd.sum()
    else:
        values = active.groupby(["cohort_month", "age_month"]).account_id.nunique().rename("value")
        base = active.loc[active.age_month == 0].groupby("cohort_month").account_id.nunique()
    matrix = values.unstack("age_month").div(base, axis=0).round(3)
    matrix.index = matrix.index.astype(str)
    return matrix

def mrr_bridge(df: pd.DataFrame) -> pd.DataFrame:
    months = sorted(df.snapshot_month.unique())
    records = []
    previous = {}
    for month in months:
        current = df.loc[(df.snapshot_month == month) & df.active].set_index("account_id").mrr_usd.to_dict()
        prior_total = sum(previous.values()); current_total = sum(current.values())
        expansion = sum(max(current.get(k, 0) - v, 0) for k, v in previous.items() if k in current)
        contraction = sum(max(v - current.get(k, 0), 0) for k, v in previous.items())
        new = sum(v for k, v in current.items() if k not in previous)
        churn = sum(v for k, v in previous.items() if k not in current)
        records.append({"month": str(month), "starting_mrr": round(prior_total, 2), "new_mrr": round(new, 2), "expansion_mrr": round(expansion, 2), "contraction_mrr": round(contraction, 2), "churned_mrr": round(churn, 2), "ending_mrr": round(current_total, 2), "nrr": round((prior_total + expansion - contraction - churn) / prior_total, 3) if prior_total else None})
        previous = current
    return pd.DataFrame(records)

def churn_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    latest = df.snapshot_month.max(); previous = latest - 1
    base = df.loc[df.snapshot_month == previous, ["account_id", "active", "plan", "channel"]].rename(columns={"active": "was_active"})
    now = df.loc[df.snapshot_month == latest, ["account_id", "active"]].rename(columns={"active": "is_active"})
    joined = base.merge(now, on="account_id", how="left").fillna({"is_active": False})
    joined = joined.loc[joined.was_active]
    return joined.groupby("plan", as_index=False).agg(starting_accounts=("account_id", "nunique"), churned=("is_active", lambda x: int((~x).sum()))).assign(churn_rate=lambda x: (x.churned / x.starting_accounts).round(3))

def churn_propensity(df: pd.DataFrame) -> dict:
    """Fit a transparent account-month logistic baseline and score current active accounts."""
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    ordered=df.sort_values(["account_id","snapshot_month"]).copy()
    grouped=ordered.groupby("account_id",sort=False)
    ordered["next_active"]=grouped.active.shift(-1)
    ordered["next_month"]=grouped.snapshot_month.shift(-1)
    adjacent=ordered.loc[ordered.active & ordered.next_active.notna() & (ordered.next_month == ordered.snapshot_month + 1)].copy()
    if len(adjacent)<20:
        return {"status":"insufficient_data","message":"At least 20 adjacent active account-month records are needed.","accounts":[]}
    adjacent["age_months"]=adjacent.snapshot_month.astype("int64")-adjacent.cohort_month.astype("int64")
    y=(~adjacent.next_active.astype(bool)).astype(int)
    if y.nunique()<2:
        return {"status":"insufficient_data","message":"Historical snapshots need both retained and churned examples.","accounts":[]}
    features=["mrr_usd","age_months","plan","channel"]
    preprocess=ColumnTransformer([("numeric",StandardScaler(),["mrr_usd","age_months"]),("categorical",OneHotEncoder(handle_unknown="ignore"),["plan","channel"])])
    model=make_pipeline(preprocess,LogisticRegression(max_iter=1000,class_weight="balanced",random_state=42))
    try:
        x_train,x_test,y_train,y_test=train_test_split(adjacent[features],y,test_size=.25,random_state=42,stratify=y)
        model.fit(x_train,y_train)
        auc=float(roc_auc_score(y_test,model.predict_proba(x_test)[:,1])) if y_test.nunique()>1 else None
    except ValueError as exc:
        return {"status":"insufficient_data","message":str(exc),"accounts":[]}
    latest=ordered.snapshot_month.max()
    current=ordered.loc[(ordered.snapshot_month==latest)&ordered.active].copy()
    current["age_months"]=current.snapshot_month.astype("int64")-current.cohort_month.astype("int64")
    current["churn_probability"]=model.predict_proba(current[features])[:,1]
    risk=current.sort_values("churn_probability",ascending=False).head(25)
    return {"status":"ok","training_rows":int(len(adjacent)),"validation_auc":round(auc,3) if auc is not None else None,"validation_method":"random account-month holdout; educational baseline only","accounts":[{"account_id":row.account_id,"plan":row.plan,"channel":row.channel,"mrr_usd":round(float(row.mrr_usd),2),"churn_probability":round(float(row.churn_probability),3)} for row in risk.itertuples()]}
