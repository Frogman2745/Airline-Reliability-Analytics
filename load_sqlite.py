"""Load the checked aggregate into a local SQL database for reproducible queries."""

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data/carrier_month_combined.csv"
DB = ROOT / "data/airline_reliability.sqlite3"
FIELDS = ("month", "marketing_carrier", "flights", "cancelled", "diverted", "arrivals_measured", "on_time_arrivals", "late_arrivals", "arrival_status_missing")


def main():
    with SOURCE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    db = sqlite3.connect(DB)
    try:
        with db:
            db.execute("DROP TABLE IF EXISTS carrier_month")
            db.execute("""CREATE TABLE carrier_month (
                month TEXT NOT NULL CHECK(month GLOB '????-??'),
                marketing_carrier TEXT NOT NULL,
                flights INTEGER NOT NULL CHECK(flights >= 0),
                cancelled INTEGER NOT NULL CHECK(cancelled >= 0),
                diverted INTEGER NOT NULL CHECK(diverted >= 0),
                arrivals_measured INTEGER NOT NULL CHECK(arrivals_measured >= 0),
                on_time_arrivals INTEGER NOT NULL CHECK(on_time_arrivals >= 0),
                late_arrivals INTEGER NOT NULL CHECK(late_arrivals >= 0),
                arrival_status_missing INTEGER NOT NULL CHECK(arrival_status_missing >= 0),
                PRIMARY KEY(month, marketing_carrier),
                CHECK(flights = cancelled + diverted + arrivals_measured + arrival_status_missing),
                CHECK(arrivals_measured = on_time_arrivals + late_arrivals)
            )""")
            db.executemany("INSERT INTO carrier_month VALUES (?,?,?,?,?,?,?,?,?)", [tuple(row[k] for k in FIELDS) for row in rows])
        result = db.execute("SELECT COUNT(*), SUM(flights), COUNT(DISTINCT month) FROM carrier_month").fetchone()
        assert result == (len(rows), sum(int(row["flights"]) for row in rows), len({row["month"] for row in rows}))
        print(f"SQL load verified: {result[0]} carrier-month rows, {result[1]:,} flights, {result[2]} months")
    finally:
        db.close()


if __name__ == "__main__":
    main()
