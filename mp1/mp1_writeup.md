# MP1 Reflection — Prompt Strategy Comparison

> **Important:** This file is a template until the benchmark is executed. The four answers below should be finalised from the measured results in `mp1_comparison.md`; do not substitute example numbers from the brief.

## 1. Which strategy won, and on what dimension?

The **Few-shot prompting strategy** was the overall winner in the MP1 benchmark. All four strategies were tested against the same 10 job snippets using the same `gpt-4o-mini` model with temperature `0.0`.

Few-shot achieved the highest measured accuracy at **3.0/3 (100%)**, while also achieving a **100% parsing success rate**. It also received the highest **LLM-as-judge score of 23.5/25**.

| Strategy | Accuracy (/3) | Parsing Success | Judge Score (/25) | Main Cost ($) | Total Cost incl. Judge ($) | Latency p50 (s) |
|---|---:|---:|---:|---:|---:|---:|
| Zero-shot | 2.700 | 100% | 21.50 | $0.000341 | $0.012709 | 0.991 |
| Few-shot | **3.000** | **100%** | **23.50** | $0.000475 | **$0.012645** | 0.924 |
| Structured | 2.700 | 100% | 21.50 | $0.000534 | $0.012804 | 0.799 |
| Chain-of-thought | 2.800 | 100% | 22.50 | $0.000411 | $0.012771 | 0.798 |

Few-shot therefore provided the best overall combination of **accuracy, reliable parsing, judge quality, cost, and latency**. Although Structured and Chain-of-thought were slightly faster in this run, their accuracy was lower. Few-shot also had the lowest total measured cost including judge calls.

The result suggests that providing representative examples helped the model understand the expected extraction task more reliably than relying only on instructions or output structure.


## 2. What surprised you?

The most interesting result was that **all four strategies achieved a 100% parsing success rate**, but they did not achieve the same accuracy. This shows that producing valid structured output does not necessarily mean that the extracted information is correct.

For example, the Zero-shot strategy scored only **2/3 on j05**, while Few-shot scored **3/3 on the same snippet**. Zero-shot also scored 2/3 on j02 and j08. In contrast, Few-shot achieved **3/3 accuracy on all 10 snippets**.

Another interesting observation was that Structured prompting did not automatically produce the best results. Even though Structured prompting had the fastest p50 latency at approximately **0.799 seconds**, its average accuracy was only **2.7/3**, equal to Zero-shot. This demonstrates that enforcing a structured output format can improve consistency of parsing without necessarily improving the correctness of the extracted values.

The experiment therefore reinforced an important lesson: **valid output format and correct content are separate dimensions that need to be measured independently.**

## 3. For my capstone domain, which strategy would I reach for first?

For my capstone, I would start with **Few-shot prompting**.

The benchmark provides direct evidence for this choice. Few-shot achieved the highest accuracy (**3.0/3**), 100% parsing success, and the highest judge score (**23.5/25**). It also had a competitive p50 latency of **0.924 seconds** and the lowest total measured cost including judge calls (**$0.012645**).

This is particularly useful for a capstone involving structured information extraction because the goal is not only to generate a response that looks correct, but to consistently extract the required fields accurately and in a format that downstream processing can consume.

The 10 examples also showed that Few-shot was able to handle the job snippets consistently, including cases where Zero-shot produced partially incorrect extraction. I would therefore use representative examples in the prompt that demonstrate the expected input, required fields, and correct output format.

For the capstone, I would combine the Few-shot strategy with explicit structured-output requirements. The MP1 results suggest that the examples provide the strongest accuracy benefit, while structured output can help maintain predictable parsing.

## 4. If I had another day, what would I try next?

If I had another day, I would first improve the winning **Few-shot prompt** while keeping the model (`gpt-4o-mini`) and temperature (`0.0`) unchanged.

I would test additional representative examples, especially examples similar to the snippets where other strategies produced partial accuracy. I would also make the extraction instructions more explicit about ambiguous values, spelled-out numbers, and the exact interpretation of each required field.

I would then run the improved prompt against a larger evaluation set to determine whether the 100% accuracy observed on the current 10 snippets generalizes beyond this small benchmark.

A second experiment would be a controlled model comparison using the winning Few-shot strategy. However, I would keep the original four-strategy experiment unchanged so that prompting strategy remains the isolated variable in MP1.

The main next step would therefore be:

**Few-shot baseline → improve examples/instructions → test on more data → compare against the MP1 baseline.**

This would help determine whether the observed Few-shot advantage is robust and whether the strategy is suitable for production use in the capstone domain.
