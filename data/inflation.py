import pandas as pd
import datetime as dt

def load_cpi(start_year: int = 1970) -> pd.DataFrame:
    start = f"{start_year}-01-01"
    end = dt.datetime.today().strftime("%Y-%m-%d")

    url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv"
        "?id=CPIAUCSL"
        f"&cosd={start}&coed={end}"
    )

    cpi = pd.read_csv(url)

    # ---- Robust date handling ----
    date_col = cpi.columns[0]  # first column is the date
    cpi[date_col] = pd.to_datetime(cpi[date_col])
    cpi.set_index(date_col, inplace=True)

    # Convert monthly CPI to daily
    cpi = cpi.resample("D").ffill()

    return cpi
