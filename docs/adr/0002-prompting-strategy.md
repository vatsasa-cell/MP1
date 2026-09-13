# ADR 0002: Prompting Strategy for the Capstone

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision:** Use Few-shot prompting as the initial prompting strategy for the capstone
- **Benchmark:** MP1 — Prompt Strategy Comparison

## Context

The capstone requires the LLM to produce reliable answers from the available knowledge data while maintaining a predictable and parseable response format.

As part of MP1, four prompting strategies were evaluated:

1. Zero-shot prompting
2. Few-shot prompting
3. Structured prompting
4. Chain-of-thought prompting

Each strategy was tested against the same 10 job snippets using the same `gpt-4o-mini` model with temperature `0.0`.

The evaluation considered:

- Accuracy
- Parsing success
- LLM-as-judge score
- Main model cost
- Total cost including judge calls
- Latency

## Decision

We will use **Few-shot prompting as the initial prompting strategy for the capstone**.

Few-shot was selected because it produced the strongest overall measured performance in the MP1 benchmark.

The measured results were:

| Strategy | Accuracy (/3) | Parsing Success | Judge Score (/25) | Main Cost ($) | Total Cost incl. Judge ($) | Latency p50 (s) |
|---|---:|---:|---:|---:|---:|---:|
| Zero-shot | 2.700 | 100% | 21.50 | 0.000341 | 0.012709 | 0.991 |
| Few-shot | **3.000** | **100%** | **23.50** | 0.000475 | **0.012645** | 0.924 |
| Structured | 2.700 | 100% | 21.50 | 0.000534 | 0.012804 | 0.799 |
| Chain-of-thought | 2.800 | 100% | 22.50 | 0.000411 | 0.012771 | 0.798 |

Few-shot achieved:

- **3.0/3 average accuracy**
- **100% parsing success**
- **23.5/25 judge score**
- **0.924 second p50 latency**
- **$0.000475 main model cost**
- **$0.012645 total measured cost including judge calls**

Most importantly, Few-shot achieved **3/3 accuracy on all 10 evaluated snippets**, while the other strategies had at least some snippets with partial accuracy.

## Rationale

The benchmark indicates that providing representative examples helps the model understand the expected extraction behavior more reliably.

This is important for the capstone because the system needs to produce useful and consistent answers from organizational knowledge.

The experiment also showed that parsing success and content accuracy are different evaluation dimensions. All four strategies achieved 100% parsing success, but their accuracy differed.

Structured prompting had the lowest p50 latency at approximately 0.799 seconds, but its accuracy was only 2.7/3. Therefore, latency alone was not sufficient to select the strategy.

Few-shot provided the best overall balance of:

- Correctness
- Reliable parsing
- Judge quality
- Cost
- Latency

## Capstone Application

The Few-shot strategy will be used as the starting point for the capstone's LLM prompts.

The prompt will provide representative examples demonstrating:

- The type of question being asked
- The expected answer behavior
- The expected response structure
- How relevant information should be extracted
- How ambiguous or unsupported information should be handled

The examples will be kept representative of the capstone's employee knowledge and question-answering domain.

Where structured output is required, the Few-shot approach can be combined with explicit structured-output/schema requirements. The MP1 results show that structured output is useful for predictable parsing, while the examples provide additional guidance for improving answer correctness.

## Consequences

### Positive consequences

- Higher measured accuracy than the other tested strategies.
- 100% parsing success in the MP1 benchmark.
- Highest LLM-as-judge score.
- Competitive latency.
- Lowest total measured cost including judge calls in this benchmark.
- Provides concrete examples of the expected behavior to the model.
- Provides a clear baseline for future prompt improvements.

### Negative consequences

- Few-shot prompts require additional prompt tokens because examples are included.
- Maintaining examples adds some prompt complexity.
- Poorly selected examples could introduce unwanted behavior or bias.
- The MP1 benchmark contains only 10 snippets, so the results may not generalize to a larger production dataset.

## Alternatives Considered

### Zero-shot

Zero-shot is simple and has a relatively low main model cost. However, its measured accuracy was only 2.7/3 and its judge score was 21.5/25.

It was therefore not selected as the primary strategy.

### Structured prompting

Structured prompting achieved 100% parsing success and the fastest p50 latency at 0.799 seconds. However, its accuracy was 2.7/3 and judge score was 21.5/25.

It may still be used together with Few-shot prompting when predictable output structure is required.

### Chain-of-thought

Chain-of-thought achieved 2.8/3 accuracy and a judge score of 22.5/25. Its p50 latency was approximately 0.798 seconds.

Although its accuracy was better than Zero-shot and Structured prompting, it did not outperform Few-shot.

It was therefore not selected as the primary strategy.

## Validation Plan

The Few-shot strategy should be validated against a larger set of examples before being considered production-ready.

The next experiment should:

1. Keep `gpt-4o-mini` and temperature `0.0` unchanged.
2. Improve the Few-shot examples and instructions.
3. Include examples representing difficult and ambiguous cases.
4. Run the improved prompt against a larger evaluation set.
5. Compare the results against the MP1 Few-shot baseline.
6. Measure accuracy, parsing success, cost, latency, and judge score again.

If the improved Few-shot prompt maintains its accuracy advantage while meeting the capstone's cost and latency requirements, it will remain the preferred prompting strategy.

## Decision Summary

**Accepted:** Start the capstone with **Few-shot prompting**, combined with explicit structured-output requirements where needed.

The decision is based on the measured MP1 results rather than the example values in the project brief.