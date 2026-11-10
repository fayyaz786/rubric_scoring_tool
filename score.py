"""Rubric scoring tool for side by side LLM evaluations.

Reads a CSV of human rubric scores (one row per response), totals each
response, applies a fixed preference rule and writes a Markdown report.

Usage:
    python score.py evaluations.csv report.md
"""

import csv
import sys
from collections import defaultdict

DIMENSIONS = [
    "accuracy",
    "completeness",
    "instruction_following",
    "reasoning",
    "clarity",
    "safety",
]

# Lower number means a worse issue.
SEVERITY_RANK = {"Critical": 0, "Major": 1, "Minor": 2, "None": 3}

# Tie breakers, in order, after worst severity.
TIE_BREAKERS = ["instruction_following", "completeness", "clarity"]


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for d in DIMENSIONS:
            value = int(row[d])
            if not 1 <= value <= 5:
                raise ValueError(f"{row['sample_id']} {row['response']}: {d} must be 1 to 5, got {value}")
            row[d] = value
        if row["worst_severity"] not in SEVERITY_RANK:
            raise ValueError(f"Unknown severity: {row['worst_severity']}")
        row["total"] = sum(row[d] for d in DIMENSIONS)
    return rows


def preference_key(row):
    """Higher key wins: severity first, then the tie breakers, then total."""
    return (
        SEVERITY_RANK[row["worst_severity"]],
        *[row[t] for t in TIE_BREAKERS],
        row["total"],
    )


def decide(rows):
    by_sample = defaultdict(list)
    for row in rows:
        by_sample[row["sample_id"]].append(row)

    results = []
    for sample_id, responses in by_sample.items():
        ranked = sorted(responses, key=preference_key, reverse=True)
        winner, runner_up = ranked[0], ranked[1] if len(ranked) > 1 else None
        if runner_up and preference_key(winner) == preference_key(runner_up):
            reason = "Tie on every criterion: flag for a second reviewer"
            preferred = "Tie"
        elif runner_up and winner["worst_severity"] != runner_up["worst_severity"]:
            reason = (f"Worst issue: {winner['worst_severity'].lower()} vs "
                      f"{runner_up['worst_severity'].lower()}")
            preferred = winner["response"]
        else:
            reason = "Same worst severity, decided on tie breakers"
            for t in TIE_BREAKERS:
                if runner_up and winner[t] != runner_up[t]:
                    reason = (f"Same worst severity; higher {t.replace('_', ' ')} "
                              f"({winner[t]} vs {runner_up[t]})")
                    break
            preferred = winner["response"]
        both_critical = all(r["worst_severity"] == "Critical" for r in responses)
        results.append({
            "sample_id": sample_id,
            "responses": responses,
            "preferred": preferred,
            "reason": reason,
            "needs_rewrite": both_critical or winner["worst_severity"] in ("Critical", "Major"),
        })
    return results


def report(results):
    lines = ["# Evaluation Report", ""]
    lines += ["| Sample | Response | " + " | ".join(d.replace("_", " ").title() for d in DIMENSIONS)
              + " | Total | Worst issue |",
              "|---|---|" + "---|" * len(DIMENSIONS) + "---|---|"]
    for r in results:
        for row in r["responses"]:
            lines.append(f"| {r['sample_id']} | {row['response']} | "
                         + " | ".join(str(row[d]) for d in DIMENSIONS)
                         + f" | **{row['total']}** | {row['worst_severity']} |")
    lines += ["", "## Decisions", "",
              "| Sample | Preferred | Reason | Gold rewrite needed |",
              "|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['sample_id']} | **{r['preferred']}** | {r['reason']} | "
                     f"{'Yes' if r['needs_rewrite'] else 'No'} |")

    totals = [row["total"] for r in results for row in r["responses"]]
    critical = sum(1 for r in results for row in r["responses"] if row["worst_severity"] == "Critical")
    lines += ["", "## Summary", "",
              f"* Samples evaluated: {len(results)}",
              f"* Responses scored: {len(totals)}",
              f"* Average total score: {sum(totals) / len(totals):.1f} out of {5 * len(DIMENSIONS)}",
              f"* Responses with a critical issue: {critical}",
              f"* Samples needing a gold standard rewrite: {sum(r['needs_rewrite'] for r in results)}",
              ""]
    return "\n".join(lines)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    results = decide(load(sys.argv[1]))
    text = report(results)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
