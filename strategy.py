from poloniex import Poloniex

#Constants below

LONG_TRADE = 0
SHORT_TRADE = 1

class Trade:
    def __init__(self, ticker, timestamp, price, amount)
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

    def calculate_shares_on_hand(order_book):
        total = 0
        for trade in order_book:
            total += trade.amount
        return total

    def backtest(self, start_date, end_date, ticker, initial_deposit, fees):
        '''
        backtest(self, start_date, end_date, initial_deposit, fees) - backtests
        the current algorithm through the start and end date provided.
            Inputs: [start_date] is a Unix timestamp start date of the back 
            test. [end_date] is a Unix timestamp end date of the back test.
            [ticker] is a string representing the ticker to trade on.
            [initial_deposit] is a float representing the amount of cash
            we start out with in USD. [fees] is a float representing the the 
            fees per transaction for trade.
            Requires: [end_date] must be greater than [start_date] and 
            [initial_deposit] must be greater than or equal to 0
            Returns: A dictionary representing performance metrics of the 
            backtest including Profit/Loss and volatility.
        '''
        security_df = get_data(start_date, end_date, ticker)
        order_book = []
        liquid_funds =  initial_deposit
        for index, row in security_df.iterrows():
            trade = self.algo(order_book, row, ticker, liquid_funds)

            if trade['order'] == LONG_TRADE:
                if row['weightedAverage'] * trade['shares'] > liquid_funds:
                    raise ValueError('Trade size exceeds liquid funds')
                else:
                    new_trade = Trade(ticker, index, row['weightedAverage'], trade['shares'])
                    order_book.append(new_trade)
                    liquid_funds -= row['weightedAverage'] * trade['shares']
            elif trade['order'] == SHORT_TRADE:
                shares_oh = calculate_shares_on_hand(order_book)
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
                            liquid_funds += row['weightedAverage'] * shares_to_sell

                        else:
                            shares_to_sell -= value.amount
                            liquid_funds += row['weightedAverage'] * value.amount
                            
        return liquid_funds 


        

if __name__ == "__main__":
