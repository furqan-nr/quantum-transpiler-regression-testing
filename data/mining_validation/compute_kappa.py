#!/usr/bin/env python3
"""Inter-rater agreement for the transpiler-fix observability mining study.

Computes Cohen's kappa between Rater 1 (data/observability_mining.csv) and
Rater 2 (data/mining_validation/rater2_sheet.csv), on:
  (a) the binary `observable_by_output_oracle` judgment  <- the headline claim
  (b) the multi-class `manifestation_channel` judgment

Dependency-free (standard library only). Run:
    python3 data/mining_validation/compute_kappa.py
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(HERE, "..", "observability_mining.csv")
R2 = os.path.join(HERE, "rater2_sheet.csv")

def load(path, fields):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pr = (row.get("pr") or "").strip()
            if not pr:
                continue
            out[pr] = {k: (row.get(k) or "").strip().lower() for k in fields}
    return out

def cohen_kappa(pairs):
    """pairs: list of (a, b) category labels. Returns (kappa, po, n)."""
    n = len(pairs)
    if n == 0:
        return None, None, 0
    cats = sorted({c for ab in pairs for c in ab})
    po = sum(1 for a, b in pairs if a == b) / n
    a_count = {c: 0 for c in cats}
    b_count = {c: 0 for c in cats}
    for a, b in pairs:
        a_count[a] += 1
        b_count[b] += 1
    pe = sum((a_count[c] / n) * (b_count[c] / n) for c in cats)
    kappa = (po - pe) / (1 - pe) if (1 - pe) > 1e-12 else 1.0
    return kappa, po, n

def interpret(k):
    if k is None: return "n/a"
    if k < 0:    return "less than chance"
    if k <= .20: return "slight"
    if k <= .40: return "fair"
    if k <= .60: return "moderate"
    if k <= .80: return "substantial"
    return "almost perfect"

def main():
    r1 = load(R1, ["observable_by_output_oracle", "manifestation_channel"])
    r2 = load(R2, ["observable_by_output_oracle", "manifestation_channel"])
    common = [pr for pr in r1 if pr in r2]
    rated = [pr for pr in common if r2[pr]["observable_by_output_oracle"]]
    if not rated:
        print("Rater 2 sheet appears empty. Fill rater2_sheet.csv first "
              "(see CODEBOOK.md), then re-run.")
        print(f"PRs awaiting Rater 2 labels: {len(common)}")
        return

    for field, label in [("observable_by_output_oracle", "BINARY observable (headline)"),
                         ("manifestation_channel", "manifestation_channel (7-class)")]:
        pairs = [(r1[pr][field], r2[pr][field]) for pr in rated
                 if r1[pr][field] and r2[pr][field]]
        k, po, n = cohen_kappa(pairs)
        print(f"\n== {label} ==")
        print(f"  n rated by both : {n}")
        if k is not None:
            print(f"  raw agreement   : {po*100:.1f}%")
            print(f"  Cohen's kappa   : {k:.3f}  ({interpret(k)})")
        disagree = [pr for pr in rated
                    if r1[pr][field] and r2[pr][field] and r1[pr][field] != r2[pr][field]]
        if disagree:
            print(f"  disagreements   : {len(disagree)} -> {', '.join(sorted(disagree))}")

    # headline count from the agreed/Rater-1 'no' set
    no1 = sum(1 for pr in r1 if r1[pr]["observable_by_output_oracle"] == "no")
    print(f"\nRater 1 output-invisible ('no'): {no1}/{len(r1)} = {no1/len(r1)*100:.0f}%")

if __name__ == "__main__":
    main()
