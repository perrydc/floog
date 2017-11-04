#quoteLater.py
import requests, re, s, pymysql, sys, datetime, pytz, json
from yahoo_finance import Share

def fetchFinancials(ticker, security=''):
    try:
        security = Share(ticker)
    except:
        print('yahoo finance server is down, as usual.') #this will result in less verbose logs, at least.
    return security

db = pymysql.connect(host=s.host, port=3306, user=s.user, passwd=s.passwd, db=s.db)
cursor = db.cursor()

timeframe20m = "BETWEEN '" + str(
    (
        datetime.datetime.now(pytz.timezone('US/Eastern')) 
        - datetime.timedelta(minutes=21,seconds=30)
    )
    .strftime('%Y-%m-%d %H:%M:%S')
) + "' AND '" + str(
    (
        datetime.datetime.now(pytz.timezone('US/Eastern')) 
        - datetime.timedelta(minutes=20)
    )
    .strftime('%Y-%m-%d %H:%M:%S')
) + "'"

timeframe7 = "BETWEEN '" + str(
    (
        datetime.datetime.now(pytz.timezone('US/Eastern')) 
        - datetime.timedelta(days=7,minutes=1,seconds=30)
    )
    .strftime('%Y-%m-%d %H:%M:%S')
) + "' AND '" + str(
    (
        datetime.datetime.now(pytz.timezone('US/Eastern')) 
        - datetime.timedelta(days=7)
    )
    .strftime('%Y-%m-%d %H:%M:%S')
) + "'"

def recordPrice(timeframe, timeslot, inx):
    sqlTemplate = """SELECT exchange, ticker FROM secQuote 
        WHERE timestamp %s
        AND ISNULL(%s)"""
    sql = (sqlTemplate % (timeframe, 'inx' + timeslot))
    cursor.execute(sql)
    rows = cursor.fetchall()
    #rows = ["IBM","GOOG"] #inserted for debugging only    
    #print("SQL in:", sql,"\n\n") #inserted for debugging only
    sql = ""
    if(rows):
        tickers = []
        for row in rows:
            ticker = row
            security = fetchFinancials(ticker)
            if security:
                price = round(float(security.get_price()),2)
                sqlTemplate = """UPDATE secQuote SET 
                    inx%s = '%s', 
                    quote%s = '%s' 
                    WHERE ticker = '%s' 
                    AND timestamp %s;"""
                sql += (sqlTemplate % (timeslot,inx,timeslot,price,ticker,timeframe))
            if(sql):
                #print("SQL out:", sql) #inserted for debugging only
                cursor.execute(sql)
benchmark = fetchFinancials("SPY")
if benchmark:
    inx = round(float(benchmark.get_price()),2) #index / benchmark
    recordPrice(timeframe20m,'20m', inx)
    recordPrice(timeframe7,'7', inx)
db.close()