def real_returns(prices, cpi):
    inflation = cpi.pct_change()
    nominal_returns = prices.pct_change()

    real_ret = nominal_returns.sub(inflation.values, axis=0)
    return real_ret
