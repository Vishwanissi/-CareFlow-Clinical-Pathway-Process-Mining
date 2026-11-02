
-- Also quantifies what the loop costs, i.e. the "reduce wait by ~20 min" claim.
CREATE OR REPLACE VIEW careflow.case_flags AS
WITH per_case AS (
  SELECT
    case_id,
    COUNTIF(activity_name = 'Triage')                  AS triage_count,
    MIN(event_timestamp)                               AS case_start,
    MAX(event_timestamp)                               AS case_end
  FROM careflow.event_log_clean
  GROUP BY case_id
),
loopbacks AS (
  SELECT DISTINCT case_id, TRUE AS xray_to_triage
  FROM careflow.transitions
  WHERE from_activity = 'X-Ray' AND to_activity = 'Triage'
)
SELECT
  p.case_id,
  p.triage_count,
  p.triage_count > 1                                   AS repeated_triage,
  COALESCE(l.xray_to_triage, FALSE)                    AS xray_to_triage_loop,
  TIMESTAMP_DIFF(p.case_end, p.case_start, MINUTE)     AS total_minutes
FROM per_case p
LEFT JOIN loopbacks l USING (case_id);

-- Headline numbers (run separately)
SELECT
  COUNT(*)                                             AS total_cases,
  COUNTIF(xray_to_triage_loop)                         AS looped_cases,
  ROUND(100 * COUNTIF(xray_to_triage_loop) / COUNT(*), 1) AS pct_looped,
  ROUND(AVG(IF(xray_to_triage_loop, total_minutes, NULL)), 1)     AS avg_min_looped,
  ROUND(AVG(IF(NOT xray_to_triage_loop, total_minutes, NULL)), 1) AS avg_min_clean,
  ROUND(AVG(IF(xray_to_triage_loop, total_minutes, NULL))
      - AVG(IF(NOT xray_to_triage_loop, total_minutes, NULL)), 1) AS extra_min_per_looped_case,
  -- overall average if looped cases behaved like clean ones
  ROUND(AVG(total_minutes)
      - (COUNTIF(xray_to_triage_loop) / COUNT(*))
        * (AVG(IF(xray_to_triage_loop, total_minutes, NULL))
         - AVG(IF(NOT xray_to_triage_loop, total_minutes, NULL))), 1) AS projected_avg_min_after_fix
FROM careflow.case_flags;
