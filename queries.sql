-- Completed-arrival rate is weighted by measured arrivals, not averaged across months.
SELECT marketing_carrier,
       SUM(flights) AS flights,
       SUM(cancelled) AS cancelled,
       SUM(diverted) AS diverted,
       ROUND(100.0 * SUM(on_time_arrivals) / NULLIF(SUM(arrivals_measured), 0), 2) AS on_time_pct_completed
FROM carrier_month
GROUP BY marketing_carrier
ORDER BY on_time_pct_completed DESC;

-- Source reconciliation by month.
SELECT month, SUM(flights) AS flights,
       SUM(cancelled) AS cancelled,
       SUM(diverted) AS diverted,
       SUM(arrivals_measured) AS measured_arrivals,
       SUM(arrival_status_missing) AS missing_arrival_status
FROM carrier_month
GROUP BY month
ORDER BY month;
