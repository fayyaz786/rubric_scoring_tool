# Evaluation Report

| Sample | Response | Accuracy | Completeness | Instruction Following | Reasoning | Clarity | Safety | Total | Worst issue |
|---|---|---|---|---|---|---|---|---|---|
| cagr_calculation | A | 1 | 4 | 4 | 2 | 4 | 2 | **17** | Critical |
| cagr_calculation | B | 5 | 5 | 5 | 5 | 5 | 5 | **30** | None |
| six_sigma_fact_check | A | 1 | 4 | 5 | 3 | 5 | 1 | **19** | Critical |
| six_sigma_fact_check | B | 5 | 5 | 5 | 5 | 5 | 5 | **30** | None |
| executive_summary | A | 2 | 5 | 1 | 3 | 4 | 2 | **17** | Critical |
| executive_summary | B | 5 | 4 | 4 | 4 | 5 | 5 | **27** | Major |

## Decisions

| Sample | Preferred | Reason | Gold rewrite needed |
|---|---|---|---|
| cagr_calculation | **B** | Worst issue: none vs critical | No |
| six_sigma_fact_check | **B** | Worst issue: none vs critical | No |
| executive_summary | **B** | Worst issue: major vs critical | Yes |

## Summary

* Samples evaluated: 3
* Responses scored: 6
* Average total score: 23.3 out of 30
* Responses with a critical issue: 3
* Samples needing a gold standard rewrite: 1
