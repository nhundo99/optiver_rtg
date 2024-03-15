import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




# making the panda dataframes
# for data 3 we have one less row
df_etf1 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data1/etf_data1.csv')
df_etf2 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data2/etf_data2.csv')
df_etf3 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data3/etf_data3.csv')
df_etf4 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data4/etf_data4.csv')

df_future1 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data1/future_data1.csv')
df_future2 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data2/future_data2.csv')
df_future3 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data3/future_data3.csv')
df_future4 = pd.read_csv('/home/nick/Projects/optiver_rtg/py/pyready_trader_go/data/data4/future_data4.csv')

df_all_etf = [df_etf1, df_etf2, df_etf3, df_etf4]
df_all_future = [df_future1, df_future2, df_future3, df_future4]


# make the header correctly and make the first row again
#first for the etf
new_row = pd.DataFrame({'0.0': 0.0, '0.0.1': 0.0, '0.0.2': 0.0}, index=[0])
new_row_1 = pd.DataFrame({'1470.0': 1470.0, '1471.0': 1471.0, '1469.0': 1469.0}, index=[0])
new_row_2 = pd.DataFrame({'1483.0': 1483.0, '1484.0': 1484.0, '1482.0': 1482.0}, index=[0])
new_row_3 = pd.DataFrame({'1134.0': 1134.0, '1135.0': 1135.0, '1133.0': 1133.0}, index=[0])
new_row_4 = pd.DataFrame({'1248.5': 1248.5, '1249.0': 1249.0, '1247.0': 1247.0}, index=[0])

df_etf1 = pd.concat([new_row,df_etf1.loc[:]]).reset_index(drop=True)
df_etf2 = pd.concat([new_row,df_etf2.loc[:]]).reset_index(drop=True)
df_etf3 = pd.concat([new_row,df_etf3.loc[:]]).reset_index(drop=True)
df_etf4 = pd.concat([new_row,df_etf4.loc[:]]).reset_index(drop=True)

df_etf1 = df_etf1.rename(columns={'0.0': 'Midprice', '0.0.1': 'Ask price', '0.0.2': 'Bid price'})
df_etf2 = df_etf2.rename(columns={'0.0': 'Midprice', '0.0.1': 'Ask price', '0.0.2': 'Bid price'})
df_etf3 = df_etf3.rename(columns={'0.0': 'Midprice', '0.0.1': 'Ask price', '0.0.2': 'Bid price'})
df_etf4 = df_etf4.rename(columns={'0.0': 'Midprice', '0.0.1': 'Ask price', '0.0.2': 'Bid price'})

# now for the future
df_future1 = pd.concat([new_row_1,df_future1.loc[:]]).reset_index(drop=True)
df_future2 = pd.concat([new_row_2,df_future2.loc[:]]).reset_index(drop=True)
df_future3 = pd.concat([new_row_3,df_future3.loc[:]]).reset_index(drop=True)
df_future4 = pd.concat([new_row_4,df_future4.loc[:]]).reset_index(drop=True)

df_future1 = df_future1.rename(columns={'1470.0': 'Midprice', '1471.0': 'Ask price', '1469.0': 'Bid price'})
df_future2 = df_future2.rename(columns={'1483.0': 'Midprice', '1484.0': 'Ask price', '1482.0': 'Bid price'})
df_future3 = df_future3.rename(columns={'1134.0': 'Midprice', '1135.0': 'Ask price', '1133.0': 'Bid price'})
df_future4 = df_future4.rename(columns={'1248.5': 'Midprice', '1249.0': 'Ask price', '1247.0': 'Bid price'})

df_etf1 = df_etf1.drop([0,1])
df_etf2 = df_etf2.drop([0,1])
df_etf3 = df_etf3.drop([0,1])
df_etf4 = df_etf4.drop([0,1])

df_future1 = df_future1.drop([0,1])
df_future2 = df_future2.drop([0,1])
df_future3 = df_future3.drop([0,1])
df_future4 = df_future4.drop([0,1])

df_diff_etfa_futureb_1 = df_etf1['Ask price']-df_future1['Bid price']
df_diff_etfb_futurea_1 = df_etf1['Bid price']-df_future1['Ask price']

print(np.mean(df_diff_etfa_futureb_1))
print(np.mean(df_diff_etfb_futurea_1))

print(df_future1)

# plots
# difference etf best ask and future best bid
plt.plot(df_etf1['Ask price']/df_future1['Bid price'])
plt.plot(df_etf1['Bid price']/df_future1['Ask price'], color='g')
plt.show()



