"""Stream the two verified BTS archives into directional carrier-route-month counts."""

import csv
import io
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "route_month_combined.csv"
CARRIER_OUTPUT = ROOT / "data" / "dim_carrier.csv"
CARRIER_NAMES = {
    "AA": "American Airlines", "AS": "Alaska Airlines", "B6": "JetBlue Airways",
    "DL": "Delta Air Lines", "F9": "Frontier Airlines", "G4": "Allegiant Air",
    "HA": "Hawaiian Airlines", "NK": "Spirit Airlines", "UA": "United Airlines",
    "WN": "Southwest Airlines",
}
COUNT_FIELDS = ("flights", "cancelled", "diverted", "arrivals_measured", "on_time_arrivals", "late_arrivals", "arrival_status_missing")


def main():
    totals = defaultdict(lambda: defaultdict(int))
    names = {}
    archive_totals = defaultdict(int)
    for month_num in (1, 2):
        path = RAW / f"bts_marketing_2025_{month_num:02d}.zip"
        with zipfile.ZipFile(path) as archive:
            member = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
            with archive.open(member) as raw:
                reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
                needed = {"Year", "Month", "Marketing_Airline_Network", "Origin", "Dest", "OriginCityName", "DestCityName", "Cancelled", "Diverted", "ArrDel15"}
                if not needed.issubset(reader.fieldnames):
                    raise ValueError(f"Missing BTS columns: {needed - set(reader.fieldnames)}")
                for row in reader:
                    if (row["Year"], row["Month"]) != ("2025", str(month_num)):
                        raise ValueError("Unexpected source month")
                    code, origin, dest = (row[f].strip() for f in ("Marketing_Airline_Network", "Origin", "Dest"))
                    if not code or not origin or not dest:
                        raise ValueError("Missing carrier or route endpoint")
                    key = (f"2025-{month_num:02d}", code, origin, dest)
                    city_pair = (row["OriginCityName"].strip(), row["DestCityName"].strip())
                    if key in names and names[key] != city_pair:
                        raise ValueError(f"Conflicting route names: {key}")
                    names[key] = city_pair
                    t = totals[key]
                    t["flights"] += 1
                    archive_totals[month_num] += 1
                    if row["Cancelled"] in ("1.00", "1"):
                        t["cancelled"] += 1
                    elif row["Diverted"] in ("1.00", "1"):
                        t["diverted"] += 1
                    elif row["ArrDel15"] in ("0.00", "0", "1.00", "1"):
                        t["arrivals_measured"] += 1
                        t["on_time_arrivals" if row["ArrDel15"] in ("0.00", "0") else "late_arrivals"] += 1
                    else:
                        t["arrival_status_missing"] += 1
    carrier_totals = defaultdict(lambda: defaultdict(int))
    fields = ["month", "marketing_carrier", "carrier_name", "origin", "destination", "origin_city", "destination_city", "route", *COUNT_FIELDS]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for key in sorted(totals):
            month, code, origin, dest = key
            if code not in CARRIER_NAMES:
                raise ValueError(f"Unknown carrier: {code}")
            t = totals[key]
            if t["flights"] != sum(t[k] for k in ("cancelled", "diverted", "arrivals_measured", "arrival_status_missing")):
                raise ValueError(f"Flight balance failed: {key}")
            if t["arrivals_measured"] != t["on_time_arrivals"] + t["late_arrivals"]:
                raise ValueError(f"Arrival balance failed: {key}")
            for field in COUNT_FIELDS:
                carrier_totals[(month, code)][field] += t[field]
            origin_city, dest_city = names[key]
            writer.writerow({"month": month, "marketing_carrier": code, "carrier_name": CARRIER_NAMES[code],
                             "origin": origin, "destination": dest, "origin_city": origin_city,
                             "destination_city": dest_city, "route": f"{origin} → {dest}",
                             **{field: t[field] for field in COUNT_FIELDS}})
    with (ROOT / "data/carrier_month_combined.csv").open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle))
    if set(carrier_totals) != {(r["month"], r["marketing_carrier"]) for r in source}:
        raise ValueError("Carrier-month key mismatch")
    for row in source:
        key = (row["month"], row["marketing_carrier"])
        for field in COUNT_FIELDS:
            if carrier_totals[key][field] != int(row[field]):
                raise ValueError(f"Carrier-month reconciliation failed: {key} {field}")
    with CARRIER_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("marketing_carrier", "carrier_name"))
        writer.writerows(sorted(CARRIER_NAMES.items()))
    print(f"Reconciled {len(totals):,} directional carrier-route-month rows; "
          f"January {archive_totals[1]:,}, February {archive_totals[2]:,} flights")


if __name__ == "__main__":
    main()
