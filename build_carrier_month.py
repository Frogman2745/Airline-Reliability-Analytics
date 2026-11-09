"""Stream one BTS monthly archive into a checked carrier-month summary."""

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def main(year: int, month: int) -> None:
    source = ROOT / f"data/raw/bts_marketing_{year}_{month:02d}.zip"
    out = ROOT / f"data/carrier_month_{year}_{month:02d}.csv"
    totals = defaultdict(lambda: defaultdict(int))
    with zipfile.ZipFile(source) as archive:
        bad = archive.testzip()
        assert bad is None, f"corrupt archive member: {bad}"
        csv_name = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
        with archive.open(csv_name) as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
            required = {"Year", "Month", "Marketing_Airline_Network", "ArrDel15", "Cancelled", "Diverted"}
            assert required.issubset(reader.fieldnames), "missing required columns"
            for row in reader:
                assert (row["Year"], row["Month"]) == (str(year), str(month))
                carrier = row["Marketing_Airline_Network"].strip()
                assert carrier, "missing marketing carrier"
                t = totals[carrier]
                t["flights"] += 1
                if row["Cancelled"] == "1.00" or row["Cancelled"] == "1":
                    t["cancelled"] += 1
                elif row["Diverted"] == "1.00" or row["Diverted"] == "1":
                    t["diverted"] += 1
                elif row["ArrDel15"] in ("0.00", "0", "1.00", "1"):
                    t["arrivals_measured"] += 1
                    if row["ArrDel15"] in ("0.00", "0"):
                        t["on_time_arrivals"] += 1
                    else:
                        t["late_arrivals"] += 1
                else:
                    t["arrival_status_missing"] += 1

    fields = ["month", "marketing_carrier", "flights", "cancelled", "diverted", "arrivals_measured", "on_time_arrivals", "late_arrivals", "arrival_status_missing", "on_time_rate_completed"]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for carrier, t in sorted(totals.items()):
            assert t["flights"] == sum(t[k] for k in ("cancelled", "diverted", "arrivals_measured", "arrival_status_missing")), carrier
            assert t["arrivals_measured"] == t["on_time_arrivals"] + t["late_arrivals"], carrier
            writer.writerow({"month": f"{year}-{month:02d}", "marketing_carrier": carrier, **{k: t[k] for k in fields[2:-1]}, "on_time_rate_completed": round(t["on_time_arrivals"] / t["arrivals_measured"], 6) if t["arrivals_measured"] else ""})
    with source.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    print(json.dumps({"source_sha256": digest, "carriers": len(totals), "flights": sum(t["flights"] for t in totals.values()), "output": str(out)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int, nargs="?", default=2025)
    parser.add_argument("month", type=int, nargs="?", default=1)
    args = parser.parse_args()
    main(args.year, args.month)
