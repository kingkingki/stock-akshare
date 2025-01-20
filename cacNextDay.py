import time
import sys
from datetime import datetime, time
import akshare as ak
from pushMessage import WxPusher

wx_pusher = WxPusher()

# 筛选符合时间段的数据
def filter_time_period(data):
    try:
        # 保留 9:23 - 9:35 时间段的数据
        data["时间"] = data["时间"].apply(lambda t: datetime.strptime(t, "%H:%M:%S").time())
        return data[(data["时间"] >= time(9, 23)) & (data["时间"] <= time(9, 35))]
    except Exception as e:
        print(f"筛选时间段时出错: {e}")
        return data

# 计算活跃度（单位：hands）
def calculate_trading_activity(stock_code):
    try:
        intraday_data = ak.stock_zh_a_tick_tx(symbol=stock_code)
        if not intraday_data.empty:
            filtered_data = filter_time_period(intraday_data)
            return len(filtered_data)  # 返回交易笔数
    except Exception as e:
        print(f"获取gg {stock_code} 的交易活动数据时出错: {e}")
        return 0

# 推送消息
def push_stock_alert(stock_code, latest_amount, volume, activity, percentage):
    message = (
        f"gg代码: {stock_code}\n"
        f"cash: {latest_amount}W\n"
        f"交易量: {volume}\n"
        f"活跃度: {activity}hands\n"
        f"活跃度占比: {percentage:.2f}%"
    )
    print(message)
    wx_pusher.send_message(message, summary="警报next")

# 获取最新的gg交易数据
def get_latest_stock_data(stock_code):
    try:
        intraday_data = ak.stock_zh_a_tick_tx(symbol=stock_code)
        if not intraday_data.empty:
            filtered_data = filter_time_period(intraday_data)
            if not filtered_data.empty:
                # 最新一条数据
                latest_trade = filtered_data.iloc[-1]
                latest_amount = latest_trade["成交额"]  # 单位: 万元
                volume = latest_trade["成交量"]
                return latest_amount, volume
    except Exception as e:
        print(f"获取gg {stock_code} 的最新数据时出错: {e}")
    return None, None

# 主逻辑
def monitor_stocks(stock_list, lower_bound):
    print("开始监控gg交易...")
    total_checks = 0

    for stock_code in stock_list:
        latest_amount, volume = get_latest_stock_data(stock_code)
        if latest_amount is not None:
            activity = calculate_trading_activity(stock_code)
            percentage = (activity / (total_checks + 1)) * 100 if total_checks > 0 else 100

            # 判断条件：交易金额超过 100 万，且活跃度占比符合阈值
            if latest_amount >= 100 and lower_bound <= percentage <= 99:
                push_stock_alert(stock_code, latest_amount, volume, activity, percentage)

        total_checks += 1
        time.sleep(3)  # 每 3 秒检查一次

    print("监控结束。")

# 获取gg列表
def get_stock_list(prefix):
    try:
        stock_list = ak.stock_zh_a_spot_em()
        return [code for code in stock_list["代码"].tolist() if code.startswith(prefix)]
    except Exception as e:
        print(f"获取gg列表时出错: {e}")
        return []

if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) >= 3:
        stock_prefix = sys.argv[1]
        lower_bound = float(sys.argv[2])
    else:
        print("用法: python script.py <gg代码前缀> <活跃度下限>")
        sys.exit(1)

    # 获取指定前缀的gg列表
    stock_list = get_stock_list(stock_prefix)
    if not stock_list:
        print(f"未找到以 {stock_prefix} 开头的gg代码。")
        sys.exit(1)

    # 开始监控
    monitor_stocks(stock_list, lower_bound)
