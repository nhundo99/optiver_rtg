import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df_etf_orderbook = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data1/etf_orderbook.csv')
df_future_orderbook = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data1/future_orderbook.csv')
df_etf_trades = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data1/etf_trades.csv')
df_future_trades = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data1/future_trades.csv')
df_etf_orderbook['time'] = df_etf_orderbook['time']
df_future_orderbook['time'] = df_future_orderbook['time']
df_etf_trades['time'] = df_etf_trades['time']
df_future_trades['time'] = df_future_trades['time']


"""
compute the midprice of future
"""
df_future_orderbook['midprice'] = (df_future_orderbook['ask price 0'] + df_future_orderbook['bid price 0'])/2


"""
compute the difference in the bid ask volume in the orderbook
a positive value means we have more bid prices 'price should go up'
also had to correect the frist three rows, just used the value of the 4th one '-3000'
"""
df_future_orderbook['volume bid - ask total']= (df_future_orderbook['bid price 0']+df_future_orderbook['bid price 1']+df_future_orderbook['bid price 2']+df_future_orderbook['bid price 3']+df_future_orderbook['bid price 4']) -(df_future_orderbook['ask price 0']+df_future_orderbook['ask price 1']+df_future_orderbook['ask price 2']+df_future_orderbook['ask price 3']+df_future_orderbook['ask price 4'])
df_future_orderbook.at[0, 'volume bid - ask total'] = -3000
df_future_orderbook.at[1, 'volume bid - ask total'] = -3000
df_future_orderbook.at[2, 'volume bid - ask total'] = -3000

"""
we want to make a rolling average of the 'volume bid - ask total' since just the normal values are to choppy
"""
df_future_orderbook['rolling volume difference'] = df_future_orderbook['volume bid - ask total'].rolling(30).mean()


"""
we now want to compute order flow imbalance
resource: https://dm13450.github.io/2022/02/02/Order-Flow-Imbalance.html
"""
df_future_orderbook['I1'] = (df_future_orderbook['bid price 0'].ge(df_future_orderbook['bid price 0'].shift(1)))*df_future_orderbook['bid volume 0']
df_future_orderbook['I2'] = (df_future_orderbook['bid price 0'].le(df_future_orderbook['bid price 0'].shift(1)))*df_future_orderbook['bid volume 0'].shift(1)
df_future_orderbook['I3'] = (df_future_orderbook['ask price 0'].le(df_future_orderbook['ask price 0'].shift(1)))*df_future_orderbook['ask volume 0']
df_future_orderbook['I4'] = (df_future_orderbook['ask price 0'].ge(df_future_orderbook['ask price 0'].shift(1)))*df_future_orderbook['ask volume 0'].shift(1)

df_future_orderbook['e'] = df_future_orderbook['I1']-df_future_orderbook['I2']-df_future_orderbook['I3']+df_future_orderbook['I4']

df_future_orderbook['rolling oi'] = df_future_orderbook['e'].rolling(4).mean()
df_future_orderbook['long rolling oi'] = df_future_orderbook['rolling oi'].rolling(80).mean()


"""
now we want to check if the orderbook imbalance predicts the future prices
when we have a positive rolling oi we expect the next prices to be higher then the last prices
first we check if when rolling oi is positive then the next bid price of the future should be higher
if rolling oi is negative we want the next ask price to be lower than the current one
"""
df_future_orderbook['prediction'] = df_future_orderbook['rolling oi'].shift(1) > 0 * df_future_orderbook['midprice'].gt(df_future_orderbook['midprice'].shift(1))
df_future_orderbook['prediction'] += (df_future_orderbook['rolling oi'].shift(1) < 0 * df_future_orderbook['midprice'].lt(df_future_orderbook['midprice'].shift(1)))




print(df_future_orderbook['prediction'].value_counts())

# df_future_orderbook.plot(x='time',y='midprice', kind='line')
# df_future_orderbook.plot(x='time', y='rolling volume difference')

# ax1 = df_future_orderbook['rolling oi'].plot(color='blue', label='short rolling')
# df_future_orderbook.plot(x='time', y='long rolling oi',color='red', label='long rolling')
# h1, l1 = ax1.get_legend_handles_labels()

# plt.legend()

# plt.show()


# plt.savefig('80_second_rolling_oi.png', dpi=500)