import numpy as np
import pandas as pd


def add_provider_risk(provider: pd.DataFrame) -> pd.DataFrame:
    frame = provider.copy()
    frame["reimbursement_risk_score"] = frame["reimbursement_risk_score"].clip(0, 100)
    frame["risk_tier"] = np.select(
        [
            frame["reimbursement_risk_score"] >= 75,
            frame["reimbursement_risk_score"] >= 55,
            frame["reimbursement_risk_score"] >= 35,
        ],
        ["Critical", "High", "Moderate"],
        default="Low",
    )
    return frame.sort_values("reimbursement_risk_score", ascending=False)
