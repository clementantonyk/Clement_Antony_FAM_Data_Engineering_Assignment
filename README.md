# Stock Monthly Aggregator

Converts daily stock price data into monthly OHLC data, calculates technical indicators, and generates one output CSV file per ticker.

## Requirements

- Python 3.10+
- pandas

## Run

```bash
python -m pip install -r requirements.txt
python main.py
```

**Input:** `data/output_file.csv`  
**Output:** `output/`

## Monthly Aggregation

Data is grouped by ticker and calendar month. Open and close represent actual trading-day prices, not averages.

- `date` — last trading date of the month
- `open` — open price on the first trading day
- `high` — highest daily high during the month
- `low` — lowest daily low during the month
- `close` — close price on the last trading day

## Technical Indicators

All indicators are calculated on the aggregated monthly data, not the original daily series.

- **SMA 10 / 20:** Rolling mean of the last 10 or 20 monthly closes.
- **EMA 10 / 20:** Seeded with the SMA of the first N monthly closes, then updated recursively using `alpha = 2 / (N + 1)`.
- **Donchian Channels:** 20-month rolling maximum of monthly highs and minimum of monthly lows.
- **Bollinger Bands:** 20-month rolling mean of monthly closes, plus and minus 2 standard deviations.
- **Z-score:** Distance of the monthly close from the 20-month rolling mean, measured in rolling standard deviations.

## Assumptions and Edge Cases

The assignment does not specify lookback periods for Donchian Channels, Bollinger Bands, or the Z-score, so I use a 20-month window to capture longer-term price trends and reduce sensitivity to short-term fluctuations. For Bollinger Bands, I use `k = 2` to measure price deviations from the rolling mean.

- Standard deviation uses pandas' sample standard deviation (`ddof=1`).
- EMA is seeded with the SMA of the first N months, then updated recursively.
- Indicators remain empty until enough monthly observations are available to calculate them.
- Z-score remains empty when the rolling standard deviation is zero.
- Missing months are not artificially filled.
- The expected output covers 24 monthly periods, from January 2018 through December 2019.

## Output

Generates 10 files named `output/result_{SYMBOL}.csv`, each containing 24 data rows plus a header.

Columns:

`date, ticker, open, high, low, close, sma_10, sma_20, ema_10, ema_20, donchian_upper, donchian_lower, bb_mid, bb_upper, bb_lower, z_score`
