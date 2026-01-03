import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data.commodities import load_commodity_prices
from data.inflation import load_cpi
from strategies.momentum import time_series_momentum
from strategies.mean_reversion import real_price_percentile


TICKER_TO_NAME = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "HG=F": "Copper",
    "PL=F": "Platinum",
    "PA=F": "Palladium",
    "CL=F": "Crude Oil",
    "NG=F": "Natural Gas",
    "ZC=F": "Corn",
    "ZW=F": "Wheat",
    "ZS=F": "Soybeans",
}
HISTORICAL_REAL_COMMODITIES = {"GC=F", "SI=F"}

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Commodity Strategy Dashboard",
    layout="wide"
)

st.title("📊 Commodity Strategy Dashboard")
st.caption(
    "A storytelling, research-driven view of commodities — "
    "focused on context, signals, and relative positioning."
)

# --------------------------------------------------
# Load & prepare data
# --------------------------------------------------
@st.cache_data
def load_all_data(start_year=1968):
    # Prices already include historical CSVs + Yahoo (stitched)
    prices = load_commodity_prices()

    # CPI (monthly)
    cpi = load_cpi(start_year=start_year)

    # Inflation adjustment (monthly CPI → daily prices)
    latest_cpi = cpi.iloc[-1, 0]

    cpi_daily = (
        cpi.iloc[:, 0]
        .resample("D")
        .ffill()
    )

    cpi_daily = cpi_daily.reindex(prices.index, method="ffill")


    real_prices = prices.mul(latest_cpi / cpi_daily, axis=0)

    return prices, real_prices


prices, real_prices = load_all_data(start_year=1968)
percentiles = real_price_percentile(real_prices)

# Only show commodities that actually loaded
available_tickers = list(prices.columns)

AVAILABLE_TICKER_TO_NAME = {
    k: v for k, v in TICKER_TO_NAME.items() if k in available_tickers
}

if not AVAILABLE_TICKER_TO_NAME:
    st.error("No commodity data available.")
    st.stop()

# --------------------------------------------------
# Sidebar selection
# --------------------------------------------------
commodity_names = list(AVAILABLE_TICKER_TO_NAME.values())

# Prefer Silver if available
default_name = "Silver" if "Silver" in commodity_names else commodity_names[0]
default_index = commodity_names.index(default_name)

commodity_name = st.selectbox(
    "Select a commodity",
    commodity_names,
    index=default_index
)

commodity = [
    k for k, v in AVAILABLE_TICKER_TO_NAME.items() if v == commodity_name
][0]


st.caption(
    "Historical prices prior to ~2000 use World Bank spot/index data "
    "scaled to modern futures prices. These are for long-term "
    "inflation-adjusted context, not tradable price levels."
)

# -------------------------------
# Display controls
# -------------------------------
st.subheader("Chart controls")

col1, col2, col3 = st.columns(3)

with col1:
    use_log = st.checkbox("Log scale (nominal only)", value=True)


with col3:
    time_window = st.selectbox(
        "Time window",
        ["Full history", "1970s inflation era", "QE era", "Post-2008"]
    )

# ==================================================
# SECTION 1 — PRICE CONTEXT (Audited, LinkedIn-style)
# ==================================================
st.header("1️⃣ Price Context: What Headlines Miss")

nominal = prices[commodity].dropna()
real = real_prices[commodity].dropna()

if nominal.empty or real.empty:
    st.warning("Not enough data to display price history.")
    st.stop()

# -------------------------------
# Time window guard
# -------------------------------
def safe_window(series):
    if time_window == "1970s inflation era":
        if series.index.min().year > 1970:
            st.info("1970s data not available for this commodity.")
            return series
        return series["1968":"1985"]
    elif time_window == "QE era":
        return series["2008":"2013"]
    elif time_window == "Post-2008":
        return series["2008":]
    return series

nominal = safe_window(nominal)
real = safe_window(real)

# -------------------------------
# Metrics
# -------------------------------
# Always compute ATH from FULL real history
real_full = real_prices[commodity].dropna()

real_ath = real_full.max()
current_real = real.iloc[-1]   # still use windowed "today"
gap_pct = (real_ath / current_real - 1) * 100

# -------------------------------
# Build figure (LINES, not candles)
# -------------------------------
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=[
        f"{commodity_name} — Inflation-Adjusted Price (Real)",
        f"{commodity_name} — Nominal Price",
    ],
)

# Real price line
fig.add_trace(
    go.Scatter(
        x=real.index,
        y=real.values,
        mode="lines",
        line=dict(color="#7FDBFF", width=2),
        hovertemplate="Date: %{x}<br>Real price: %{y:.2f}<extra></extra>",
    ),
    row=1,
    col=1,
)

# Nominal price line
fig.add_trace(
    go.Scatter(
        x=nominal.index,
        y=nominal.values,
        mode="lines",
        line=dict(color="#CCCCCC", width=2),
        hovertemplate="Date: %{x}<br>Nominal price: %{y:.2f}<extra></extra>",
    ),
    row=2,
    col=1,
)

# -------------------------------
# Historical peak line
# -------------------------------
fig.add_hline(
    y=real_ath,
    line_dash="dash",
    line_color="white",
    annotation_text="Historical real peak",
    annotation_position="top left",
    row=1,
    col=1,
)

# -------------------------------
# PURE ANNOTATION "I-BAR" (paper coords)
# -------------------------------
# X position near right edge (constant)
x_bracket = 0.97

# Vertical line: current price → historical peak
fig.add_shape(
    type="line",
    xref="paper",
    yref="y",
    x0=x_bracket,
    x1=x_bracket,
    y0=current_real,
    y1=real_ath,
    line=dict(color="white", width=3),
)

# Top cap
fig.add_shape(
    type="line",
    xref="paper",
    yref="y",
    x0=x_bracket - 0.015,
    x1=x_bracket + 0.015,
    y0=real_ath,
    y1=real_ath,
    line=dict(color="white", width=3),
)

# Bottom cap
fig.add_shape(
    type="line",
    xref="paper",
    yref="y",
    x0=x_bracket - 0.015,
    x1=x_bracket + 0.015,
    y0=current_real,
    y1=current_real,
    line=dict(color="white", width=3),
)

# Label
fig.add_annotation(
    xref="paper",
    yref="y",
    x=x_bracket - 0.02,
    y=(current_real + real_ath) / 2,
    text=f"Needs +{gap_pct:.0f}% to reach real peak",
    showarrow=False,
    font=dict(size=12),
    align="right",
)

# -------------------------------
# Layout
# -------------------------------
fig.update_layout(
    template="plotly_dark",
    height=850,
    showlegend=False,
    yaxis_title="Real price (inflation-adjusted)",
    yaxis2_title="Nominal price",
    xaxis_rangeslider_visible=False,
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "scrollZoom": False,
        "displayModeBar": "hover",  # only shows on desktop hover
        "responsive": True
    }
)

# -------------------------------
# Explanation
# -------------------------------
def valuation_story(pct_to_peak, percentile):
    if percentile is None or pd.isna(percentile):
        return (
            "There is not enough long-term historical data to make a "
            "reliable valuation comparison."
        )

    if percentile >= 90 and pct_to_peak > 50:
        return (
            "Prices are high relative to most of history, "
            "but still well below the most extreme historical spike.\n\n"
            "This means the asset feels expensive compared to typical past prices, "
            "yet remains far from the most exceptional moment ever recorded."
        )

    if percentile >= 90 and pct_to_peak <= 20:
        return (
            "Prices are high relative to history and are approaching "
            "their historical extremes.\n\n"
            "Both typical historical comparisons and extreme comparisons "
            "suggest elevated valuation."
        )

    if percentile < 70:
        return (
            "Prices are within the normal historical range.\n\n"
            "They are neither close to historical extremes nor elevated "
            "relative to most of history."
        )

    return (
        "Prices are moderately elevated compared to history, "
        "but not near historical extremes."
    )


st.markdown(
    f"""
### 🧠 How to Read This Chart

This chart answers **two different questions**.  
They measure **different things**, so they can point in opposite directions.

---

### 1️⃣ How far are prices from the most extreme moment in history?

- The dashed line shows the **single highest inflation-adjusted price ever**
- The white bracket shows how much prices would need to rise *from today* to match it
- Current gap: **+{gap_pct:.0f}%**

That historical peak was **brief and exceptional** — it did not last long.

---

### 2️⃣ How expensive is today compared to *most* of history?

- The percentile compares today’s price to **every historical observation**
- Current position: **{percentiles[commodity]:.0f}th percentile**

This means today’s price is higher than **most historical prices**,  
even if it is still far below the most extreme spike ever recorded.

---

### 🧩 Why both statements can be true

- Extreme peaks are **rare**
- Most prices in history were much lower
- So prices can feel **expensive compared to typical history**,  
  yet still be **far below a once-in-a-generation extreme**

That’s why headlines and long-term context often disagree.
"""
)

st.divider()



# ==================================================
# SECTION 2 — SIGNALS
# ==================================================
st.header("2️⃣ What History & Trend Say Right Now")

momentum = time_series_momentum(prices).iloc[-1]
percentiles = real_price_percentile(real_prices)

def trend_label(x):
    return "Upward trend 📈" if x == 1 else "Downward trend 📉"

def valuation_label(p):
    if p is None or pd.isna(p):
        return "Limited historical data"
    if p < 30:
        return "Historically cheap"
    elif p > 70:
        return "Historically expensive"
    else:
        return "Fairly priced"

st.subheader(commodity_name)

st.markdown(
    f"""
    **Trend:** {trend_label(momentum[commodity])}  
    **Valuation:** {valuation_label(percentiles[commodity])}  
    ({percentiles[commodity]:.0f}th percentile of history)

    *Trend measures recent price direction.  
    Valuation compares today’s real price to available historical data.*
    """
)

st.divider()

# ==================================================
# SECTION 3 — RELATIVE RANKING
# ==================================================
st.header("3️⃣ Relative Positioning Across Commodities")

normalized_val = 1 - (percentiles / 100)   # cheap = high score
ranking = normalized_val.fillna(0) + momentum.fillna(0)
ranking = ranking.sort_values(ascending=False)


rank_df = pd.DataFrame({
    "Commodity": [TICKER_TO_NAME.get(c, c) for c in ranking.index],
    "Relative Score": ranking.values
})

st.dataframe(rank_df, use_container_width=True)

st.markdown(
    """
    **How to read this table**

    - Higher scores → cheaper *and* trending upward  
    - Lower scores → expensive *and/or* trending downward  

    This is **not a prediction**.  
    It highlights where **historical context and trend currently align**.
    """
)

# --------------------------------------------------
# Footer
# --------------------------------------------------

