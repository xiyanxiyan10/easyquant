from ccxtbt import CCXTStore
import backtrader.analyzers as btanalyzers
import matplotlib.pyplot as plt
import matplotlib
import PyQt5
matplotlib.use('Qt5Agg')

import backtrader as bt
from  lib.mail import qq_mail_send
from  lib.period import EventPeriod
from lib.tokeninsight import csv_to_btdata
from datetime import datetime, timedelta
from backtrader.feeds import GenericCSVData

import json


# Policy for make profit from volatility in hudge
# Refers:
# https://github.com/ccxt/ccxt/issues/11961
# https://www.marketcalls.in/wp-content/uploads/2021/02/Backtrader101.html

level = 4

backtest_mode = False
with open('./token.json', 'r') as f:
    config_params = json.load(f)

if config_params["backtest"]["mode"] == 'True':
    backtest_mode = True

mail_address = config_params["mail"]["address"]
mail_password = config_params["mail"]["password"]
mail_period = int(config_params["mail"]["period"])
event_period = EventPeriod(mail_period)
symbol_tuple = config_params["live"]["datas"]
backfile_array = config_params["backtest"]["datas"]
backfile_path = config_params["backtest"]["path"]

## 0 is long and 1 is short
price_tuple = (3659.19, 158.55)

class Hudge_Indicator(bt.Indicator):
    lines = ('relative_volatility', 'long_price', 'short_price')
    params = (('value', 5),)

    def __init__(self):
        self.addminperiod(1)

    def next(self):
        long_price = self.data0.close[0]
        short_price = self.data1.close[0]
        self.lines.relative_volatility[0] = hudge_dist(price_tuple[0], long_price, price_tuple[1], short_price)*100

def hudge_dist(old_long, new_long, old_short, new_short):
    long_price_volatility = (new_long - old_long)*1.0/old_long    #long price volatility
    short_price_volatility = (old_short - new_short)*1.0/old_short # shot price volatility

    long_profit_volatility = (new_long - old_long)*1.0/new_long*level*100    #long price volatility
    short_profit_volatility = (old_short - new_short)*1.0/new_short*level*100 # shot price volatility

    relative_volatility = long_price_volatility + short_price_volatility
    if relative_volatility < 0.0:
        relative_volatility = 0 - relative_volatility
    return relative_volatility

class HudgeGripStrategy(bt.Strategy):

    def __init__(self):
        self.hudge_Indicator = Hudge_Indicator(self.data0, self.data1)

        self.ma = bt.indicators.SimpleMovingAverage(self.datas[0])
        self.ma = bt.indicators.SimpleMovingAverage(self.datas[1])

        # self.relative_volatility = self.hudge_Indicator.relative_volatility
        #self.sma = bt.indicators.SMA(self.data,period=21)

    def next(self):

        # Get cash and balance
        # New broker method that will let you get the cash and balance for
        # any wallet. It also means we can disable the getcash() and getvalue()
        # rest calls before and after next which slows things down.

        # NOTE: If you try to get the wallet balance from a wallet you have
        # never funded, a KeyError will be raised! Change LTC below as approriate
        # if self.live_data:
        #    cash, value = self.broker.get_wallet_balance('BNB')
        # else:
            # Avoid checking the balance during a backfill. Otherwise, it will
            # Slow things down.
        #    cash = 'NA'

        output = ''
        for data in self.datas:
            output += ('{} - {} | O: {} H: {} L: {} C: {} V:{}\n'.format(data.datetime.datetime(),
                                                                                   data._name, data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0],
                                                                                   ))
        long_price = self.data0.close[0]
        short_price = self.data1.close[0]

        output += ("long price: %f, shot price %f\n" % (long_price, short_price))
        output += ("%f %%\n" % (self.hudge_Indicator.relative_volatility[0]))
        print(output)
        if not backtest_mode and event_period.check():
            #import pdb
            #pdb.set_trace()
            qq_mail_send(mail_address, [mail_address], mail_password, 'hudgegride', output)
            print("send email notify")

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg= 'Data Status: {}'.format(data._getstatusname(status))
        print(dt,dn,msg)
        # if data._getstatusname(status) == 'LIVE':
        #    self.live_data = True
        #else:
        #    self.live_data = False



# Get the broker and pass any kwargs if needed.
# ----------------------------------------------
# Broker mappings have been added since some exchanges expect different values
# to the defaults. Case in point, Kraken vs Bitmex. NOTE: Broker mappings are not
# required if the broker uses the same values as the defaults in CCXTBroker.
broker_mapping = {
    'order_types': {
        bt.Order.Market: 'market',
        bt.Order.Limit: 'limit',
        bt.Order.Stop: 'stop-loss', #stop-loss for kraken, stop for bitmex
        bt.Order.StopLimit: 'stop limit'
    },
    'mappings':{
        'closed_order':{
            'key': 'status',
            'value':'closed'
        },
        'canceled_order':{
            'key': 'result',
            'value':1}
    }
}


def run_backtest():
    cerebro = bt.Cerebro()
    for i in range(len(backfile_array)):
        back_data = csv_to_btdata(backfile_path + backfile_array[i] + ".csv")
        cerebro.adddata(back_data, name=backfile_array[i])

    cerebro.addstrategy(HudgeGripStrategy)
    cerebro.run()
    cerebro.plot()

def run_live():
    cerebro = bt.Cerebro(quicknotify=True)

    # Add the strategy
    cerebro.addstrategy(HudgeGripStrategy)

    # Create our store
    config = {'apiKey': config_params["live"]["apikey"],
          'secret': config_params["live"]["secret"],
          'enableRateLimit': True,
          'options': {
            'defaultType': config_params["live"]["type"],
          },
          'proxies': {'https':config_params["live"]["proxy"], 'http':config_params["live"]["proxy"]}
          }



    # IMPORTANT NOTE - Kraken (and some other exchanges) will not return any values
    # for get cash or value if You have never held any BNB coins in your account.
    # So switch BNB to a coin you have funded previously if you get errors
    store = CCXTStore(exchange=config_params["live"]["exchange"], currency=config_params["live"]["currency"], config=config, retries=5, debug=False)

    broker = store.getbroker(broker_mapping=broker_mapping)
    cerebro.setbroker(broker)

    # Get our data
    # Drop newest will prevent us from loading partial data from incomplete candles
    hist_start_date = datetime.utcnow() - timedelta(minutes=50)

    for i in range(len(symbol_tuple)):
        live_data = store.getdata(dataname=symbol_tuple[i], name=symbol_tuple[i],
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=1, ohlcv_limit=50, drop_newest=True) #, historical=True)

        # Add the feed
        cerebro.adddata(live_data, name = symbol_tuple[i])

    # Run the strategy
    cerebro.run()

def run():
    if backtest_mode:
        print('run backtest!!')
        run_backtest()
    else:
        print('run live!!')
        run_live()
