from pathlib import Path

import pandas as pd

TICKERS = [
    "AAPL",
    "AMD",
    "AMZN",
    "AVGO",
    "CSCO",
    "MSFT",
    "NFLX",
    "PEP",
    "TMUS",
    "TSLA",
]
INPUT_FILE = Path("data/output_file.csv")
OUTPUT_DIR = Path("output")
WINDOW = 20
BOLLINGER_K = 2

OUTPUT_COLUMNS = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "sma_10",
    "sma_20",
    "ema_10",
    "ema_20",
    "donchian_upper",
    "donchian_lower",
    "bb_mid",
    "bb_upper",
    "bb_lower",
    "z_score",
]


def load_data(file_path):
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


def aggregate_monthly(daily):
    daily = daily.copy()
    daily["year_month"] = daily["date"].dt.to_period("M")
    monthly = (
        daily.groupby(["ticker", "year_month"], sort=True)
        .agg(
            date=("date", "last"),
            open=("open", "first"),
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
        )
        .reset_index()
    )
    return monthly.sort_values(["ticker", "date"]).reset_index(drop=True)


def calculate_ema(close, span):
    seeded = close.copy()
    seeded.iloc[:span - 1] = float("nan")
    if len(close) >= span:
        seeded.iloc[span - 1] = close.iloc[:span].mean()
    return seeded.ewm(span=span, adjust=False).mean()


def add_technical_indicators(monthly):
    parts = [
        _indicators_for_symbol(group.copy())
        for _, group in monthly.groupby("ticker", sort=True)
    ]
    return pd.concat(parts, ignore_index=True)


def _indicators_for_symbol(monthly):
    close = monthly["close"]
    high = monthly["high"]
    low = monthly["low"]

    monthly["sma_10"] = close.rolling(10).mean()
    monthly["sma_20"] = close.rolling(20).mean()
    monthly["ema_10"] = calculate_ema(close, 10)
    monthly["ema_20"] = calculate_ema(close, 20)
    monthly["donchian_upper"] = high.rolling(WINDOW).max()
    monthly["donchian_lower"] = low.rolling(WINDOW).min()

    mid = close.rolling(WINDOW).mean()
    std = close.rolling(WINDOW).std()
    monthly["bb_mid"] = mid
    monthly["bb_upper"] = mid + BOLLINGER_K * std
    monthly["bb_lower"] = mid - BOLLINGER_K * std
    monthly["z_score"] = (close - mid) / std.mask(std.eq(0))
    return monthly


def write_partitioned_outputs(monthly, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for ticker in TICKERS:
        symbol = monthly.loc[monthly["ticker"] == ticker]
        if len(symbol) != 24:
            raise ValueError(f"{ticker} must have 24 monthly rows.")
        symbol[OUTPUT_COLUMNS].to_csv(output_dir / f"result_{ticker}.csv", index=False)


def main():
    daily = load_data(INPUT_FILE)
    monthly = aggregate_monthly(daily)
    enriched = add_technical_indicators(monthly)
    write_partitioned_outputs(enriched, OUTPUT_DIR)


if __name__ == "__main__":
    main()
