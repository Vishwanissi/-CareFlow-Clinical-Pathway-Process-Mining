"""
CareFlow - Member 3 Analytics Engineer
Run from the project root:
    python src/member3_analytics.py

Input:
    data/hospital_event_log.csv
Output:
    outputs/*.csv
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "hospital_event_log.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["Timestamp"])
df = df.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)

# 1) Transition-time analysis
df["Next_Activity"] = df.groupby("Case_ID")["Activity"].shift(-1)
df["Next_Timestamp"] = df.groupby("Case_ID")["Timestamp"].shift(-1)
df["Transition_Minutes"] = (
    df["Next_Timestamp"] - df["Timestamp"]
).dt.total_seconds() / 60

transition = (
    df.dropna(subset=["Next_Activity"])
      .groupby(["Activity", "Next_Activity"], as_index=False)
      .agg(Transition_Count=("Case_ID", "count"),
           Avg_Transition_Minutes=("Transition_Minutes", "mean"),
           Median_Transition_Minutes=("Transition_Minutes", "median"),
           P90_Transition_Minutes=("Transition_Minutes", lambda x: x.quantile(.90)),
           Max_Transition_Minutes=("Transition_Minutes", "max"))
      .sort_values("Avg_Transition_Minutes", ascending=False)
)
transition.to_csv(OUT / "transition_time_analysis.csv", index=False)

# 2) Patient-level journey, repeated triage and conformance
expected = ["Triage", "Doctor Consultation", "Blood Test", "X-Ray", "Treatment", "Discharge"]
rows = []
for case_id, group in df.groupby("Case_ID"):
    journey = group["Activity"].tolist()
    xray_index = journey.index("X-Ray") if "X-Ray" in journey else -1
    repeated = journey.count("Triage") > 1
    post_xray = xray_index >= 0 and "Triage" in journey[xray_index + 1:]
    rows.append({
        "Case_ID": case_id,
        "Actual_Journey": " > ".join(journey),
        "Expected_Journey": " > ".join(expected),
        "Triage_Count": journey.count("Triage"),
        "Repeated_Triage": repeated,
        "Post_XRay_Triage": post_xray,
        "Conformance_Status": "Conforming" if journey == expected else "Non-Conforming",
        "Total_Visit_Minutes": (group["Timestamp"].max() - group["Timestamp"].min()).total_seconds()/60,
        "Event_Count": len(journey)
    })
cases = pd.DataFrame(rows)
cases.to_csv(OUT / "patient_conformance_results.csv", index=False)

# 3) KPI validation
n = len(cases)
repeat_n = int(cases["Repeated_Triage"].sum())
post_xray_n = int(cases["Post_XRay_Triage"].sum())
nonconf_n = int((cases["Conformance_Status"] == "Non-Conforming").sum())
kpis = pd.DataFrame([
    ["Total Patients", n, "patients"],
    ["Patients with Repeated Triage", repeat_n, "patients"],
    ["Repeated Triage Rate", repeat_n/n*100, "%"],
    ["Patients with Triage After X-Ray", post_xray_n, "patients"],
    ["Post X-Ray Triage Rate", post_xray_n/n*100, "%"],
    ["Non-Conforming Cases", nonconf_n, "patients"],
    ["Conformance Rate", (n-nonconf_n)/n*100, "%"],
    ["Average Visit Duration", cases["Total_Visit_Minutes"].mean(), "minutes"],
], columns=["KPI", "Value", "Unit"])
kpis.to_csv(OUT / "project_kpi_summary.csv", index=False)

# 4) Department and severity breakdown for dashboard filters
attributes = (df.sort_values("Timestamp")
                .groupby("Case_ID", as_index=False)
                .first()[["Case_ID", "Department", "Severity"]])
case_breakdown = cases.merge(attributes, on="Case_ID", how="left")
department_kpis = (
    case_breakdown.groupby(["Department", "Severity"], as_index=False)
    .agg(Patient_Count=("Case_ID", "count"),
         Avg_Visit_Minutes=("Total_Visit_Minutes", "mean"),
         Repeated_Triage_Rate=("Repeated_Triage", "mean"),
         Non_Conformance_Rate=("Conformance_Status",
                               lambda x: (x == "Non-Conforming").mean()))
)
department_kpis.to_csv(OUT / "department_severity_kpis.csv", index=False)

# 5) Bottleneck ranking
transition["Bottleneck_Rank"] = range(1, len(transition)+1)
transition.to_csv(OUT / "bottleneck_ranking.csv", index=False)

print(f"Analytics completed for {n} patients.")
print(kpis.to_string(index=False))
