import akshare as ak
import pandas as pd
import time
import sys
from datetime import datetime
import os

def update_stock_details(output_folder, symbol):
    output_file = os.path.join(output_folder, f'stock_details_{symbol}.csv')
    # 尝试读取现有文件内容
    try:
        existing_data = pd.read_csv(output_file)
    except FileNotFoundError:
        existing_data = pd.DataFrame()
    
    while True:
        try :
            # 获取实时数据
            stock_intraday_em_df = ak.stock_intraday_em(symbol=symbol)
            
            # 替换‘买盘’和‘卖盘’为对应的数值
            stock_intraday_em_df.replace({'买盘': 1,'中性盘': 0, '卖盘': -1}, inplace=True)

            # 检查新数据是否与旧数据相同
            if not stock_intraday_em_df.equals(existing_data):
                # 检查新数据中超出1000手的行
                new_big_count_data = stock_intraday_em_df[stock_intraday_em_df['手数'] > 1000]

                # 过滤掉已经显示过的数据
                new_big_count_data = new_big_count_data[~new_big_count_data.index.isin(existing_data.index)]

                # 如果有超出1000手的行，输出到屏幕并记录到已有数据中
                if not new_big_count_data.empty:
                    print(new_big_count_data)
                    existing_data = pd.concat([existing_data, new_big_count_data])

                # 更新文件数据
                stock_intraday_em_df.to_csv(output_file, index=False, encoding="utf-8")
            else:
                print("数据未变化，不更新文件。")
            
            time.sleep(6)
        except:
            print(f"Failed to fetch data for {symbol}. Retrying in 5 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <symbol>")
        sys.exit(1)

    output_folder = datetime.now().strftime("%Y%m%d")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    symbol = sys.argv[1]
    update_stock_details(output_folder, symbol)
