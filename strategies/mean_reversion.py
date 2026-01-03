import pandas as pd

def real_price_percentile(real_prices: pd.DataFrame) -> pd.Series:
    """
    Computes where the latest real price sits relative to its own history.
    Returns percentile (0–100).
    """

    percentiles = {}

    for col in real_prices.columns:
        series = real_prices[col].dropna()

        if len(series) < 252:  # < ~1 year of data
            percentiles[col] = None
            continue

        current = series.iloc[-1]
        percentile = (series < current).mean() * 100
        percentiles[col] = percentile

    return pd.Series(percentiles)
