from poloniex import Poloniex
from IchimokuClouds import IchimokuClouds
from SMAMomentum import SMAMomentum
import time
import datetime
import pandas as pd
#Constants below

LONG_TRADE = 0
SHORT_TRADE = 1
NO_TRADE = -1

class Trade:
    def __init__(self, ticker, timestamp, price, amount):
        self.ticker = ticker
        self.timestamp = timestamp
        self.price = price
        self.amount = amount

class Strategy:
    def __init__(self, algo, tickers):
        '''
        Strategy is a class representing an algorithmic trading strategy.
        '''
        self.algo = algo
        self.polo = Poloniex()
        self.tickers = tickers
        self.polo.key = 'KEFPS6QC-CE8KHULI-ACLJY1GC-L4P923CC'
        self.polo.secret = '4121c780577b601b051c2de8325e977cab65dbee250027c166d52762d7bee3dbd48245d9e0c89830a327fd05f0481c0433556be2c8a9bc6d775e8a84c6ad7df361'

    def calculate_shares_on_hand(self, order_book):
        total = 0.0
        for trade in order_book:
            total += trade.amount
        return total

    def get_data(self, start_date, end_date, period,  ticker):
        '''
        get_data(self, start_date, end_date, ticker) - gets the historical data
        as a dataframe
            Inputs: [start_date] is a string start date following the form 'MM/DD/YYYY'.
            [end_date] is the end date following the form 'MM/DD/YYYY'. [ticker] is the 
            currency pair to trade on.
            Returns: a python data frame where each row represents a ticker
        '''
        start_unix = time.mktime(datetime.datetime.strptime(start_date, "%m/%d/%Y").timetuple())
        end_unix = time.mktime(datetime.datetime.strptime(end_date, "%m/%d/%Y").timetuple())
        historical_data = self.polo.returnChartData(currencyPair=ticker, period=period, start=start_unix,
                                               end=end_unix)
        data_frame = pd.DataFrame.from_dict(historical_data, orient='columns',
                                            dtype=None)

        return data_frame


    def backtest(self, start_date, end_date, ticker, initial_deposit, fees):
        '''
        backtest(self, start_date, end_date, initial_deposit, fees) - backtests
        the current algorithm through the start and end date provided.
            Inputs: [start_date] is a string start date of the following form
            'MM/DD/YYYY'. [end_date] is a string end date of the following form
            'MM/DD/YYYY. [ticker] is a string representing the ticker to trade on.
            [initial_deposit] is a float representing the amount of cash
            we start out with in USD. [fees] is a float representing the the 
            fees per transaction for trade.
            Requires: [end_date] must be greater than [start_date] and 
            [initial_deposit] must be greater than or equal to 0
            Returns: A dictionary representing performance metrics of the 
            backtest including Profit/Loss and volatility.
        '''
        security_df = self.get_data(start_date, end_date, 300, ticker)
        order_book = []
        liquid_funds =  initial_deposit
        for index, row in security_df.iterrows():
            #at each iteration send a row from dataframe into the algo
            trade = self.algo(order_book, ticker, liquid_funds, row)
            datestring = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(int(row['date'])))

            if trade['order'] == LONG_TRADE:
                print("Long trade: " + str(trade['shares']) + " shares @ " + row['weightedAverage'] + " on " + datestring)
                if float(row['weightedAverage']) * trade['shares'] > liquid_funds:
                    raise ValueError('Trade size exceeds liquid funds')
                else:
                    new_trade = Trade(ticker, index, float(row['weightedAverage']), trade['shares'])
                    order_book.append(new_trade)
                    liquid_funds -= float(row['weightedAverage']) * trade['shares']
            elif trade['order'] == SHORT_TRADE:
                print("Short trade: " + str(trade['shares']) + " shares @ " + row['weightedAverage'] + " on " + datestring)
                shares_oh = self.calculate_shares_on_hand(order_book)
                if trade['shares'] > shares_oh:
                    raise ValueError('Trade size exceeds shares in portfolio')
                else:
                    shares_to_sell = trade['shares']
                    new_order_book = []
                    for counter, value in enumerate(order_book):
                        if shares_to_sell == 0:
                            new_order_book.append(value)
                        elif value.amount >= shares_to_sell:
                            if value.amount > shares_to_sell:
                                new_amt = value.amount-shares_to_sell
                                new_order_book.append(Trade(value.ticker, value.timestamp, value.price, new_amt))

                            shares_to_sell = 0
                            liquid_funds += float(row['weightedAverage']) * shares_to_sell

                        else:
                            shares_to_sell -= value.amount
                            liquid_funds += float(row['weightedAverage']) * value.amount
                    order_book = new_order_book
            last_row = row

        if len(order_book) > 0:
            #closes last open trades
            for counter, value in enumerate(order_book):
                liquid_funds += float(last_row['weightedAverage']) * value.amount

                            
        return liquid_funds 
        
if __name__ == "__main__":
    sma_strat = SMAMomentum()
    start_date = "03/01/2018"
    end_date = "05/01/2018"
    ticker = "BTC_ETH"
    initial_deposit = 5000
    fees = 0.1
    print ("********Simulating from " + start_date + " to " + end_date)
    strat = Strategy(sma_strat.algo, ticker)
    print ("********Total Returns: " + str(strat.backtest(start_date, end_date, ticker, initial_deposit, fees)))
    '''
    ichimoku_strat = IchimokuClouds(9, 26, 52)
    start_date = "06/01/2017"
    end_date = "04/01/2018"
    ticker = "BTC_ETH"
    initial_deposit = 5000
    fees = 0.1
    strat = Strategy(ichimoku_strat.cloud_algo, ticker)
    strat.backtest(self, start_date, end_date, ticker, initial_deposit, fees)
    '''