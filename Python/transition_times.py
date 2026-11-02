"""Week 3 | Pandas twin of sql/01-03. Used to cross-check the SQL results (KPI validation)."""
import pandas as pd
from common import load_event_log, COLS

C, A, T = COLS["case"], COLS["activity"], COLS["ts"]


def transitions(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(C)
    out = df.assign(to_activity=g[A].shift(-1), to_ts=g[T].shift(-1)).dropna(subset=["to_activity"])
    out["wait_minutes"] = (out["to_ts"] - out[T]).dt.total_seconds() / 60
    return out.rename(columns={A: "from_activity"})


def bottlenecks(tr: pd.DataFrame, min_n=30) -> pd.DataFrame:
    s = (tr.groupby(["from_activity", "to_activity"])["wait_minutes"]
           .agg(n="count", avg="mean", median="median", p90=lambda x: x.quantile(.9), total="sum")
           .query("n >= @min_n"))
    s["pct_of_total_wait"] = 100 * s["total"] / s["total"].sum()
    return s.sort_values("avg", ascending=False).round(1)


def loopback_stats(df: pd.DataFrame, tr: pd.DataFrame) -> dict:
    looped = set(tr.loc[(tr.from_activity == "X-Ray") & (tr.to_activity == "Triage"), C])
    dur = df.groupby(C)[T].agg(lambda x: (x.max() - x.min()).total_seconds() / 60)
    is_loop = dur.index.isin(looped)
    return {
        "total_cases": len(dur),
        "pct_looped": round(100 * is_loop.mean(), 1),
        "avg_min_looped": round(dur[is_loop].mean(), 1),
        "avg_min_clean": round(dur[~is_loop].mean(), 1),
        "extra_min_per_looped_case": round(dur[is_loop].mean() - dur[~is_loop].mean(), 1),
        "projected_avg_after_fix": round(
            dur.mean() - is_loop.mean() * (dur[is_loop].mean() - dur[~is_loop].mean()), 1),
    }


if __name__ == "__main__":
    df = load_event_log()
    tr = transitions(df)
    b = bottlenecks(tr)
    print(b.head(10).to_string())
    print(loopback_stats(df, tr))
    b.to_csv("../output/bottlenecks_python.csv")
