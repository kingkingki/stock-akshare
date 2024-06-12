# import akshare as ak

# stock_institute_hold_df = ak.stock_institute_hold(symbol="20201")
# print(stock_institute_hold_df)
# output_file = 'stock_institute_hold.csv'
# stock_institute_hold_df.to_csv(output_file, index=False, encoding="utf-8")


# import akshare as ak

# stock_institute_hold_detail_df = ak.stock_institute_hold_detail(stock="002188", quarter="20201")
# print(stock_institute_hold_detail_df)
# output_file = 'stock_institute_hold_detail1.csv'
# stock_institute_hold_detail_df.to_csv(output_file, index=False, encoding="utf-8")


import akshare as ak
import os
import sys
from datetime import datetime
import config  # 导入配置文件

def fetch_and_save_stock_institute_hold_details(symbols, output_folder):
    for symbol in symbols:
        try:
            # 获取机构持股详情
            stock_institute_hold_detail_df = ak.stock_institute_hold_detail(stock=symbol, quarter="20201")
            print(f"Fetched data for stock: {symbol}")
            print(stock_institute_hold_detail_df)

            # 保存数据到CSV文件
            output_file = os.path.join(output_folder, f'stock_institute_hold_detail_{symbol}.csv')
            stock_institute_hold_detail_df.to_csv(output_file, index=False, encoding="utf-8")
        except Exception as e:
            print(f"Failed to fetch data for stock: {symbol}")
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No symbols provided, using default symbols.")
        symbols = config.default_symbols
    else:
        symbols = sys.argv[1:]

    output_folder = datetime.now().strftime("%Y%m%d")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fetch_and_save_stock_institute_hold_details(symbols, output_folder)










# import akshare as ak

# output_file = 'stock_zh_a_new_em.csv'
# stock_zh_a_new_em_df = ak.stock_zh_a_new_em()
# print(stock_zh_a_new_em_df)
# stock_zh_a_new_em_df.to_csv(output_file, index=False, encoding="utf-8")

# import akshare as ak

# output_file = 'nicorn_company.csv'
# nicorn_company_df = ak.nicorn_company()
# print(nicorn_company_df)
# nicorn_company_df.to_csv(output_file, index=False, encoding="utf-8")


# new stock
# import akshare as ak

# stock_tfp_em_df = ak.stock_tfp_em(date="20240521")
# print(stock_tfp_em_df)
# output_file = 'stock_tfp_em.csv'
# stock_tfp_em_df.to_csv(output_file, index=False, encoding="utf-8")