from ccxtbt import CCXTStore
import backtrader.analyzers as btanalyzers
import matplotlib.pyplot as plt
import backtrader as bt
#from  lib.mail import qq_mail_send
from datetime import datetime, timedelta

import json


# Policy for make profit from volatility in hudge
# Refers:
# https://github.com/ccxt/ccxt/issues/11961

level = 4

## 0 is long and 1 is short
symbol_tuple = ('ETH/USDT', 'SOL/USDT')
price_tuple = (3659.19, 158.55)

def hudge_dist(old_long, new_long, old_short, new_short):
    long_price_volatility = (new_long - old_long)*1.0/old_long    #long price volatility
    short_price_volatility = (old_short - new_short)*1.0/old_short # shot price volatility

    long_profit_volatility = (new_long - old_long)*1.0/new_long*level*100    #long price volatility
    short_profit_volatility = (old_short - new_short)*1.0/new_short*level*100 # shot price volatility

    print("long_price_volatility: %f %% short_price_volatility: %f %%" % (long_price_volatility*100, short_price_volatility*100))
    print("long_profit_volatility: %f %% short_profit_volatility: %f %% , relative_profit: %f %%" % (long_profit_volatility, short_profit_volatility, \
                                                                                       long_profit_volatility + short_profit_volatility))
    relative_volatility = long_price_volatility + short_price_volatility
    if relative_volatility < 0.0:
        relative_volatility = 0 - relative_volatility
    return relative_volatility

class HudgeGripStrategy(bt.Strategy):

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data)
        #self.sma = bt.indicators.SMA(self.data,period=21)

    def next(self):

        # Get cash and balance
        # New broker method that will let you get the cash and balance for
        # any wallet. It also means we can disable the getcash() and getvalue()
        # rest calls before and after next which slows things down.

        # NOTE: If you try to get the wallet balance from a wallet you have
        # never funded, a KeyError will be raised! Change LTC below as approriate
        if self.live_data:
            cash, value = self.broker.get_wallet_balance('BNB')
        else:
            # Avoid checking the balance during a backfill. Otherwise, it will
            # Slow things down.
            cash = 'NA'

        long_price = -1.0
        short_price = -1.0
        for data in self.datas:
            print('{} - {} | Cash {} | O: {} H: {} L: {} C: {} V:{} SMA:{}'.format(data.datetime.datetime(),
                                                                                   data._name, cash, data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0],
                                                                                   self.sma[0]))
            if data._name == symbol_tuple[0]:
                long_price = data.close[0]

            if data._name == symbol_tuple[1]:
                short_price = data.close[0]

        print("long price: %f, shot price %f" % (long_price, short_price))
        relative_volatility = hudge_dist(price_tuple[0], long_price, price_tuple[1], short_price)
        print("%f %%" % (relative_volatility * 100))

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg= 'Data Status: {}'.format(data._getstatusname(status))
        print(dt,dn,msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False

with open('./token.json', 'r') as f:
    params = json.load(f)

cerebro = bt.Cerebro(quicknotify=True)


# Add the strategy
cerebro.addstrategy(HudgeGripStrategy)

# Create our store
config = {'apiKey': params["binance"]["apikey"],
          'secret': params["binance"]["secret"],
          'enableRateLimit': True,
          'options': {
            'defaultType': 'future',
          },
          'proxies': {'https':"http://127.0.0.1:7890", 'http':"http://127.0.0.1:7890"}
          }


# IMPORTANT NOTE - Kraken (and some other exchanges) will not return any values
# for get cash or value if You have never held any BNB coins in your account.
# So switch BNB to a coin you have funded previously if you get errors
store = CCXTStore(exchange='binance', currency='BNB', config=config, retries=5, debug=False)


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

broker = store.getbroker(broker_mapping=broker_mapping)
cerebro.setbroker(broker)

# Get our data
# Drop newest will prevent us from loading partial data from incomplete candles
hist_start_date = datetime.utcnow() - timedelta(minutes=50)

short_data = store.getdata(dataname=symbol_tuple[1], name=symbol_tuple[1],
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=1, ohlcv_limit=50, drop_newest=True) #, historical=True)

long_data = store.getdata(dataname=symbol_tuple[0], name=symbol_tuple[0],
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=1, ohlcv_limit=50, drop_newest=True) #, historical=True)

# Add the feed
cerebro.adddata(long_data)
cerebro.adddata(short_data)

# Run the strategy
cerebro.run()
cerebro.plot()
