import akshare as ak
import pandas as pd
from pushMessage import WxPusher
import datetime

def sendMessage(content=""):
    summary = "stock_new_low"
    wx_pusher = WxPusher()
    wx_pusher.send_message(content, summary=summary)
    
def find_and_save_new_low_stocks(output_file):
    # 获取今天的日期
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # 查找创新低的股票
    new_low_stocks = ak.stock_rank_cxd_ths()
    
    # 过滤股票代码以3开头的股票
    filtered_stocks = new_low_stocks[new_low_stocks["股票代码"].str.startswith("3")]
    
    # 初始化结果列表
    result_stocks = []

    for index, row in filtered_stocks.iterrows():
        stock_code = row["股票代码"]
        
        # 获取股票日K线数据
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=today, end_date=today, adjust="qfq")
        
        if not stock_zh_a_hist_df.empty:
            open_price = stock_zh_a_hist_df.at[0, "开盘"]
            current_price = stock_zh_a_hist_df.at[0, "收盘"]
            low_price = stock_zh_a_hist_df.at[0, "最低"]
            
            # 判断开盘价和当前价接近（可以定义一个误差范围，如0.5%）
            if abs(current_price - open_price) / open_price <= 0.005:
                # 判断最低价降幅在2%-5%之间
                if 0.02 <= (open_price - low_price) / open_price <= 0.05:
                    result_stocks.append(row)
    
    # 转换为DataFrame
    result_stocks_df = pd.DataFrame(result_stocks)
    
    # 打印并发送消息
    print(result_stocks_df)
    sendMessage(result_stocks_df.to_csv(index=False))   
    
    # 将结果保存到文件
    result_stocks_df.to_csv(output_file, index=False)

# 测试函数
output_file = "filtered_newlow_stocks.csv"  # 文件名
find_and_save_new_low_stocks(output_file)
