# ADR 0002 --- Prompting Strategy Choice

## Status

Proposed

## Context

MP1 compares zero-shot, few-shot, structured/role-based, and
chain-of-thought prompting on the supplied 10-job extraction task.

## Decision

Use the strategy that wins on the measured MP1 results, prioritising
extraction accuracy and parse reliability while considering cost and
latency.

## Evidence

Run `python mp1/mp1_prompt_lab.py` and record the measured result in
`mp1/mp1_comparison.md`.

## Consequences

The chosen prompting pattern becomes the starting point for the
capstone. Revisit the decision if later evaluation on capstone-domain
examples shows materially different behaviour.
