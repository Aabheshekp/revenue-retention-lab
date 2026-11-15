# Metric definitions

- **MRR** is the sum of active account monthly recurring revenue for a snapshot month.
- **Logo retention** is active accounts in a cohort at age N divided by active cohort accounts at age 0.
- **NRR** is `(starting MRR + expansion − contraction − churn) / starting MRR`; new sales are excluded.
- The month-over-month churn view compares accounts active in the preceding available month with their current snapshot.

The churn propensity endpoint fits a scaled logistic regression on account-month features (`mrr_usd`, account age, plan, and channel). It reports a random account-month holdout AUC and ranks current active accounts. This is an exploratory baseline: account-month samples are not independent, so it is not a production retention intervention model. Use a time-based split, leakage review, calibration, and business validation before acting on scores.

Rows are account-month snapshots. Backfilled corrections should replace a snapshot, not add a duplicate. Use consistent billing currency and revenue recognition rules before business reporting.
