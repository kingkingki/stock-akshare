import os
import akshare as ak
from akshare import stock_bid_ask_em
from datetime import datetime
import pandas as pd
from io import StringIO
import config

# 初始化上一次的信息为空字典
last_stock_info = {}

# 个stock
def print_stock_bid_ask(symbols, output_file):
    global last_stock_info  # 声明为全局变量
    
    # 根据股票代码分类文件
    output_folder = datetime.now().strftime("%Y%m%d")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for symbol in symbols:
        # 获取买卖盘信息
        stock_bid_ask_em_df = stock_bid_ask_em(symbol=symbol)
        
        # 仅保留第一行和第二行数据
        # transposed_df = stock_bid_ask_em_df.T
        relevant_data = stock_bid_ask_em_df
        
        # 处理索引，将 "sell_" 替换为 "s"，将 "buy_" 替换为 "b"
        # relevant_data.index = relevant_data.index
        
        # 转换为 CSV 格式的字符串
        csv_data = relevant_data.to_csv(index=False,header=False, lineterminator='\n')
        csv_data = csv_data.replace("sell_", "s").replace("_vol", "v").replace("buy_", "b").replace('----------------------------------------------------------------------------------------------------,','-,')
        
        # 检查信息是否和上一次相同
        if last_stock_info.get(symbol) == csv_data:
            continue
        else:
            # 打印买卖盘信息到控制台
            # 获取当前时间并格式化为字符串
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"代码,{symbol}", f"time,{timestamp}")

            # 读取 CSV 格式字符串到 pandas DataFrame
            df = pd.read_csv(StringIO(csv_data))

            # 输出 DataFrame 到屏幕并呈现为对齐的表格列
            print(df)
            # print(csv_data)
            

            
            # 写入买卖盘信息和时间戳到文件
            file_path = os.path.join(output_folder, f"{output_file[:-4]}{symbol}.txt")
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"time,{timestamp}\n")
                f.write(csv_data + "\n")
                
            # 更新上一次的信息
            last_stock_info[symbol] = csv_data

# 优化文件名
symbols = config.default_symbols  # 示例代码列表
output_file = "stock_buys.txt"  # 文件名
# print_stock_bid_ask(symbols, output_file)

import time

# todo 所有文件按照日期建立文件夹，所有stock文件记录在类似20240511目录中： 20240511/stock_info600990.txt

# 定时任务V3
def call_print_stock_bid_ask(symbols, output_file):
    while True:
        print_stock_bid_ask(symbols, output_file)
        time.sleep(2)  # 每隔 2 秒调用一次 print_stock_bid_ask() 函数
        
call_print_stock_bid_ask(symbols, output_file)