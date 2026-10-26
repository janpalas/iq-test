#!/usr/bin/env python3
"""Zvaliduje všechny úlohy v data/*.json a složí je do tasks.js,
který načítá index.html (aplikace tak funguje i otevřená přímo ze souboru)."""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "tasks.js"
ALLOWED_KEYS = {"category", "difficulty", "question", "options", "answer", "accept", "explanation"}


def validate(task, where):
    errors = []
    extra = set(task) - ALLOWED_KEYS
    if extra:
        errors.append(f"neznámé klíče {sorted(extra)}")
    for key in ("category", "question", "answer"):
        if not isinstance(task.get(key), str) or not task[key].strip():
            errors.append(f"chybí nebo je prázdné '{key}'")
    if task.get("difficulty") not in (1, 2, 3):
        errors.append("difficulty musí být 1, 2 nebo 3")
    options = task.get("options")
    if options is not None:
        if not isinstance(options, list) or len(options) < 2 or not all(isinstance(o, str) for o in options):
            errors.append("options musí být seznam alespoň dvou řetězců")
        elif len(set(options)) != len(options):
            errors.append("options obsahují duplicity")
        elif task.get("answer") not in options:
            errors.append("answer není mezi options")
        if "accept" in task:
            errors.append("accept nedává smysl u úlohy s výběrem")
    if "accept" in task and not (isinstance(task["accept"], list) and all(isinstance(a, str) for a in task["accept"])):
        errors.append("accept musí být seznam řetězců")
    return [f"{where}: {e}" for e in errors]


def main():
    tasks, errors = [], []
    seen_questions = {}
    for path in sorted(DATA.glob("*.json")):
        items = json.loads(path.read_text())
        for i, task in enumerate(items):
            where = f"{path.name}[{i}]"
            errors += validate(task, where)
            # Zadání „Co nepatří?“ se liší jen možnostmi, proto se porovnávají i ty.
            q = (task.get("question", "").strip(), tuple(sorted(task.get("options") or [])))
            if q in seen_questions:
                errors.append(f"{where}: duplicitní zadání s {seen_questions[q]}")
            seen_questions[q] = where
            tasks.append({"id": f"{path.stem}-{i + 1}", **task})

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)

    OUT.write_text(
        "// Vygenerováno skriptem scripts/build.py z data/*.json – needitovat ručně.\n"
        "window.TASKS = " + json.dumps(tasks, ensure_ascii=False, indent=1) + ";\n"
    )
    print(f"Celkem {len(tasks)} úloh -> {OUT.name}")
    for cat, n in sorted(Counter(t["category"] for t in tasks).items()):
        print(f"  {cat}: {n}")
    print("  obtížnost:", dict(sorted(Counter(t["difficulty"] for t in tasks).items())))


if __name__ == "__main__":
    main()
