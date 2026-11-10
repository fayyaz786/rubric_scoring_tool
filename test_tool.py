"""Basic tests. Run with: python test_tool.py"""

from check_constraints import check
from score import decide


def row(sample, name, scores, severity):
    keys = ["accuracy", "completeness", "instruction_following", "reasoning", "clarity", "safety"]
    r = {"sample_id": sample, "response": name, "worst_severity": severity, **dict(zip(keys, scores))}
    r["total"] = sum(scores)
    return r


def test_severity_beats_total():
    # A has the higher total but a critical issue, so B must win.
    rows = [row("s1", "A", [5, 5, 5, 5, 5, 1], "Critical"), row("s1", "B", [4, 4, 4, 4, 4, 4], "Minor")]
    assert decide(rows)[0]["preferred"] == "B"


def test_tie_is_flagged():
    rows = [row("s1", "A", [4] * 6, "Minor"), row("s1", "B", [4] * 6, "Minor")]
    assert decide(rows)[0]["preferred"] == "Tie"


def test_constraints():
    text = "* one two three\n* four five\n\nRecommendation: act now"
    results = check(text, {"exact_bullets": 2, "max_words_per_bullet": 3, "last_line_starts_with": "Recommendation:"})
    assert all(ok for _, ok, _ in results)


if __name__ == "__main__":
    test_severity_beats_total()
    test_tie_is_flagged()
    test_constraints()
    print("All tests passed")
