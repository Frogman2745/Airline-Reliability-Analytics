# Airline Reliability Analytics

**Question:** How did arrival punctuality, cancellations, and diversions vary across marketing carriers in a bounded public BTS extract?

**Work:** Downloaded the official January–February 2025 monthly archives; transformed flight rows into carrier-month and directional route-month aggregates with row-balance assertions; loaded the checked carrier-month aggregates into SQLite; wrote weighted SQL queries and a portable interactive HTML dashboard. Built a Power BI report with named airlines, route and city details, a monthly comparison, and an airline-filtered route explorer.

**Verified result:** 1,158,590 source flight rows reconcile to 20 carrier-month and 17,291 carrier-route-month records across two months and ten marketing carriers. In this extract, on-time arrivals among measured completed arrivals were 81.07% in January and 79.14% in February. The denominator excludes cancelled, diverted, and missing-status flights.

**Tools:** Python, SQL/SQLite, HTML/CSS/JavaScript, and Power BI Desktop. The editable Power BI report uses a weighted DAX rate with month, airline, and route views. The static dashboard and report download are public; PostgreSQL/dbt and scheduled refresh remain future extensions.

**What a reviewer can inspect:** [Dashboard](Airline_Reliability_Dashboard.html), [editable Power BI report](Airline_Reliability_2025.pbix), [results and definitions](RESULTS.md), [SQL](queries.sql), the transformation and validation scripts, and both aggregate CSVs.

**Limits:** Two months do not establish a trend or cause. Carrier comparisons need coverage and operating-context review. This project demonstrates a reproducible analysis workflow, not an operational improvement to an airline.
