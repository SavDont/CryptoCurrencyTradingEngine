from poloniex import Poloniex
polo = Poloniex()

print(polo.returnTicker()['BTC_ETH'])
