
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

# 符合局部匹配的股票代码列表
matched_stock_codes = ["600968"]  # 示例，你可以根据需求修改

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
    # 遍历股票数据
    contents = '';
    for index, row in stock_zh_a_spot_em_df.iterrows():
        if row['量比'] > 5:
            stock_detail = f"{row['代码']} , {row['名称']} , {row['最新价']} , {row['涨跌幅']}, {row['量比']}\n"
            print(stock_detail)
            iCount += 1
            f.write(stock_detail)
            contents += stock_detail
            
    sendMessage(contents)            
            
            
    # # 检查股票代码是否符合局部匹配条件
    # for stock_code in matched_stock_codes:
    #     if stock_code in row["代码"]:
    #         # 将符合条件的股票详情逐行输出并写入文件
    #         stock_detail = f"{row['代码']} - {row['名称']} - {row['最新价']} - {row['涨跌幅']}%\n"
    #         print(stock_detail)
    #         print(row.to_csv())
    #         f.write(row.to_csv())
    #         break  # 退出内部循环，避免重复写入
    

print("详情已保存到文件:", output_file, 'iCount= {}'.format(iCount))
