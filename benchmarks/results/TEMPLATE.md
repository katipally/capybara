# Benchmark run: YYYY-MM-DD

- **Models:** (e.g. Haiku 4.5, Sonnet 4.6)
- **Repeats per cell:** N
- **Tasks:** 5 (email-validator, debounce, csv-column-sum, flatten, date-input)
- **Command:** `npx promptfoo eval -c promptfooconfig.yaml --output results/latest.json`

## Medians (from `node score.js`)

| variant  | runs | pass% | loc | cost($) | latency(ms) |
|----------|------|-------|-----|---------|-------------|
| baseline |      |       |     |         |             |
| capybara |      |       |     |         |             |

**capybara vs baseline:** __% fewer lines, __% cheaper, __% faster. Correctness:
baseline __%, capybara __%.

## Notes

What surprised you, which tasks drove the gap, any task where capybara lost or broke
correctness. Be honest, a regression here is worth more than a clean chart.
