import pandas as pd


def _smooth(series: pd.Series, alpha: float = 0.35) -> float:
    level = float(series.iloc[0])
    for value in series.iloc[1:]:
        level = alpha * float(value) + (1 - alpha) * level
    return level


def forecast_reimbursement(variance: pd.DataFrame, horizon: int = 3) -> pd.DataFrame:
    monthly = variance.groupby("service_month").agg(
        monthly_reimbursement_spend=("contract_total_paid", "sum"),
        monthly_benchmark_variance=("total_financial_variance", "sum"),
        provider_exposure=("total_financial_variance", lambda s: s.abs().sum()),
    ).reset_index().sort_values("service_month")
    rows = []
    future_months = pd.date_range(monthly["service_month"].max() + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    for metric in ["monthly_reimbursement_spend", "monthly_benchmark_variance", "provider_exposure"]:
        series = monthly[metric].astype(float)
        rolling = series.tail(3).mean()
        smoothed = _smooth(series)
        slope = (series.tail(6).iloc[-1] - series.tail(6).iloc[0]) / max(len(series.tail(6)) - 1, 1)
        for step, month in enumerate(future_months, 1):
            rows.append(
                {
                    "forecast_month": month,
                    "metric": metric,
                    "forecast_value": (0.55 * smoothed) + (0.45 * rolling) + slope * step,
                    "method": "rolling average + exponential smoothing",
                }
            )
    return pd.DataFrame(rows), monthly
