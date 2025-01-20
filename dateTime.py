from datetime import datetime, time, timedelta

def is_trading_time():
    """
    判断当前时间是否属于交易时间。
    返回:
        True: 当前属于交易时间
        False: 当前不属于交易时间
    """
    # 获取当前时间
    now = datetime.now()
    current_time = now.time()

    # 定义交易时间段
    trading_start = time(9, 14)       # 早上 9:13 开始
    trading_mid_end = time(11, 33)   # 早上 11:30 结束
    trading_mid_start = time(13, 0)  # 下午 13:00 开始
    trading_end = time(15, 5)        # 下午 15:00 结束

    # 判断是否是周末（周六、周日）
    if now.weekday() in [5, 6]:  # 0-周一, 5-周六, 6-周日
        return False

    # 定义 2025 年法定节假日
    holidays_2025 = [
        "2025-01-01",  # 元旦
        "2025-02-04", "2025-02-05", "2025-02-06", "2025-02-07", "2025-02-08", "2025-02-09", "2025-02-10",  # 春节
        "2025-04-05",  # 清明节
        "2025-05-01",  # 劳动节
        "2025-06-01",  # 端午节
        "2025-09-15",  # 中秋节
        "2025-10-01", "2025-10-02", "2025-10-03", "2025-10-04", "2025-10-05", "2025-10-06", "2025-10-07"  # 国庆节
    ]
    # 转换为日期对象列表
    holidays_2025 = [datetime.strptime(date, "%Y-%m-%d").date() for date in holidays_2025]

    # 判断是否是节假日
    if now.date() in holidays_2025:
        return False

    # 判断是否处于交易时间范围
    if trading_start <= current_time <= trading_mid_end or trading_mid_start <= current_time <= trading_end:
        return True
    return False
