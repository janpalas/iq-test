# Procvičování IQ úloh

Jednoduchá webová aplikace v češtině: zobrazí jednu náhodnou úlohu typu IQ testu,
počká na odpověď (výběr z možností nebo volný text), vyhodnotí ji, při chybě ukáže
správnou odpověď se zdůvodněním a pokračuje další náhodnou úlohou. Žádné skóre.

## Spuštění

Stačí otevřít `index.html` v prohlížeči – aplikace nemá žádné závislosti ani build.

Ovládání z klávesnice: `A`–`E` (nebo `1`–`5`) vybere možnost, `Enter` odešle odpověď
a přejde na další úlohu.

## Úlohy

Úlohy jsou v `data/*.json` (jeden soubor na kategorii). Formát:

```json
{
  "category": "Analogie",
  "difficulty": 2,
  "question": "Zadání (\n = nový řádek)",
  "options": ["…", "…"],
  "answer": "…",
  "accept": ["…"],
  "explanation": "…"
}
```

- `options` – jen u úloh s výběrem; `answer` pak musí být přesně jedna z možností.
- `accept` – jen u volné odpovědi; další přijatelné varianty. Porovnání ignoruje
  velikost písmen, diakritiku a interpunkci, čísla se porovnávají numericky.
- `difficulty` – 1 lehká, 2 střední, 3 těžká.

Číselné a písmenné řady generuje `scripts/generate_series.py`. Po jakékoli změně dat
spusť `scripts/build.py`, který úlohy zvaliduje a složí do `tasks.js`:

```bash
python3 scripts/generate_series.py
python3 scripts/build.py
```
