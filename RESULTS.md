# Verified airline data slice

Source: [BTS marketing carrier on-time performance](https://transtats.bts.gov/PREZIP/).
These figures describe the downloaded January-February 2025 snapshot, not a live feed or a causal analysis.

| Month | Flights | Cancelled | Diverted | Measured arrivals | Missing arrival status | On-time among measured arrivals |
|---|---:|---:|---:|---:|---:|---:|
| 2025-01 | 599,013 | 18,740 | 1,316 | 578,957 | 0 | 81.07% |
| 2025-02 | 559,577 | 8,541 | 1,149 | 549,887 | 0 | 79.14% |

**Reconciled total:** 1,158,590 flight rows across 2 months and 10 marketing carrier codes.

The directional route transformation produces 17,291 carrier-route-month rows. Its flight, cancellation, diversion, measured-arrival, on-time, and late-arrival totals reconcile to the carrier-month aggregates for each carrier and month. The Power BI route view divides summed on-time arrivals by summed measured arrivals; it does not average route percentages.

The rate denominator excludes cancelled, diverted, and missing-status flights. It is computed from this extract and should not be presented as an exact reproduction of all published BTS measures.
Carrier-code comparisons require a coverage and operating-context review. No causal explanation or operational improvement is claimed.
