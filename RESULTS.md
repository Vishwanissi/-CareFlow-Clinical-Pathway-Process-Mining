# Member 3 – Analytics Results

All figures below are calculated from the included synthetic dataset.

- Total patient visits: **2,000**
- Total event records: **13,548**
- Repeated Triage cases: **794 (39.70%)**
- Triage after X-Ray: **794 (39.70%)**
- Non-conforming cases: **834 (41.70%)**
- Average visit duration: **122.09 minutes**

## Longest average transitions

| From activity | To activity | Cases | Average minutes | P90 minutes |
|---|---|---:|---:|---:|
| Blood Test | X-Ray | 1960 | 30.01 | 42.00 |
| Treatment | Discharge | 2000 | 25.98 | 38.00 |
| X-Ray | Triage | 794 | 25.08 | 33.00 |
| X-Ray | Treatment | 1206 | 24.85 | 33.00 |
| Triage | Doctor Consultation | 2794 | 17.54 | 25.00 |
| Doctor Consultation | Treatment | 794 | 15.88 | 22.00 |
| Doctor Consultation | X-Ray | 40 | 12.05 | 16.00 |
| Doctor Consultation | Blood Test | 1960 | 10.94 | 16.00 |

## Notes

- The data is synthetic and created for this academic project.
- The intended loopback rate is 40%; the observed result is calculated from the generated cases.
- Conformance is strict sequence matching against the expected pathway. A skipped Blood Test or an extra Triage/Doctor loop makes a case non-conforming.
- Transition time measures elapsed time between activity start timestamps.