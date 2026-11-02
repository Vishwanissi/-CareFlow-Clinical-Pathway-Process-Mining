-- Week 4 | KPI definitions + data-quality checks. Hand careflow.kpi_summary to Member 4 for Power BI.
CREATE OR REPLACE VIEW careflow.kpi_summary AS
SELECT
  COUNT(*)                                              AS total_cases,
  ROUND(AVG(f.total_minutes), 1)                        AS avg_total_minutes,
  ROUND(APPROX_QUANTILES(f.total_minutes, 100)[OFFSET(50)], 1) AS median_total_minutes,
  ROUND(APPROX_QUANTILES(f.total_minutes, 100)[OFFSET(90)], 1) AS p90_total_minutes,
  ROUND(100 * COUNTIF(c.is_compliant) / COUNT(*), 1)    AS pct_compliant,
  ROUND(100 * COUNTIF(f.xray_to_triage_loop) / COUNT(*), 1) AS pct_xray_triage_loop,
  ROUND(100 * COUNTIF(f.repeated_triage) / COUNT(*), 1) AS pct_repeated_triage
FROM careflow.case_flags f
JOIN careflow.case_conformance c USING (case_id);

-- Validation checks (run separately): every row should say PASS
WITH checks AS (
  SELECT 'case count: raw vs clean' AS check_name,
         (SELECT COUNT(DISTINCT case_id) FROM careflow.event_log_raw)  AS expected,
         (SELECT COUNT(DISTINCT case_id) FROM careflow.event_log_clean) AS actual
  UNION ALL
  SELECT 'null case_id/activity/timestamp rows', 0,
         (SELECT COUNT(*) FROM careflow.event_log_clean
          WHERE case_id IS NULL OR activity_name IS NULL OR event_timestamp IS NULL)
  UNION ALL
  SELECT 'negative transition times', 0,
         (SELECT COUNT(*) FROM careflow.transitions WHERE wait_minutes < 0)
  UNION ALL
  SELECT 'duplicate events (same case, activity, timestamp)', 0,
         (SELECT COUNT(*) FROM (
            SELECT case_id, activity_name, event_timestamp
            FROM careflow.event_log_clean
            GROUP BY 1,2,3 HAVING COUNT(*) > 1))
  UNION ALL
  SELECT 'sum of hops = sum of case durations (minutes, rounded)',
         (SELECT CAST(ROUND(SUM(total_minutes)) AS INT64) FROM careflow.case_flags),
         (SELECT CAST(ROUND(SUM(wait_minutes)) AS INT64) FROM careflow.transitions)
)
SELECT *, IF(expected = actual, 'PASS', 'FAIL') AS status FROM checks;
