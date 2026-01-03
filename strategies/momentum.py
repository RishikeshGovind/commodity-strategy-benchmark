def time_series_momentum(prices, lookback=252):
    returns = prices.pct_change(lookback)
    signal = returns.applymap(lambda x: 1 if x > 0 else -1)
    return signal
