import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "historical"

CSV_MAP = {
    "Gold": "gold_price.csv",
    "Silver": "silver_price.csv",
}


def load_historical_series(name: str) -> pd.Series | None:
    """
    Load historical DAILY prices from local CSV (pre-2000).
    """
    filename = CSV_MAP.get(name)
    if not filename:
        return None

    path = DATA_DIR / filename
    if not path.exists():
        return None

    df = pd.read_csv(path)

    # normalize column names
    df.columns = [c.lower() for c in df.columns]

    if "date" not in df.columns:
        raise ValueError(f"'date' column not found in {filename}")

    price_col = (
        "price" if "price" in df.columns
        else "close" if "close" in df.columns
        else None
    )

    if price_col is None:
        raise ValueError(f"No price column found in {filename}")

    df["date"] = pd.to_datetime(df["date"])
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

    df = (
        df.dropna(subset=[price_col])
          .set_index("date")
          .sort_index()
    )

    return df[price_col]
