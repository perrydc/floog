# secIndex.py
# feeds from: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent
# optional params: &output=atom &count=100 &start=0 &CIK=IBM &type=3 &company=berkshire 
# &owner=exclude (removes form 3,4,5) &dateb=
import untangle, re, s, pymysql, datetime, pytz
from subprocess import Popen, PIPE, STDOUT
from dateutil import parser

recentIds = [] #removes entries with duplicate IDs
sql = ''
commands = []
now = str(datetime.datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'))
num = str(40)

db = pymysql.connect(host=s.host, port=3306, user=s.user, passwd=s.passwd, db=s.db)
cursor = db.cursor()
cursor.execute("SELECT * FROM secIndex ORDER BY updated DESC LIMIT 0," + num + ";")
rows = cursor.fetchall()
if(rows):
    for row in rows:
        recentIds.append(row[0])

url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&count=' + num + '&output=atom'
obj = untangle.parse(url)
for entry in obj.feed.entry:
    id = entry.id.cdata #this is the same for issuer and filer of form 4
    title = entry.title.cdata
    try:
        filerType = re.search(r'\((Issuer|Filer|Reporting|Subject|Filed By|Securitizer|Depositor)\)', title, flags=re.IGNORECASE).group(1)
    except(AttributeError):
        print(title, 'failed with attribution error.')
    form = entry.category['term']
    if(filerType == 'Reporting' and (form == '3' or form == '3/A' or form == '4' or form == '4/A' or form == '5' or form == '5/A')):
        #print("\n\n form4s from insiders:\n" + entry.id.cdata)
        pass
    elif(id in recentIds):
        #print("\n\n dupes within atom feed:\n" + entry.id.cdata)
        pass
    else:
        #print("\n\n valid to add to db:\n" + entry.id.cdata)
        recentIds.append(id)
        cik = re.search(r'\((\d{10})\)',title).group(1)
        updated = str(parser.parse(entry.updated.cdata).strftime('%Y-%m-%d %H:%M:%S'))

        sql += ('INSERT INTO secIndex(id,cik,form,title,link,timestamp,updated) VALUES ("'
               + id + '","'
               + cik + '","'
               + form + '","'
               + title + '","'
               + entry.link['href'] + '","'
               + now + '","'
               + updated + '");\n')

        cursor.execute("SELECT issuerTradingSymbol FROM secTickers WHERE cik = " + cik + ";")
        rows = cursor.fetchone()
        if(rows):
            ticker = rows[0]
            sp = "~/anaconda3/bin/python3 ~/floog/quote0.py " + id + " " + ticker + " >> ~/floog/log.txt 2>&1;"
            commands.append(sp)
        else:
            ticker = "NoMatch"
            #print(cik + ': ' + ticker)
        
        if(form == '3' or form == '3/A' or form == '4' or form == '4/A' or form == '5' or form == '5/A'):
            txtUrl = re.sub(r'-index.htm', r'.txt', entry.link['href'])
            sp = "~/anaconda3/bin/python3 ~/floog/secOwnership.py " + id + " " + txtUrl + " " + ticker + " >> ~/floog/log.txt 2>&1;"
            commands.append(sp)

if(sql):
    #print(sql)
    cursor.execute(sql)
    if(commands):
        processes = [Popen(cmd, shell=True, stdout=PIPE) for cmd in commands]
        for p in processes: 
            #p.wait() #need this if you don't have any of the below (runs the process)
            stdout = p.communicate()
            #print(stdout)    
        
db.close()