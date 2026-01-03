# 📊 Commodity Strategy Dashboard

A research-driven, visual dashboard for understanding commodity prices through **long-term historical context**, **inflation adjustment**, and **simple quantitative signals**.

This project is designed to answer a common question:

> “Are commodity prices really at all-time highs — or do they just *look* that way because of inflation?”

---

## 🚀 What This Dashboard Does

The dashboard combines **historical spot data**, **modern futures prices**, and **inflation adjustment** to show:

- How today’s prices compare to **true historical extremes**
- Whether commodities are **cheap or expensive relative to history**
- How **trend and valuation** align across commodities

It emphasizes **context over prediction**.

---

## 🧠 Key Concepts

### 1️⃣ Nominal vs Inflation-Adjusted Prices

- **Nominal price**  
  The price you see in headlines (not adjusted for inflation).

- **Inflation-adjusted (real) price**  
  Prices adjusted using CPI so that a dollar in 1975 is comparable to a dollar today.

This explains why prices can:
- Look like “all-time highs” nominally  
- Yet still be below past peaks in real terms

---

### 2️⃣ Historical Data Stitching (Gold & Silver)

For **Gold and Silver only**, the dashboard uses:

- **Pre-2000 historical spot/index data** (World Bank-style series)
- **Post-2000 futures data** (Yahoo Finance)

These are **stitched together** to create a long real-price history going back to the late 1960s.

⚠️ These historical prices are:
- For **context only**
- **Not tradable price levels**

---

### 3️⃣ Other Commodities (Post-2000 Only)

For commodities like:
- Crude Oil
- Copper
- Natural Gas
- Corn, Wheat, Soybeans

Reliable inflation-adjusted data **does not exist before modern futures markets**, so:

- Analysis starts in the 2000s
- Long-term comparisons are limited
- Signals are still useful for **relative positioning**, not century-long valuation

---

## 📈 Dashboard Sections

### 🟦 Section 1 — Price Context

A LinkedIn-style visual showing:

- **Top chart:** Inflation-adjusted price (candlesticks)
- **Bottom chart:** Nominal price (candlesticks)
- A visual “bracket” showing how far today’s real price is from the historical real peak

This helps answer:
> “How far are we from true historical extremes?”

---

### 🟨 Section 2 — Signals

Two simple, interpretable signals:

#### 📉 Valuation (Mean Reversion)
- Compares today’s **real price** to historical prices
- Expressed as a **percentile**
  - Low percentile → historically cheap
  - High percentile → historically expensive

#### 📈 Trend (Momentum)
- Looks at recent price direction
- Classifies trend as:
  - Upward 📈
  - Downward 📉

---

### 🟩 Section 3 — Relative Ranking

All commodities are ranked based on:
- Cheapness (valuation percentile)
- Trend direction

This highlights where **historical context and momentum align**.

> This is **not a prediction model** — it’s a positioning framework.

---

## 🗂️ Project Structure

```
📁 commodity-strategy-dashboard/
├── app.py # Streamlit app
├── requirements.txt # Python dependencies
├── data/
  ├── commodities.py # Yahoo + historical stitching logic
  ├── stitching.py # CSV + Yahoo merge logic
  ├── inflation.py # CPI loading & handling
  ├── historical/ # Gold & Silver CSVs
├── strategies/
  ├── momentum.py # Trend signal
  ├── mean_reversion.py # Valuation percentile
├── README.md

```
---

## 🔧 Requirements

Install packages:
```bash
pip install -r requirements.txt
```

---

## ⚠️ Important Limitations

- Historical pre-2000 data is approximate and scaled

- Inflation-adjusted analysis is most reliable for Gold & Silver

- Futures prices ≠ spot prices

- This is not financial advice

The dashboard is intended for:

- Education

- Research

- Long-term perspective

---

## 📜 License

MIT License---

---
