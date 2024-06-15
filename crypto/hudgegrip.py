#!/usr/local/bin/python3
import ccxt
import time

# Policy for make profit from volatility in hudge
# Refers:
# https://github.com/ccxt/ccxt/issues/11961

level = 4
old_long = 3695.36
#new_long = 3688.68
old_short = 161.46
#new_short = 161.18

def cal_dist(old_long, new_long, old_short, new_short):
    long_volatility = (new_long - old_long)*1.0/old_long    #long price volatility
    short_volatility = (old_short - new_short)*1.0/old_short # shot price volatility

    long_profit_volatility = (new_long - old_long)*1.0/new_long    #long price volatility
    short_profit_volatility = (old_short - new_short)*1.0/new_short # shot price volatility

    print("long_volatility: %f short_volatility: %f" % (long_volatility, short_volatility))
    print("long_profit_volatility: %f short_profit_volatility: %f" % (long_profit_volatility*level, short_profit_volatility*level))
    relative_volatility = long_volatility + short_volatility
    if relative_volatility < 0.0:
        relative_volatility = 0 - relative_volatility
    return relative_volatility

proxy = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# 创建 Binance 交易所实例
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
    'proxies': proxy
})

def get_future_price(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

while True:
    sol_price = get_future_price(exchange, 'SOL/USDT')
    eth_price = get_future_price(exchange, 'ETH/USDT')

    print('eth: %f, sol: %f' % (eth_price, sol_price))
    relative_volatility = cal_dist(old_long, eth_price, old_short, sol_price)
    print("%f %%" % (relative_volatility * 100))

    time.sleep(180)
    #print(f"Binance eth期货当前价格: {eth_price} USDT")
    #print(f"Binance sol期货当前价格: {sol_price} USDT")
