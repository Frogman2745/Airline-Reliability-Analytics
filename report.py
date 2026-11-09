"""Write a reproducible, bounded summary from the checked local SQL table."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data/airline_reliability.sqlite3"
OUT = ROOT / "RESULTS.md"


def main():
    if not DB.exists():
        raise FileNotFoundError("Run python load_sqlite.py first")
    with sqlite3.connect(DB) as db:
        months = db.execute("""SELECT month, SUM(flights), SUM(cancelled), SUM(diverted),
                            SUM(arrivals_measured), SUM(on_time_arrivals), SUM(late_arrivals),
                            SUM(arrival_status_missing) FROM carrier_month GROUP BY month ORDER BY month""").fetchall()
        carriers = db.execute("""SELECT marketing_carrier, SUM(flights), SUM(arrivals_measured),
                              SUM(on_time_arrivals) FROM carrier_month GROUP BY marketing_carrier
                              ORDER BY marketing_carrier""").fetchall()
    if not months or len(carriers) != 10:
        raise ValueError("Expected a nonempty two-month slice with ten carrier codes")
    for month, flights, cancelled, diverted, measured, on_time, late, missing in months:
        if flights != cancelled + diverted + measured + missing or measured != on_time + late:
            raise ValueError(f"Source totals do not reconcile for {month}")
    lines = ["# Verified airline data slice", "", "Source: [BTS marketing carrier on-time performance](https://transtats.bts.gov/PREZIP/).",
             "These figures describe the downloaded January-February 2025 snapshot, not a live feed or a causal analysis.", "",
             "| Month | Flights | Cancelled | Diverted | Measured arrivals | Missing arrival status | On-time among measured arrivals |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for month, flights, cancelled, diverted, measured, on_time, late, missing in months:
        lines.append(f"| {month} | {flights:,} | {cancelled:,} | {diverted:,} | {measured:,} | {missing:,} | {100 * on_time / measured:.2f}% |")
    lines += ["", f"**Reconciled total:** {sum(row[1] for row in months):,} flight rows across {len(months)} months and {len(carriers)} marketing carrier codes.",
              "", "The rate denominator excludes cancelled, diverted, and missing-status flights. It is computed from this extract and should not be presented as an exact reproduction of all published BTS measures.",
              "Carrier-code comparisons require a coverage and operating-context review. No causal explanation or operational improvement is claimed.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.name}: {len(months)} months, {sum(row[1] for row in months):,} reconciled flights")


if __name__ == "__main__":
    main()
