# encoding: utf-8

import LocalPaths
reload(LocalPaths)

from libDatabase import GetDataFolder
from libDatabase import GetDOD
from libConstants import cnListNameECL
from libConstants import cnStatsList
from E3MailingList import GetList
from datetime import date
from datetime import timedelta
import random
from E3HTML import UpdateCacheItem
from libConstants import cnFirstDate
from libConstants import cnLastDate
from E3Messages import CreateCountList
from libDate import MonthName
from libEmail import SendHTMLEmail

from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import Axis

def GetFullMemberCount(objHere):
    dictResult = {}
    for objBatch in GetDataFolder(objHere, "E3ListStat").objectValues("Folder"):
        for objListStat in objBatch.objectValues("E3ListStat"):
            if "Live" in objListStat.propertyIds() and objListStat.Live:
                dictResult[objListStat.GetDateOfCount()] = objListStat.Live
    lstDates = dictResult.keys()
    lstDates.sort()
    dtmFirstDate = lstDates[0]
    dtmLastDate = date.today()
    dtmDate = dtmFirstDate
    intLive = dictResult[dtmFirstDate]
    deltaDay = timedelta(days=1)
    while dtmDate < dtmLastDate:
        dtmDate += deltaDay
        if dictResult.has_key(dtmDate):
            intLive = dictResult[dtmDate]
        else:
            dictResult[dtmDate] = intLive
    return (dictResult, intLive)

def GetLiveForPeriod(dictMemberCount, dtmStart, dtmFinish):
    lstResult = []
    dtmDate = dtmStart
    deltaDay = timedelta(days=1)
    while dtmDate <= dtmFinish:
        lstResult.append(dictMemberCount[dtmDate])
        dtmDate += deltaDay
    return lstResult

def SameDate(dtmOne, dtmTwo):
    if dtmOne.year == dtmTwo.year and dtmOne.month == dtmTwo.month and dtmOne.day == dtmTwo.day:
        return True
    return False

def JustDate(dtmDate):
    dtmResult = date(year = dtmDate.year, month = dtmDate.month, day = dtmDate.day)
    return dtmResult

def During(dtmDate, dtmStart, dtmEnd):
    dtmDate = JustDate(dtmDate)
    dtmStart = JustDate(dtmStart)
    dtmEnd = JustDate(dtmEnd)
#    print "%s in [%s .. %s]?" % (dtmDate, dtmStart, dtmEnd)
    if dtmDate < dtmStart:
        return False
    if dtmDate > dtmEnd:
        return False
    return True

def GetYesterdaysActivity(objHere):
    dtmYesterday = date.today() - timedelta(days = 1)
    dtm31DaysAgo = date.today() - timedelta(days = 31)
    lstJoined = []
    lstFirstPayment = []
    lstExpired = []
    lstRenewed = []
    lstJoined30Days = []
    lstExpired30Days = []
    lstFirstPayment30Days = []
    lstRenewed30Days = []
    for objBatch in GetDataFolder(objHere, "E3Member").objectValues('Folder'):
        for objMember in objBatch.objectValues("E3Member"):
            if SameDate(objMember.GetCreatedDate(), dtmYesterday):
                lstJoined.append(objMember)
            if During(objMember.GetCreatedDate(), dtm31DaysAgo, dtmYesterday):
                lstJoined30Days.append(objMember)
            for objEvent in objMember.Historic.objectValues("E3Event"):
                if objEvent.EventType == "ExpiryMessageSent":
                    if SameDate(objEvent.GetDate(), dtmYesterday):
                        lstExpired.append(objMember)
                    if During(objEvent.GetDate(), dtm31DaysAgo, dtmYesterday):
                        lstExpired30Days.append(objMember)
                 
            for objPayment in objMember.Historic.objectValues("E3Payment"):
                if SameDate(objPayment.GetDate(), dtmYesterday):
                    if len(objMember.Historic.objectValues("E3Payment")) > 1:
                        lstRenewed.append(objMember)
                    else:
                        lstFirstPayment.append(objMember)
                if During(objPayment.GetDate(), dtm31DaysAgo, dtmYesterday):
                    if len(objMember.Historic.objectValues("E3Payment")) > 1:
                        lstRenewed30Days.append(objMember)
                    else:
                        lstFirstPayment30Days.append(objMember)
    return (lstJoined, lstExpired, lstFirstPayment, lstRenewed, 
            len(lstJoined30Days), len(lstExpired30Days), len(lstFirstPayment30Days), len(lstRenewed30Days))

def ShowList(strTitle, lstMembers):
    strResult = ""
    if lstMembers:
        for objMember in lstMembers:
            strResult += "<li>%s: %s (%s payment(s) total)</li>" % (objMember.id, objMember.EmailDeliveryAddress,
                            len(objMember.Historic.objectValues("E3Payment")))
        strResult = """<p>%s, yesterday:</p>
        <ol>
        %s
        </ol>""" % (strTitle, strResult)

    return strResult

def GetDailyEmail(objHere):
    # Figure: current number of members
    # Get latest stats record
    (dictMemberCount, intCurrentNumberOfMembers) = GetFullMemberCount(objHere)
    strResult = "<p>Current number of members: %s</p>\n" % intCurrentNumberOfMembers

    dtmToday = date.today()
    dtmLastYear = dtmToday - timedelta(days = 365)
    lstDataCurrent = GetLiveForPeriod(dictMemberCount, dtmToday - timedelta(days = 59), dtmToday)
    lstDataLastYear = GetLiveForPeriod(dictMemberCount, dtmLastYear - timedelta(days = 59), dtmLastYear)

#    print lstDataCurrent
#    print lstDataLastYear

# 700 x 420
    objChart = SimpleLineChart(700, 420, y_range=[300, 800])
    objChart.add_data(lstDataCurrent)
    objChart.add_data(lstDataLastYear)
    objChart.set_colours(['14c85c', 'a7ffca'])
    strResult += """
<fieldset>
    <legend>Live members last 60 days, compared with same period last year</legend>
    <img src="%s" width="700" height="420">
</fieldset>""" % objChart.get_url()

    (lstJoined, lstExpired, lstFirstPayment, lstRenewed, 
     intJoined30Days, intExpired30Days, intFirstPayment30Days, intRenewed30Days
     ) = GetYesterdaysActivity(objHere)

    strResult += ShowList("New members", lstJoined)
    strResult += ShowList("Expired members", lstExpired)
    strResult += ShowList("First payments", lstFirstPayment)
    strResult += ShowList("Renewals", lstRenewed)
    strResult += """<p>Over the past 30 days</p>
    <ul>
        <li>New members: %s</li>
        <li>Expired members: %s</li>
        <li>First payments: %s</li>
        <li>Renewals: %s</li>
    </ul>
    """ % (intJoined30Days, intExpired30Days, intFirstPayment30Days, intRenewed30Days)

    return strResult

def ShowDailyEmail(objHere):
    strResult = GetDailyEmail(objHere)
    return strResult

def SendDailyEmail(objHere):
    strHTML = GetDailyEmail(objHere)
    SendHTMLEmail(objHere, strHTML, "Daily ECL stats", "coen@coachcoen.com")

def AddConversionData(dictData, dtmDate):
    if dictData.has_key(dtmDate):
        dictData[dtmDate] += 1
    else:
        dictData[dtmDate] = 1
    return dictData

def GetConversionData(objHere):
    dictPaid = {}
    dictExpired = {}
    for objBatch in GetDataFolder(objHere, "E3Member").objectValues('Folder'):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.HasConfirmedEmailAddress:
                for objEvent in objMember.Historic.objectValues("E3Event"):
                    if objEvent.EventType == "ExpiryMessageSent":
                        dictExpired = AddConversionData(dictExpired, objEvent.GetDate())
                for objPayment in objMember.Historic.objectValues("E3Payment"):
                    dictPaid = AddConversionData(dictPaid, objPayment.GetDate())
    return (dictPaid, dictExpired)

def GetConversionRates(objHere, intDays):
    dtmStart = date.today() - timedelta(days = intDays)
    dictPaymentCounts = {}
    dictExpiryCounts = {}
    for intI in range(0, 20):
        dictPaymentCounts[intI] = 0
        dictExpiryCounts[intI] = 0
    for objBatch in GetDataFolder(objHere, "E3Member").objectValues('Folder'):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.HasConfirmedEmailAddress:
                for objEvent in objMember.Historic.objectValues("E3Event"):
                    if objEvent.EventType == "ExpiryMessageSent" and objEvent.GetDate() >= dtmStart:
                        intPaymentCount = len(objMember.Historic.objectValues("E3Payment"))
                        dictExpiryCounts[intPaymentCount] += 1
                for objPayment in objMember.Historic.objectValues("E3Payment"):
                    if objPayment.GetDate() >= dtmStart:
                        intPaymentCount = len(objMember.Historic.objectValues("E3Payment")) - 1
                        dictPaymentCounts[intPaymentCount] += 1

#    print dictPaymentCounts
#    print dictExpiryCounts
    lstCounts = []
    intTotalPayments = 0
    intTotalExpiry = 0
    for intI in range(0, 20):
        intExpiry = dictExpiryCounts[intI]
        intPayments = dictPaymentCounts[intI]
        intTotal = intExpiry + intPayments
        if intTotal:
            lstCounts.append((intI, int((100 * intPayments) / intTotal), intPayments, intTotal))
        intTotalPayments += intPayments
        intTotalExpiry += intExpiry

    strTable = """<table border="0">
    """
    for (intPeriod, intConversionRate, intPayments, intTotal) in lstCounts:
        strTable += """<tr>
        <td>%s:</td>
        <td>%s</td>
        <td>(%s %%)</td>
        <td>out of %s</td>
    </tr>
    """ % (intPeriod, intPayments, intConversionRate, intTotal)
    strTable += "</table>\n"
    strTable += "<p>Total %s payments (<b>%s %%</b>) out of %s</p>\n" % \
        (intTotalPayments, int((100 * intTotalPayments) / (intTotalPayments + intTotalExpiry)), intTotalPayments + intTotalExpiry)

    return strTable

def GetWeeklyEmail(objHere):
    # For each available date, get number of expiries plus number of payments
    # By week: Add up number of expiries, number of payments, then work out:
    # (payments) / (expiries + payments) * 100 = conversion rate
    (dictPaid, dictExpired) = GetConversionData(objHere)
    dtmToday = date.today()
    dtmDate = dtmToday - timedelta(days = 730)
    while dtmDate.weekday():
        dtmDate = dtmDate - timedelta(days = 1)

    dictWeeklyResult = {}
    lstData = []
    lstAverage = []

    intWeeks = 0
    intTotal = 0

    while dtmDate + timedelta(days = 6) < dtmToday:
        intExpired = 0
        intPaid = 0
        for intI in range (0, 7):
            dtmI = dtmDate + timedelta(days = intI)
            if dictPaid.has_key(dtmI):
                intPaid += dictPaid[dtmI]
            if dictExpired.has_key(dtmI):
                intExpired += dictExpired[dtmI]
        if intExpired + intPaid:
            intConversionRate = int((100*intPaid) / (intExpired + intPaid))
        else:
            intConversionRate = 0
        dictWeeklyResult[dtmDate] = intConversionRate
        lstData.append(intConversionRate)
        dtmDate += timedelta(days = 7)

        # Keep track of average:
        intWeeks += 1
        intTotal += intConversionRate
        lstAverage.append(intTotal / intWeeks)

    objChart = SimpleLineChart(700, 420, y_range=[0, 100])
    objChart.add_data(lstData)
    objChart.add_data(lstAverage)
    objChart.set_colours(['14c85c', 'a7ffca'])
    strResult = """
<fieldset>
    <legend>Conversion rate over last 2 years</legend>
    <img src="%s" width="700" height="420">
</fieldset>""" % objChart.get_url()

    strConversionTable = GetConversionRates(objHere, 60)
    strResult += """
<fieldset>
    <legend>Conversion rate over last 60 days by number of past payments</legend>
    %s
</fieldset>""" % strConversionTable

    strConversionTable = GetConversionRates(objHere, 365)
    strResult += """
<fieldset>
    <legend>Conversion rate over last year by number of past payments</legend>
    %s
</fieldset>""" % strConversionTable

    return strResult

def ShowWeeklyEmail(objHere):
    strResult = GetWeeklyEmail(objHere)
    return strResult

def SendWeeklyEmail(objHere):
    strHTML = GetWeeklyEmail(objHere)
    SendHTMLEmail(objHere, strHTML, "Weekly ECL stats", "coen@coachcoen.com")

def GetTables(objHere):
    dictResult = {}
    intFirstYear = 2000
    intLastYear = 1900
    for intYear in range(1998, 2020):
        dictResult[intYear] = {}
        for intMonth in range(1, 13):
            dictResult[intYear][intMonth] = {'MembersAtStart': 0,
                'Payments': 0,
                'NewMembers': 0}
    objStats = GetDataFolder(objHere, 'E3ListStat')
    for objBatch in objStats.objectValues('Folder'):
        for objStat in objBatch.objectValues('E3ListStat'):
            dtmDate = objStat.GetDateOfCount()
            intDate = dtmDate.day
            intMonth = dtmDate.month
            intYear = dtmDate.year
            if intYear > intLastYear:
                intLastYear = intYear
            if intYear < intFirstYear:
                intFirstYear = intYear
            if objStat.hasProperty("PaymentYesterday"):
                dictResult[intYear][intMonth]['Payments'] += objStat.PaymentYesterday
            if objStat.hasProperty("JoinedYesterday"):
                dictResult[intYear][intMonth]['NewMembers'] += objStat.JoinedYesterday
            if intDate == 1:
                if objStat.hasProperty("Live"):
                    if objStat.Live:
                        dictResult[intYear][intMonth]['MembersAtStart'] = objStat.Live
                elif objStat.hasProperty("Count"):
                    if objStat.Count:
                        dictResult[intYear][intMonth]['MembersAtStart'] = objStat.Count
    return (intFirstYear, intLastYear, dictResult)

def OneTableLine(intMonth, intMembersAtStart, intMembersDelta, intPayments, intNewMembers):
    if intMembersAtStart or intMembersDelta or intPayments or intNewMembers:
        return """
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>""" % (MonthName(intMonth),
        intMembersAtStart,
        intMembersDelta,
        intPayments,
        intNewMembers)
    return ""

def ShowTables(objHere):
    # For each month since we've got statistics, show:
    #   Number of members at start of the month
    #   Increase or decrease in members
    #   Number of payments during the month
    #   Number of new members during the month
    (intFirstYear, intLastYear, dictResult) = GetTables(objHere)
    strResult = """
<table>
"""
    for intYear in range(intFirstYear, intLastYear + 1):
        strResult += """
    <tr>
        <td>%s</td>
        <td>Members at 1st</td>
        <td>Increase</td>
        <td>Payments</td>
        <td>New members</td>
    </tr>""" % intYear

        for intMonth in range(1, 13):
            intMembersAtStart = dictResult[intYear][intMonth]['MembersAtStart']
            intNextMonth = intMonth + 1
            intNextYear = intYear
            if intNextMonth > 12:
                intNextMonth = 1
                intNextYear += 1
            intMembersAtEnd = dictResult[intNextYear][intNextMonth]['MembersAtStart']
            if intMembersAtStart and intMembersAtEnd:
                intMembersDelta = intMembersAtEnd - intMembersAtStart
            else:
                intMembersDelta = 0
            strResult += OneTableLine(intMonth, intMembersAtStart, intMembersDelta, dictResult[intYear][intMonth]['Payments'], dictResult[intYear][intMonth]['NewMembers'])
    strResult += "</table>\n"
    return strResult

def MembershipProfile(objHere):
    dictResult = {}
    for intI in range(0, 20):
        dictResult[intI] = 0
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            intPayments = len(objMember.Historic.objectValues("E3Payment"))
            dictResult[intPayments] += 1
    strResult = """
<table>
    <tr>
        <td colspan="2">Membership profile</td>
    </tr>
    <tr>
        <td>Years membership</td>
        <td>Number of members</td>
    </tr>
"""
    for intI in range(0, 20):
        strResult += "<tr><td>%s</td><td>%s</td></tr>\n" % (intI, dictResult[intI])
    strResult += "</table>\n"
    return strResult

def GetConversionRate(dictPayment, dictExpired, intFirstYear, intLastYear):
    dictResult = {}
    for intYear in range(intFirstYear, intLastYear + 1):
        for intMonth in range(1, 13):
            lstKey = (intYear, intMonth)
            if dictPayment.has_key(lstKey) and dictExpired.has_key(lstKey):
                intPaid = dictPayment[lstKey]
                intExpired = dictExpired[lstKey]
                if (intExpired + intPaid):
                    intRate = 100 * intPaid / (intExpired + intPaid)
                    dictResult[lstKey] = intRate
    return dictResult

def BuildTables(dictData):
# Format: dictData[strItem][dtmDate]

    # Add up by month
    dictResult = {}
    dtmFirstDate = date(3000, 1, 1)
    dtmLastDate = date(1, 1, 1)
#    print dictData.keys()
    for strItem in dictData.keys():
        dictResult[strItem] = {}
        for dtmDate in dictData[strItem].keys():
            if dtmDate < dtmFirstDate:
                dtmFirstDate = dtmDate
            if dtmDate > dtmLastDate:
                dtmLastDate = dtmDate
            lstKey = (dtmDate.year, dtmDate.month)
#            print lstKey
            if not dictResult[strItem].has_key(lstKey):
                dictResult[strItem][lstKey] = 0
            dictResult[strItem][lstKey] += dictData[strItem][dtmDate]

#    print dictResult
    # Create the table
#    print "First date: %s" % dtmFirstDate
#    print "Last date: %s" % dtmLastDate

    intFirstYear = 2003
    intLastYear = dtmLastDate.year

    dictResult['ConversionRateFirst'] = GetConversionRate(dictResult['FirstPaymentYesterday'], dictResult['TrialExpiredYesterday'], intFirstYear, intLastYear)

    dictResult['ConversionRateRenewal'] = GetConversionRate(dictResult['RenewalYesterday'], dictResult['ExpiredYesterday'], intFirstYear, intLastYear)

    strResult = ""
    for strItem in ('JoinedYesterday', 'ConversionRateFirst', 'ConversionRateRenewal', 'FirstPaymentYesterday', 'TrialExpiredYesterday', 'RenewalYesterday', 'ExpiredYesterday', 'WarningSentYesterday', 'BonusSentYesterday'):
        strResult += """
<table border="1">
    <tr>
        <td>%s</td>
""" % strItem

        for intMonth in range(1, 13):
            strResult += "<td>%s</td>\n" % intMonth
        if 'Rate' in strItem:
            strResult += "<td>Avg</td></tr>"
        else:
            strResult += "<td>Totals</td></tr>"
        for intYear in range(intFirstYear, intLastYear + 1):
            strResult += "<tr><td>%s</td>" % intYear
            intYearTotal = 0
            for intMonth in range(1, 13):
                if dictResult[strItem].has_key((intYear, intMonth)):
                    intCount = dictResult[strItem][(intYear, intMonth)]
                    strResult += '<td>%s</td>\n' % intCount
                    intYearTotal += intCount
                else:
                    strResult += '<td>&nbsp;</td>'
            if 'Rate' in strItem:
                intYearTotal = intYearTotal / 12
            strResult += "<td>%s</td></tr>\n" % intYearTotal
        strResult += "</table><br><br>"

    return strResult

def ConvertToDateOnly(dtmDate):
    dtmResult = date(year=dtmDate.year, month=dtmDate.month, day=dtmDate.day)
    return dtmResult

def AddCount(dictResult, dtmDate):
    dtmDate = ConvertToDateOnly(dtmDate)
    if not dictResult.has_key(dtmDate):
        dictResult[dtmDate] = 0
    dictResult[dtmDate] += 1

def GetMailmanPeriods(objMember):
    dtmFirstStartDate = cnLastDate
    dtmLastEndDate = cnFirstDate
    for objPeriod in objMember.FromMailman.objectValues():
        if objPeriod.GetStartDate() < dtmFirstStartDate:
            dtmFirstStartDate = objPeriod.GetStartDate()
        if objPeriod.GetEndDate() > dtmLastEndDate:
            dtmLastEndDate = objPeriod.GetEndDate()
    return (dtmFirstStartDate, dtmLastEndDate)

def GetLastExpiryDate(objMember):
    dtmResult = cnFirstDate
    for objEvent in objMember.Historic.objectValues('E3Event'):
        if objEvent.EventType == 'Expiry' or objEvent.EventType == "ExpiryMessageSent":
            if objEvent.GetDate() > dtmResult:
                dtmResult = objEvent.GetDate()
    return dtmResult

def ReportStats(strResultFile, lstResults):
    fileResult = open(strResultFile, 'w')
    for (strDescription, dictStats) in lstResults:
        fileResult.write("Result set: %s\n" % strDescription)
        lstDates = dictStats.keys()
        lstDates.sort()

        for dtmDate in lstDates:
            fileResult.write("%s: %s\n" % (dtmDate, dictStats[dtmDate]))
    fileResult.close()

def GenerateOldStats(objContext):
# What statistics can I create, based on date stored in the old system (even pre-Zope)?
# For each member I can see when they joined, from a certain date
# I can see when payments were made
# Expiries
    dictJoined = {}
    dictFirstPayment = {}
    dictRenewal = {}
    dictExpired = {}
    dictTrialExpired = {}
    dictBonusSent = {}
    dictWarningSent = {}
    objMembers = GetDataFolder(objContext, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not objMember.ParkingMember():
                if "FromMailman" in objMember.objectIds():
                    (dtmFirstStartDate, dtmLastEndDate) = GetMailmanPeriods(objMember)
                else:
                    dtmFirstStartDate = objMember.GetCreatedDate()
    #                print dtmFirstDate
                    dtmLastEndDate = None
                AddCount(dictJoined, dtmFirstStartDate)

                if objMember.MembershipType == "None":
                    dtmLastExpiryDate = GetLastExpiryDate(objMember)
                    if dtmLastEndDate:
                        if dtmLastExpiryDate > dtmLastEndDate:
                            dtmLastEndDate = dtmLastExpiryDate
                    else:
                        dtmLastEndDate = dtmLastExpiryDate
                    if objMember.Historic.objectValues('E3Payment'):
                        AddCount(dictExpired, dtmLastEndDate)
#                        if dtmLastEndDate.year == 2007:
#                            print "Expired: ", dtmLastEndDate
                    else:
                        AddCount(dictTrialExpired, dtmLastEndDate)
#                        if dtmLastEndDate.year == 2007:
#                            print "Trial expired: ", dtmLastEndDate

                lstPayments = []
                for objPayment in objMember.Historic.objectValues('E3Payment'):
                    lstPayments.append(objPayment.GetDate())
                    lstPayments.sort()
    #                print lstPayments
                    if lstPayments:
                        AddCount(dictFirstPayment, lstPayments[0])
                        for dtmPaymentDate in lstPayments[1:]:
                            AddCount(dictRenewal, dtmPaymentDate)

                for objEvent in objMember.Historic.objectValues("E3Event"):
                    if objEvent.EventType == "BonusSent":
                        AddCount(dictBonusSent, objEvent.GetDate())
                    elif objEvent.EventType == "WarningSent":
                        AddCount(dictWarningSent, objEvent.GetDate())

#    strResultFile = "/var2/lib/Zope/Statistics/OldStats.txt"
#    ReportStats(strResultFile, (('Joined', dictJoined), ('Payment', dictPayment), ('Expired', dictExpired)))
    return (dictJoined, dictFirstPayment, dictRenewal, dictTrialExpired, dictExpired, dictWarningSent, dictBonusSent)

def LoadCurrentStats(objHere):
    dictResult = {}
    for objBatch in GetDataFolder(objHere, "E3ListStat").objectValues("Folder"):
        for objListStat in objBatch.objectValues("E3ListStat"):
            dictResult[objListStat.GetDateOfCount()] = objListStat
    return dictResult

def UpdateOneOldStats(objHere, dictCurrentStats, strItem, dtmDate, intCount, dodListStat, blnOverwrite):
    dtmTomorrow = dtmDate + timedelta(days=1)
    if not dictCurrentStats.has_key(dtmTomorrow):
        objListStat = dodListStat.NewObject()
        objListStat.SetDateOfCount(dtmTomorrow)
    else:
        objListStat = dictCurrentStats[dtmTomorrow]

    strItem = strItem + "Yesterday"
    if not objListStat.hasProperty(strItem):
        objListStat.manage_addProperty(strItem, intCount, 'int')
    elif blnOverwrite:
        objListStat.manage_changeProperties({strItem: intCount})

#JoinedYesterday, WarningSentYesterday, BonusSentYesterday, PaymentYesterday, ExpiredYesterday,

def UpdateOldStats(objHere, blnOverwrite = False):
    dodListStat = GetDOD(objHere, "E3ListStat")
    dictOldStats = {}
    (dictOldStats['Joined'], dictOldStats['FirstPayment'], dictOldStats['Renewal'], dictOldStats['TrialExpired'], dictOldStats['Expired'], dictOldStats['WarningSent'], dictOldStats['BonusSent']) = GenerateOldStats(objHere)

#    print dictOldStats['FirstPayment']
    dictCurrentStats = LoadCurrentStats(objHere)
    for strItem in dictOldStats.keys():
#        print strItem
        for dtmDate in dictOldStats[strItem]:
            UpdateOneOldStats(objHere, dictCurrentStats, strItem, dtmDate, dictOldStats[strItem][dtmDate], dodListStat, blnOverwrite)

def GenerateRandomStats(objContext):
    dtmDate = date.today() - timedelta(days=150)
    dictResult = {}
    for strResult in cnStatsList:
        dictResult[strResult] = random.randint(1, 500)
    dodListStat = GetDOD(objContext, 'E3ListStat')
    while dtmDate <= date.today():
        objListStat = dodListStat.NewObject()
        objListStat.SetDateOfCount(dtmDate)
        objListStat.SetStats(dictResult)
        dtmDate = dtmDate + timedelta(days = 1)
        for strItem in dictResult.keys():
            dictResult[strItem] += 10 - random.randint(1, 20)

def GatherStatsData(objContext, dtmDate, intDuration, dtmDateFrom = ""):
    dictResult = {}
    for strItem in cnStatsList:
        dictResult[strItem] = {}
    if dtmDateFrom:
        dtmStartDate = dtmDateFrom
    else:
        dtmStartDate = dtmDate - timedelta(days=intDuration)
    objStats = GetDataFolder(objContext, 'E3ListStat')
    for objBatch in objStats.objectValues('Folder'):
        for objStat in objBatch.objectValues('E3ListStat'):
            dtmDate = objStat.GetDateOfCount()
            if dtmDate >= dtmStartDate:
                print dtmDate
                for strItem in cnStatsList:
                    intResult = objStat.getProperty(strItem)
                    if not intResult:
                        intResult = 0
                    dictResult[strItem][dtmDate] = intResult
    return dictResult

def CreateOneGraph(strItem, dictData, dtmDate):
    lstData = []
    lstKeys = dictData.keys()
    lstKeys.sort()
    for dtmNumberDate in lstKeys:
        lstData.append(dictData[dtmNumberDate])
    clf()
    title("%s up to %s" % (strItem, dtmDate.strftime("%d/%m/%Y")))
    plot(lstData)
#    plot(lstKeys, lstData)
    strDate = dtmDate.strftime("%Y%m%d")
    fileGraph = open("/var/lib/zope/charts/chart%s-%s" % (strDate, strItem), "w")
    savefig(fileGraph)
    fileGraph.close()

def CreateGraphs(objContext):
    dtmDate = date.today()
    dictResult = GatherStatsData(objContext, dtmDate)
    for strItem in cnStatsList:
        CreateOneGraph(strItem, dictResult[strItem], dtmDate)

def GetMinValue(dictStats):
    intMinValue = 10000
    for dtmDate in dictStats.keys():
        if dictStats[dtmDate] and dictStats[dtmDate] < intMinValue:
            intMinValue = dictStats[dtmDate]
    return intMinValue

def SummariseByWeek(dictStats):
    dictResult = {}
    lstDates = dictStats.keys()
    lstDates.sort()
    intTotal = 0
    intToSave = 0
    blnStarted = False
    for dtmDate in lstDates:
        intTotal += dictStats[dtmDate]
        if dtmDate.weekday() == 6:
            if blnStarted:
                dictResult[dtmDate] = intTotal
            intTotal = 0
            blnStarted = True
    return dictResult

def CreateGraph(dictStats, strTitle, intHeight, intWidth, intSpacing, blnMarkers, blnByWeek = False):
    if blnByWeek:
        dictStats = SummariseByWeek(dictStats)

    lstDates = dictStats.keys()
    lstDates.sort()
    intMinValue = GetMinValue(dictStats)
    if blnMarkers:
        intMarkers = 1
    else:
        intMarkers = 0

    strPoints = ""
    for dtmDate in lstDates:
        if dictStats[dtmDate]:
            strPoints += "g.add('', %s);\n" % (dictStats[dtmDate] - intMinValue)

    strResult = """
<script type="text/javascript" src="/js/wz_jsgraphics.js"></script>
<script type="text/javascript" src="/js/line.js">

<!-- Line Graph script-By Balamurugan S http://www.sbmkpm.com/ //-->
<!-- Script featured/ available at Dynamic Drive code: http://www.dynamicdrive.com //-->

</script>

<div id="lineCanvas" style="margin-top: 15px; overflow: auto; position:relative;height:%spx;width:%spx;"></div>

<script type="text/javascript">
var g = new line_graph();
    %s
    g.render("lineCanvas", "%s", %s, %s, %s, %s);
</script>""" % ((intHeight + 40), intWidth, strPoints, strTitle, intMinValue, intHeight, intSpacing, intMarkers)
    return strResult

def CreateSmallGraph(dictStats, strTitle):
    return CreateGraph(dictStats, strTitle, 100, 150, 2, False)

def CreateLargeGraph(dictStats, strTitle):
    return """<fieldset>
        <legend>%s</legend>
        %s
    </fieldset>""" % (strTitle, CreateGraph(dictStats, "", 250, 860, 2, False))

def CreateWeeklyGraph(dictStats, strTitle):
    return """<fieldset>
        <legend>%s</legend>
        %s
    </fieldset>""" % (strTitle, CreateGraph(dictStats, strTitle, 250, 900, 14, False, True))

def CreateNarrowWeeklyGraph(dictStats, strTitle):
    return """<fieldset>
        <legend>%s</legend>
        %s
    </fieldset>""" % (strTitle, CreateGraph(dictStats, strTitle, 250, 900, 5, False, True))

def ShowTotalMembersGraph(objContext):
    dtmDate = date.today()
    dictResult = GatherStatsData(objContext, dtmDate, 60)
    strResult = CreateSmallGraph(dictResult['Live'], "Live members")
    return strResult

def SumResults(dictResult1, dictResult2):
    dictResult = {}
    for dtmDate in dictResult1.keys():
        dictResult[dtmDate] = dictResult1[dtmDate]
    for dtmDate in dictResult2.keys():
        if not dictResult.has_key(dtmDate):
            dictResult[dtmDate] = 0
        dictResult[dtmDate] += dictResult2[dtmDate]
    return dictResult

def GetRatio(dictPart, dictTotal):
    dictResult = {}
    for dtmDate in dictTotal.keys():
        if dictPart.has_key(dtmDate):
            intPart = dictPart[dtmDate]
        else:
            intPart = 0
        if dictTotal[dtmDate] <> 0:
            dictResult[dtmDate] = int(100 * intPart / dictTotal[dtmDate])
    return dictResult

def ListValues(objLastNumbers):
    strResult = ""
    for objProperty in objLastNumbers.propertyMap():
        if objProperty['type'] == 'int':
            strResult += """<span style="font-size: 70%%; display: block; width: 15em; float:left">%s: %s</span>""" % (objProperty['id'], objLastNumbers.getProperty(objProperty['id']))
    return strResult

def GetLastNumbers(objContext):
    objStats = GetDataFolder(objContext, 'E3ListStat')
    objLastBatch = None
    for objBatch in objStats.objectValues('Folder'):
        objLastBatch = objBatch

    objLastStat = None
    for objStat in objLastBatch.objectValues('E3ListStat'):
        objLastStat = objStat

    return objLastStat

def GetCurrentNumbers(objContext):
    objLastNumbers = GetLastNumbers(objContext)
    strValues = ListValues(objLastNumbers)
    return """<fieldset>
<legend>Current figures</legend>
    %s
</fieldset>""" % strValues

def ShowPastGraphs(objContext):
    strResult = ""
    (dictJoined, dictPayment, dictExpired, dictWarningSent, dictBonusSent) = GenerateOldStats(objContext)
    strResult += CreateNarrowWeeklyGraph(dictJoined, "Joined, by week")
    strResult += CreateNarrowWeeklyGraph(dictPayment, "Paid, by week")
    strResult += CreateNarrowWeeklyGraph(dictExpired, "Expired, by week")
    strResult += CreateNarrowWeeklyGraph(dictWarningSent, "Warning sent, by week")
    strResult += CreateNarrowWeeklyGraph(dictBonusSent, "Bonus sent, by week")
    return strResult

def ExtractDataSets(dictData):
    dictResult = {}
    intStartYear = 2004
    dtmNow = date.today()
    intEndYear = dtmNow.year
#    print dictData.keys()
    for intYear in range(intStartYear, intEndYear + 1):
        dictResult[intYear] = []
        dtmDate = date(intYear, 1, 1)
        for intI in range(1, 53):
            intValue = 0
            for intJ in range(0, 6):
                dtmTestDate = dtmDate + timedelta(days = intJ)
                if dictData.has_key(dtmTestDate):
                    intValue = dictData[dtmTestDate]
            dictResult[intYear].append(intValue)
            dtmDate = dtmDate + timedelta(days = 7)
    print dictResult
    return dictResult

def CreateChart(dictDataSets, strTitle):
#    print dictDataSets
    # Set the vertical range from 0 to 100
    max_y = 450
    min_y = 200

    # Chart size of 200x125 pixels and specifying the range for the Y axis
    chart = SimpleLineChart(700, 425, y_range=[min_y, max_y])

    # Add the chart data
    for intYear in dictDataSets.keys():
        chart.add_data(dictDataSets[intYear])
#    data = [
#        32, 34, 34, 32, 34, 34, 32, 32, 32, 34, 34, 32, 29, 29, 34, 34, 34, 37,
#        37, 39, 42, 47, 50, 54, 57, 60, 60, 60, 60, 60, 60, 60, 62, 62, 60, 55,
#        55, 52, 47, 44, 44, 40, 40, 37, 34, 34, 32, 32, 32, 31, 32
#    ]
#    data2 = []
#    for intData in data:
#        data2.append(intData * 2)
#    chart.add_data(data)
#    chart.add_data(data2)

    # Set the line colour to blue
    lstColors = ['FF0000', '00FF00', '0000FF', '00FFFF', 'FF00FF', 'FFFF00']
    lstColors = lstColors[:len(dictDataSets.keys())]
    print lstColors
    chart.set_colours(lstColors)

    # Set the legend
    print dictDataSets.keys()
#    chart.set_legend(dictDataSets.keys())

    # Set the vertical stripes
    chart.fill_linear_stripes(Chart.CHART, 0, 'CCCCCC', 0.08333, 'FFFFFF', 0.08333)

    # Set the horizontal dotted lines
    chart.set_grid(0, 25, 5, 5)

    # The Y axis labels contains 0 to 100 skipping every 25, but remove the
    # first number because it's obvious and gets in the way of the first X
    # label.
    left_axis = range(min_y, max_y + 1, 25)
    left_axis[0] = ''
    chart.set_axis_labels(Axis.LEFT, left_axis)

    # X axis labels
    chart.set_axis_labels(Axis.BOTTOM, \
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', ''])
    return chart


def ShowAllGraphs(objContext):
    dtmDate = date.today()
    dictAllStats = GatherStatsData(objContext, dtmDate, 0, date(2011, 1, 1))
    dictLive = dictAllStats["Live"]
    dictDataSets = ExtractDataSets(dictLive)
    objChart = CreateChart(dictDataSets, "Live members")
    strResult = """<img src = "%s">""" % objChart.get_url()
    return strResult

def OldShowAllGraphs(objContext):
    strResult = GetCurrentNumbers(objContext)
    dtmDate = date.today()

    strResult += MembershipProfile(objContext)

    dictAllStats = GatherStatsData(objContext, dtmDate, 3000)
    strResult += BuildTables(dictAllStats)

    dictResult = GatherStatsData(objContext, dtmDate, 300)
    strResult += CreateLargeGraph(dictResult['Live'], "Live members")
    strResult += CreateLargeGraph(dictResult['TotalPublicPostings'], "Public postings")
    strResult += CreateLargeGraph(dictResult['TotalPostings'], "Total postings")
    strResult += CreateLargeGraph(dictResult["LiveOfferings"], "Live offerings")
    strResult += CreateLargeGraph(dictResult["LiveProfiles"], "Live profiles")
#    strResult = CreateWeeklyGraph(dictResult['Live'], 'Live members, by week')
    strResult += CreateLargeGraph(dictResult['Trial'], "Trial members")
    strResult += CreateLargeGraph(dictResult['Paid'], "Paid members")

    dictMIMEDigestRatio = GetRatio(dictResult['MIMEDigest'], dictResult['Live'])
    strResult += CreateLargeGraph(dictMIMEDigestRatio, "MIME digest addresses as percentage of live members")

    dictTextDigestRatio = GetRatio(dictResult['TextDigest'], dictResult['Live'])
    strResult += CreateLargeGraph(dictTextDigestRatio, "Text digest addresses as percentage of live members")

    dictTextDigestRatio = GetRatio(dictResult['Direct'], dictResult['Live'])
    strResult += CreateLargeGraph(dictTextDigestRatio, "Direct email addresses as percentage of live members")

    dictTextDigestRatio = GetRatio(dictResult['HolidayMode'], dictResult['Live'])
    strResult += CreateLargeGraph(dictTextDigestRatio, "Members in holiday mode as percentage of live members")

    strResult += CreateWeeklyGraph(dictResult['JoinedYesterday'], "New members, by week")
    strResult += CreateWeeklyGraph(dictResult['BonusSentYesterday'], "Bonus messages sent, by week")
    strResult += CreateWeeklyGraph(dictResult['WarningSentYesterday'], "Warning messages sent, by week")
    strResult += CreateWeeklyGraph(dictResult['ExpiredYesterday'], "Expired members, by week")
    strResult += CreateWeeklyGraph(dictResult['PaymentYesterday'], "Payments, by week")
    dictPosted = SumResults(dictResult['AdvertPostedYesterday'], dictResult['NonAdvertPostedYesterday'])
    strResult += CreateLargeGraph(dictPosted, "Messages posted")
    dictAdvertRatio = GetRatio(dictResult['AdvertPostedYesterday'], dictPosted)
    strResult += CreateLargeGraph(dictAdvertRatio, "Adverts as percentage of total")
    return strResult

def GetTotalMessages(dictCounts):
    intResult = 0
    int3Months = 0
    dtmToday = date.today()
    intCurrentYear = dtmToday.year
    intCurrentMonth = dtmToday.month
    for intYear in dictCounts.keys():
        for intMonth in range(0, 12):
            intResult += int(dictCounts[intYear][intMonth])
            if (intYear * 12) + intMonth + 3 >= (intCurrentYear * 12) + intCurrentMonth:
                int3Months += int(dictCounts[intYear][intMonth])
    return (intResult, int3Months)

def CountLiveProfiles(objHere):
    intResult = 0
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == "Full":
                intResult += 1
    return intResult

def CountLiveOfferings(objHere):
    intResult = 0
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == "Full":
                for objOffering in objMember.Offerings.objectValues("E3Offering"):
                    if objOffering.Status == "Published" and objOffering.Deleted == "No":
                        intResult += 1
    return intResult

def GetCurrentStats(objContext):
    # Gather following details, by going through all members:
    #   Total number of live members
    #   Members on MIME digest, Text digest, direct (as stored in objMailBoxerMembers)
    #   Members on holiday mode
    #   Members with at least 1 payment, not counting lifetime members
    #   Members without payments, not counting lifetime members
    #   Lifetime members
    #   Expired members

    # Also go through payments and events, for each member, to see if any of the following happened yesterday:
    #   Payment made
    #   Expiry warning sent
    #   Bonus message sent

    dictResult = {}
    for strResult in cnStatsList:
        dictResult[strResult] = 0

    dtmYesterday = date.today() - timedelta(days = 1)

    objMembers = GetDataFolder(objContext, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not objMember.HasConfirmedEmailAddress:
                if objMember.Live():
                    dictResult["UnconfirmedLive"] += 1
                dictResult["Unconfirmed"] += 1
            else:
                if objMember.Live():
                    dictResult['Live'] += 1
                    if objMember.NoMail:
                        dictResult['HolidayMode'] += 1
                    if objMember.LifetimeMember:
                        dictResult['Lifetime'] += 1
                    elif objMember.Historic.objectValues('E3Payment'):
                        dictResult['Paid'] += 1
                    else:
                        dictResult['Trial'] += 1
                else:
                    dictResult['Expired'] += 1
                dictResult['Total'] += 1
                for objEvent in objMember.Historic.objectValues('E3Event'):
                    if objEvent.GetDate() == dtmYesterday:
                        if objEvent.EventType == 'WarningSent':
                            dictResult['WarningSentYesterday'] += 1
                        elif objEvent.EventType == 'BonusSent':
                            dictResult['BonusSentYesterday'] += 1
                        elif objEvent.EventType == 'ExpirySent':
                            dictResult['ExpiredYesterday'] += 1
                for objPayment in objMember.Historic.objectValues('E3Payment'):
                    if objPayment.GetDate() == dtmYesterday:
                        dictResult['PaymentYesterday'] += 1
                dtmCreated = objMember.GetCreatedDate()
                if dtmCreated.year == dtmYesterday.year and dtmCreated.month == dtmYesterday.month and dtmCreated.day == dtmYesterday.month:
                    dictResult['JoinedYesterday'] += 1

    objList = GetList(objContext, cnListNameECL)

    for strDeliveryMode in ('MIMEDigest', 'TextDigest', 'Direct'):
        dictResult[strDeliveryMode] = len(objList.GetMailBoxerMembers(strDeliveryMode))

    # Now work out yesterday's message counts
    intYear = dtmYesterday.year
    intMonth = dtmYesterday.month
    objArchive = GetDataFolder(objContext, 'E3Messages')
    try:
        objMonth = objArchive.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
    except:
        objMonth = None

    if objMonth:
        for objMessage in objMonth.objectValues():
            if objMessage.mailDate == dtmYesterday:
                if 'adv' in objMessage.mailSubject.lower():
                    dictResult['AdvertPostedYesterday'] += 1
                else:
                    dictResult['NonAdvertPostedYesterday'] += 1

#    for strKey in dictResult.keys():
#        print strKey, dictResult[strKey]

    dictPublicMessages = CreateCountList(objArchive.PublicMessageCount)
    dictAllMessages = CreateCountList(objArchive.MessageCount)

    (dictResult['TotalPostings'], dictResult['Postings3Months']) = GetTotalMessages(dictAllMessages)
    (dictResult['TotalPublicPostings'], dictResult['PublicPostings3Months']) = GetTotalMessages(dictPublicMessages)

    dictResult['LiveProfiles'] = CountLiveProfiles(objContext)
    dictResult['LiveOfferings'] = CountLiveOfferings(objContext)

    dodListStat = GetDOD(objContext, 'E3ListStat')
    objListStat = dodListStat.NewObject()
    objListStat.SetDateOfCount(date.today())
    objListStat.SetStats(dictResult)
    UpdateCacheItem(objContext, "LHBlockManager")

def BlankStats():
    dictResult = {}
    for intYear in range(2003, 2009):
        for intMonth in range(1, 13):
            dictResult[(intYear, intMonth)] = {'Payments': 0, 'Expiries': 0, 'New': 0}
    return dictResult

def BuildTable(dictResult, strType):
    strResult = """%s<br>
    <table">
    <tr><td>&nbsp;</td>""" % strType
    for intI in range(1, 13):
        strResult = strResult + """<td>%s</td>""" % {1:'J', 2:'F', 3:'M', 4:'A', 5:'M', 6:'J', 7:'J', 8:'A', 9:'S', 10:'O', 11:'N', 12:'D'}[intI]
    strResult = strResult + "</tr>"
    for intI in range(2003, 2009):
        strResult = strResult + "<tr><td>%s</td>" % intI
        for intJ in range(1, 13):
            strResult = strResult + """<td>%s</td>""" % dictResult[(intI, intJ)][strType]
        strResult = strResult + "</tr>"
    strResult = strResult + "</table><br>"
    return strResult

def AddOneEvent(dictAllEvents, dtmDate, strEvent, intCount):
    if not dtmDate in dictAllEvents.keys():
        dictAllEvents[dtmDate] = {}
    if not strEvent in dictAllEvents[dtmDate].keys():
        dictAllEvents[dtmDate][strEvent] = 0
    dictAllEvents[dtmDate][strEvent] += intCount

def AddToEvents(dictAllEvents, dictMemberEvents):
    for dtmDate in dictMemberEvents.keys():
        for strEvent in dictMemberEvents[dtmDate].keys():
            AddOneEvent(dictAllEvents, dtmDate, strEvent, dicMemberEvents[dtmDate][strEvent])

# To get the statistics, get the events on a daily basis, then work out the numbers
# Events to gather:

# From each member, get list of events, as follows:
    # {Date:{Event: count}}

# Process:
    # Start with status on day 0 (i.e. day before the start of the day range)
    # Get events on day 1
    # Work out new status at end of day 1
    # Save stats record in database
    # Repeat for day 2, etc, until last day for which we've got a full set of stats


def GetRawStats(objContext, dtmFromDate = None):
    # Count events that happened around membership, for all members, starting from dtmDate:
        # "New" - New member joined
        # "ExpPaid" - Paid membership expired
        # "ExpTrial" - Trial membership expired
        # "FirstPayment" - First payment made
        # "NextPayment" - Subsequent payment made
        # "Lifetime" - Member became a lifetime member
        # "WarningMsg" - Warning message sent
        # "ExpiryMsg" - Expiry message sent
        # "BonusMsg" - Bonus message sent
    objMembers = GetDataFolder('E3Members')
    dictResult = {}
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            dictMemberEvents = objMember.ListEvents(dtmFromDate)
            AddToResults(dictResult, strEvent)
    return dictResult

def StoreOneDayMemberStats(objContext, dtmDate):
    dictStats = GetOneDaymemberStats(objContext, dtmDate)


def GetStatistics(objContext):
    objMembers = GetDataFolder('E3Members')
    dictResult = BlankStats()
    for objMember in objMembers.objectValues():
        for objPayment in objMember.objectValues('E3Payment'):
            lstWhen = (objPayment.GetDate().year, objPayment.GetDate().month)
            try:
                dictResult[lstWhen]['Payments'] = dictResult[lstWhen]['Payments'] + 1
            except:
                pass
        for objPeriod in objMember.objectValues('E3Period'):
            if objPeriod.PeriodType == 'Trial':
                lstWhen = (objPeriod.GetStartDate().year, objPeriod.GetStartDate().month)
                try:
                    dictResult[lstWhen]['New'] = dictResult[lstWhen]['New'] + 1
                except:
                    pass
        if objMember.GetNextExpiry() <> cnFirstDate and objMember.GetNextExpiry() <> cnLastDate:
            lstWhen = (objMember.GetNextExpiry().year, objMember.GetNextExpiry().month)
            try:
                dictResult[lstWhen]['Expiries'] = dictResult[lstWhen]['Expiries'] + 1
            except:
                pass
    return BuildTable(dictResult, 'Payments') + BuildTable(dictResult, 'Expiries') + BuildTable(dictResult, 'New')

def StatsForTotalNumberOfMembers(dictResult):
    lstStats = dictResult['Total']

def GetDateRange(lstRawStats):
    dtmFirstDate = date(3000, 1, 1)
    dtmLastDate = date(1000, 1, 1)
    for dictRawStats in lstRawStats:
        lstDates = dictRawStats.keys()
        lstDates.sort()
        if lstDates:
            if lstDates[0] < dtmFirstDate:
                dtmFirstDate = lstDates[0]
            if lstDates[len(lstDates) - 1] > dtmLastDate:
                dtmLastDate = lstDates[len(lstDates) - 1]
#    print "First & last dates:", dtmFirstDate, dtmLastDate
    return (dtmFirstDate, dtmLastDate)

def EmptyStats(dtmFirstDate, dtmLastDate):
    lstFields = ("Joined", "FirstPayment", "RenewalPayment",
                 "WarningSent", "BonusSent",
                 "TrialMemberExpired", "PaidMemberExpired",
                 "ExpiredMembers", "LivePaidMembers", "LiveTrialMembers",
                 "MIMEDigestMode", "TextDigestMode", "DirectMode", "HolidayMode", "StructuredDigestMode",
                 "NonAdvertPosted", "AdvertPosted",
                 "TotalPublicPostings", "TotalPrivatePostings",
                 "MembersWhoVisitedWebsiteInLast7Days", "MembersWhoVisitedWebsiteInLast30Days")
    dictResult = {}
    dtmDate = dtmFirstDate
    while dtmDate <= dtmLastDate:
        dictResult[dtmDate] = {}
        for strField in lstFields:
            dictResult[dtmDate][strField] = None
        dtmDate = dtmDate + timedelta(days = 1)
    return dictResult

def BuildExportFile(objHere, intYear, intMonth):
    strResult = ""
    # Start: Figure out number of members for each of the days of this month
    dtmStartDate = date(intYear, intMonth, 1)

    intNextYear = intYear
    intNextMonth = intMonth + 1
    if intNextMonth > 12:
        intNextYear += 1
        intNextMonth = 1
    dtmEndDate = date(intNextYear, intNextMonth, 1) - timedelta(days=1)

    dtmPrevDate = dtmStartDate - timedelta(days = 30)
    dtmNextDate = dtmEndDate + timedelta(days = 30)

    dictResult = {}
    dtmDate = dtmPrevDate
    while dtmDate <= dtmNextDate:
        dictResult[dtmDate] = {}
        dtmDate = dtmDate + timedelta(days = 1)

    objStats = GetDataFolder(objHere, 'E3ListStat')
    for objBatch in objStats.objectValues('Folder'):
        for objStat in objBatch.objectValues('E3ListStat'):
            dtmDate = objStat.GetDateOfCount()
            if dtmDate > dtmPrevDate and dtmDate < dtmNextDate:
                dtmYesterday = dtmDate - timedelta(days = 1)
                if objStat.hasProperty("Live"):
                    dictResult[dtmDate]["Live"] = objStat.Live
                if objStat.hasProperty("ExpiredYesterday"):
                    dictResult[dtmYesterday]["Expired"] = objStat.ExpiredYesterday
                if objStat.hasProperty("JoinedYesterday"):
                    dictResult[dtmYesterday]["Joined"] = objStat.JoinedYesterday

    # Now fill the gaps (any date/range which doesn't have any Live stats)
    # For every gap between dtmPrevDate and dtmNextDate
        # Work out number of days in the gap
        # Work out difference between Live just before and just after the gap
        # Work out number of Expired and Joined over that period, i.e. net change
        # If all days in the gap have an Expired and Joined property
            # Take net change, compare to difference between Live before and after
            # If same, just apply the Expired/Joined every day
            # Otherwise, apply it pro-rata, as well as possible
        # Otherwise,
            # For days which have Expired/Joined, apply that
            # For other days, apply missing change, spread out over the number of missing days

    intLastLive = 0
    dtmDate = dtmPrevDate
    while dtmDate <= dtmNextDate:
        if not dictResult[dtmDate]:
            dtmDate = dtmDate + timedelta(days = 1)

    return strResult

def ExportYearToSpreadsheet(objHere, intYear):
    for intMonth in range(1, 13):
        strFile = BuildExportFile(objHere, intYear, intMonth)
        if strFile:
            fileExport = open("ECLStats-%s-%s" % (intYear, str(intMonth).zfill(2)), "w")
            fileExport.write(strFile)
            fileExport.close()
            print intMonth

def ExportAllYears(objHere):
    for intYear in range(1997, 2010):
        ExportYearToSpreadsheet(objHere, intYear)
        print intYear

def ExportMonthToSpreadsheet(objHere, intYear, intMonth):
    """Comma Separated Values (CSV) is text file format that you can use to exchange data
    from a database or a spreadsheet between applications. Each line in a Text CSV file
    represents a record in the database, or a row in a spreadsheet. Each field in a database
    record or cell in a spreadsheet row is usually separated by a comma. However, you
    can use other characters to delimit a field, such as a tabulator character.
    If the content of a field or cell contains a comma, the contents of the field or cell
    must be enclosed by single quotes (') or double quotes (")."""
    (dictJoined, dictFirstPayment, dictRenewal, dictTrialExpired, dictExpired,
     dictWarningSent, dictBonusSent) = GenerateOldStats(objHere)

    # What else can we work out or retrieve:
        # Number of live members - based on (listStat).Members, but correct
        #   using dictJoined, dictTrialExpired, dictExpired: .Live, .Expired, .Trial
        # Who uses what setting: .MIMEDigest, .TextDigest, .Direct, .HolidayMode
        # Postings: .NonAdvertPostedYesterday, .AdvertPostedYesterday, .TotalPublicPostings, .TotalPostings
    dictRawStats = LoadCurrentStats(objHere)
    (dtmFirstDate, dtmLastDate) = GetDateRange((dictRawStats, dictJoined, dictFirstPayment,
                                                dictRenewal, dictTrialExpired, dictExpired,
                                                dictWarningSent, dictBonusSent))
    dictResult = EmptyStats(dtmFirstDate, dtmLastDate)

# Statistics required:

# By month:
#    New ECL trial members via affiliate referral
#    New ECL trial member via search engines
#    New ECL trial members, overall
#    ECL conversion rate for new members
#        Within 30 days
#        Within 31 - 60 days
#        Within 61 - 100 days
#        After 100 days
#    ECL conversion rate for existing members
#    Number of trial members expired this month
#    Number of paid members expired this month

# By day:
#    Number of paid, trial, expired members
#    Percentage of live members in Direct (messages), Direct (adverts)
#    Percentage of live members with messages and/or adverts in digest mode: MIMEDigest, TextDigest, StructuredDigest
#    Percentage of live members in HolidayMode
#    Members who visited website during last 24 hours, during last 7 days, during last 30 days
#    Number of archive searches, number of general searches
#    Number of products and services viewed, number of events viewed
#    Number of profiles viewed
#    Number of live members with profile ready to be featured member
#    Number of live members with at least ??? details filled in on their profile
#    Number of live members with a photo
#    Number of coaching networks listed
#    Number of coaching organisations listed
#    Number of other organisations listed
#    Number of products and services listed
#    Number of live (i.e. published, today/future) events listed
