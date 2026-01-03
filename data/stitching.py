import pandas as pd
from pathlib import Path

HISTORICAL_DIR = Path(__file__).resolve().parent / "historical"

HISTORICAL_MAP = {
    "GC=F": "gold_price.csv",
    "SI=F": "silver_price.csv",
}

def load_historical_prices(ticker: str) -> pd.Series | None:
    """
    Load historical prices from CSV with flexible schema.
    """

    if ticker not in HISTORICAL_MAP:
        return None

    csv_path = HISTORICAL_DIR / HISTORICAL_MAP[ticker]
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)

    # normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # detect date column
    date_col = None
    for c in df.columns:
        if c in ["date", "datetime", "time", "timestamp"]:
            date_col = c
            break

    if date_col is None:
        raise ValueError(
            f"No date column found in {csv_path.name}. "
            f"Found columns: {list(df.columns)}"
        )

    # detect price column
    price_col = None
    for c in ["price", "close", "value"]:
        if c in df.columns:
            price_col = c
            break

    if price_col is None:
        raise ValueError(
            f"No price column found in {csv_path.name}. "
            f"Found columns: {list(df.columns)}"
        )

    df[date_col] = pd.to_datetime(df[date_col])
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

    df = (
        df.dropna(subset=[price_col])
          .set_index(date_col)
          .sort_index()
    )

    return df[price_col]


def stitch_prices(historical: pd.Series | None, yahoo: pd.Series | None) -> pd.Series | None:
    """
    Combine historical (CSV) and Yahoo prices.

    - Historical CSV is used up to its last date
    - Yahoo data is appended AFTER that date
    - If only one exists, use it
    """
    if historical is None and yahoo is None:
        return None

    if historical is None:
        return yahoo.sort_index()

    if yahoo is None:
        return historical.sort_index()

    last_hist_date = historical.index.max()

    yahoo_after = yahoo[yahoo.index > last_hist_date]

    combined = pd.concat([historical, yahoo_after])
    return combined.sort_index()

