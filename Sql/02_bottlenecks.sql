-- Week 3 | Average / median / P90 time for every transition (node-to-node), ranked.
-- e.g. "Average time from Triage to Doctor Consultation"
CREATE OR REPLACE VIEW careflow.bottlenecks AS
WITH stats AS (
  SELECT
    from_activity,
    to_activity,
    COUNT(*)                                   AS n_transitions,
    ROUND(AVG(wait_minutes), 1)                AS avg_min,
    ROUND(APPROX_QUANTILES(wait_minutes, 100)[OFFSET(50)], 1) AS median_min,
    ROUND(APPROX_QUANTILES(wait_minutes, 100)[OFFSET(90)], 1) AS p90_min,
    SUM(wait_minutes)                          AS total_min
  FROM careflow.transitions
  GROUP BY from_activity, to_activity
)
SELECT
  *,
  ROUND(100 * total_min / SUM(total_min) OVER (), 1) AS pct_of_total_wait,
  RANK() OVER (ORDER BY avg_min DESC)                AS rank_by_avg,
  RANK() OVER (ORDER BY total_min DESC)              AS rank_by_total_impact
FROM stats
WHERE n_transitions >= 30;          -- ignore rare paths
