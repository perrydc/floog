#tickerLoad.py
import csv, untangle, s, pymysql, sys, datetime, pytz, requests
#source of below csvs: http://www.nasdaq.com/screening/company-list.aspx
#any list of tickers will work, as long as it is a csv with tickers in the first column
nasdaqTickers = 'http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download'
nyseTickers = 'http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download'
amexTickers = 'http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download'

#response = requests.get(amexTickers)
#response = requests.get(nasdaqTickers)
#response = requests.get(nyseTickers)

with open('temp.csv', 'wb') as f:
    f.write(response.content)
with open("temp.csv") as f:
    rawList = [row.split(',')[0].replace('"', '') for row in f]
rawList.pop(0)
cleanList = [s for s in rawList if (s.find("^") < 0 and s.find(".") < 0)]
#print(cleanList)
def loadTicker(issuerTradingSymbol):
    issuerTradingSymbol = issuerTradingSymbol.strip()
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=&dateb=&owner=exclude&start=0&count=10&output=atom'.format(issuerTradingSymbol)
    r = requests.head(url)
    if r.encoding == None:
        obj = untangle.parse(url)
        cik = obj.feed.company_info.cik.cdata
        industry = ''
        if 'assigned_sic_desc' in dir(obj.feed.company_info):
            industry = obj.feed.company_info.assigned_sic_desc.cdata
        sik = str(0)
        if 'assigned_sic' in dir(obj.feed.company_info):
            sik = obj.feed.company_info.assigned_sic.cdata
        companyName = ''
        if 'conformed_name' in dir(obj.feed.company_info):
            companyName = obj.feed.company_info.conformed_name.cdata
        cursor.execute("SELECT issuerTradingSymbol FROM secTickers WHERE cik = " + cik + ";")
        rows = cursor.fetchone()
        if(rows):
            cursor.execute("DELETE FROM secTickers WHERE cik = " + cik + ";")

        sql = ('INSERT INTO secTickers SET '
            'companyName = "%s", '
            'issuerTradingSymbol = "' + issuerTradingSymbol + '", '
            'industry = "%s", '
            'updated = "' + now + '", '
            'sik = "' + sik + '", '
            'cik = "' + cik + '"')
        #print(sql % (companyName, industry))
        cursor.execute(sql, (companyName.replace("'",""), industry.replace("'","")))
        print(issuerTradingSymbol,'loaded')
    else:
        print(issuerTradingSymbol,'NOT FOUND')
now = str(datetime.datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'))
db = pymysql.connect(host=s.host, port=3306, user=s.user, passwd=s.passwd, db=s.db)
cursor = db.cursor()

for ticker in cleanList:
    loadTicker(ticker)
    #pass

db.close()