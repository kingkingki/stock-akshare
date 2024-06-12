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


# new 停复牌 stock
import akshare as ak

stock_tfp_em_df = ak.stock_tfp_em(date="20240612")
print(stock_tfp_em_df)
output_file = 'stock_tfp_em.csv'
stock_tfp_em_df.to_csv(output_file, index=False, encoding="utf-8")