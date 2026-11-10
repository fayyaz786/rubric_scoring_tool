"""Automatic constraint checker for LLM responses.

Checks a response against the explicit, countable rules in a prompt
(bullet count, words per bullet, required closing line, banned phrases)
so a human reviewer can focus on meaning and accuracy.

Usage:
    python check_constraints.py responses.json
"""

import json
import re
import sys


def bullets(text):
    return [l.strip()[1:].strip() for l in text.splitlines() if l.strip().startswith(("*", "•"))]


def words(text):
    return len(text.split())


def check(response, rules):
    results = []
    b = bullets(response)

    if "exact_bullets" in rules:
        n = rules["exact_bullets"]
        results.append((f"Exactly {n} bullets", len(b) == n, f"found {len(b)}"))

    if "max_words_per_bullet" in rules:
        n = rules["max_words_per_bullet"]
        counts = [words(x) for x in b]
        longest = max(counts) if counts else 0
        results.append((f"Each bullet {n} words or fewer", longest <= n, f"longest has {longest}"))

    if "last_line_starts_with" in rules:
        prefix = rules["last_line_starts_with"]
        lines = [l.strip() for l in response.splitlines() if l.strip()]
        last = lines[-1] if lines else ""
        results.append((f'Ends with "{prefix}"', last.startswith(prefix), f'last line: "{last[:40]}"'))

    if "banned_phrases" in rules:
        found = [p for p in rules["banned_phrases"] if re.search(re.escape(p), response, re.I)]
        results.append(("No unsupported phrases", not found, "found: " + ", ".join(found) if found else "none found"))

    return results


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)

    rules = data["rules"]
    for name, text in data["responses"].items():
        results = check(text, rules)
        passed = sum(ok for _, ok, _ in results)
        print(f"\n{name}: {passed} of {len(results)} checks passed")
        for label, ok, detail in results:
            print(f"  {'PASS' if ok else 'FAIL'}  {label} ({detail})")


if __name__ == "__main__":
    main()
