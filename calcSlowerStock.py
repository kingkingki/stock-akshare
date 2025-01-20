from datetime import datetime, time
import akshare as ak
import sys

import config
from pushMessage import WxPusher

wx_pusher = WxPusher()

# 计算当前时间的jy时长（单位：秒）
def calculate_trading_seconds(current_time):
    # 定义jy时段
    trading_periods = [
        (time(9, 15), time(9, 25)),
        (time(9, 30), time(11, 30)),
        (time(13, 0), time(15, 0)),
    ]

    # 将时间转换为秒
    def time_to_seconds(t):
        return t.hour * 3600 + t.minute * 60 + t.second

    # 当前时间的秒数
    current_seconds = time_to_seconds(current_time)
    total_seconds = 0

    for start, end in trading_periods:
        start_seconds = time_to_seconds(start)
        end_seconds = time_to_seconds(end)

        if current_seconds <= start_seconds:
            # 当前时间在此jy时段开始之前
            break
        elif current_seconds >= end_seconds:
            # 当前时间在此jy时段之后
            total_seconds += end_seconds - start_seconds
        else:
            # 当前时间在此jy时段内
            total_seconds += current_seconds - start_seconds
            break

    return total_seconds

# 获取gg实际jy次数
def get_actual_trading_count(stock_code):
    try:
        stock_df = ak.stock_intraday_em(symbol=stock_code)  # 使用 akshare 获取gg的jy数据
        return len(stock_df)  # 返回jy记录数（实际jy次数）
    except Exception as e:
        print(f"获取gg {stock_code} 数据时出错: {e}")
        return 0

# 主函数
def analyze_stocks(stock_list, lower):
    # 当前时间
    current_time = datetime.now().time()
    trading_seconds = calculate_trading_seconds(current_time)  # 获取当前jy秒数
    estimated_trades = trading_seconds // 3  # 每 3 秒一次jy，计算预估jy次数
    
    # t.hour * 3600 + t.minute * 60 + t.second
    content = f"cur: {current_time.hour}:{current_time.minute}:{current_time.second}: 预估Count: {estimated_trades}\n"
    print(content)

    stock_data = []
    
    # 遍历gg列表
    for stock_code in stock_list:
        actual_trades = get_actual_trading_count(stock_code)  # 获取实际jy次数
        if estimated_trades > 0:
            percentage = (actual_trades / estimated_trades) * 100  # 计算百分比
        else:
            percentage = 0


        # 将结果保存到列表
        if lower <= percentage <= 99:
            stock_data.append({
                "stock_code": stock_code,
                "actual_trades": actual_trades,
                "percentage": percentage
            })
            
        # 将结果保存到列表
        # stock_data.append({
        #     "stock_code": stock_code,
        #     "actual_trades": actual_trades,
        #     "percentage": percentage
        # })

    # 按百分比从小到大排序
    sorted_stock_data = sorted(stock_data, key=lambda x: x["percentage"], reverse=True)

    # 打印结果
    for stock in sorted_stock_data:
        status = "⚠️ 少于50%" if stock["percentage"] < 50 else "✅ ok"
        temp = f"Code: {stock['stock_code']}, Count: {stock['actual_trades']}, per: {stock['percentage']:.2f}% {status}\n"
        content += temp
    
    if content:
        wx_pusher.send_message(content, summary='频次统计')


# 获取所有以360开头的hh代码
def get_360_stocks(begin):
    try:
        stock_list = ak.stock_zh_a_spot_em()
        stock_codes = stock_list["代码"].tolist()
        return [code for code in stock_codes if code.startswith(begin)]
    except Exception as e:
        print(f"获取hh列表时出错: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        lower = float(sys.argv[1])
        print("sys:", lower)
    else:
        lower = 75
    

    # 示例gg列表
    stock_list = list(set(config.look_symbols + config.default_symbols))
    analyze_stocks(stock_list, lower)
    # stock_list = get_360_stocks()
    # print(len(stock_list))
    # # analyze_stocks(stock_list)


