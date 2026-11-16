# CareFlow – Member 3: Analytics Engineer

This folder contains the Analytics Engineer contribution for the CareFlow Clinical Pathway Process Mining project.

## Dataset
- **Patients:** 2,000
- **Events:** 13,548
- **Format:** CSV
- **Synthetic data:** All records are generated for academic demonstration. They are not real patient records and contain no real patient identifiers.

## Member 3 responsibilities completed
1. Transition-time analysis between consecutive hospital activities.
2. Bottleneck ranking using average, median, 90th percentile and maximum transition times.
3. Repeated Triage detection, including Triage occurring after X-Ray.
4. Conformance checking against the expected pathway:
   `Triage → Doctor Consultation → Blood Test → X-Ray → Treatment → Discharge`
5. KPI validation and department/severity breakdown.

## Folder structure
```text
CareFlow_Member3/
├── data/
│   ├── hospital_event_log.csv
│   └── patient_master.csv
├── outputs/
│   ├── bottleneck_ranking.csv
│   ├── department_severity_kpis.csv
│   ├── patient_conformance_results.csv
│   ├── project_kpi_summary.csv
│   └── transition_time_analysis.csv
├── src/
│   └── member3_analytics.py
├── requirements.txt
└── README.md
```

## Run the analysis
Install dependencies:
```bash
pip install -r requirements.txt
```
From the `CareFlow_Member3` folder:
```bash
python src/member3_analytics.py
```
The script reads `data/hospital_event_log.csv` and regenerates the main analytics outputs in `outputs/`.

## Dataset columns
### hospital_event_log.csv
- `Case_ID`: unique synthetic patient visit/case identifier
- `Activity`: hospital activity
- `Timestamp`: timestamp when the activity starts
- `Event_Order`: event sequence number within the case
- `Department`, `Age`, `Gender`, `Severity`: synthetic case attributes

### patient_master.csv
One row per patient visit, including demographic fields and flags describing the generated process path.

## Important interpretation
- A repeated Triage case is a case where Triage occurs more than once.
- A post-X-Ray Triage case is a case where Triage appears after the X-Ray event.
- A case is marked conforming only when its complete activity sequence exactly matches the expected pathway. Therefore, a Triage loopback or skipped Blood Test is non-conforming.
- Transition time is the elapsed time between the start timestamp of one activity and the start timestamp of the next activity. It is an elapsed waiting/flow interval, not a direct measurement of staff service duration.
- The generator intentionally creates a Triage loopback in approximately 40% of cases to model the project problem statement. The realized percentage is reported in the KPI file.

## Reproducibility
The included dataset was generated with a fixed random seed. The CSVs are synthetic and intended for process-mining/analytics demonstrations, not clinical decision-making.
