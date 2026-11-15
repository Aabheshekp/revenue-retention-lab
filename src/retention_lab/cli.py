import argparse
from .pipeline import generate_demo, read_snapshots
from .metrics import cohort_retention, mrr_bridge, churn_by_segment
from .settings import DATA_PATH

def main():
    p = argparse.ArgumentParser(prog="retention-lab"); s = p.add_subparsers(dest="command", required=True)
    d=s.add_parser("demo"); d.add_argument("--output", default=str(DATA_PATH))
    r=s.add_parser("report"); r.add_argument("--input", default=str(DATA_PATH))
    args=p.parse_args()
    if args.command == "demo": print(generate_demo(args.output)); return
    df=read_snapshots(args.input)
    print("MRR bridge\n", mrr_bridge(df).to_string(index=False))
    print("\nAccount retention\n", cohort_retention(df).to_string())
    print("\nChurn by plan\n", churn_by_segment(df).to_string(index=False))

if __name__ == "__main__": main()
