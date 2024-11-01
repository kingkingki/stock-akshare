import akshare as ak
import os
from datetime import datetime
from pushMessage import WxPusher

def sendMessage(content=""):
    summary = "stock_details"
    wx_pusher = WxPusher()
    wx_pusher.send_message(content, summary=summary)

# 获取实时 A 股股票数据
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
# stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em() // stock_zh_a_spot_em_df 包含 stock_sh_a_spot_em_df

# 获取当前时间
now = datetime.now()
date_str = now.strftime("%Y%m%d")
time_str = now.strftime("%H%M%S")
date_time_str = now.strftime("%Y年%m月%d日%H:%M:%S")

# 创建对应日期的文件夹
output_folder = date_str
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 保存到文件的路径，文件名包含时间戳
output_file = os.path.join(output_folder, f"stock_details_{time_str}.txt")

iCount = 1
# 打开文件准备写入数据
with open(output_file, "w", encoding="utf-8") as f:
    # 遍历股票数据并筛选股票代码
    contents = ''
    
    # 定义符合条件的股票代码开头
    valid_prefixes = ('3', '6', '0')

    # 最高接近最新价的容差百分比（例如，最高与最新价相差不超过2%）
    tolerance_percentage = 0.02

    def process_stock_data(stock_df):
        global iCount, contents
        for index, row in stock_df.iterrows():
            stock_code = str(row['代码'])  # 确保股票代码为字符串格式
            latest_price = row['最新价']
            opening_price = row['今开']
            lowest_price = row['最低']
            highest_price = row['最高']
            quantity_ratio = row['量比']
            buffer = row['涨跌幅']
            total_value = row['总市值']
            
            # 仅保留以 '3', '6', '0' 开头的股票代码，并满足策略条件
            if (
                stock_code.startswith(valid_prefixes) 
                and not stock_code.startswith('688') 
                and quantity_ratio >= 1 # 量比大于5
                and latest_price > opening_price  # 最新价大于今开
                and opening_price > lowest_price  # 今开大于最低
                and latest_price < 13 and latest_price > 2.01
                # and latest_price > 13
                and buffer < 1
                and total_value < 30000000000
                and abs(highest_price - latest_price) / highest_price < tolerance_percentage  # 最高接近最新价
            ):
                stock_detail = f"{row['代码']} , {row['名称']} , {row['最新价']} , {row['涨跌幅']}, {row['量比']}, {row['今开']}, {row['最低']}, {row['最高']}\n"
                print(stock_detail)
                iCount += 1
                f.write(stock_detail)
                contents += stock_detail

    # 处理两个股票数据集
    process_stock_data(stock_zh_a_spot_em_df)
    # process_stock_data(stock_sh_a_spot_em_df)

    # 发送消息
    sendMessage(contents)

print(f"详情已保存到文件: {output_file}, 总计记录数: {iCount}")
