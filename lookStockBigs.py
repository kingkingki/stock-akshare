import akshare as ak
import pandas as pd
import time
import sys
from datetime import datetime
import os
import config
from pushMessage import WxPusher
from config import stLabel 

# 启用未来行为
pd.set_option('future.no_silent_downcasting', True)

wx_pusher = WxPusher()
# 缓存字典，用于存储每个股票在每分钟的发送状态
cache = {}
    
def look_stock_details(symbols):

    output_folder = ''
    if symbols :
        outputtmp = datetime.now().strftime("%Y%m%d")
        if outputtmp != output_folder :
            output_folder = outputtmp
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        send_content = ''
        for symbol in symbols:
            output_file = os.path.join(output_folder, f'bigs_{symbol}.csv')
            # 尝试读取现有文件内容
            try:
                existing_data = pd.read_csv(output_file)
            except FileNotFoundError:
                existing_data = pd.DataFrame()

            try:
                big_buy_count = 0  # 记录当前分钟内的超大buyPlate数量
                threshold = stLabel['maxCount']  # 达到此阈值输出符号
                # 获取实时数据
                stock_intraday_em_df = ak.stock_intraday_em(symbol=symbol)

                # 替换和重命名列
                stock_intraday_em_df.replace(
                    {stLabel['buyPlate']: 1, stLabel['middlePlate']: 0, stLabel['sailPlate']: -1}, inplace=True
                )
                stock_intraday_em_df.rename(
                    columns={
                        stLabel['buyOrSail']: "1-1",
                        stLabel['hands']: "hands",
                        "时间": "Time",
                        stLabel['dealPrice']: "Pri",
                    },
                    inplace=True,
                )

                # 提取时间的分钟部分，格式为 HH:MM
                stock_intraday_em_df['Minute'] = stock_intraday_em_df['Time'].apply(lambda x: x[:5])

                # 获取当前最新的分钟数据（例如 "15:27"）
                # last_minute = stock_intraday_em_df['Minute'].max()
                # testlast_minute = "14:14"
                last_minute = "14:30"
                
                 # 判断缓存中是否已有该分钟内的记录
                if symbol in cache and cache[symbol] == last_minute:
                    continue  # 跳过发送，避免重复

                # 筛选出该分钟内的数据
                last_minute_data = stock_intraday_em_df[stock_intraday_em_df['Minute'] == last_minute]

                # 判断累计大buyPlate数
                big_buy_data = last_minute_data[
                    (last_minute_data["hands"] > stLabel['handsMax']) & (last_minute_data["1-1"] == 1)
                ]


                # 判断是否达到阈值
                if len(big_buy_data) >= threshold:
                    print(f"Symbol: {symbol} - 在{last_minute} 超过{stLabel['handsMax']} 的大buyPlate达到 {len(big_buy_data)} 次")
                    send_content += f"{symbol} 在{last_minute} 大buyPlate达到 {len(big_buy_data)} 次\n"

                # 更新已有数据
                if not big_buy_data.empty:
                    existing_data = pd.concat([existing_data, big_buy_data]).drop_duplicates()

                # 将当前股票和分钟记录到缓存
                cache[symbol] = last_minute

            except Exception as e:
                print(f"Failed to fetch data for {symbol}. Retrying in 10 seconds...")
                print(f"Error: {e}")

        if send_content:
            print(f"send_content: {send_content}")
            wx_pusher.send_message(send_content, summary='look_stock_bags')


# 定时任务V3
def call_print_stock_details_task(symbols = None):
    if symbols == None:
        symbols = config.default_symbols
    look_stock_details(symbols)
        
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        symbols = sys.argv[1:]
    else:
        print("No symbols provided, using default symbols.")
        symbols = config.default_symbols
    while True:
        call_print_stock_details_task(symbols)
        time.sleep(3)  # 每隔 2 秒调用一次 print_stock_bid_ask() 函数


# python lookStockBigs.py