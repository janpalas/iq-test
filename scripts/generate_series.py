#!/usr/bin/env python3
"""Vygeneruje úlohy s číselnými a písmennými řadami do data/ciselne-rady.json
a data/pismenne-rady.json. Generování je deterministické (pevný seed),
takže opakované spuštění dá stejné úlohy."""

import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

rng = random.Random(20261026)


def fmt(seq):
    return ", ".join(str(x) for x in seq)


def num_task(seq, explanation, difficulty, hide=None):
    """Úloha s číselnou řadou; `hide` je index skrytého členu (výchozí poslední)."""
    if len(set(seq)) < len(seq):
        return None  # degenerovaná řada (opakující se členy) se zahodí
    if hide is None:
        hide = len(seq) - 1
    shown = [("?" if i == hide else str(x)) for i, x in enumerate(seq)]
    if hide == len(seq) - 1:
        question = f"Jaké číslo následuje v řadě?\n\n{', '.join(shown[:-1])}, ?"
    else:
        question = f"Jaké číslo patří místo otazníku?\n\n{', '.join(shown)}"
    return {
        "category": "Číselné řady",
        "difficulty": difficulty,
        "question": question,
        "answer": str(seq[hide]),
        "explanation": explanation,
    }


def gen_arithmetic():
    a, d = rng.randint(2, 60), rng.choice([3, 4, 6, 7, 8, 9, 11, 12, 13, 15, -4, -6, -7, -9])
    if d < 0:
        a += 80
    seq = [a + d * i for i in range(6)]
    sign = "přičítá" if d > 0 else "odečítá"
    return num_task(seq, f"Ke každému členu se {sign} {abs(d)}.", 1)


def gen_geometric():
    q = rng.choice([2, 3, 4, 5])
    a = rng.randint(1, 7)
    n = 6 if q <= 3 else 5
    seq = [a * q ** i for i in range(n)]
    if rng.random() < 0.35:
        seq.reverse()
        return num_task(seq, f"Každý člen je {q}× menší než předchozí (dělí se {q}).", 1)
    return num_task(seq, f"Každý člen je {q}× větší než předchozí.", 1)


def gen_increasing_diff():
    a = rng.randint(1, 30)
    d = rng.randint(1, 6)
    k = rng.choice([1, 2, 3])
    seq = [a]
    diffs = []
    for i in range(6):
        diffs.append(d + k * i)
        seq.append(seq[-1] + diffs[-1])
    return num_task(seq, f"Rozdíly mezi členy rostou o {k}: {fmt(diffs)}.", 2)


def gen_powers():
    kind = rng.choice(["sq", "sq", "sq_plus", "cube"])
    if kind == "sq":
        s = rng.randint(1, 7)
        seq = [n * n for n in range(s, s + 6)]
        return num_task(seq, f"Druhé mocniny po sobě jdoucích čísel: {s}², {s + 1}², … {s + 5}² = {seq[-1]}.", 1)
    if kind == "sq_plus":
        s = rng.randint(1, 6)
        c = rng.choice([-1, 1, 2, 3, -2])
        seq = [n * n + c for n in range(s, s + 6)]
        op = f"+ {c}" if c > 0 else f"− {-c}"
        return num_task(seq, f"Členy jsou n² {op} pro n = {s}…{s + 5}; poslední je {s + 5}² {op} = {seq[-1]}.", 2)
    s = rng.randint(1, 3)
    seq = [n ** 3 for n in range(s, s + 5)]
    return num_task(seq, f"Třetí mocniny po sobě jdoucích čísel: {s}³, … {s + 4}³ = {seq[-1]}.", 2)


def gen_fibonacci():
    a, b = rng.randint(1, 6), rng.randint(1, 8)
    seq = [a, b]
    while len(seq) < 8:
        seq.append(seq[-1] + seq[-2])
    return num_task(seq, f"Každý člen je součtem dvou předchozích: {seq[-3]} + {seq[-2]} = {seq[-1]}.", 2)


def gen_alternating_ops():
    a = rng.randint(1, 9)
    p = rng.randint(1, 6)
    m = rng.choice([2, 3])
    seq = [a]
    for i in range(6):
        seq.append(seq[-1] + p if i % 2 == 0 else seq[-1] * m)
    return num_task(seq, f"Střídají se operace +{p} a ×{m}.", 3)


def gen_interleaved():
    a, d1 = rng.randint(1, 20), rng.choice([2, 3, 4, 5])
    b, d2 = rng.randint(30, 60), rng.choice([-1, -2, -3, -5, 5, 10])
    seq = []
    for i in range(4):
        seq += [a + d1 * i, b + d2 * i]
    seq = seq[:7]
    second = "roste" if d2 > 0 else "klesá"
    return num_task(
        seq,
        f"Jde o dvě proložené řady: na lichých pozicích čísla rostou o {d1} ({fmt(seq[0::2])}), "
        f"na sudých pozicích {second} o {abs(d2)} ({fmt(seq[1::2])}).",
        3,
    )


def gen_linear_recurrence():
    m = rng.choice([2, 3])
    c = rng.choice([1, -1, 2, 3])
    a = rng.randint(1, 5)
    seq = [a]
    n = 6 if m == 2 else 5
    while len(seq) < n:
        seq.append(seq[-1] * m + c)
    op = f"+ {c}" if c > 0 else f"− {-c}"
    return num_task(seq, f"Každý člen vznikne vynásobením předchozího {m} a {op}: {seq[-2]} × {m} {op} = {seq[-1]}.", 3)


def gen_primes():
    s = rng.randint(0, 12)
    seq = PRIMES[s:s + 6]
    return num_task(seq, f"Po sobě jdoucí prvočísla; další prvočíslo po {seq[-2]} je {seq[-1]}.", 2)


def gen_doubling_diff():
    a = rng.randint(1, 20)
    d = rng.choice([1, 2, 3])
    seq = [a]
    diffs = []
    for i in range(6):
        diffs.append(d * 2 ** i)
        seq.append(seq[-1] + diffs[-1])
    return num_task(seq, f"Rozdíly mezi členy se zdvojnásobují: {fmt(diffs)}.", 2)


def gen_triangular():
    s = rng.randint(1, 5)
    seq = [n * (n + 1) // 2 for n in range(s, s + 7)]
    diffs = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
    return num_task(seq, f"Rozdíly mezi členy rostou o 1: {fmt(diffs)} (trojúhelníková čísla).", 2)


def gen_growing_factor():
    a = rng.randint(1, 4)
    start = rng.choice([2, 3])
    seq = [a]
    for k in range(start, start + 4):
        seq.append(seq[-1] * k)
    factors = [seq[i + 1] // seq[i] for i in range(len(seq) - 1)]
    return num_task(seq, f"Násobí se postupně rostoucím číslem: ×{', ×'.join(map(str, factors))}.", 3)


def gen_middle_missing():
    a, d = rng.randint(3, 40), rng.choice([3, 4, 5, 6, 7, 8, 9, 12])
    seq = [a + d * i for i in range(7)]
    hide = rng.randint(2, 4)
    return num_task(seq, f"Ke každému členu se přičítá {d}; chybí {seq[hide - 1]} + {d} = {seq[hide]}.", 1, hide)


def gen_middle_missing_geo():
    a, q = rng.randint(1, 5), rng.choice([2, 3])
    seq = [a * q ** i for i in range(6)]
    hide = rng.randint(1, 4)
    return num_task(seq, f"Každý člen je {q}× větší než předchozí; chybí {seq[hide]}.", 2, hide)


def gen_alternating_signs():
    a = rng.randint(40, 90)
    p, m = rng.randint(5, 15), rng.randint(2, 9)
    while p == m:
        m = rng.randint(2, 9)
    seq = [a]
    for i in range(6):
        seq.append(seq[-1] + p if i % 2 == 0 else seq[-1] - m)
    return num_task(seq, f"Střídavě se přičítá {p} a odečítá {m}.", 2)


def gen_squares_diff():
    a = rng.randint(1, 10)
    seq = [a]
    for k in range(1, 7):
        seq.append(seq[-1] + k * k)
    return num_task(seq, f"Přičítají se druhé mocniny: +1, +4, +9, +16, +25, +36.", 3)


def gen_n_times_n_plus1():
    s = rng.randint(1, 4)
    seq = [n * (n + 1) for n in range(s, s + 6)]
    return num_task(
        seq,
        f"Členy jsou součiny sousedních čísel n·(n+1): poslední je {s + 5}·{s + 6} = {seq[-1]}. "
        f"(Rozdíly rostou o 2.)",
        2,
    )


NUMBER_GENERATORS = [
    (gen_arithmetic, 9), (gen_geometric, 7), (gen_increasing_diff, 7), (gen_powers, 7),
    (gen_fibonacci, 5), (gen_alternating_ops, 6), (gen_interleaved, 6), (gen_linear_recurrence, 6),
    (gen_primes, 4), (gen_doubling_diff, 5), (gen_triangular, 3), (gen_growing_factor, 3),
    (gen_middle_missing, 6), (gen_middle_missing_geo, 5), (gen_alternating_signs, 6),
    (gen_squares_diff, 3), (gen_n_times_n_plus1, 3),
]


def letter_task(letters, answer, explanation, difficulty, sep=", "):
    return {
        "category": "Písmenné řady",
        "difficulty": difficulty,
        "question": "Které písmeno (nebo skupina písmen) následuje? Použij abecedu bez háčků, čárek a CH (A–Z).\n\n"
        + sep.join(letters) + sep + "?",
        "answer": answer,
        "explanation": explanation,
    }


def L(i):
    return ALPHABET[i % 26]


def gen_letter_skip():
    k = rng.choice([2, 3, 4, 5])
    s = rng.randint(0, 25 - 5 * k)
    seq = [L(s + k * i) for i in range(6)]
    return letter_task(seq[:-1], seq[-1], f"Posun vždy o {k} písmena dopředu (vynechá se {k - 1}).", 1)


def gen_letter_back():
    k = rng.choice([1, 2, 3])
    s = rng.randint(5 * k, 25)
    seq = [L(s - k * i) for i in range(6)]
    return letter_task(seq[:-1], seq[-1], f"Abeceda pozpátku s krokem {k}.", 1)


def gen_letter_growing():
    s = rng.randint(0, 6)
    idx, step, seq = s, 1, []
    for _ in range(6):
        seq.append(L(idx))
        idx += step
        step += 1
    return letter_task(seq[:-1], seq[-1], "Posun se zvětšuje: +1, +2, +3, +4, +5 písmen.", 2)


def gen_letter_interleaved():
    a = rng.randint(0, 8)
    b = rng.randint(17, 25)
    seq = []
    for i in range(4):
        seq += [L(a + i), L(b - i)]
    seq = seq[:7]
    return letter_task(
        seq[:-1], seq[-1],
        f"Dvě proložené řady: {', '.join(seq[0::2])} jde dopředu, {', '.join(seq[1::2])} jde dozadu.", 2,
    )


def gen_letter_pairs_mirror():
    s = rng.randint(0, 8)
    pairs = [L(s + i) + L(25 - s - i) for i in range(5)]
    return letter_task(
        pairs[:-1], pairs[-1],
        "První písmeno postupuje od začátku abecedy, druhé je jeho „zrcadlo“ od konce (A↔Z, B↔Y, …).", 2,
    )


def gen_letter_pairs_shift():
    s = rng.randint(0, 10)
    k = rng.choice([1, 2, 3])
    gap = rng.choice([1, 2, 3])
    pairs = [L(s + k * i) + L(s + k * i + gap) for i in range(5)]
    return letter_task(
        pairs[:-1], pairs[-1],
        f"Dvojice se posouvá o {k}; druhé písmeno je vždy o {gap} dál než první.", 2,
    )


def gen_letter_triples():
    s = rng.randint(0, 6)
    k = rng.choice([2, 3, 4])
    triples = [L(s + k * i) + L(s + k * i + 1) + L(s + k * i + 2) for i in range(4)]
    return letter_task(
        triples[:-1], triples[-1],
        f"Trojice po sobě jdoucích písmen; každá další začíná o {k} písmen dál.", 3,
    )


def gen_letter_alternating_steps():
    s = rng.randint(0, 5)
    p, m = 3, 1
    idx, seq = s, []
    for i in range(7):
        seq.append(L(idx))
        idx += p if i % 2 == 0 else -m
    return letter_task(seq[:-1], seq[-1], f"Střídavě +{p} a −{m} písmena.", 3)


def gen_letter_number_mix():
    s = rng.randint(0, 8)
    k = rng.choice([2, 3])
    items = [f"{L(s + k * i)}{s + k * i + 1}" for i in range(5)]
    return letter_task(
        items[:-1], items[-1],
        f"Písmeno se posouvá o {k} a číslo udává jeho pořadí v abecedě.", 3,
    )


LETTER_GENERATORS = [
    (gen_letter_skip, 7), (gen_letter_back, 5), (gen_letter_growing, 4), (gen_letter_interleaved, 4),
    (gen_letter_pairs_mirror, 4), (gen_letter_pairs_shift, 5), (gen_letter_triples, 4),
    (gen_letter_alternating_steps, 3), (gen_letter_number_mix, 4),
]


def generate(generators):
    tasks, seen = [], set()
    for fn, count in generators:
        made, attempts = 0, 0
        while made < count and attempts < 500:
            attempts += 1
            t = fn()
            if t is None or t["question"] in seen:
                continue
            seen.add(t["question"])
            tasks.append(t)
            made += 1
    return tasks


def main():
    numbers = generate(NUMBER_GENERATORS)
    letters = generate(LETTER_GENERATORS)
    (DATA / "ciselne-rady.json").write_text(json.dumps(numbers, ensure_ascii=False, indent=2) + "\n")
    (DATA / "pismenne-rady.json").write_text(json.dumps(letters, ensure_ascii=False, indent=2) + "\n")
    print(f"číselné řady: {len(numbers)}, písmenné řady: {len(letters)}")


if __name__ == "__main__":
    main()
