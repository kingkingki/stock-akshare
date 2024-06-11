import akshare as ak
from pushMessage import WxPusher

def sendMessage(content=""):
    summary = "stock_new_low"
    wx_pusher = WxPusher()
    wx_pusher.send_message(content, summary=summary)
    
def find_and_save_new_low_stocks(output_file):
    # 查找创新低的股票
    new_low_stocks = ak.stock_rank_cxd_ths()
    
    # 过滤股票代码以30和8开头的股票
    filtered_stocks = new_low_stocks[new_low_stocks["股票代码"].str.startswith(("3"))]
    
    print(filtered_stocks)
    sendMessage(filtered_stocks.to_csv())   
    
    # 将结果保存到文件
    filtered_stocks.to_csv(output_file, index=False)

# 测试函数
output_file = "filtered_new_low_stocks.csv"  # 文件名
find_and_save_new_low_stocks(output_file)
