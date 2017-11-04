# make.py
# cd ~/
# git clone https://github.com/perrydc/floog
# OR...
# git pull origin master
import s, pymysql
# note: ^ s is not really a module, just a file s.py that you save in your package index for easy access.
# format:
#  host = '69.196.232.173'
#  db = 'honkin_db'
#  user = 'bamf'
#  passwd = 'B!gB0y'

# to make files executable:
#   chmod +x secIndex.py
#   chmod +x secOwnership.py
#   chmod +x quote0.py
#   chmod +x quoteLater.py
#   crontab: * * * * * ~/anaconda3/bin/python3 ~/floog/secIndex.py >> ~/floog/log.txt 2>&1
#   crontab: * * * * * ~/anaconda3/bin/python3 ~/floog/quoteLater.py >> ~/floog/log.txt 2>&1
# note: secOwnership.py and quote0.py are run sequentially from secIndex.py, so don't cron these!

# with above setup, just uncomment the cursor.execute commands below and run this script once.
# For further reference on pymysql, go to:
#   https://www.tutorialspoint.com/python3/python_database_access.htm

# secTickers table gets data from the SEC over time and a learning algorithm makes it smarter in its matching
# of CIK to tickers.  To prepopulate the table, just run tickerLoad.py, uncommenting the top response lines
# to alternately cross-load from NYSE, Nasdaq and AMEX (run between each uncomment)

db = pymysql.connect(host=s.host, port=3306, user=s.user, passwd=s.passwd, db=s.db)
cursor = db.cursor()

sql = ('CREATE TABLE secIndex('
       'id VARCHAR(100) NOT NULL,'
       'form VARCHAR(20) NULL,'
       'cik INT(11) NULL,'
       'title VARCHAR(255) NULL,'
       'link VARCHAR(255) NULL,'
       'updated DATETIME NULL,'
       'timestamp DATETIME NULL,'
       'PRIMARY KEY (id),'
       'UNIQUE INDEX id_UNIQUE (id ASC));')
#cursor.execute(sql)

sql = ('CREATE TABLE secOwnership('
       'id VARCHAR(100) NOT NULL,'
       'transactionCode VARCHAR(100) NULL,'
       'documentType VARCHAR(4) NULL,'
       'periodOfReport DATE NULL,'
       'notSubjectToSection16 INT(1) NULL,'
       'issuerCik INT(11) NULL,'
       'issuerName VARCHAR(255) NULL,'
       'issuerTradingSymbol VARCHAR(10) NULL,'
       'rptOwnerCik INT(11) NULL,'
       'rptOwnerName VARCHAR(255) NULL,'
       'rptOwnerStreet1 VARCHAR(100) NULL,'
       'rptOwnerCity VARCHAR(100) NULL,'
       'rptOwnerState VARCHAR(2) NULL,'
       'rptOwnerZipCode VARCHAR(10) NULL,'
       'isDirector TINYINT(4) NULL,'
       'isOfficer TINYINT(4) NULL,'
       'isTenPercentOwner TINYINT(4) NULL,'
       'isOther TINYINT(4) NULL,'
       'officerTitle VARCHAR(100) NULL,'
       'nonDerivativeValue BIGINT(20) NULL,'
       'derivativeValue BIGINT(20) NULL,'
       'sharesOwnedFollowingTransaction BIGINT(20) NULL,'
       'directOrIndirectOwnership VARCHAR(5) NULL,'
       'link VARCHAR(255) NULL,'
       'footnote TEXT NULL,'
       'timestamp DATETIME NULL,'
       'PRIMARY KEY (id),'
       'UNIQUE INDEX id_UNIQUE (id ASC));')
#cursor.execute(sql)

sql = ('CREATE TABLE secQuote('
       'id VARCHAR(100) NOT NULL,'
       'exchange VARCHAR(10) NULL,'
       'ticker VARCHAR(10) NULL,'
       'timestamp DATETIME NULL,'
       'last DATETIME NULL,'
       'pe INT(5) NULL,'
       'market_cap DECIMAL(15,0) NULL,'
       'volume DECIMAL(15,0) NULL,'
       'year_high DECIMAL(15,2) NULL,'
       'year_low DECIMAL(15,2) NULL,'
       'short_ratio DECIMAL(15,2) NULL,'
       'dividend_yield DECIMAL(15,2) NULL,'
       'quote0 DECIMAL(10,2) NULL,'
       'quote20m DECIMAL(10,2) NULL,'
       'quote7 DECIMAL(10,2) NULL,'
       'inx0 DECIMAL(10,2) NULL,'
       'inx20m DECIMAL(10,2) NULL,'
       'inx7 DECIMAL(10,2) NULL,'
       'PRIMARY KEY (id),'
       'UNIQUE INDEX id_UNIQUE (id ASC));')
#cursor.execute(sql)

sql = ('CREATE TABLE secTickers('
       'issuerTradingSymbol VARCHAR(10) NOT NULL,'
       'cik INT(15) NOT NULL,'
       'sik INT(15) NULL,'
       'companyName VARCHAR(255) NOT NULL,'
       'industry VARCHAR(255) NULL,'
       'updated DATETIME NULL,'
       'PRIMARY KEY (cik),'
       'INDEX issuerTradingSymbol (issuerTradingSymbol ASC),'
       'UNIQUE INDEX cik_UNIQUE (cik ASC));')
#cursor.execute(sql)

db.close()
