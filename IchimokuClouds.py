import pandas as pd
import datetime
from poloniex import Poloniex


polo = Poloniex()

class IchimokuClouds:

    def __init__(self, base_line, leading_line, period_high):
        self.base_line = base_line
        self.leading_line = leading_line
        self.period_high = period_high

    def gen_cloud(self):
        high_prices = self.data_frame['High']
        close_prices = self.data_frame['Close']
        low_prices = self.data_frame['Low']
        dates = self.data_frame.index
        nine_period_high = pd.rolling_max(self.data_frame['High'], window= self.period_high)
        nine_period_low = pd.rolling_min(self.data_frame['Low'], window= self.period_high )
        self.data_frame['tenkan_sen'] = (nine_period_high + nine_period_low) /2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = pd.rolling_max(high_prices, window= self.base_line)
        period26_low = pd.rolling_min(low_prices, window= self.base_line)
        self.data_frame['kijun_sen'] = (period26_high + period26_low) / 2

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        self.data_frame['senkou_span_a'] = ((data_frame['tenkan_sen'] + data_frame['kijun_sen']) / 2).shift(self.base_line)

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = pd.rolling_max(high_prices, window=self.leading_line)
        period52_low = pd.rolling_min(low_prices, window=self.leading_line)
        self.data_frame['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)

        # The most current closing price plotted 22 time periods behind (optional)
        #self.data_frame['chikou_span'] = close_prices.shift(-22) # 22 according to investopedia
        print(self.data_frame.plot())

    def cloud_algo(self, order_book, ticker, current, time):
        self.order_book = order_book
        self.ticker= ticker
        self.current = current
        self.time = time
        historical_data = polo.returnChartData(ticker, 300,
                                               (self.start - self.leading_line * 86400),
                                               self.start)
        data_frame = pd.DataFrame.from_dict(historical_data, orient='columns',
                                            dtype=None)
        data_frame = data_frame[
            ['date', 'high', 'low', 'open', 'close', 'quoteVolume', 'volume',
             'weightedAverage']]

