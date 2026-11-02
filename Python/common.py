import os
import pandas as pd

COLS = {"case": "case_id", "activity": "activity_name", "ts": "event_timestamp"}
IDEAL_VARIANTS = [
    ["Registration", "Triage", "Doctor Consultation", "X-Ray", "Doctor Review", "Discharge"],
    ["Registration", "Triage", "Doctor Consultation", "Discharge"],
]  # edit to match Member 2's activity names


def load_event_log(csv_path="../data/sample_event_log.csv") -> pd.DataFrame:
    if os.getenv("CAREFLOW_SOURCE") == "bigquery":
        from google.cloud import bigquery
        df = bigquery.Client().query(
            "SELECT case_id, activity_name, event_timestamp FROM careflow.event_log_clean"
        ).to_dataframe()
    else:
        df = pd.read_csv(csv_path)
    df[COLS["ts"]] = pd.to_datetime(df[COLS["ts"]])
    return df.sort_values([COLS["case"], COLS["ts"]]).reset_index(drop=True)
