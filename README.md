# stock-akshare
自由策略
在 GitHub 中建立一个项目并将代码提交到该项目的过程包括以下几个步骤。假设你已经有一个 GitHub 账户，并且在本地安装了 Git 和 Python 开发环境。

### 第一步：在 GitHub 上创建一个新的仓库

1. **登录到 GitHub**：
   打开浏览器并登录到你的 GitHub 账户。

2. **创建一个新的仓库**：
   - 点击页面右上角的加号（+）按钮，然后选择“New repository”。
   - 输入仓库名称（例如 `stock_new_low`），并填写仓库描述（可选）。
   - 选择仓库的可见性（Public 或 Private）。
   - 勾选 “Initialize this repository with a README” 选项。
   - 点击“Create repository”按钮。

### 第二步：在本地设置项目文件夹并初始化 Git

1. **在本地创建项目文件夹**：
   打开终端（或命令提示符）并导航到你想创建项目的目录，然后创建一个新文件夹并进入该文件夹。

   ```sh
   mkdir stock_new_low
   cd stock_new_low
   ```

2. **初始化 Git 仓库**：
   初始化一个新的 Git 仓库。

   ```sh
   git init
   ```

3. **添加远程仓库**：
   将 GitHub 上的新仓库添加为远程仓库。

   ```sh
   git remote add origin https://github.com/你的用户名/stock_new_low.git
   ```

### 第三步：添加代码文件并提交到 GitHub

1. **创建并编辑代码文件**：
   在项目文件夹中创建一个新的 Python 文件，并将你的代码粘贴进去。你可以使用你喜欢的文本编辑器（例如 VS Code、Sublime Text、Notepad++ 或 PyCharm）。

   ```sh
   touch stock_new_low.py
   ```

   打开 `stock_new_low.py` 并粘贴以下代码：

   ```python
   import akshare as ak
   import pandas as pd
   from pushMessage import WxPusher
   import datetime

   def sendMessage(content=""):
       summary = "stock_new_low"
       wx_pusher = WxPusher()
       wx_pusher.send_message(content, summary=summary)

   def find_and_save_new_low_stocks(output_file):
       # 获取今天的日期
       today = datetime.datetime.now().strftime("%Y%m%d")

       # 查找创新低的股票
       new_low_stocks = ak.stock_rank_cxd_ths()

       # 过滤股票代码以3开头的股票
       filtered_stocks = new_low_stocks[new_low_stocks["股票代码"].str.startswith("3")]

       # 初始化结果列表
       result_stocks = []

       for index, row in filtered_stocks.iterrows():
           stock_code = row["股票代码"]

           # 获取股票日K线数据
           stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=today, end_date=today, adjust="qfq")

           if not stock_zh_a_hist_df.empty:
               open_price = stock_zh_a_hist_df.iloc[0]["开盘"]
               current_price = stock_zh_a_hist_df.iloc[0]["收盘"]
               low_price = stock_zh_a_hist_df.iloc[0]["最低"]

               # 判断开盘价和当前价接近（可以定义一个误差范围，如0.5%）
               if abs(current_price - open_price) / open_price <= 0.005:
                   # 判断最低价降幅在2%-5%之间
                   if 0.02 <= (open_price - low_price) / open_price <= 0.05:
                       result_stocks.append(row)

       # 转换为DataFrame
       result_stocks_df = pd.DataFrame(result_stocks)

       # 打印并发送消息
       print(result_stocks_df)
       sendMessage(result_stocks_df.to_csv(index=False))

       # 将结果保存到文件
       result_stocks_df.to_csv(output_file, index=False)

   # 测试函数
   output_file = "filtered_new_low_stocks.csv"  # 文件名
   find_and_save_new_low_stocks(output_file)
   ```

2. **添加 README 文件（可选）**：
   创建一个 README 文件来描述你的项目。

   ```sh
   touch README.md
   ```

   打开 `README.md` 并写一些项目的描述。

3. **添加文件到 Git**：
   添加所有文件到 Git 仓库。

   ```sh
   git add .
   ```

4. **提交文件**：
   提交文件到本地 Git 仓库。

   ```sh
   git commit -m "Initial commit with stock_new_low script"
   ```

5. **推送到 GitHub**：
   将提交的文件推送到 GitHub 仓库。

   ```sh
   git push -u origin master
   ```

### 第四步：验证提交

1. **在 GitHub 上检查**：
   打开你的 GitHub 仓库页面（`https://github.com/你的用户名/stock_new_low`），你应该能够看到刚刚提交的代码文件。

完成这些步骤后，你的项目已经成功上传到 GitHub。以后可以根据需要继续更新和维护这个项目。

要将代码提交到 GitHub 仓库，需要验证你的身份。你可以通过浏览器登录 GitHub 或使用个人访问令牌（Personal Access Token, PAT）进行身份验证。以下是详细步骤：

通过浏览器登录 GitHub
运行 git push 命令后，如果 Git 需要你验证身份，它会提示你进行身份验证。
选择 "Sign in with your browser"。
浏览器将打开一个新的页面，要求你登录到 GitHub。
登录到 GitHub，并授权 Git 访问你的账户。
授权成功后，回到终端继续操作。

