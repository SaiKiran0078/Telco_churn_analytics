"""Metrics, threshold choice and the money view of a retention campaign."""
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, precision_score, recall_score, roc_auc_score


def score(y, p, threshold=0.5) -> dict:
    pred = (p >= threshold).astype(int)
    return {
        "roc_auc": roc_auc_score(y, p), "pr_auc": average_precision_score(y, p), "brier": brier_score_loss(y, p),
        "precision": precision_score(y, pred, zero_division=0), "recall": recall_score(y, pred), "f1": f1_score(y, pred),
    }


def campaign_value(y, p, monthly, threshold, offer_cost, success_rate, horizon_months):
    """Net value of sending a retention offer to everyone with p >= threshold.

    Gain per contacted true churner = success_rate x monthly charge x horizon months.
    Cost per contacted customer (churner or not) = offer_cost.
    """
    y, p, monthly = np.asarray(y), np.asarray(p), np.asarray(monthly)
    sel = p >= threshold
    gain = (success_rate * monthly[sel & (y == 1)] * horizon_months).sum()
    cost = offer_cost * sel.sum()
    return {"contacted": int(sel.sum()), "true_churners_reached": int((sel & (y == 1)).sum()), "gain": float(gain), "cost": float(cost), "net": float(gain - cost)}


def best_threshold(y, p, monthly, **kw):
    grid = np.round(np.arange(0.05, 0.96, 0.01), 2)
    rows = [(t, campaign_value(y, p, monthly, t, **kw)) for t in grid]
    t, v = max(rows, key=lambda r: r[1]["net"])
    return float(t), v, rows
