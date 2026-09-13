# MP1 Prompt Strategy Comparison

This table is generated from the actual 10-snippet × 4-strategy run.
Main model: `gpt-4o-mini`; temperature: `0.0`; judge: `gpt-4o`.

| Strategy | Accuracy (mean / 3) | Parse rate | Judge score / 25 | Main cost ($) | Total cost incl. judge ($) | Latency p50 (s) |
|---|---:|---:|---:|---:|---:|---:|
| zero_shot | 2.700 | 100.0% | 21.50 | $0.000341 | $0.012709 | 0.991 |
| few_shot | 3.000 | 100.0% | 23.50 | $0.000475 | $0.012645 | 0.924 |
| structured | 2.700 | 100.0% | 21.50 | $0.000534 | $0.012804 | 0.799 |
| cot | 2.800 | 100.0% | 22.50 | $0.000411 | $0.012771 | 0.798 |

**Measured leading strategy:** `few_shot` using the primary ordering of accuracy, parse rate, then judge score.

## Per-snippet results

- `cot` / `j01`: accuracy 3/3, parse=True, judge=25, latency=0.754s, main cost=$0.000040
- `cot` / `j02`: accuracy 2/3, parse=True, judge=20, latency=0.873s, main cost=$0.000040
- `cot` / `j03`: accuracy 3/3, parse=True, judge=25, latency=0.723s, main cost=$0.000042
- `cot` / `j04`: accuracy 3/3, parse=True, judge=25, latency=0.743s, main cost=$0.000041
- `cot` / `j05`: accuracy 3/3, parse=True, judge=25, latency=1.729s, main cost=$0.000041
- `cot` / `j06`: accuracy 3/3, parse=True, judge=15, latency=0.756s, main cost=$0.000042
- `cot` / `j07`: accuracy 3/3, parse=True, judge=25, latency=0.754s, main cost=$0.000040
- `cot` / `j08`: accuracy 2/3, parse=True, judge=20, latency=0.870s, main cost=$0.000042
- `cot` / `j09`: accuracy 3/3, parse=True, judge=20, latency=0.963s, main cost=$0.000041
- `cot` / `j10`: accuracy 3/3, parse=True, judge=25, latency=0.840s, main cost=$0.000043
- `few_shot` / `j01`: accuracy 3/3, parse=True, judge=25, latency=1.019s, main cost=$0.000046
- `few_shot` / `j02`: accuracy 3/3, parse=True, judge=25, latency=0.924s, main cost=$0.000046
- `few_shot` / `j03`: accuracy 3/3, parse=True, judge=25, latency=0.924s, main cost=$0.000048
- `few_shot` / `j04`: accuracy 3/3, parse=True, judge=25, latency=0.863s, main cost=$0.000047
- `few_shot` / `j05`: accuracy 3/3, parse=True, judge=25, latency=0.945s, main cost=$0.000047
- `few_shot` / `j06`: accuracy 3/3, parse=True, judge=15, latency=0.857s, main cost=$0.000048
- `few_shot` / `j07`: accuracy 3/3, parse=True, judge=25, latency=0.983s, main cost=$0.000046
- `few_shot` / `j08`: accuracy 3/3, parse=True, judge=25, latency=0.865s, main cost=$0.000049
- `few_shot` / `j09`: accuracy 3/3, parse=True, judge=20, latency=0.817s, main cost=$0.000047
- `few_shot` / `j10`: accuracy 3/3, parse=True, judge=25, latency=1.205s, main cost=$0.000050
- `structured` / `j01`: accuracy 3/3, parse=True, judge=25, latency=0.751s, main cost=$0.000053
- `structured` / `j02`: accuracy 2/3, parse=True, judge=20, latency=0.780s, main cost=$0.000052
- `structured` / `j03`: accuracy 2/3, parse=True, judge=15, latency=1.035s, main cost=$0.000054
- `structured` / `j04`: accuracy 3/3, parse=True, judge=25, latency=0.764s, main cost=$0.000053
- `structured` / `j05`: accuracy 3/3, parse=True, judge=25, latency=0.838s, main cost=$0.000053
- `structured` / `j06`: accuracy 3/3, parse=True, judge=15, latency=0.828s, main cost=$0.000054
- `structured` / `j07`: accuracy 3/3, parse=True, judge=25, latency=0.895s, main cost=$0.000053
- `structured` / `j08`: accuracy 2/3, parse=True, judge=20, latency=0.818s, main cost=$0.000055
- `structured` / `j09`: accuracy 3/3, parse=True, judge=20, latency=0.760s, main cost=$0.000053
- `structured` / `j10`: accuracy 3/3, parse=True, judge=25, latency=0.759s, main cost=$0.000055
- `zero_shot` / `j01`: accuracy 3/3, parse=True, judge=25, latency=1.370s, main cost=$0.000033
- `zero_shot` / `j02`: accuracy 2/3, parse=True, judge=20, latency=1.272s, main cost=$0.000033
- `zero_shot` / `j03`: accuracy 3/3, parse=True, judge=25, latency=1.194s, main cost=$0.000035
- `zero_shot` / `j04`: accuracy 3/3, parse=True, judge=25, latency=0.892s, main cost=$0.000034
- `zero_shot` / `j05`: accuracy 2/3, parse=True, judge=20, latency=0.966s, main cost=$0.000033
- `zero_shot` / `j06`: accuracy 3/3, parse=True, judge=15, latency=0.943s, main cost=$0.000035
- `zero_shot` / `j07`: accuracy 3/3, parse=True, judge=25, latency=0.896s, main cost=$0.000033
- `zero_shot` / `j08`: accuracy 2/3, parse=True, judge=20, latency=1.003s, main cost=$0.000035
- `zero_shot` / `j09`: accuracy 3/3, parse=True, judge=15, latency=0.978s, main cost=$0.000034
- `zero_shot` / `j10`: accuracy 3/3, parse=True, judge=25, latency=1.427s, main cost=$0.000036
