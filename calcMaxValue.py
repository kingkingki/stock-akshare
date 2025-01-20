from datetime import datetime, time
import akshare as ak
import sys

import config
from pushMessage import WxPusher

wx_pusher = WxPusher()

# 计算当前时间的yy时长（单位：秒）
def calculate_trading_seconds(current_time):
    trading_periods = [
        (time(9, 15), time(9, 25)),
        (time(9, 30), time(11, 30)),
        (time(13, 0), time(15, 0)),
    ]

    def time_to_seconds(t):
        return t.hour * 3600 + t.minute * 60 + t.second

    current_seconds = time_to_seconds(current_time)
    total_seconds = 0

    for start, end in trading_periods:
        start_seconds = time_to_seconds(start)
        end_seconds = time_to_seconds(end)

        if current_seconds <= start_seconds:
            break
        elif current_seconds >= end_seconds:
            total_seconds += end_seconds - start_seconds
        else:
            total_seconds += current_seconds - start_seconds
            break

    return total_seconds

# 获取单个hh的日内最值及当前价
def get_stock_prices(stock_code):
    try:
        today = datetime.now().strftime("%Y%m%d")
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=today, end_date=today, adjust="qfq")
        
        if not stock_zh_a_hist_df.empty:
            turnover = stock_zh_a_hist_df.at[0, "换手率"]  # 换手率（%）
            amount = stock_zh_a_hist_df.at[0, "成交额"]  # 成交额（单位：万元）

            if turnover > 0:
                # 计算市值（单位：亿元）
                market_cap = (amount / 100000000) / (turnover / 100)

                # 过滤市值在 10 亿到 150 亿之间的股票
                if 10 <= market_cap <= 180:
                    open_price = stock_zh_a_hist_df.at[0, "开盘"]
                    current_price = stock_zh_a_hist_df.at[0, "收盘"]
                    low_price = stock_zh_a_hist_df.at[0, "最低"]
                    high_price = stock_zh_a_hist_df.at[0, "最高"]
                    return open_price, current_price, low_price, high_price
    except Exception as e:
        print(f"获取hh {stock_code} 的价格数据时出错: {e}")
    return None, None, None, None

# 分析hh
def analyze_stocks(stock_list, lower):
    current_time = datetime.now().time()
    trading_seconds = calculate_trading_seconds(current_time)
    estimated_trades = trading_seconds // 3

    content = f"当前时间: {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}, 预估yy次数: {estimated_trades}\n"
    print(content)

    stock_data = []
    filtered_stocks = []
    buffer_stocks = []

    for stock_code in stock_list:
        # 获取日内最值
        open_price, current_price, low_price, high_price = get_stock_prices(stock_code)
        if open_price is None or current_price is None:
            continue

        buffer_stocks.append(stock_code)
        
        # 判断是否符合策略
        if current_price > low_price * 1.04 and current_price > open_price and \
           high_price * 0.80 <= current_price <= high_price:
            filtered_stocks.append(stock_code)
            print(f"hh {stock_code} ")
        else :
            continue

        # 获取实际yy次数
        actual_trades = get_actual_trading_count(stock_code)
        if estimated_trades > 0:
            percentage = (actual_trades / estimated_trades) * 100
        else:
            percentage = 0

        if lower <= percentage <= 99:
            stock_data.append({
                "stock_code": stock_code,
                "actual_trades": actual_trades,
                "percentage": percentage
            })

    # 按百分比从小到大排序
    sorted_stock_data = sorted(stock_data, key=lambda x: x["percentage"])

    # 打印结果
    for stock in sorted_stock_data:
        status = "⚠️ 少于50%" if stock["percentage"] < 50 else "✅ ok"
        temp = f"Co: {stock['stock_code']}, Cn: {stock['actual_trades']}, Pc: {stock['percentage']:.2f}% {status}\n"
        print(temp)
        content += temp

    wx_pusher.send_message(content, summary='接近最大值')

    # 打印符合策略的hh
    # print("hh: ", filtered_stocks)
    return filtered_stocks

# 获取所有以360开头的hh代码
def get_360_stocks(begin):
    try:
        stock_list = ak.stock_zh_a_spot_em()
        stock_codes = stock_list["代码"].tolist()
        return [code for code in stock_codes if code.startswith(begin)]
    except Exception as e:
        print(f"获取hh列表时出错: {e}")
        return []

# 获取实际yy次数
def get_actual_trading_count(stock_code):
    try:
        stock_df = ak.stock_intraday_em(symbol=stock_code)
        return len(stock_df)
    except Exception as e:
        print(f"获取hh {stock_code} 的数据时出错: {e}")
        return 0

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        lower = float(sys.argv[1])
    else:
        lower = 70

    # 示例hh列表（替换为从配置或 API 获取的hh列表）
    # stock_list = get_360_stocks()
    stock_list = list(set(config.look_symbols + config.default_symbols))

    # 分析hh
    result = analyze_stocks(stock_list, lower)
    # print("最终符合条件的hh列表: ", result)
