import pandas as pd
import pm4py
from collections import Counter
from common import load_event_log, COLS, IDEAL_VARIANTS

C, A, T = COLS["case"], COLS["activity"], COLS["ts"]


def ideal_model():
    rows = [(f"ideal_{i}", act, pd.Timestamp("2026-01-01") + pd.Timedelta(minutes=j))
            for i, v in enumerate(IDEAL_VARIANTS) for j, act in enumerate(v)]
    ideal = pm4py.format_dataframe(pd.DataFrame(rows, columns=[C, A, T]),
                                   case_id=C, activity_key=A, timestamp_key=T)
    return pm4py.discover_petri_net_inductive(ideal)


def main():
    raw = load_event_log()
    df = pm4py.format_dataframe(raw, case_id=C, activity_key=A, timestamp_key=T)
    net, im, fm = ideal_model()

    # 1) Token-based replay: fast, per-case fitness
    log = pm4py.convert_to_event_log(df)
    case_ids = [t.attributes["concept:name"] for t in log]
    tbr = pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)
    res = pd.DataFrame({
        "case_id": case_ids,
        "is_compliant": [d["trace_is_fit"] for d in tbr],
        "fitness": [round(d["trace_fitness"], 3) for d in tbr],
        "missing_tokens": [d["missing_tokens"] for d in tbr],
        "remaining_tokens": [d["remaining_tokens"] for d in tbr],
    })

    # 2) Alignments: WHICH deviations occurred (log-only move = extra step, model-only = skipped step)
    aligns = pm4py.conformance_diagnostics_alignments(log, net, im, fm)
    extra, skipped = Counter(), Counter()
    for a in aligns:
        for log_move, model_move in a["alignment"]:
            if model_move == ">>" and log_move != ">>":
                extra[log_move] += 1
            elif log_move == ">>" and model_move not in (None, ">>"):
                skipped[model_move] += 1
    res["alignment_cost"] = [a["cost"] for a in aligns]

    res.to_csv("../output/conformance_results.csv", index=False)

    print(f"Cases: {len(res)} | compliant: {res.is_compliant.mean():.1%} | avg fitness: {res.fitness.mean():.3f}")
    print("Most frequent EXTRA steps:", extra.most_common(5))
    print("Most frequent SKIPPED steps:", skipped.most_common(5))
    return res


if __name__ == "__main__":
    main()
