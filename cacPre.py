import pandas as pd
from datetime import datetime, timedelta
import sys
import akshare as ak
import config
import stock_buffer as stb
import os
from config import stLabel 
from pushMessage import WxPusher
import time
from operator import itemgetter
from dateTime import is_trading_time
from operator import itemgetter

pd.set_option('future.no_silent_downcasting', True)
wx_pusher = WxPusher()

beforeCount = ''
beforeCount_async = ''
mustOnce= True
g_topSymbols= []
g_rateSymbols= []
g_lowerFileSymbols= []
g_curDayTime= ''
g_rateMax = 1.5

# 返回数据结构
def calculate_summary(symbol, df, start_time: str, end_time: str, showAll=False):
    global g_lowerFileSymbols
    global g_rateMax # 调整概率
    
    # 转换时间为标准格式
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')
    start_time = pd.to_datetime(start_time, format='%H:%M:%S')
    end_time = pd.to_datetime(end_time, format='%H:%M:%S')

    # 筛选时间区间，精确到时分秒
    df_filtered = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)].copy()

    # 对连续的 '1-1' 值分组
    df_filtered['shifted'] = df_filtered['1-1'].shift()
    df_filtered['group'] = (df_filtered['1-1'] != df_filtered['shifted']).cumsum()

    # 按组统计 hands 的总和并除以 1000
    grouped = df_filtered.groupby(['group', '1-1'])['hands'].sum().reset_index()
    grouped['hands_k'] = grouped['hands'] // 1000  # 转换为 k 值

    # 按 '1-1' 分类汇总每组的 hands_k
    summary = grouped.groupby('1-1')['hands_k'].sum()

    # 格式化输出
    result = ",".join([f"{'+' if key > 0 else ''}{key * value if key < 0 else value}k" for key, value in summary.items()])

    # 判断 big 的条件
    count_1 = summary.get(1, 0)  # 显式按标签访问
    count_minus_1 = summary.get(-1, 0)  # 显式按标签访问
    if showAll or ((count_1 >= 2) and (count_minus_1 == 0 or (count_minus_1 > 0 and count_1 > count_minus_1 * 1.7))):
        if count_minus_1 == 0 and count_1 > 0:
            rate = round(count_1 * 3 , 2)
        elif count_minus_1 == 0 and count_1 == 0:
            rate = 1
        else:
            rate = round(count_1 / count_minus_1, 2)
        status = "⚠️" if rate < 2 else "✅"
        big = {"symbol": symbol, "result": result, "rate": rate, "status": status, "count_1": count_1}
        return big
    else: 
        if symbol not in g_lowerFileSymbols:
            if count_minus_1 > 1 and count_1 >= 0 :
                rate = round(count_1 / count_minus_1, 2)
                if rate < g_rateMax :
                    g_lowerFileSymbols.append(symbol)

    return None


# 分组求和除以1000，而不是所有加起来求和除以1000
def calculate_hands_summary2(symbol, df, start_time: str, end_time: str, showAll=False):
    # 转换时间为标准格式
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')
    start_time = datetime.strptime(start_time, '%H:%M:%S')
    end_time = datetime.strptime(end_time, '%H:%M:%S')

    # 筛选时间区间
    df_filtered = df[(df['Time'].dt.time >= start_time.time()) & (df['Time'].dt.time <= end_time.time())].copy()

    # 对连续的 '1-1' 值分组
    df_filtered['shifted'] = df_filtered['1-1'].shift()
    df_filtered['group'] = (df_filtered['1-1'] != df_filtered['shifted']).cumsum()

    # 按组统计 hands 的总和并除以 1000
    grouped = df_filtered.groupby(['group', '1-1'])['hands'].sum().reset_index()
    grouped['hands_k'] = grouped['hands'] // 1000  # 转换为 k 值

    # 按 '1-1' 分类汇总每组的 hands_k
    summary = grouped.groupby('1-1')['hands_k'].sum()

    # 格式化输出
    result = " "
    result += ",".join([f"{'+' if key > 0 else ''}{key * value if key < 0 else value}k" for key, value in summary.items()])
 
    # 判断 big 的条件
    big = None
    gKey = None
    count_1 = summary.get(1, 0)
    count_minus_1 = summary.get(-1, 0)
    if showAll or ((count_1 > 5) and (count_minus_1 == 0 or (count_minus_1 > 0 and count_1 > count_minus_1 * 1.4))):
        if count_minus_1 == 0 and count_1 > 0:
            rate = 3
        elif count_minus_1 == 0 and count_1 == 0 :
            rate = 1
        else:
            rate = round(count_1 / count_minus_1, 2)
        status = "⚠️" if rate < 1.4 else "✅"

        big = f"{symbol} {result} r={rate} {status}"
        gKey = symbol

    return result.strip(), big, gKey


####
# data = {
#     "Time": ["09:25:00", "09:26:00", "09:27:00", "09:28:00", "09:29:00", "09:30:00"],
#     "1-1": [1, 1, -1, -1, 1, 1],
#     "hands": [500, 600, 300, 400, 1200, 1000],
# }
# df = pd.DataFrame(data)
# symbol = "ABC"
# start_time = "09:25"
# end_time = "09:30"
# result, big, gKey = calculate_hands_summary2(symbol, df, start_time, end_time)
# print(result)  # 输出: "1C:3k , -1C:0k"
# print(big)     # 输出: "ABC 1C:3k , -1C:0k"
# print(gKey)    # 输出: "ABC"


# ###

def save_stock_details(symbols, begin):
    output_folder = ''
    if symbols :
        outputtmp = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%H_%M_%S")
        if outputtmp != output_folder :
            output_folder = outputtmp
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        output_file = os.path.join(output_folder, f'save_stock{begin}.csv')
        
        # 更新文件数据
        # 将字符串数组写入文件，每行一个字符串
        with open(output_file, "a", encoding="utf-8") as file:
            file.write(f'{timestamp}: caclPre :' + str(symbols) + '\n')
        
def save_stock_prev(content, begin):
    output_folder = ''
    if content :
        outputtmp = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%H_%M_%S")
        if outputtmp != output_folder :
            output_folder = outputtmp
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        output_file = os.path.join(output_folder, f'cacpre{begin}_{outputtmp}.csv')
        
        # 更新文件数据
        # 将字符串数组写入文件，每行一个字符串
        with open(output_file, "a", encoding="utf-8") as file:
            file.write(f'{timestamp}: ' + str(content) + '\n')    

import asyncio

async def calculate_summary_async_detail(symbols, df, startT, endT, showAll=False, desType='全天'):
    global beforeCount_async  # 声明在函数内使用全局变量

    countMax = 5
    while symbols and countMax > 0:
        countMax -= 1
        
        current_time = datetime.now()
        curT = current_time.strftime('%H:%M:%S')
        print(calculate_summary_async_detail,len(symbols))
        showAll = True if len(symbols) < 40 else False
        filtered_stocks = []
        content = ""
        
        contentTime = startT + "~" + curT + "\n"

        for symbol in symbols:
            try:

                # 获取实时数据
                stock_intraday_em_df = ak.stock_intraday_em(symbol=symbol)

                # 替换对应的数值
                stock_intraday_em_df.replace(
                    {
                        stLabel['buyPlate']: 1,
                        stLabel['middlePlate']: 0,
                        stLabel['sailPlate']: -1,
                    },
                    inplace=True,
                )
                stock_intraday_em_df.rename(
                    columns={
                        stLabel['buyOrSail']: '1-1',
                        stLabel['hands']: 'hands',
                        '时间': 'Time',
                        stLabel['dealPrice']: 'Pri',
                    },
                    inplace=True,
                )

                # 调用缓存数据进行排序
                big_result = calculate_summary(symbol, stock_intraday_em_df, startT, endT, showAll)
                if big_result:
                    print(big_result)
                    top_results.append(big_result)
                
            except Exception as e:
                print(f"Failed to fetch data for {symbol}. Retrying in 10 seconds...")
        
        try:
            save_stock_details(filtered_stocks, 3)
        except Exception as e:
            print(f"{e}")

        # 汇报内容
        for result in top_results:
            content += f"{result['symbol']} {result['result']} r:{result['rate']} {result['status']}\n"
                
        # 推送消息
        if content and content != beforeCount_async:
            summary=begin + "Cac统计"+ "_" + cateLabel + "_" + desType + "_"+ curT + "\n"
            wx_pusher.send_message(summary + contentTime + content, summary=summary)
            save_stock_prev(summary + contentTime + content, begin)
            beforeCount_async= content;
            
        time.sleep(3)

    
# 定义异步函数
async def calculate_summary_async(symbol, df, start_time, end_time, showAll=False, desType='全天'):
     # 在事件循环中创建任务，但不阻塞主线程
    loop = asyncio.get_event_loop()
    asyncio.create_task(calculate_summary_async_detail(symbol, df, start_time, end_time, showAll, desType))
    print('asyncio.create_task end ')

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
                    buff_price = stock_zh_a_hist_df.at[0, "涨跌幅"]
                    return  {
                    "stock_code": stock_code,
                    "open_price": open_price,
                    "current_price": current_price,
                    "low_price": low_price,
                    "high_price": high_price,
                    "buff_price": buff_price,
                    "market_cap": round(market_cap, 2)  # 保留两位小数
                }
    except Exception as e:
        print(f"获取hh {stock_code} 的价格数据时出错: {e}")
    return None

def update_stock_details(symbols, type = 1, begin = 3, listCate = 0, hasFilter = False):
    global beforeCount  # 声明在函数内使用全局变量
    global g_lowerFileSymbols # 过滤不必要的类型
    global g_rateMax 
    
    cateLabel = '车'
    
    # 示例hh列表（替换为从配置或 API 获取的hh列表）
    if listCate == 0 :
        cateLabel = '车'
    elif listCate == 1 :
        cateLabel = '全集'
        useFilter = True
    elif listCate == 2 :
        cateLabel = '精简'
        useFilter = True
    elif listCate == 3 :
        cateLabel = '监听'
    else :
        cateLabel = '默认'
    
    asyncRun = type == 3 and begin == 3 and cateLabel == '精简'
    agSymbols = []
    useFilter = True if len(symbols) >= 30 else False
    
    desType = '全天'
    current_time = datetime.now()
    curT = current_time.strftime('%H:%M:%S')
    
    if symbols:
        print(len(symbols))
        showAll = True if len(symbols) < 30 else False
        filtered_stocks = []
        content = ""
        if type == 0 :
            # 早上
            startT = "09:16:00"
            endT = "09:31:30"
            desType = '早'

        elif type == 1 :
            # 早上
            startT = "09:16:00"
            endT = "09:45:01"
            desType = '前15分'
            
        elif type == 3 :
            # 早上
            startT = (current_time - timedelta(minutes=3)).strftime('%H:%M:%S')
            endT = curT
            
            print(startT, endT)
            desType = '3分钟内'
            
        else :
            # 下午
            startT = "09:16:01"
            endT = "15:00:01"
        contentTime = startT + "~" + curT + "\n"
        
        # 假设 symbols_list 是待处理的gg数据集合，每个元素包含 symbol 和其对应的 DataFrame
        top_results = []
        tmp_em_df = {}

                    
        for symbol in symbols:
            try:
                if hasFilter and useFilter and symbol in g_lowerFileSymbols:
                    continue
                
                # 获取实时数据
                stock_intraday_em_df = ak.stock_intraday_em(symbol=symbol)

                # 替换对应的数值
                stock_intraday_em_df.replace(
                    {
                        stLabel['buyPlate']: 1,
                        stLabel['middlePlate']: 0,
                        stLabel['sailPlate']: -1,
                    },
                    inplace=True,
                )
                stock_intraday_em_df.rename(
                    columns={
                        stLabel['buyOrSail']: '1-1',
                        stLabel['hands']: 'hands',
                        '时间': 'Time',
                        stLabel['dealPrice']: 'Pri',
                    },
                    inplace=True,
                )
                
               
                # 调用缓存数据进行排序
                big_result = calculate_summary(symbol, stock_intraday_em_df, startT, endT, showAll)
                if big_result:
                    # print(big_result)
                    top_results.append(big_result)
                    tmp_em_df[symbol] = stock_intraday_em_df
                
            except Exception as e:
                print(f"Failed to fetch data for {symbol}. Retrying in 10 seconds...")
        
        try:
            save_stock_details(filtered_stocks, 3)
        except Exception as e:
            print(f"{e}")

        # 根据 count_1 进行降序排序
        sorted_results = sorted(top_results, key=itemgetter("count_1"), reverse=True)

        # 取前 20
        top_20_results = sorted_results[:10]
        
        g_rateMax *= 0.999

        # 汇报内容
        for result in top_20_results:
            sym_tmp = result['symbol']
            # 如果 sym_tmp 不在 agSymbols 中，添加 *
            prefix = "*" if sym_tmp not in g_topSymbols else ""

            # 添加 sym_tmp 到 agSymbols
            agSymbols.append(sym_tmp)
            history_info = get_stock_prices(sym_tmp)
            
            if prefix == "*":
                g_topSymbols.append(sym_tmp)

            if history_info:
                content += f"{prefix}{result['symbol']} {result['result']} r:{result['rate']} {result['status']}"
                content += (
                    f"_o: {history_info['open_price']},"
                    f"c: {history_info['current_price']},"
                    f"b: {history_info['buff_price']}%\n"
                )
                if prefix == "*":
                    if desType != '全天' :
                        big_result = calculate_summary(sym_tmp, tmp_em_df[sym_tmp], "09:15:00", "15:16:00", True)
                        content += f"全         {big_result['result']} r:{big_result['rate']} {big_result['status']}\n"
                    content += "_" * 15 + "\n"
            else :
                content += f"{prefix}{result['symbol']} {result['result']} r:{result['rate']} {result['status']}\n"
        
        if len(top_results) > 10 :
            # 根据 rate 进行降序排序
            sorted_rate = sorted(top_results, key=itemgetter("rate"), reverse=True)

            # 取前 5
            top_5_results = sorted_rate[:10]

            content += "-" * 10 + "\n"
            # 汇报内容
            for result in top_5_results:
                sym_tmp = result['symbol']
                prefixRate = "*" if sym_tmp not in g_rateSymbols else ""
                if prefixRate == "*":
                    g_rateSymbols.append(sym_tmp)
                
                history_info = get_stock_prices(sym_tmp)
                agSymbols.append(result['symbol'])
                if history_info:
                    content += f"{prefixRate} {result['symbol']} {result['result']} r:{result['rate']} b: {history_info['buff_price']} {result['status']} \n"
                    if prefixRate == "*":
                        if desType != '全天' :
                            big_result = calculate_summary(sym_tmp, tmp_em_df[sym_tmp], "09:15:00", "15:16:00", True)
                            content += f"全         {big_result['result']} r:{big_result['rate']} {big_result['status']}\n"
                    content += "_" * 15 + "\n"
                else:
                    content += f"{prefixRate} {result['symbol']} {result['result']} r:{result['rate']} {result['status']}\n"

        # 更新详情信息
        # if asyncRun and len(agSymbols) > 0 :
            # 推送消息
            # asyncio.run(calculate_summary_async("agSymbols","stock_intraday_em_df", startT, endT, showAll,desType))
                
        # 推送消息
        if content and content != beforeCount:
            summary=begin + "Cac"+ "_" + cateLabel + "_" + desType + "_"+ curT + "\n"
            wx_pusher.send_message(summary + contentTime + content, summary=summary)
            save_stock_prev(summary + contentTime + content, begin)
            beforeCount= content;


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
    begin = '3'
    # 0-9:25; 1- 9:45  2- 15:00
    if len(sys.argv) >= 2:
        type = int(sys.argv[1])
    else:
        type = 2

    if len(sys.argv) >= 3:
        listCate = int(sys.argv[2])
    else:
        listCate = 2

    if len(sys.argv) >= 4:
        begin = sys.argv[3]
    else:
        begin = '3'
        
    if len(sys.argv) >= 5:
        alwaysRun = int(sys.argv[4])
    else:
        alwaysRun = 0    

    if len(sys.argv) >= 6:
        hasFilter = int(sys.argv[5]) == 1
    else:
        hasFilter = True    

    tCount = 10
    # 示例hh列表（替换为从配置或 API 获取的hh列表）
    if listCate == 0 :
        stock_list = list(set(config.car_symbols))
    elif listCate == 1 :
        tCount = 1
        stock_list = get_360_stocks(begin)
    elif listCate == 2 :
        tCount = 3
        stock_list = list(set(stb.stock107 + config.default_symbols))
    elif listCate == 3 :
        stock_list = list(set(stb.look_symbols))
    else :
        stock_list = list(set(config.default_symbols))
        
    g_curDayTime = datetime.now().strftime("%Y%m%d")

    stock_list.sort()
    if alwaysRun == 1 :
        while True:
            if mustOnce or is_trading_time() :
                mustOnce = False;
                update_stock_details(stock_list, type, begin, listCate, hasFilter)
                print('len:_lowerSymbols = ', len(g_lowerFileSymbols))
                if g_curDayTime != datetime.now().strftime("%Y%m%d"):
                    g_curDayTime = datetime.now().strftime("%Y%m%d")
                    g_lowerFileSymbols = [] // 隔天清理
                    g_rateSymbols = []
                    print(g_curDayTime, '-',len(g_lowerFileSymbols))
            time.sleep(tCount) # 每隔 tCount 秒调用一次 函数
    else :
        update_stock_details(stock_list, type, begin, listCate)
    
# param1:  type  # 0-9:25; 1- 9:45  2- 15:00 ； 3- 近5分钟
# param2:  listCate  0-购物车; 1-360全集; 2-精简全集；3-监听；4 默认
# param3:  begin 360代码前缀
# param4:  alwaysRun 0-只执行一次; 1-循环执行
# param5:  hasFilter 是否过滤 0-False 1- True

# 常用 
# 3分钟内 # 15:00 3精简全集 循环 python cacPre.py 3 2 3 1
# 3分钟内 # 15:00 3购物车 循环 python cacPre.py 3 0 3 1
# 全时段 # 15:00 3精简全集 循环 python cacPre.py 2 2 3 1
# # 15:00 3车 循环 python cacPre.py 2 0 3 1
# 9:45 # 9:45 3车 循环 python cacPre.py 1 0 3 1

# 全时段 # 15:00 6全集 单次 python cacPre.py 2 1 6

# 3分钟内 # 15:00 3全集 循环 python cacPre.py 3 1 3 1
# # 15:00 3全集 单次 python cacPre.py 2 1 3
# # 9:25 3全集 单次  python cacPre.py 0 1 3
# # 9:45 3全集 单次  python cacPre.py 1 1 3

# # 9:25 3车 单次 python cacPre.py 0 0 3
# # 9:25 3全集 单次 python cacPre.py 0 1 3
# # 9:25 6全集 单次 python cacPre.py 0 1 6
# # 9:25 0全集 单次 python cacPre.py 0 1 0

# # 9:45 3全集 单次 python cacPre.py 1 1 3
# # 9:45 6全集 单次 python cacPre.py 1 1 6
# # 9:45 0全集 单次 python cacPre.py 1 1 0

# # 15:00 3全集 单次 python cacPre.py 2 1 3
# # 15:00 6全集 单次 python cacPre.py 2 1 6
# # 15:00 0全集 单次 python cacPre.py 2 1 0

# # 9:45 3全集 循环 python cacPre.py 1 1 3 1
# # 15:00 3全集 循环 python cacPre.py 2 1 3 1
