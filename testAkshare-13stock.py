import akshare as ak

# 获取所有的股票代码
stockname = ak.stock_zh_a_spot_em()
df = stockname['代码']

for i in df:
    try:
        stock_history = ak.stock_zh_a_hist(symbol=i,period='daily',adjust='').iloc[:,0:6]

    # 列名
        stock_history.columns = [
            'date',
            'open',
            'close',
            'high',
            'low',
            'volume',

    ]
    # 对列进行重新排序设置成OHLC
        stock_history = stock_history[['date','open','high','low','close','volume']]

    # 设置以日期为索引
        stock_history.set_index('date',drop=True,inplace=True)

    # 保存成csv文件，这里可以设置自己的路径。

        stock_history.to_csv(f'./{i}.csv')
    except:
        continue