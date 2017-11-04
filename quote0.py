#quote0.py
# other data available: https://pypi.python.org/pypi/yahoo-finance/1.4.0
import requests, re, s, pymysql, sys, datetime, pytz, json
from dateutil import parser
from yahoo_finance import Share

def fetchFinancials(ticker, security=''):
    try:
        security = Share(ticker)
    except:
        print('yahoo finance server is down, as usual.') #this will result in less verbose logs, at least.
    return security

id = sys.argv[1]
ticker = sys.argv[2]
ticker = re.match(r'[A-Z]+',ticker, re.IGNORECASE).group(0)

now = str(datetime.datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'))

# UNCOMMENT BELOW FOR DEBUGGING
#import random
#id = 'test' + str(random.randint(0,1000))
#ticker = 'GETG'
#print("\n\n id =", id, " issuerTradingSymbol = ", issuerTradingSymbol, "\n")

security = fetchFinancials(ticker)
if security:
    quote0 = round(float(security.get_price()),2)
    benchmark = fetchFinancials("SPY")
    if benchmark:
        inx0 = round(float(benchmark.get_price()),2) #this is the benchmark that we'll compare performance against.
        last = str(parser.parse(security.get_trade_datetime()).strftime('%Y-%m-%d %H:%M:%S'))
        exchange = '0'
        if security.get_stock_exchange() != None:
            exchange = security.get_stock_exchange()
        pe = '0'
        if security.get_price_earnings_ratio() != None:
            pe = round(float(security.get_price_earnings_ratio()),0)
        if security.get_market_cap():
            market_cap = security.get_market_cap()
        else:
            market_cap = '0'
        if market_cap.find('B') != -1:
            market_cap = market_cap.replace('B','')
            market_cap = int(float(market_cap)*1000000000)
        elif market_cap.find('M') != -1:
            market_cap = market_cap.replace('M','')
            market_cap = int(float(market_cap)*1000000)
        volume = 0
        if security.get_avg_daily_volume() != None:
            volume = security.get_avg_daily_volume()
        year_high = 0
        if security.get_year_high() != None:
            year_high = round(float(security.get_year_high()),2)
        year_low = 0
        if security.get_year_low() != None:
            year_low = round(float(security.get_year_low()),2)
        short_ratio = 0
        if security.get_short_ratio() != None:
            short_ratio = security.get_short_ratio()
        dividend_yield = '0'
        if security.get_dividend_yield() != None:
            dividend_yield = security.get_dividend_yield()

        db = pymysql.connect(host=s.host, port=3306, user=s.user, passwd=s.passwd, db=s.db)
        cursor = db.cursor()

        sql = ('INSERT INTO secQuote SET '
               'id = "' + id + '", '
               'exchange = "' + exchange + '", '
               'ticker = "' + ticker + '", '
               'inx0 = "' + str(inx0) + '", '
               'pe = "' + str(pe) + '", '
               'market_cap = "' + str(market_cap) + '", '
               'volume = "' + str(volume) + '", '
               'year_high = "' + str(year_high) + '", '
               'year_low = "' + str(year_low) + '", '
               'short_ratio = "' + str(short_ratio) + '", '
               'dividend_yield = "' + str(dividend_yield) + '", '
               'timestamp = "' + now + '", '
               'last = "' + last + '", '
               'quote0 = "' + str(quote0) + '"')

        #print(sql)
        cursor.execute(sql)

        db.close()