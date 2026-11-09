# Airline Reliability Analytics Pipeline

**Status:** January–February 2025 source months ingested, reconciled, and loaded into a local SQLite database. A portable HTML dashboard and an editable Power BI report are published with the [portfolio case study](https://froghausstudios.com/work/airline-reliability-analytics). The analysis is a bounded, static extract; there is no scheduled refresh.

## Question

How do on-time performance and reported delay causes vary by carrier and month, and what operational patterns can be described without overstating causality?

## Public source

Use the U.S. Bureau of Transportation Statistics' [marketing carrier on-time performance dataset](https://catalog.data.gov/dataset/u-s-marketing-air-carriers-on-time-performance). Its on-time definition is arrival within 15 minutes of schedule. Check the source's reporting-carrier coverage rules and publication lag before comparing periods.

## Planned workflow

1. Download a bounded period of source data with Python and preserve a dated raw snapshot plus source URL.
2. Load the snapshot into PostgreSQL and document table keys, missing values, and refresh behavior.
3. Transform carrier-month metrics with SQL/dbt, including tests for keys, dates, ranges, and reconciliation to source totals.
4. Connect Power BI to PostgreSQL and build a small decision-oriented report with definitions and data-quality notes.
5. Add a scheduled refresh or repeatable local run, then document what actually ran and what remains manual.

This adds a public-source ingest, PostgreSQL, dbt, quality tests, and repeatable refresh to the SQL/Python/Power BI work in the synthetic reconciliation project. Power BI's [PostgreSQL connector](https://learn.microsoft.com/en-us/power-query/connectors/postgresql) and [dbt data tests](https://docs.getdbt.com/docs/build/data-tests) support the proposed stack.

## First deliverable

A source inventory and a single validated carrier-month table for a fixed date window.

### January 2025 verified slice

- Official BTS TranStats marketing-carrier prezip: https://transtats.bts.gov/PREZIP/On_Time_Marketing_Carrier_On_Time_Performance_Beginning_January_2018_2025_1.zip
- Raw snapshot: `data/raw/bts_marketing_2025_01.zip` (31,599,374 bytes); SHA-256 `0feaabdbc9e4bd851ef717f342678cdcc5ea0822dd706359aab030bb1a5d1c24`.
- Reproducible transformation: `python build_carrier_month.py`.
- Output: `data/carrier_month_2025_01.csv`; 599,013 flight rows, 10 marketing-carrier rows.
- Each carrier's flight count equals cancelled + diverted + measured completed arrivals + missing arrival status. Measured arrivals equal on-time + late arrivals. All assertions passed; missing arrival status was zero in this month.
- `on_time_rate_completed` means on-time arrivals divided by measured completed arrivals. Cancelled and diverted flights are reported separately, not silently treated as on-time or late. This is a project-specific rate and should not be passed off as an exact reproduction of every BTS published metric.

### February 2025 and combined slice

The February 2025 BTS archive was downloaded (`data/raw/bts_marketing_2025_02.zip`, 29,442,140 bytes, SHA-256 `080ad48e2826a6b4c3f39690f75a08dea9ad4e0831ff82958656cdb61693dd15`) and processed. `python build_carrier_month.py 2025 2` regenerates that month; `python combine_months.py` regenerates the combined 20-row file. It reconciles to 1,158,590 flights across January and February 2025. Raw archives remain local and are excluded from source control.

PostgreSQL/dbt and scheduled refresh are still extensions. Carrier coverage and data publication lag must be called out in any comparison.

### Local SQL proof

Run `python load_sqlite.py` to load the combined CSV into a local SQLite database with carrier-month uniqueness and row-balance constraints. The load currently verifies 20 rows and 1,158,590 flights over two months. `queries.sql` contains weighted on-time and source-reconciliation queries. PostgreSQL is still a planned extension; this local SQLite run is not evidence that PostgreSQL has been deployed.

Run `python report.py` to regenerate [the bounded results summary](RESULTS.md) from the checked SQL table.

### Portfolio dashboard

Run `python build_dashboard.py` to regenerate [the standalone interactive dashboard](Airline_Reliability_Dashboard.html) from the checked combined CSV and route table, then open that HTML file in a browser. The [published dashboard](https://froghausstudios.com/downloads/airline-reliability-dashboard.html) needs no external JavaScript library. Its filters recompute the on-time rate from summed arrivals rather than averaging carrier-month percentages. The HTML embeds 20 carrier-month rows and 17,291 directional carrier-route-month rows, not the raw flight records. It includes airline names and a route explorer with city, airport, airline, and month filters. The dashboard is descriptive and does not imply causal findings or operational improvements.

### Editable Power BI report

`Airline_Reliability_2025.pbix` imports the checked 20-row carrier-month CSV and the 17,291-row directional carrier-route-month CSV. Its rate measures divide summed on-time arrivals by summed measured arrivals, so grouped comparisons are weighted. The first page compares named airlines and displays a monthly trend. The Route Explorer page adds an airline slicer and a sortable table with airline name, directional route, origin and destination cities, flights, and weighted on-time rate. Route rows reconcile to 1,158,590 flights. The report was saved in Power BI Desktop on November 8, 2026. The Power BI source paths point to local CSV files; after extracting the ZIP elsewhere, update the source paths before refreshing. The portable HTML dashboard remains the easiest artifact to inspect without Power BI Desktop.

Run `python build_route_month.py` to regenerate the route table and carrier lookup from the raw BTS archives; it checks every carrier-month count against the existing aggregate. For a handoff, include `Airline_Reliability_2025.pbix`, `Airline_Reliability_Dashboard.html`, `RESULTS.md`, this README, the scripts, `queries.sql`, and the aggregate CSVs. The raw BTS ZIPs are available from the cited official source and are deliberately excluded from the lightweight handoff. The static dashboard and Power BI download are public; no live data service or PostgreSQL/dbt pipeline is claimed.
