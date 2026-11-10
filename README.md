# Rubric Scoring Tool

A small Python tool for side by side LLM evaluation. It does the parts of an evaluator's job that should never be done by eye:

1. **`score.py`** totals human rubric scores, applies a fixed preference rule and writes a Markdown report
2. **`check_constraints.py`** automatically checks a response against countable prompt rules (bullet count, words per bullet, required closing line, banned phrases)

No external packages are needed. It runs on standard Python 3.

**Author:** Fayyaz Shahid, AI Trainer and LLM Response Evaluator  
**Contact:** [Upwork](https://www.upwork.com/freelancers/~01b0b9c69d62c91200) · [LinkedIn](https://www.linkedin.com/in/fayyazshahid) · [fayyazshahid.com](https://fayyazshahid.com)

---

## Why I built it

When you evaluate hundreds of response pairs, two kinds of mistakes creep in: adding up scores wrongly, and preferring the response that *reads* better over the one that is *correct*. This tool removes both. Scores are summed by code, and the preference rule puts the severity of the worst issue first, so a fluent answer with a critical error can never win on style.

## Preference rule

1. The response whose worst issue is **less severe** wins (Critical, then Major, then Minor, then none)
2. If the worst severity is equal, compare **instruction following**, then **completeness**, then **clarity**
3. If still equal, compare the **total score**
4. A full tie is flagged for a second reviewer instead of being decided at random

A gold standard rewrite is flagged whenever the preferred response still has a Critical or Major issue.

## Quick start

```bash
python score.py evaluations.csv report.md
python check_constraints.py responses.json
python test_tool.py
```

## Input format

**evaluations.csv:** one row per response, each dimension scored 1 to 5.

| Column | Meaning |
|---|---|
| `sample_id` | Groups the responses being compared |
| `response` | Response label, for example A or B |
| `accuracy`, `completeness`, `instruction_following`, `reasoning`, `clarity`, `safety` | Scores from 1 to 5 |
| `worst_severity` | `Critical`, `Major`, `Minor` or `None` |

**responses.json:** the prompt's rules plus the responses to check.

```json
{
  "rules": {
    "exact_bullets": 3,
    "max_words_per_bullet": 15,
    "last_line_starts_with": "Recommendation:",
    "banned_phrases": ["industry average", "churn"]
  },
  "responses": { "Response A": "...", "Response B": "..." }
}
```

## Example output

The sample data comes from my [LLM Evaluation Portfolio](https://github.com/fayyaz786/llm_evaluation_portfolio). The full generated report is in [example_report.md](example_report.md).

```text
| Sample               | Preferred | Reason                          | Gold rewrite needed |
| cagr_calculation     | B         | Worst issue: none vs critical   | No                  |
| six_sigma_fact_check | B         | Worst issue: none vs critical   | No                  |
| executive_summary    | B         | Worst issue: major vs critical  | Yes                 |

Response A: 1 of 4 checks passed
  FAIL  Exactly 3 bullets (found 4)
  FAIL  Each bullet 15 words or fewer (longest has 20)
  PASS  Ends with "Recommendation:"
  FAIL  No unsupported phrases (found: industry average, churn)

Gold standard: 4 of 4 checks passed
```

## Ideas for extending it

* Add an LLM judge that proposes scores, with the human score always taking priority
* Track agreement between two reviewers (for example Cohen's kappa)
* Export results to Excel or Power BI for a quality dashboard

## License

MIT
