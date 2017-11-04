#updateTicker.py which will be executed from secOwnership.py and populated by...
#list of tickers: http://www.nasdaq.com/screening/company-list.aspx
import untangle, s, pymysql, sys, datetime, pytz, requests, re

now = str(datetime.datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'))

issuerTradingSymbol = sys.argv[1]
#issuerTradingSymbol = 'IBM'

db = pymysql.connect(host=s.host, port=3306, user=s.user, passwd=s.passwd, db=s.db)
cursor = db.cursor()

def loadTicker(issuerTradingSymbol):
    issuerTradingSymbol = issuerTradingSymbol.strip()
    issuerTradingSymbol = re.match(r'[A-Z]+',issuerTradingSymbol, re.IGNORECASE).group(0)
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
        sqlFetchTicker = "SELECT issuerTradingSymbol FROM secTickers WHERE cik = " + cik + ";"
        #print(sqlFetchTicker)
        cursor.execute(sqlFetchTicker)
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
        #print(issuerTradingSymbol,'loaded')
    else:
        #print(issuerTradingSymbol,'NOT FOUND')
        pass
loadTicker(issuerTradingSymbol)
db.close()