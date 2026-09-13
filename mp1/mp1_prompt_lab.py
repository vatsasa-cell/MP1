#!/usr/bin/env python3
"""
MP1 Prompt Lab — end-to-end comparison of four prompting strategies.

Task:
  Extract company, role, years_experience_required from 10 job snippets.

Strategies:
  1. zero_shot
  2. few_shot
  3. structured
  4. cot

Main model: gpt-4o-mini, temperature 0.0
Judge model: gpt-4o, temperature 0.0

Run from the repository root:
    python mp1/mp1_prompt_lab.py

Or from mp1/:
    python mp1_prompt_lab.py

Outputs:
  mp1/results.json
  mp1/comparison_results.csv
  mp1/mp1_comparison.md
  mp1/mp1_writeup.md
  mp1/raw_results.json
"""

import asyncio
import json
import os
import re
import statistics
import time
from pathlib import Path
from typing import Any

import pandas as pd
from openai import AsyncOpenAI

MODEL = "gpt-4o-mini"
JUDGE_MODEL = "gpt-4o"
TEMPERATURE = 0.0
MAX_CONCURRENCY = 10

RATES = {
    "gpt-4o-mini": {"in": 0.15 / 1_000_000, "out": 0.60 / 1_000_000},
    "gpt-4o": {"in": 2.50 / 1_000_000, "out": 10.00 / 1_000_000},
}

FIELDS = ("company", "role", "years_experience_required")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_JSON = ROOT / "results.json"
RAW_RESULTS_JSON = ROOT / "raw_results.json"
CSV_RESULTS = ROOT / "comparison_results.csv"
COMPARISON_MD = ROOT / "mp1_comparison.md"
WRITEUP_MD = ROOT / "mp1_writeup.md"

FEW_SHOT_EXAMPLES = """
Example 1
Job: Acme Corp is hiring a Senior Software Engineer. The ideal candidate has 5+ years of backend experience.
Output: {"company":"Acme Corp","role":"Senior Software Engineer","years_experience_required":5}

Example 2
Job: Hooli is looking for a Junior Frontend Developer. Fresh grads welcome — no prior experience required.
Output: {"company":"Hooli","role":"Junior Frontend Developer","years_experience_required":0}

Example 3
Job: Stark Industries needs a Cybersecurity Analyst. Three to five years in a SOC environment.
Output: {"company":"Stark Industries","role":"Cybersecurity Analyst","years_experience_required":3}
"""

JSON_INSTRUCTION = """
Return exactly one JSON object with these exact fields:
{
  "company": string,
  "role": string,
  "years_experience_required": integer or null
}
Rules:
- Use only information stated in the snippet.
- Do not infer or invent missing years.
- "7+ years" -> 7.
- "around 6 years" -> 6.
- "three to five years" -> 3.
- "fresh grads welcome / no prior experience required" -> 0.
- If no years requirement is stated, use null.
"""

def load_data():
    snippets = [
        json.loads(line)
        for line in (DATA_DIR / "job_snippets.jsonl").read_text().splitlines()
        if line.strip()
    ]
    golden = {
        row["id"]: row
        for row in (
            json.loads(line)
            for line in (DATA_DIR / "golden_set.jsonl").read_text().splitlines()
            if line.strip()
        )
    }
    if len(snippets) != 10 or len(golden) != 10:
        raise ValueError(f"Expected 10 snippets and 10 golden rows; got {len(snippets)} and {len(golden)}.")
    return snippets, golden

def prompt_zero_shot(snippet_text: str) -> list[dict[str, str]]:
    return [{
        "role": "user",
        "content": (
            "Extract the company, role, and minimum years of experience required "
            "from this job posting. Return JSON with fields company, role, "
            "years_experience_required. Return null for years if no requirement is stated.\n\n"
            f"Job posting:\n{snippet_text}"
        ),
    }]

def prompt_few_shot(snippet_text: str) -> list[dict[str, str]]:
    return [{
        "role": "user",
        "content": (
            "Extract company, role, and minimum years of experience required. "
            "Follow the examples and return JSON with the exact fields "
            "company, role, years_experience_required. Use null when no years "
            "requirement is stated.\n\n"
            f"{FEW_SHOT_EXAMPLES}\n\n"
            f"Now extract from:\n{snippet_text}"
        ),
    }]

def prompt_structured(snippet_text: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are an expert technical recruiter performing precise information extraction. "
                "Return only valid JSON. Never guess or fabricate information. "
                "For years, use the stated number: 7+ -> 7, around 6 -> 6, "
                "3-5 -> 3, fresh graduates/no experience -> 0, and no stated "
                "requirement -> null.\n\n" + JSON_INSTRUCTION
            ),
        },
        {"role": "user", "content": f"Job posting:\n{snippet_text}"},
    ]

def prompt_cot(snippet_text: str) -> list[dict[str, str]]:
    return [{
        "role": "user",
        "content": (
            "Analyse the job posting carefully before giving the final answer. "
            "Identify the hiring company, exact role title, and the minimum stated "
            "years of experience. Do not infer a years requirement when none is stated. "
            "Use these conventions: 7+ -> 7, around 6 -> 6, 3-5 -> 3, fresh grads/no "
            "experience -> 0, and no stated requirement -> null. "
            "After your analysis, finish with exactly one JSON object using the fields "
            "company, role, years_experience_required.\n\n"
            f"Job posting:\n{snippet_text}"
        ),
    }]

STRATEGIES = {
    "zero_shot": prompt_zero_shot,
    "few_shot": prompt_few_shot,
    "structured": prompt_structured,
    "cot": prompt_cot,
}

def extract_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = cleaned.replace("```", "").strip()
    decoder = json.JSONDecoder()
    # Try the complete response first, then locate a JSON object within prose.
    try:
        obj = json.loads(cleaned)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    for match in re.finditer(r"\{", cleaned):
        try:
            obj, _ = decoder.raw_decode(cleaned[match.start():])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    return None

def norm_string(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).casefold()

def norm_year(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip().casefold()
    if s in {"", "null", "none", "n/a", "na", "not stated"}:
        return None
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None

def score_accuracy(extracted: dict[str, Any] | None, gold: dict[str, Any]) -> int:
    if not isinstance(extracted, dict):
        return 0
    score = 0
    if norm_string(extracted.get("company")) == norm_string(gold.get("company")):
        score += 1
    if norm_string(extracted.get("role")) == norm_string(gold.get("role")):
        score += 1
    if norm_year(extracted.get("years_experience_required")) == norm_year(gold.get("years_experience_required")):
        score += 1
    return score

def estimate_cost(usage: Any, model: str) -> float:
    if not usage:
        return 0.0
    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0
    rate = RATES[model]
    return prompt_tokens * rate["in"] + completion_tokens * rate["out"]

async def run_one(client: AsyncOpenAI, sem: asyncio.Semaphore, strategy_name: str, snippet: dict) -> dict:
    async with sem:
        start = time.perf_counter()
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                messages=STRATEGIES[strategy_name](snippet["snippet"]),
            )
            latency = time.perf_counter() - start
            raw = response.choices[0].message.content or ""
            parsed = extract_json_object(raw)
            usage = response.usage
            return {
                "strategy": strategy_name,
                "snippet_id": snippet["id"],
                "raw_response": raw,
                "extracted": parsed,
                "parse_success": parsed is not None,
                "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
                "cost_usd": estimate_cost(usage, MODEL),
                "latency_s": latency,
                "error": None,
            }
        except Exception as exc:
            return {
                "strategy": strategy_name,
                "snippet_id": snippet["id"],
                "raw_response": "",
                "extracted": None,
                "parse_success": False,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost_usd": 0.0,
                "latency_s": time.perf_counter() - start,
                "error": f"{type(exc).__name__}: {exc}",
            }

JUDGE_RUBRIC = """
Score the candidate extraction from 1 to 25.

25: all three fields are correct and fully grounded in the snippet.
20: all three are effectively correct with only a very minor formatting/detail issue.
15: two fields are correct and the remaining issue is minor or ambiguous.
10: two fields are correct but the remaining field is materially wrong or fabricated.
5: one field is correct, or the answer contains substantial unsupported information.
1: none are correct, the answer is unusable, or it is unparsable.

Important:
- Compare against the reference extraction and the actual snippet.
- Do not reward fabricated years.
- For j10, years_experience_required must be null because no years requirement is stated.
Return JSON only: {"score": integer, "reasoning": "brief explanation"}.
"""

async def judge_one(client: AsyncOpenAI, sem: asyncio.Semaphore, row: dict, snippet: dict, gold: dict) -> dict:
    async with sem:
        extracted_json = json.dumps(row["extracted"], ensure_ascii=False)
        gold_json = json.dumps({k: gold.get(k) for k in FIELDS}, ensure_ascii=False)
        prompt = (
            f"{JUDGE_RUBRIC}\n\n"
            f"Job snippet:\n{snippet['snippet']}\n\n"
            f"Reference extraction:\n{gold_json}\n\n"
            f"Candidate extraction:\n{extracted_json}\n"
        )
        try:
            response = await client.chat.completions.create(
                model=JUDGE_MODEL,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": "You are a strict evaluator of structured job-posting extraction."},
                    {"role": "user", "content": prompt},
                ],
            )
            raw = response.choices[0].message.content or ""
            obj = extract_json_object(raw) or {}
            score = obj.get("score")
            try:
                score = int(score)
            except (TypeError, ValueError):
                score = 1 if not row["parse_success"] else 5
            score = max(1, min(25, score))
            row["llm_judge_score"] = score
            row["judge_reasoning"] = str(obj.get("reasoning", "")).strip()
            row["judge_cost_usd"] = estimate_cost(response.usage, JUDGE_MODEL)
        except Exception as exc:
            row["llm_judge_score"] = None
            row["judge_reasoning"] = f"Judge error: {type(exc).__name__}: {exc}"
            row["judge_cost_usd"] = 0.0
        return row

def build_comparison(scored: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(scored)
    summary = df.groupby("strategy").agg(
        accuracy=("accuracy", "mean"),
        parse_rate=("parse_success", "mean"),
        judge_score=("llm_judge_score", "mean"),
        cost_usd=("cost_usd", "sum"),
        judge_cost_usd=("judge_cost_usd", "sum"),
        latency_p50_s=("latency_s", "median"),
    ).reindex(list(STRATEGIES))
    summary["total_cost_usd"] = summary["cost_usd"] + summary["judge_cost_usd"]
    return summary.reset_index()

def write_outputs(scored: list[dict], summary: pd.DataFrame):
    serialisable = []
    for row in scored:
        r = dict(row)
        serialisable.append(r)
    RESULTS_JSON.write_text(json.dumps(serialisable, indent=2, ensure_ascii=False))
    RAW_RESULTS_JSON.write_text(json.dumps(serialisable, indent=2, ensure_ascii=False))

    out = summary.copy()
    out["accuracy"] = out["accuracy"].round(3)
    out["parse_rate"] = (out["parse_rate"] * 100).round(1)
    out["judge_score"] = out["judge_score"].round(2)
    out["cost_usd"] = out["cost_usd"].round(6)
    out["judge_cost_usd"] = out["judge_cost_usd"].round(6)
    out["total_cost_usd"] = out["total_cost_usd"].round(6)
    out["latency_p50_s"] = out["latency_p50_s"].round(3)
    out.to_csv(CSV_RESULTS, index=False)

    lines = [
        "# MP1 Prompt Strategy Comparison",
        "",
        "This table is generated from the actual 10-snippet × 4-strategy run.",
        "Main model: `gpt-4o-mini`; temperature: `0.0`; judge: `gpt-4o`.",
        "",
        "| Strategy | Accuracy (mean / 3) | Parse rate | Judge score / 25 | Main cost ($) | Total cost incl. judge ($) | Latency p50 (s) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in out.iterrows():
        lines.append(
            f"| {r['strategy']} | {r['accuracy']:.3f} | {r['parse_rate']:.1f}% | "
            f"{r['judge_score']:.2f} | ${r['cost_usd']:.6f} | ${r['total_cost_usd']:.6f} | "
            f"{r['latency_p50_s']:.3f} |"
        )
    winner = out.sort_values(["accuracy", "parse_rate", "judge_score"], ascending=False).iloc[0]["strategy"]
    lines += [
        "",
        f"**Measured leading strategy:** `{winner}` using the primary ordering of accuracy, parse rate, then judge score.",
        "",
        "## Per-snippet results",
        "",
    ]
    for _, r in pd.DataFrame(scored).sort_values(["strategy", "snippet_id"]).iterrows():
        lines.append(
            f"- `{r['strategy']}` / `{r['snippet_id']}`: accuracy {r['accuracy']}/3, "
            f"parse={r['parse_success']}, judge={r.get('llm_judge_score')}, "
            f"latency={r['latency_s']:.3f}s, main cost=${r['cost_usd']:.6f}"
        )
    COMPARISON_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    writeup = f"""# MP1 Reflection — Prompt Strategy Comparison

> **Important:** This file is a template until the benchmark is executed. The four answers below should be finalised from the measured results in `mp1_comparison.md`; do not substitute example numbers from the brief.

## 1. Which strategy won, and on what dimension?

After running all 10 snippets with the same `gpt-4o-mini` model at temperature 0.0, the measured results should be compared primarily on accuracy and parse rate, with judge score, cost and latency as supporting dimensions. The final version of this section should name the winning strategy and quote its measured metrics from the comparison table.

## 2. What surprised you?

Describe one concrete result from the 40 main calls. Good examples include a strategy failing on the deliberately ambiguous `j10`, mishandling a spelled-out number such as `j07`, or producing valid JSON but an incorrect field. Explain what happened rather than making a general claim about prompting.

## 3. For my capstone domain, which strategy would I reach for first?

For the capstone, choose the strategy that provides the best balance of reliable extraction, clean parsing and acceptable cost. Explain why the measured evidence supports that choice and how it maps to the capstone's structured-answer requirements.

## 4. If I had another day, what would I try next?

A useful next experiment would be to improve the winning prompt without changing the model, then test it on more examples. Another option is to run a controlled model comparison after MP1, while keeping the four-strategy experiment itself unchanged so that prompt shape remains the isolated variable.

"""
    WRITEUP_MD.write_text(writeup, encoding="utf-8")

async def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Set it in the environment and rerun.")
    snippets, golden = load_data()
    client = AsyncOpenAI()
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    tasks = [
        run_one(client, sem, strategy, snippet)
        for strategy in STRATEGIES
        for snippet in snippets
    ]
    results = await asyncio.gather(*tasks)

    snippet_by_id = {s["id"]: s for s in snippets}
    scored = []
    for row in results:
        gold = golden[row["snippet_id"]]
        row["accuracy"] = score_accuracy(row["extracted"], gold)
        scored.append(row)

    judge_tasks = [
        judge_one(client, sem, row, snippet_by_id[row["snippet_id"]], golden[row["snippet_id"]])
        for row in scored
    ]
    scored = await asyncio.gather(*judge_tasks)

    summary = build_comparison(scored)
    write_outputs(scored, summary)

    print("\n=== MP1 COMPARISON ===")
    print(summary.to_string(index=False))
    print(f"\nWrote: {CSV_RESULTS}")
    print(f"Wrote: {COMPARISON_MD}")
    print(f"Wrote: {WRITEUP_MD}")

if __name__ == "__main__":
    asyncio.run(main())
