import backtrader as bt
from backtrader.feeds import GenericCSVData
from datetime import date

def csv_to_btdata(path, **kwargs):
    load_dict = {
        "dataname":path,
        "dtformat":('%Y-%m-%d'),
        "datetime":0,  
        "high": 1,      
        "low": 1,
        "open": 1,
        "close": 1,
        "volume": 2,
        "openinterest":-1
    }
    load_dict.update(kwargs)
    btdata = GenericCSVData(**load_dict)

    return btdata



import datetime
import backtrader as bt
import backtrader.feeds as btfeeds

class PrintClose(bt.Strategy):

    def __init__(self):
        self.dataclose = self.datas[0].close

    def next(self):
        output = ''
        for data in self.datas:
            output += ('{} - {} | O: {} H: {} L: {} C: {} V:{}\n'.format(data.datetime.datetime(),
                                                                                   data._name, data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0],
                                                                                   ))
        print(output)

if __name__ == '__main__':
    btdata = csv_to_btdata('./eth.csv')

    cerebro = bt.Cerebro()
    cerebro.addstrategy(PrintClose)
    cerebro.adddata(btdata)
    cerebro.run()
