import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import streamlit as st
from retention_lab.pipeline import read_snapshots
from retention_lab.metrics import cohort_retention, mrr_bridge, churn_by_segment, churn_propensity
from retention_lab.settings import DATA_PATH

st.set_page_config(page_title="Retention Lab", layout="wide")
st.title("Subscription Revenue & Retention")
try: df=read_snapshots(DATA_PATH)
except (OSError, ValueError) as exc: st.error(str(exc)); st.stop()
bridge=mrr_bridge(df); current=float(bridge.iloc[-1].ending_mrr); nrr=bridge.iloc[-1].nrr
a,b,c=st.columns(3); a.metric("Current MRR", f"${current:,.0f}"); b.metric("Net revenue retention", f"{nrr:.1%}" if nrr is not None else "—"); c.metric("Accounts", f"{df.loc[df.snapshot_month==df.snapshot_month.max(),'active'].sum():,}")
st.subheader("MRR bridge"); st.dataframe(bridge, use_container_width=True, hide_index=True)
st.subheader("Account retention by cohort"); st.dataframe(cohort_retention(df), use_container_width=True)
st.subheader("Current churn by plan"); st.dataframe(churn_by_segment(df), use_container_width=True, hide_index=True)
st.subheader("Exploratory churn propensity")
model=churn_propensity(df)
if model["status"]=="ok":
    st.caption(f"Educational logistic baseline · holdout AUC: {model['validation_auc']} · {model['validation_method']}")
    st.dataframe(model["accounts"],use_container_width=True,hide_index=True)
else: st.info(model["message"])
st.download_button("Download MRR bridge", bridge.to_csv(index=False), "mrr-bridge.csv", "text/csv")
