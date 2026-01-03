import yfinance as yf
import pandas as pd

from data.stitching import load_historical_prices, stitch_prices

TICKERS = [
    "GC=F", "SI=F", "HG=F", "PL=F", "PA=F",
    "CL=F", "NG=F", "ZC=F", "ZW=F", "ZS=F",
]

def load_commodity_prices() -> pd.DataFrame:
    """
    Load commodity prices with historical stitching where available.
    Yahoo data is optional; historical CSVs are allowed standalone.
    """
    prices = {}

    for ticker in TICKERS:
        # --- Yahoo (modern data, optional) ---
        yf_data = yf.download(
            ticker,
            start="2000-01-01",  # Yahoo era only
            auto_adjust=True,
            progress=False,
        )

        yahoo_series = None

        if isinstance(yf_data, pd.DataFrame) and not yf_data.empty:
            # Handle MultiIndex columns from yfinance
            if isinstance(yf_data.columns, pd.MultiIndex):
                if ("Close", ticker) in yf_data.columns:
                    s = yf_data[("Close", ticker)].dropna()
                else:
                    s = None
            else:
                s = yf_data["Close"] if "Close" in yf_data.columns else None

            if isinstance(s, pd.Series) and not s.empty:
                s.name = ticker
                yahoo_series = s

        if yahoo_series is not None:
            print(f"[Yahoo OK] {ticker}: {yahoo_series.index.min()} → {yahoo_series.index.max()}")
        else:
            print(f"[Yahoo MISSING] {ticker}")


        # --- Historical CSV (optional) ---
        hist_series = load_historical_prices(ticker)

        # --- Stitch logic ---
        if hist_series is not None and yahoo_series is not None:
            full_series = stitch_prices(hist_series, yahoo_series)
        elif hist_series is not None:
            full_series = hist_series
        elif yahoo_series is not None:
            full_series = yahoo_series
        else:
            continue  # nothing usable

        if not isinstance(full_series, pd.Series) or full_series.empty:
            continue

        prices[ticker] = full_series

    if not prices:
        raise RuntimeError(
            "No commodity price series could be loaded. "
            "Check CSV files or Yahoo connectivity."
        )

    return pd.concat(prices, axis=1, join="outer").sort_index()
