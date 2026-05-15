"""Spike D — Calibration policy on toy data.

Validates the calibration math that powers the audit-the-auditor wow moment:
  - Generate 100 synthetic examples of (hat, criterion, evidence_depth,
    predicted_score, ground_truth_score) with a known bias pattern
  - Compute per-(hat, criterion, evidence_depth_bucket) mean_delta from
    the training half (50 examples)
  - Apply calibration policy on held-out half (50 examples):
        new_score = clip(predicted - 0.8 * mean_delta, anchor_p25, anchor_p75)
  - Compare calibrated MAE vs uncalibrated MAE

PASS criterion:
  - Calibrated MAE ≤ 0.85 × uncalibrated MAE on held-out (≥15% improvement)
  - Policy doesn't catastrophically over-correct (no point worse by >2.0)
"""

import json
import random
import statistics
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def synth_dataset(n: int = 100, seed: int = 42):
    """Yellow over-confident on A1 when evidence_depth low.
    Black calibrated. Both hats on B2 also calibrated.
    Ground truth ~ N(predicted - bias(hat,criterion,depth), 0.4)."""
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        hat = rng.choice(["yellow", "yellow", "yellow", "black", "black"])
        criterion = rng.choice(["A1", "A1", "A1", "B2"])
        depth = round(rng.uniform(0.1, 0.9), 2)
        # ground truth roughly uniform [4, 9]
        gt = round(rng.uniform(4.0, 9.0), 2)
        # predicted = gt + bias(hat, criterion, depth) + noise
        bias = 0.0
        if hat == "yellow" and criterion == "A1" and depth < 0.4:
            bias = 1.4  # over-confident
        elif hat == "yellow" and criterion == "A1":
            bias = 0.3  # mild over-confidence at higher depth
        # add small symmetric noise
        noise = rng.gauss(0, 0.25)
        predicted = round(max(0, min(10, gt + bias + noise)), 2)
        rows.append(
            {
                "hat": hat,
                "criterion": criterion,
                "evidence_depth": depth,
                "evidence_depth_bucket": "<0.4" if depth < 0.4 else ">=0.4",
                "predicted_score": predicted,
                "ground_truth_score": gt,
            }
        )
    return rows


def compute_calibration(train: list[dict]) -> dict:
    """Compute per-(hat, criterion, depth_bucket) mean_delta and anchor quantiles."""
    table = {}
    buckets = {}
    for r in train:
        key = (r["hat"], r["criterion"], r["evidence_depth_bucket"])
        buckets.setdefault(key, []).append(
            (r["predicted_score"], r["ground_truth_score"])
        )

    for key, pairs in buckets.items():
        deltas = [p - g for p, g in pairs]
        gts = sorted(g for _, g in pairs)
        n = len(gts)
        if n < 2:
            continue
        p25 = gts[int(n * 0.25)]
        p75 = gts[int(n * 0.75)]
        table[key] = {
            "mean_delta": round(statistics.mean(deltas), 3),
            "n": n,
            "anchor_p25": p25,
            "anchor_p75": p75,
        }
    return table


def apply_calibration(row: dict, cal: dict) -> float:
    key = (row["hat"], row["criterion"], row["evidence_depth_bucket"])
    info = cal.get(key)
    if info is None or info["n"] < 3:
        return row["predicted_score"]  # insufficient data, pass through
    raw = row["predicted_score"] - 0.8 * info["mean_delta"]
    # cap delta at ±2.0
    delta = raw - row["predicted_score"]
    delta = max(-2.0, min(2.0, delta))
    candidate = row["predicted_score"] + delta
    # clip toward anchor band
    return round(
        max(info["anchor_p25"], min(info["anchor_p75"], candidate)), 3
    )


def mae(rows: list[dict], score_key: str = "predicted_score") -> float:
    if not rows:
        return float("inf")
    return statistics.mean(
        abs(r[score_key] - r["ground_truth_score"]) for r in rows
    )


def main():
    print("=" * 60)
    print("SPIKE D — Calibration policy on toy data")
    print("=" * 60)

    # Generate dataset, split train/test 50/50
    data = synth_dataset(n=100, seed=42)
    train = data[:50]
    held_out = data[50:]

    # Compute calibration from train
    cal = compute_calibration(train)
    print(f"\nCalibration table ({len(cal)} cells):")
    for key, info in cal.items():
        print(f"  {key}: {info}")

    # Apply on held-out
    for r in held_out:
        r["calibrated_score"] = apply_calibration(r, cal)

    mae_raw = mae(held_out, "predicted_score")
    mae_cal = mae(held_out, "calibrated_score")
    improvement = (mae_raw - mae_cal) / mae_raw if mae_raw > 0 else 0
    print(f"\nHeld-out MAE:")
    print(f"  Uncalibrated: {mae_raw:.3f}")
    print(f"  Calibrated:   {mae_cal:.3f}")
    print(f"  Improvement:  {improvement*100:.1f}%")

    # Catastrophic over-correction check
    worse_count = sum(
        1
        for r in held_out
        if abs(r["calibrated_score"] - r["ground_truth_score"])
        > abs(r["predicted_score"] - r["ground_truth_score"]) + 2.0
    )

    # Inspect outliers — examine which buckets got the biggest improvement
    yellow_a1_low = [
        r
        for r in held_out
        if r["hat"] == "yellow"
        and r["criterion"] == "A1"
        and r["evidence_depth_bucket"] == "<0.4"
    ]
    yellow_a1_low_mae_raw = mae(yellow_a1_low, "predicted_score")
    yellow_a1_low_mae_cal = mae(yellow_a1_low, "calibrated_score")
    print(f"\nYellow A1 (depth<0.4) on held-out, n={len(yellow_a1_low)}:")
    print(f"  Uncalibrated: {yellow_a1_low_mae_raw:.3f}")
    print(f"  Calibrated:   {yellow_a1_low_mae_cal:.3f}")

    # Pass criteria
    overall_improved = improvement >= 0.15
    no_catastrophic = worse_count == 0
    targeted_improvement = yellow_a1_low_mae_cal < yellow_a1_low_mae_raw

    overall = overall_improved and no_catastrophic and targeted_improvement

    result = {
        "spike": "D",
        "title": "Calibration policy on toy data",
        "n_train": len(train),
        "n_held_out": len(held_out),
        "calibration_cells": len(cal),
        "mae_uncalibrated": round(mae_raw, 3),
        "mae_calibrated": round(mae_cal, 3),
        "improvement_pct": round(improvement * 100, 1),
        "catastrophic_over_corrections": worse_count,
        "yellow_a1_low_mae_uncalibrated": round(yellow_a1_low_mae_raw, 3),
        "yellow_a1_low_mae_calibrated": round(yellow_a1_low_mae_cal, 3),
        "overall_improved_>=15pct": overall_improved,
        "no_catastrophic_over_correction": no_catastrophic,
        "targeted_bucket_improved": targeted_improvement,
        "overall_pass": overall,
        "calibration_table": {
            f"{k[0]}|{k[1]}|{k[2]}": v for k, v in cal.items()
        },
        "findings": [
            f"Calibration achieves {improvement*100:.1f}% MAE reduction on held-out",
            f"Yellow A1 low-evidence bucket improved {(yellow_a1_low_mae_raw - yellow_a1_low_mae_cal):.3f} MAE absolute",
            "Policy clip to [p25, p75] band prevents anchor over-pull",
            "Delta cap ±2.0 prevents catastrophic over-correction",
            "Calibration table sparse (n_cells = " + str(len(cal)) + "); v1.13 production seed needs ≥3 samples per cell",
        ]
        if overall
        else ["FAILURE — see metrics"],
    }

    out_path = RESULTS_DIR / "spike_d_calibration_toy.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nResult written: {out_path}")
    print(f"\n[{'PASS' if overall else 'FAIL'}] Spike D")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
