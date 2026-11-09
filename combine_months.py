"""Combine checked carrier-month files and verify cross-month counts."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = sorted((ROOT / "data").glob("carrier_month_20??_??.csv"))
OUT = ROOT / "data/carrier_month_combined.csv"
COUNTS = ("flights", "cancelled", "diverted", "arrivals_measured", "on_time_arrivals", "late_arrivals", "arrival_status_missing")


def main():
    if len(FILES) < 2:
        raise ValueError("At least two validated monthly files are required")
    rows, keys = [], set()
    for path in FILES:
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = (row["month"], row["marketing_carrier"])
                assert key not in keys, f"duplicate carrier-month: {key}"
                assert row["month"].replace("-", "_") in path.stem, f"month/file mismatch: {path}"
                keys.add(key)
                counts = {name: int(row[name]) for name in COUNTS}
                assert counts["flights"] == counts["cancelled"] + counts["diverted"] + counts["arrivals_measured"] + counts["arrival_status_missing"]
                assert counts["arrivals_measured"] == counts["on_time_arrivals"] + counts["late_arrivals"]
                rows.append(row)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (row["month"], row["marketing_carrier"])))
    print(f"{len(FILES)} months, {len(rows)} carrier-month rows, {sum(int(r['flights']) for r in rows):,} flights reconciled")


if __name__ == "__main__":
    main()
