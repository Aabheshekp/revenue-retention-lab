from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = Path(os.getenv("RETENTION_DATA_PATH", ROOT / "data" / "snapshots.csv"))
