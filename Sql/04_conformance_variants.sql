CREATE OR REPLACE VIEW careflow.case_conformance AS
WITH params AS (
  SELECT
    ['Registration','Triage','Doctor Consultation','X-Ray','Doctor Review','Discharge'] AS ideal,
    ['Registration','Triage','Doctor Consultation','Discharge']                         AS ideal_no_xray
),
variants AS (
  SELECT
    case_id,
    ARRAY_AGG(activity_name ORDER BY event_timestamp, activity_name) AS path
  FROM careflow.event_log_clean
  GROUP BY case_id
)
SELECT
  v.case_id,
  ARRAY_TO_STRING(v.path, ' > ')                         AS variant,
  ARRAY_LENGTH(v.path)                                   AS n_events,
  (TO_JSON_STRING(v.path) IN (TO_JSON_STRING(p.ideal), TO_JSON_STRING(p.ideal_no_xray))) AS is_compliant,
  (SELECT COUNT(1) FROM UNNEST(p.ideal) a
     WHERE a NOT IN UNNEST(v.path) AND a != 'X-Ray')     AS missing_mandatory_steps,
  ARRAY_LENGTH(v.path) - (SELECT COUNT(DISTINCT x) FROM UNNEST(v.path) x) AS repeated_steps,
  v.path[SAFE_OFFSET(0)] != 'Registration'               AS bad_start,
  v.path[SAFE_OFFSET(ARRAY_LENGTH(v.path) - 1)] != 'Discharge' AS bad_end
FROM variants v CROSS JOIN params p;

-- Top variants (run separately): happy path vs. "spaghetti"
SELECT
  variant,
  COUNT(*)                                        AS n_cases,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_cases,
  ANY_VALUE(is_compliant)                         AS is_compliant
FROM careflow.case_conformance
GROUP BY variant
ORDER BY n_cases DESC
LIMIT 20;
