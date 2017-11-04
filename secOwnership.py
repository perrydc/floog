#secOwnership.py
import requests, untangle, re, s, pymysql, sys, subprocess, datetime, pytz

id = sys.argv[1]
link = sys.argv[2]
tickerGuess = sys.argv[3]

# UNCOMMENT BELOW FOR DEBUGGING
#import random
#id = 'test' + str(random.randint(0,1000))
#link = 'https://www.sec.gov/Archives/edgar/data/1477246/000124915517000058/0001249155-17-000058.txt'
#tickerGuess = 'SANW'
#u = 'http://www.sec.gov/Archives/edgar/data/1308547/000120919117048674/0001209191-17-048674-index.htm'
#link = re.sub(r'-index.htm', r'.txt', u)

now = str(datetime.datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'))
#print(now,tickerGuess)

db = pymysql.connect(host=s.host, port=3306, user=s.user, passwd=s.passwd, db=s.db)
cursor = db.cursor()

txtStr = str(requests.get(link).content)
xml = re.compile(r'\?>\\n(.*?)\\n</XML>').search(txtStr).group(1)
root = untangle.parse(xml)
issuerTradingSymbol = re.match(r'[A-Z]+',root.ownershipDocument.issuer.issuerTradingSymbol.cdata, re.IGNORECASE).group(0) #SRPT
if issuerTradingSymbol == tickerGuess:
    pass
elif tickerGuess == 'NoMatch':
    sp = "~/anaconda3/bin/python3 ~/sec/updateTicker.py " + issuerTradingSymbol + " >> ~/sec/log.txt 2>&1"
    subprocess.run([sp], stdout=subprocess.PIPE, shell=True)
    sp = "~/anaconda3/bin/python3 ~/sec/quote0.py " + id + " " + issuerTradingSymbol + " >> ~/sec/log.txt 2>&1"
    subprocess.run([sp], stdout=subprocess.PIPE, shell=True)
else:
    sp = "~/anaconda3/bin/python3 ~/sec/updateTicker.py " + issuerTradingSymbol + " >> ~/sec/log.txt 2>&1"
    subprocess.run([sp], stdout=subprocess.PIPE, shell=True)
    #but really it should update quote0 also

documentType = root.ownershipDocument.documentType.cdata #4
periodOfReport = root.ownershipDocument.periodOfReport.cdata #2017-07-20
notSubjectToSection16 = 0
if 'notSubjectToSection16' in dir(root.ownershipDocument):
    notSubjectToSection16 = root.ownershipDocument.notSubjectToSection16.cdata #0
    if notSubjectToSection16 == 'false':
        notSubjectToSection16 = 0
    elif notSubjectToSection16 == 'true':
        notSubjectToSection16 = 1
issuerCik = root.ownershipDocument.issuer.issuerCik.cdata #0000873303
issuerName = root.ownershipDocument.issuer.issuerName.cdata #Sarepta Therapeutics, Inc.
rptOwnerCik = ''

for owner in root.ownershipDocument.reportingOwner:
    if 'rptOwnerCik' in dir(owner.reportingOwnerId):
        rptOwnerCik = owner.reportingOwnerId.rptOwnerCik.cdata #0001511034
    rptOwnerName = owner.reportingOwnerId.rptOwnerName.cdata #Mahatme Sandesh
    rptOwnerStreet1 = owner.reportingOwnerAddress.rptOwnerStreet1.cdata #215 FIRST STREET, SUITE 415
    rptOwnerCity = owner.reportingOwnerAddress.rptOwnerCity.cdata #CAMBRIDGE
    rptOwnerState = owner.reportingOwnerAddress.rptOwnerState.cdata #MA
    rptOwnerZipCode = owner.reportingOwnerAddress.rptOwnerZipCode.cdata #02142

isDirector = 0
isOfficer = 0
isTenPercentOwner = 0
isOther = 0
officerTitle = ''
if 'reportingOwnerRelationship' in dir(root.ownershipDocument):
    if 'isDirector' in dir(root.ownershipDocument.reportingOwnerRelationship):
        isDirector = root.ownershipDocument.reportingOwner.reportingOwnerRelationship.isDirector.cdata #0
    if 'isOfficer' in dir(root.ownershipDocument.reportingOwnerRelationship):
        isOfficer = root.ownershipDocument.reportingOwner.reportingOwnerRelationship.isOfficer.cdata #1
    if 'isTenPercentOwner' in dir(root.ownershipDocument.reportingOwnerRelationship):
        isTenPercentOwner = root.ownershipDocument.reportingOwner.reportingOwnerRelationship.isTenPercentOwner.cdata #0
    if 'isOther' in dir(root.ownershipDocument.reportingOwnerRelationship):
        isOther = root.ownershipDocument.reportingOwner.reportingOwnerRelationship.isOther.cdata #0
    if 'officerTitle' in dir(root.ownershipDocument.reportingOwnerRelationship):
        officerTitle = root.ownershipDocument.reportingOwner.reportingOwnerRelationship.officerTitle.cdata #EVP, CFO & CBO

nonDerivativeValue = 0
derivativeValue = 0
transactionList = []
sharesOwnedFollowingTransaction = 0
directOrIndirectOwnership = ''

if 'nonDerivativeTable' in dir(root.ownershipDocument):
    if 'nonDerivativeTransaction' in dir(root.ownershipDocument.nonDerivativeTable):
        for trans in root.ownershipDocument.nonDerivativeTable.nonDerivativeTransaction:
            transactionList.append(trans.transactionCoding.transactionCode.cdata)
            transactionAcquiredDisposedCode = trans.transactionAmounts.transactionAcquiredDisposedCode.value.cdata #A
            transactionShares = trans.transactionAmounts.transactionShares.value.cdata #9375
            if 'value' in dir(trans.transactionAmounts.transactionPricePerShare):
                transactionPricePerShare = trans.transactionAmounts.transactionPricePerShare.value.cdata #13.71
                value = float(transactionShares) * float(transactionPricePerShare)
                if transactionAcquiredDisposedCode == 'A':
                    nonDerivativeValue += value
                else:
                    nonDerivativeValue -= value

            #take last value
            sharesOwnedFollowingTransaction = trans.postTransactionAmounts.sharesOwnedFollowingTransaction.value.cdata #41736
            directOrIndirectOwnership = trans.ownershipNature.directOrIndirectOwnership.value.cdata #D
    elif 'nonDerivativeHolding' in dir(root.ownershipDocument.nonDerivativeTable):
        for hold in root.ownershipDocument.nonDerivativeTable.nonDerivativeHolding:
            sharesOwnedFollowingTransaction = hold.postTransactionAmounts.sharesOwnedFollowingTransaction.value.cdata

if 'derivativeTable' in dir(root.ownershipDocument):
    if 'derivativeTransaction' in dir(root.ownershipDocument.derivativeTable):
        for trans in root.ownershipDocument.derivativeTable.derivativeTransaction:
            transactionList.append(trans.transactionCoding.transactionCode.cdata)
            transactionAcquiredDisposedCode = trans.transactionAmounts.transactionAcquiredDisposedCode.value.cdata #A
            transactionShares = trans.transactionAmounts.transactionShares.value.cdata #9375
            if 'value' in dir(trans.transactionAmounts.transactionPricePerShare):
                transactionPricePerShare = trans.transactionAmounts.transactionPricePerShare.value.cdata #13.71
                value = float(transactionShares) * float(transactionPricePerShare)
                if transactionAcquiredDisposedCode == 'A':
                    derivativeValue += value
                else:
                    derivativeValue -= value

            #take last value
            sharesOwnedFollowingTransaction = trans.postTransactionAmounts.sharesOwnedFollowingTransaction.value.cdata #41736
            directOrIndirectOwnership = trans.ownershipNature.directOrIndirectOwnership.value.cdata #D
transactionList = list(sorted(set(transactionList)))
transactionCode = ''.join(transactionList)

footnote = ''
if 'footnotes' in dir(root.ownershipDocument):
    if 'footnote' in dir(root.ownershipDocument.footnotes):
        for fn in root.ownershipDocument.footnotes.footnote:
            footnote += fn.cdata

sql = ('INSERT INTO secOwnership SET '
       'id = "' + id + '", '
       'transactionCode = "' + transactionCode + '", '
       'documentType = "' + documentType + '", '
       'periodOfReport = "' + periodOfReport + '", '
       'notSubjectToSection16 = "' + str(notSubjectToSection16) + '", '
       'issuerCik = "' + issuerCik + '", '
       'issuerName = "' + issuerName + '", '
       'issuerTradingSymbol = "' + issuerTradingSymbol + '", '
       'rptOwnerCik = "' + rptOwnerCik + '", '
       'rptOwnerName = "' + rptOwnerName + '", '
       'rptOwnerStreet1 = "' + rptOwnerStreet1 + '", '
       'rptOwnerCity = "' + rptOwnerCity + '", '
       'rptOwnerState = "' + rptOwnerState + '", '
       'rptOwnerZipCode = "' + rptOwnerZipCode + '", '
       'isDirector = "' + str(isDirector) + '", '
       'isOfficer = "' + str(isOfficer) + '", '
       'isTenPercentOwner = "' + str(isTenPercentOwner) + '", '
       'isOther = "' + str(isOther) + '", '
       'officerTitle = "' + officerTitle + '", '
       'nonDerivativeValue = "' + str(nonDerivativeValue) + '", '
       'derivativeValue = "' + str(derivativeValue) + '", '
       'sharesOwnedFollowingTransaction = "' + str(sharesOwnedFollowingTransaction) + '", '
       'directOrIndirectOwnership = "' + directOrIndirectOwnership + '", '
       'link = "' + str(link) + '", '
       'timestamp = "' + now + '", '
       'footnote = "%s"')
cursor.execute(sql, (footnote))
db.close()