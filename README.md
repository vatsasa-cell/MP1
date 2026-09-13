# MP1 Deliverables

## Run

From the repository root:

``` bash
python -m pip install -r mp1/requirements.txt
export OPENAI_API_KEY="your-key"
python mp1/mp1_prompt_lab.py
```

The runner performs 10 snippets × 4 strategies = 40 main `gpt-4o-mini`
calls in parallel, then evaluates the results with `gpt-4o` as the
judge.

## Deliverables

-   `mp1/mp1_prompt_lab.py` --- end-to-end runner
-   `mp1/mp1_comparison.md` --- generated comparison table
-   `mp1/mp1_writeup.md` --- one-page reflection template to finalise
    from measured results
-   `mp1/data/job_snippets.jsonl` --- supplied 10 snippets
-   `mp1/data/golden_set.jsonl` --- supplied reference extractions
-   `docs/adr/0002-prompting-strategy.md` --- optional ADR

## Important

Do not use the example numbers from the Week 5 brief. The comparison
must contain values from the actual run.
