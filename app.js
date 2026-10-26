(() => {
  const TASKS = window.TASKS || [];
  const DIFFICULTY = { 1: "lehká", 2: "střední", 3: "těžká" };
  const KEYS = "ABCDEFGH";

  const $ = (id) => document.getElementById(id);
  const el = {
    category: $("category"),
    difficulty: $("difficulty"),
    question: $("question"),
    options: $("options"),
    form: $("text-form"),
    input: $("text-answer"),
    feedback: $("feedback"),
    verdict: $("verdict"),
    correctAnswer: $("correct-answer"),
    explanationBox: $("explanation-box"),
    explanation: $("explanation"),
    skip: $("skip"),
    next: $("next"),
  };

  // Úlohy se berou z náhodně zamíchaného balíčku, aby se neopakovaly,
  // dokud nebyly vystřídány všechny.
  let deck = [];
  let current = null;
  let answered = false;

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  function drawTask() {
    if (deck.length === 0) {
      deck = shuffle(TASKS.slice());
      // Po zamíchání nového balíčku nezačínat stejnou úlohou, jakou skončil předchozí.
      if (current && deck.length > 1 && deck[deck.length - 1] === current) deck.unshift(deck.pop());
    }
    return deck.pop();
  }

  function normalize(s) {
    return String(s)
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim()
      .replace(/[.!]+$/, "")
      .trim();
  }

  function asNumber(s) {
    const t = normalize(s).replace(/(\d)\s+(?=\d)/g, "$1").replace(",", ".");
    return /^[-+−]?\d+(\.\d+)?$/.test(t) ? parseFloat(t.replace("−", "-")) : null;
  }

  function matches(given, expected) {
    const a = normalize(given);
    const b = normalize(expected);
    if (a === b) return true;
    const na = asNumber(given);
    const nb = asNumber(expected);
    if (na !== null && nb !== null) return Math.abs(na - nb) < 1e-9;
    // Tolerance pro oddělovače: „J, Q“ = „JQ“, „15 min“ = „15min“.
    const strip = (s) => s.replace(/[^\p{L}\p{N}]/gu, "");
    return strip(a) !== "" && strip(a) === strip(b);
  }

  function isCorrectText(given) {
    return [current.answer, ...(current.accept || [])].some((exp) => matches(given, exp));
  }

  function render(task) {
    current = task;
    answered = false;

    el.category.textContent = task.category;
    el.difficulty.textContent = `obtížnost: ${DIFFICULTY[task.difficulty] || "?"}`;
    // Odstavce zadání; ty s mřížkou zarovnanou mezerami potřebují neproporcionální písmo.
    el.question.replaceChildren(
      ...task.question.split(/\n\s*\n/).map((part) => {
        const p = document.createElement("p");
        p.textContent = part;
        if (/\S {2,}\S/.test(part)) p.className = "mono";
        return p;
      })
    );

    el.feedback.hidden = true;
    el.next.hidden = true;
    el.skip.hidden = false;
    el.options.replaceChildren();

    if (task.options) {
      el.form.hidden = true;
      el.options.hidden = false;
      task.options.forEach((opt, i) => {
        const btn = document.createElement("button");
        btn.type = "button";
        const key = document.createElement("span");
        key.className = "key";
        key.textContent = KEYS[i] + ")";
        const text = document.createElement("span");
        text.textContent = opt;
        btn.append(key, text);
        btn.addEventListener("click", () => answerChoice(i));
        el.options.append(btn);
      });
    } else {
      el.options.hidden = true;
      el.form.hidden = false;
      el.input.value = "";
      el.input.disabled = false;
      el.input.className = "";
      el.form.querySelector("button").hidden = false;
      el.input.focus();
    }
    window.scrollTo(0, 0);
  }

  function answerChoice(index) {
    if (answered) return;
    const buttons = [...el.options.children];
    const correctIndex = current.options.indexOf(current.answer);
    buttons.forEach((b, i) => {
      b.disabled = true;
      if (i === correctIndex) b.classList.add("correct");
      else if (i === index) b.classList.add("wrong");
    });
    showFeedback(index === correctIndex, `${KEYS[correctIndex]}) ${current.answer}`);
  }

  function answerText(value) {
    if (answered || !value.trim()) return;
    const ok = isCorrectText(value);
    el.input.disabled = true;
    el.input.className = ok ? "correct" : "wrong";
    el.form.querySelector("button").hidden = true;
    showFeedback(ok, current.answer);
  }

  function showFeedback(ok, correctLabel) {
    answered = true;
    el.feedback.hidden = false;
    el.feedback.className = "feedback " + (ok ? "ok" : "bad");
    el.verdict.textContent = ok ? "Správně!" : "Špatně.";
    el.correctAnswer.hidden = ok;
    el.correctAnswer.textContent = ok ? "" : `Správná odpověď: ${correctLabel}`;

    const hasExplanation = Boolean(current.explanation);
    el.explanationBox.hidden = !hasExplanation;
    el.explanation.textContent = current.explanation || "";
    // Při chybě je zdůvodnění rovnou rozbalené, při správné odpovědi jen na kliknutí.
    el.explanationBox.open = hasExplanation && !ok;

    el.skip.hidden = true;
    el.next.hidden = false;
    el.next.focus();
  }

  function nextTask() {
    render(drawTask());
  }

  el.form.addEventListener("submit", (e) => {
    e.preventDefault();
    answerText(el.input.value);
  });
  el.next.addEventListener("click", nextTask);
  el.skip.addEventListener("click", nextTask);

  document.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (answered && e.key === "Enter" && document.activeElement !== el.next) {
      e.preventDefault();
      nextTask();
      return;
    }
    if (!answered && current && current.options && e.target === document.body) {
      const k = e.key.toUpperCase();
      let i = KEYS.indexOf(k);
      if (i < 0 && /^[1-9]$/.test(e.key)) i = Number(e.key) - 1;
      if (i >= 0 && i < current.options.length) answerChoice(i);
    }
  });

  if (TASKS.length === 0) {
    el.question.textContent = "Nepodařilo se načíst úlohy (chybí tasks.js).";
    el.skip.hidden = true;
    return;
  }
  nextTask();
})();
