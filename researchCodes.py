import akshare as ak
import os
from datetime import datetime
import pandas as pd

# 获取实时 A 股股票数据
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
# stock_zh_a_spot_em_df = stock_zh_a_spot_em_tmp[stock_zh_a_spot_em_tmp["股票代码"].str.startswith(("3"))]

# 获取当前时间
now = datetime.now()
date_str = now.strftime("%Y%m%d")
time_str = now.strftime("%H%M%S")
date_time_str = now.strftime("%Y年%m月%d日%H:%M:%S")

# 初始化记录买盘和卖盘股票代码的列表
red = []
green = []

# 遍历股票数据
for index, row in stock_zh_a_spot_em_df.iterrows():
    if row['代码'].startswith(("3")) == False:
        continue
    # 检查 sell_2_vol 和 buy_2_vol 的情况
    sell_2_vol = row.get('sell_2_vol', 0)
    buy_2_vol = row.get('buy_2_vol', 0)

    if pd.isna(sell_2_vol) or sell_2_vol == 0:
        red.append(row['代码'])
    if pd.isna(buy_2_vol) or buy_2_vol == 0:
        green.append(row['代码'])

# 输出结果
# print(f"纯红色线股票代码: {red}")
print(f"纯绿色线股票代码: {green}")

# 保存结果到文件
output_folder = date_str
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

red_output_file = os.path.join(output_folder, f"red_stocks_{time_str}.txt")
green_output_file = os.path.join(output_folder, f"green_stocks_{time_str}.txt")

with open(red_output_file, "w", encoding="utf-8") as f:
    for code in red:
        f.write(f"{code}\n")

with open(green_output_file, "w", encoding="utf-8") as f:
    for code in green:
        f.write(f"{code}\n")

print(f"纯红色线股票代码已保存到: {red_output_file}")
print(f"纯绿色线股票代码已保存到: {green_output_file}")
