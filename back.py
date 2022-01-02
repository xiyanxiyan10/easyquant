import backtrader as bt
import tushare as ts
import pandas as pd
from datetime import datetime

# data cleaning
# get date from tushare
ts.set_token('968f5f34be59eb4bbcdbcd6ae456eebac2d4f9706ff6fea778333523')
pro = ts.pro_api()
df = pro.coin_bar(start_date='20200615', end_date='20210616',
                  freq='15min', exchange='huobi', ts_code='ETH_USDT')

df.rename(columns={'trade_time':'datetime', 'vol':'volume'}, inplace=True)
df['datetime']=df.datetime.apply(lambda x:pd.to_datetime(x))
df['openinterest']=0
df.index=pd.to_datetime(df.datetime)

print(df)


#回测期间
start=datetime(2020, 6, 15)
end=datetime(2021, 6, 16)
# 加载数据
data = bt.feeds.PandasData(dataname=df,fromdate=start,todate=end)

# policy 
class MacdStrategy(bt.Strategy):
    """
    继承并构建自己的bt策略
    """

    def log(self, txt, dt=None, doprint=False):
        ''' 日志函数，用于统一输出日志格式 '''
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        # 初始化相关数据
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 五日移动平均线
        self.sma5 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=5)
        # 十日移动平均线
        self.sma10 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=10)

    def next(self):
        ''' 下一次执行 '''
        
        # 记录收盘价
        # self.log('Close, %.2f' % self.dataclose[0])
        

        # 是否正在下单，如果是的话不能提交第二次订单
        if self.order:
            return

        # 是否已经买入
        if not self.position:
            # 还没买，如果 MA5 > MA10 说明涨势，买入
            if self.sma5[0] > self.sma10[0]:
                self.order = self.buy()
        else:
            # 已经买了，如果 MA5 < MA10 ，说明跌势，卖出
            if self.sma5[0] < self.sma10[0]:
                self.order = self.sell()

    def stop(self):
        self.log(u' Ending Value %.2f' %
                 (self.broker.getvalue()), doprint=True)

cerebro = bt.Cerebro()
cerebro.adddata(data=data)
cerebro.addstrategy(MacdStrategy)
startcash=1000
cerebro.broker.setcash(startcash)
cerebro.broker.setcommission(commission=0.002)

d1=start.strftime('%Y%m%d')
d2=end.strftime('%Y%m%d')
print(f'初始资金: {startcash}\n回测期间：{d1}:{d2}')
#运行回测系统

cerebro.run()
cerebro.plot()
#portvalue = cerebro.broker.getvalue()
#pnl = portvalue - startcash
#打印结果
#print(f'总资金: {round(portvalue,2)}')
