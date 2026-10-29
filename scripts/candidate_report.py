"""Read-only ranking of explicitly supplied, consistently scored candidates.

Quality and identity labels are assertions supplied by the caller, not verified
simulation provenance. Standard library only; no solver or filesystem writes.
"""

import argparse
import json
import math
import sys
from pathlib import Path

CHANNELS = ("S21", "GD", "S11", "S22")
UNITS = {"S21": "dB", "GD": "ns", "S11": "dB", "S22": "dB"}
QUALITY = {"exported": 0, "converged": 1, "precision_validated": 2}


def number(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a finite numeric value")
    if not math.isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError("Numeric value is outside the allowed range")
    return float(value)


def analyze(data, minimum_quality="exported"):
    if minimum_quality not in QUALITY:
        raise ValueError("Unknown minimum quality")
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Expected schema_version 1")
    if data.get("units") != UNITS:
        raise ValueError("Units must be S21/S11/S22=dB and GD=ns")
    identities = ("sim_id", "score_id")
    if any(not isinstance(data.get(k), str) or not data[k] for k in identities):
        raise ValueError("Explicit sim_id and score_id are required")
    try:
        scales = {k: number(data["scales"][k], True) for k in CHANNELS}
        weights = {k: number(data["weights"][k], True) for k in CHANNELS}
    except (KeyError, TypeError) as exc:
        raise ValueError("Four channel scales and weights are required") from exc
    if not isinstance(data.get("candidates"), list):
        raise ValueError("candidates must be an array")

    included, excluded, seen = [], [], {}
    for index, row in enumerate(data["candidates"]):
        reason = None
        if not isinstance(row, dict):
            reason = "not_an_object"
        elif not isinstance(row.get("id"), str) or not row["id"]:
            reason = "invalid_id"
        elif any(row.get(k) != data[k] for k in identities):
            reason = "identity_mismatch"
        elif row.get("status") != "ok":
            reason = "not_successful"
        elif row.get("quality") not in QUALITY:
            reason = "unknown_quality"
        elif QUALITY[row["quality"]] < QUALITY[minimum_quality]:
            reason = "below_minimum_quality"
        else:
            try:
                errors = {k: number(row["rmse"][k]) for k in CHANNELS}
                normalized = {k: errors[k] / scales[k] for k in CHANNELS}
                score = sum(weights[k] * normalized[k] ** 2 for k in CHANNELS) / sum(weights.values())
                if not math.isfinite(score):
                    raise ValueError("Score overflow")
            except (KeyError, TypeError, ValueError, OverflowError):
                reason = "invalid_metrics"
        if reason:
            excluded.append({"index": index, "reason": reason})
            continue
        item = {"id": row["id"], "quality": row["quality"], "rmse": errors,
                "J": score, "max_normalized_error": max(normalized.values())}
        if item["id"] in seen:
            if item != seen[item["id"]]:
                raise ValueError("Conflicting successful records for id " + item["id"])
            excluded.append({"index": index, "reason": "duplicate"})
            continue
        seen[item["id"]] = item
        included.append(item)
    if not included:
        raise ValueError("No eligible candidates")
    ranked = sorted(included, key=lambda r: (r["J"], r["id"]))
    best_metric = {k: min(included, key=lambda r: (r["rmse"][k], r["id"]))["id"] for k in CHANNELS}
    balanced = min(included, key=lambda r: (r["max_normalized_error"], r["J"], r["id"]))
    pareto = []
    for row in ranked:
        dominated = any(
            all(other["rmse"][k] <= row["rmse"][k] for k in CHANNELS)
            and any(other["rmse"][k] < row["rmse"][k] for k in CHANNELS)
            for other in included
        )
        if not dominated:
            pareto.append(row["id"])
    baseline = data.get("baseline_id")
    changes = None
    if baseline is not None:
        if baseline not in seen:
            raise ValueError("baseline_id must identify an eligible candidate")
        base = seen[baseline]
        changes = {}
        for row in ranked:
            changes[row["id"]] = {
                k: (100 * (base["rmse"][k] - row["rmse"][k]) / base["rmse"][k]
                    if base["rmse"][k] != 0 else None) for k in CHANNELS
            }
    return {
        "provenance": "caller_labels_only_not_raw_curve_verified",
        "sim_id": data["sim_id"], "score_id": data["score_id"],
        "minimum_quality": minimum_quality, "included_count": len(included),
        "excluded": excluded, "best_J": ranked[0]["id"],
        "best_by_metric": best_metric, "balanced": balanced["id"],
        "balanced_rule": "minimize maximum RMSE/scale; break ties by J then id",
        "pareto": pareto, "baseline_id": baseline,
        "metric_improvement_percent": changes, "ranked": ranked,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--minimum-quality", choices=QUALITY, default="exported")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = analyze(data, args.minimum_quality)
    except (OSError, ValueError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
