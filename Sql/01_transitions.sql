-- Week 3 | Transition times between consecutive activities, per case.
-- Input : careflow.event_log_clean (case_id, activity_name, event_timestamp)  <- Member 1's dbt output
-- Output: careflow.transitions (one row per hop)
CREATE OR REPLACE VIEW careflow.transitions AS
WITH ordered AS (
  SELECT
    case_id,
    activity_name,
    event_timestamp,
    LEAD(activity_name)   OVER w AS next_activity,
    LEAD(event_timestamp) OVER w AS next_timestamp,
    ROW_NUMBER()          OVER w AS step_no
  FROM careflow.event_log_clean
  WINDOW w AS (PARTITION BY case_id ORDER BY event_timestamp, activity_name)
)
SELECT
  case_id,
  step_no,
  activity_name  AS from_activity,
  next_activity  AS to_activity,
  event_timestamp AS from_ts,
  next_timestamp  AS to_ts,
  TIMESTAMP_DIFF(next_timestamp, event_timestamp, SECOND) / 60.0 AS wait_minutes
FROM ordered
WHERE next_activity IS NOT NULL;
