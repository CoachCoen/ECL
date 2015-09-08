# coding=utf-8

from libDatabase import GetDOD
from E3Members import GetCurrentMember
from libDatabase import GetDataFolder
from E3TempData import SetMessage
import datetime
from libDate import MonthName
from libDatabase import Catalogue
from libDatabase import SearchOne
from libDatabase import SearchMany
from libEmail import SendEmail
from E3Members import ManagerLoggedIn
from libString import ToUnicode
from E3AutoEmails import StartEmailSequence
from libConstants import cnShortDateFormat, cnEmptyDate
from libForms import SimpleBuildSelectControl, CheckRequiredFields
from libForms import TextControl, Fieldset, Paragraph, PureText, SubmitControl
from libForms import CreateForm, GetDataFromForm
from libConstants import cnCountryNames
from libConstants import cnConf08Price
from libConstants import cnConf08EBDiscount
from libConstants import cnConf08EBDate
from libConstants import cnConf08FullPaymentDate
from libConstants import cnConf08Deposit
from libConstants import cnConf08MembersDiscount
from libGeneral import GetParameter
from libGeneral import GetNextCartId
from libBuildHTML import InsertParagraphs
from libDatabase import NextInvoiceNumber
from libDate import DateFromString
from libString import ValidEmailAddress
from libString import ListToText
from libBuildHTML import ShowChecked


#FriEvePresence: 5
#FriEveInformalMeal: 5
#FriEveOther:
#SatEvePresence: 5
#SatEveCeilidh: 5
#SatEveLeroc: 1
#SatEveSalsa: 1
#SatEveBallroom: 1
#SatEveQuiz: 2
#SatEveOwnMusic: 3
#SatEveAdvWalk: 1
#SatEveOther:
#SunAmPresence: 5
#SunAmSessions: 5
#SunAmOther:
#SunLunchPresence: 5
#SunLunchInformalMeal: 5
#SunLunchOther:

def RebuildIndexes(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objBooking in objMember.Events.objectValues("E3Conf08Booking"):
                Catalogue(objBooking)
    return "Done"

def SendKeepInformed(objHere, strEmailAddress, strAbout):
	strMessage = """
Please keep me informed, details:
%s
%s
""" % (strEmailAddress, strAbout)
	strSubject = "Conference - keep informed"
	SendEmail(objHere, strMessage, strSubject, "coen@coachcoen.com")

def KeepMeInformed(objHere, strAbout):
	strURL = objHere.REQUEST.VIRTUAL_URL
	if strAbout == "SunAm":
		strIntro = "<p>Registration opens soon. Enter your email address below to be kept informed, and to be one of the first to register</p>"
		strPrivacy = "<p>We will only use your email address to send you information about the Coaching Master-Class and the Euro Coach List Conference</p>"
	else:
		strIntro = ""
		strPrivacy = ""

	strAction = GetParameter(objHere, "Action")
	print "Action: ", strAction

	strForm = """<form action="%s" method="post">
    <p>
		<input name="EmailAddress" value="%s" class="txt" type="text">
        <input name="Action" value="KeepInformed" type="hidden">
    </p>
	<p>
        <input name="" value="Keep me informed" class="btn" type="submit">
	</p>
</form>"""

	strForm = strIntro + strForm + strPrivacy

	if strAction == "KeepInformed":
		strEmailAddress = GetParameter(objHere, "EmailAddress")
		if ValidEmailAddress(strEmailAddress):
			strResult = """<p class="InfoMessage">Thanks for your interest. We will keep you informed by email</p>"""
			SendKeepInformed(objHere, strEmailAddress, strAbout)
		else:
			strResult = """<p class="ErrorMessage">This is not a valid email address. Please submit a valid email address\n"""
			strResult += strForm % (strURL, strEmailAddress)
	else:
		strResult = strForm % (strURL, "Email Address")
	return strResult



def ParsePreferences(lstPreferences):
#    lstPreferences = strPreferences.split("\n")
    dictResult = {}
    for strPreference in lstPreferences:
        if ":" in strPreference:
            (strKey, strPref) = strPreference.split(": ")
            if strPref.isdigit():
                dictResult[strKey] = int(strPref)
            else:
                dictResult[strKey] = strPref
#    print dictResult
    return dictResult

def GetActivityResults(dictResult, intPresenceChance, intActivityChance):
#    dictActivity = {
#        'WeightedScore': 0,
#        'UnweightedScore': 0,
#        'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}}
    dictResult['WeightedScore'] += intPresenceChance * intActivityChance
    dictResult['UnweightedScore'] += intActivityChance
    dictResult['Chart'][intActivityChance] += 1
    return dictResult

def AddSuggestions(lstSuggestions, strSuggestion):
    if strSuggestion:
        lstSuggestions.append(strSuggestion)
    return lstSuggestions

def AddOnePreference(strPreferences, intCount, dictResult):
    dictPrefs = ParsePreferences(strPreferences)
    if len(dictPrefs) <> 18:
        return (intCount, dictResult)

# Fri evening
    # Presence
        # Estimated number: sum of (score / 5)
        # Chart: number of (count of 1's, 2's, etc)
    # Suggestions: List of suggestions
    dictResult['FriEvePresence']['Estimate'] += (dictPrefs['FriEvePresence'] / 5.0)
    dictResult['FriEvePresence']['Chart'][dictPrefs['FriEvePresence']] += 1
    dictResult['FriEveInformalMeal'] = GetActivityResults(dictResult['FriEveInformalMeal'], dictPrefs['FriEvePresence'], dictPrefs['FriEveInformalMeal'])
    dictResult['FriEveOther'] = AddSuggestions(dictResult['FriEveOther'], dictPrefs['FriEveOther'])

    dictResult['SatEvePresence']['Estimate'] += dictPrefs['SatEvePresence'] / 5
    dictResult['SatEvePresence']['Chart'][dictPrefs['SatEvePresence']] += 1

    for strActivity in ('SatEveCeilidh', 'SatEveLeroc', 'SatEveSalsa', 'SatEveBallroom', 'SatEveQuiz', 'SatEveOwnMusic', 'SatEveAdvWalk'):
        dictResult[strActivity] = GetActivityResults(dictResult[strActivity], dictPrefs['SatEvePresence'], dictPrefs[strActivity])

    dictResult['SatEveOther'] = AddSuggestions(dictResult['SatEveOther'], dictPrefs['SatEveOther'])

    dictResult['SunAmPresence']['Estimate'] += dictPrefs['SunAmPresence'] / 5
    dictResult['SunAmPresence']['Chart'][dictPrefs['SunAmPresence']] += 1
    dictResult['SunAmSessions'] = GetActivityResults(dictResult['SunAmSessions'], dictPrefs['SunAmPresence'], dictPrefs['SunAmSessions'])

    dictResult['SunAmOther'] = AddSuggestions(dictResult['SunAmOther'], dictPrefs['SunAmOther'])

    dictResult['SunLunchPresence']['Estimate'] += dictPrefs['SunLunchPresence'] / 5
    dictResult['SunLunchPresence']['Chart'][dictPrefs['SunLunchPresence']] += 1
    dictResult['SunLunchInformalMeal'] = GetActivityResults(dictResult['SunLunchInformalMeal'], dictPrefs['SunLunchPresence'], dictPrefs['SunLunchInformalMeal'])

    dictResult['SunLunchOther'] = AddSuggestions(dictResult['SunLunchOther'], dictPrefs['SunLunchOther'])

# Sat evening
    # Presence
        # Estimated number - as above
        # Activity, for each:
            # Weighted score: sum of (SatEvePresence * ActivityScore)
            # Unweighted score: sum of ActivityScore
            # Chart
    # Suggestions: List of suggestions

# Sun am
    # Presence
        # Estimated number - as above
        # Sessions
            # Weighted score: sum of (SatEvePresence * ActivityScore)
            # Unweighted score: sum of ActivityScore
            # Chart
    # Suggestions: List of suggestions

# Sun lunch
    # Presence
        # Estimated number - as above
        # Informal meal
            # Weighted score: sum of (SatEvePresence * ActivityScore)
            # Unweighted score: sum of ActivityScore
            # Chart
    # Suggestions: List of suggestions

    return (intCount + 1, dictResult)

def ShowChart(dictChart):
    strResult = ""
    for intI in range(1, 6):
        strResult += "%s: <b>%s</b> | " % (intI, dictChart[intI])
    return strResult

def ShowActivity(dictActivity):
#    dictActivity = {
#        'WeightedScore': 0,
#        'UnweightedScore': 0,
#        'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}}
    strResult = "Weighted score: %s, Unweighted score: %s, Chart: %s" % (dictActivity['WeightedScore'], dictActivity['UnweightedScore'], ShowChart(dictActivity['Chart']))
    return strResult

def ShowSuggestions(lstSuggestions):
    if lstSuggestions:
        strResult = """<p>Suggestions:</p>
<ul>
"""
        for strSuggestion in lstSuggestions:
            strResult += "<li>%s</li>\n" % strSuggestion
        strResult += "</ul>\n"
    else:
        strResult = ""
    return strResult

def ShowPresence(intCount, realScore):
    return "%s out of %s, %.1f%% of 60 - 100 makes %.1f - %.1f" % (realScore, intCount, (realScore/intCount * 100), (realScore/intCount * 60), (realScore/intCount * 100))

def ReportPreferencesSummary(intCount, dictResult):
#    print dictResult['FriEvePresence']['Estimate']
    strResult = ""
    strResult += """
<fieldset>
    <legend>Friday evening</legend>
    <p>Total attendance: %s</p>
    <p>Chart: %s</p>
    <p>Informal meal: %s</p>
    %s
</fieldset>""" % \
        (ShowPresence(intCount, dictResult['FriEvePresence']['Estimate']),
        ShowChart(dictResult['FriEvePresence']['Chart']),
        ShowActivity(dictResult['FriEveInformalMeal']),
        ShowSuggestions(dictResult['FriEveOther']))

    strResult += """
<fieldset>
    <legend>Saturday evening</legend>
    <p>Total attendance: %s</p>
    <p>Chart: %s</p>
    <p>Ceilidh: %s</p>
    <p>Leroc: %s</p>
    <p>Salsa: %s</p>
    <p>Ballroom: %s</p>
    <p>Quiz: %s</p>
    <p>Own music: %s</p>
    <p>Adventure walk: %s</p>
    %s
</fieldset>""" % \
    (ShowPresence(intCount, dictResult['SatEvePresence']['Estimate']),
        ShowChart(dictResult['SatEvePresence']['Chart']),
        ShowActivity(dictResult['SatEveCeilidh']),
        ShowActivity(dictResult['SatEveLeroc']),
        ShowActivity(dictResult['SatEveSalsa']),
        ShowActivity(dictResult['SatEveBallroom']),
        ShowActivity(dictResult['SatEveQuiz']),
        ShowActivity(dictResult['SatEveOwnMusic']),
        ShowActivity(dictResult['SatEveAdvWalk']),
        ShowSuggestions(dictResult['SatEveOther']))

    strResult += """
<fieldset>
    <legend>Sunday morning</legend>
    <p>Total attendance: %s</p>
    <p>Chart: %s</p>
    <p>Sessions: %s</p>
    %s
</fieldset>""" % \
        (ShowPresence(intCount, dictResult['SunAmPresence']['Estimate']),
        ShowChart(dictResult['SunAmPresence']['Chart']),
        ShowActivity(dictResult['SunAmSessions']),
        ShowSuggestions(dictResult['SunAmOther']))

    strResult += """
<fieldset>
    <legend>Sunday lunch</legend>
    <p>Total attendance: %s</p>
    <p>Chart: %s</p>
    <p>Informal meal: %s</p>
    %s
</fieldset>""" % \
        (ShowPresence(intCount, dictResult['SunLunchPresence']['Estimate']),
        ShowChart(dictResult['SunLunchPresence']['Chart']),
        ShowActivity(dictResult['SunLunchInformalMeal']),
        ShowSuggestions(dictResult['SunLunchOther']))

    return strResult


def SummarisePreferences(objHere):
    lstBookings = GetAllBookings(objHere)
    dictActivity = {
        'WeightedScore': 0,
        'UnweightedScore': 0,
        'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}}

    dictResult = \
        {'FriEvePresence': {
            'Estimate': 0.0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'FriEveInformalMeal': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'FriEveOther': [],
         'SatEvePresence': {
            'Estimate': 0.0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveCeilidh': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveLeroc': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveSalsa': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveBallroom': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveQuiz': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveOwnMusic': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveAdvWalk': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SatEveOther': [],
         'SunAmPresence': {
            'Estimate': 0.0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SunAmSessions': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SunAmOther': [],
         'SunLunchPresence': {
            'Estimate': 0.0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SunLunchInformalMeal': {
            'WeightedScore': 0,
            'UnweightedScore': 0,
            'Chart': {1: 0, 2: 0, 3:0, 4:0, 5:0}},
         'SunLunchOther': []}

    intCount = 0

    for objBooking in lstBookings:
        lstPreferences = objBooking.Preferences
        if lstPreferences:
            (intCount, dictResult) = AddOnePreference(lstPreferences, intCount, dictResult)
    strResult = ReportPreferencesSummary(intCount, dictResult)
    return strResult

def SendConf08Receipt(objHere, strEmailAddress, strName, intInvoiceNumber, intAmount, blnFullAmount, intRemainder):
    if blnFullAmount:
        strDescription = "Euro Coach List Conference 2008"
    elif intRemainder:
        strDescription = """Euro Coach List Conference 2008 - Deposit
Note: Balance of GBP%s to be paid by 20 August 2008""" % intRemainder
    else:
        strDescription = "Euro Coach List Conference 2008 - Final Payment"
    strReceipt = cnGeneralReceipt % {'InvoiceNumber': intInvoiceNumber,
        'InvoiceDate': datetime.date.today().strftime(cnShortDateFormat),
        'Name': strName,
        'EmailAddress': strEmailAddress,
        'Description': strDescription,
        'Amount': "GBP%s" % intAmount}
    strReceipt = strReceipt.encode('ascii', 'ignore')
    strSubject = "Euro Coach List Conference 2008 - Receipt"
    SendEmail(objHere, strReceipt, strSubject, strEmailAddress)

def ProcessPayment(objBooking):
    strPaymentAmount = GetParameter(objBooking.REQUEST, "PaymentAmount")
    intPaymentAmount = int(strPaymentAmount)
    strPaymentMethod = GetParameter(objBooking.REQUEST, "PaymentMethod")
    strDate = GetParameter(objBooking.REQUEST, "PaymentDate")
    dtmPaymentDate = DateFromString(strDate)

    objBooking.PaidAmount += intPaymentAmount
    objBooking.RemainingAmount -= intPaymentAmount

    AddToRegistrationHistory(objBooking, "Paid GBP%s using %s" % (intPaymentAmount, strPaymentMethod), strDate)
    if objBooking.RemainingAmount == 0:
        AddToRegistrationHistory(objBooking, "Paid in full", strDate)
    else:
        AddToRegistrationHistory(objBooking, "Remaining: GBP%s" % objBooking.RemainingAmount, strDate)

    objBooking.InvoiceNumber = NextInvoiceNumber(objBooking)
    AddToRegistrationHistory(objBooking, "Invoice number %s" % objBooking.InvoiceNumber, strDate)

    SendConf08Receipt(objBooking, objBooking.EmailAddress, objBooking.Name, objBooking.InvoiceNumber, intPaymentAmount, (objBooking.RemainingAmount == 0), objBooking.RemainingAmount)

def HasOutstandingPayments(objBooking):
    if objBooking.GetDepositPaid() == datetime.date(1901, 1, 1):
        return True
    if objBooking.PayLaterAmount:
        if objBooking.GetRemainderPaid() == datetime.date(1901, 1, 1):
            return True
    return False

def PaymentForm(objBooking):
    strToday = datetime.date.today().strftime(cnShortDateFormat)
    lstOptions = ("PayPal", "Online", "UKCheque", "BankTransfer", "Cash")
    strOptions = ""
    for strOneOption in lstOptions:
        strOptions += """<option>%s</option>\n""" % strOneOption
    strPaymentMethod = """
<select name="PaymentMethod">
    %s
</select>""" % strOptions

    return """<form method="post" action=".">
<fieldset>
    <legend>Process a payment</legend>
    <input type="hidden" name="BookingId" value="%s">
    <input type="hidden" name="Action" value="SubmitConferencePayment">
    <p>Date <input type="text" name="PaymentDate" value="%s"></p>
    <p>Amount &pound;<input type="text" name="PaymentAmount" value="%s"></p>
    %s
    <p><input type="submit" value="Submit payment"></p>
</fieldset>""" % (objBooking.id, strToday, objBooking.RemainingAmount, strPaymentMethod)

def ShowOneBooking(objBooking):
    strAction = GetParameter(objBooking.REQUEST, "Action")
    if strAction == "SubmitConferencePayment":
        ProcessPayment(objBooking)
    strResult = """
<fieldset>
    <legend>Booking details for %s</legend>
    <p>Booking id: %s</p>
    <p>Date of booking: %s</p>
    <p>Name: %s</p>
    <p>Country: %s</p>
    <p>Telephone: %s</p>
    <p>Email address: <a href="mailto:%s">%s</a></p>
    <p>Member id: %s</p>
</fieldset>
""" % (objBooking.Name,
        objBooking.id,
        objBooking.GetDateCreated().strftime(cnShortDateFormat),
        objBooking.Name,
        objBooking.Country,
        objBooking.Telephone,
        objBooking.EmailAddress,
        objBooking.EmailAddress,
        objBooking.unrestrictedTraverse('../..').id)

    strResult += """
<fieldset>
    <legend>Payment summary</legend>
    <p>Paid: %s</p>
    <p>Outstanding: %s</p>
</fieldset>""" % (objBooking.PaidAmount, objBooking.RemainingAmount)

    if objBooking.RemainingAmount > 0:
        strResult += PaymentForm(objBooking)

    strResult += """
<fieldset>
    <legend>Booking history</legend>
    %s
</fieldset>""" % FormatBookingHistory(objBooking.History)
    return strResult

def ShowAttendees(objHere):
    strBookingId = GetParameter(objHere.REQUEST, "BookingId")
    if strBookingId:
        objBooking = SearchOne(objHere, "E3Conf08Booking", "id", strBookingId)
        if objBooking:
            return ShowOneBooking(objBooking)
    return ListBookings(objHere)

def GetAllBookings(objHere):
    lstBookings = []
    objMembers = objHere.unrestrictedTraverse('/Data/E3/E3Members')
    for objBatch in objMembers.objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if "Events" in objMember.objectIds("Folder"):
                for objConf08Booking in objMember.Events.objectValues("E3Conf08Booking"):
                    lstBookings.append(objConf08Booking)
    for objConf08Booking in objHere.unrestrictedTraverse('/Data/E3/E3Conf08Booking').objectValues('E3Conf08Booking'):
        lstBookings.append(objConf08Booking)
    return lstBookings

def SortByBookingName(obj1, obj2):
    return cmp(ToUnicode(obj1.Name), ToUnicode(obj2.Name))

def PaidInfo(dtmDate):
    if dtmDate == datetime.date(1901, 1, 1):
        return "<b>unpaid</b>"
    else:
        return "paid %s" % dtmDate.strftime(cnShortDateFormat)

def GetYN(blnN):
    if blnN:
        return "Y"
    return "&nbsp;"

def HideZeros(intI):
    if intI:
        return intI
    return "&nbsp;"

def ListBookings(objHere):
#    lstBookings = GetAllBookings(objHere)
    lstBookings = SearchMany(objHere, "E3Conf08Booking", "None", "")
    lstBookings.sort(SortByBookingName)
    strEmailAddresses = ""
    # One payment of <amount>, paid <date>/unpaid
    # Deposit of <amount>, paid <date>/unpaid, plus remainder of <amount>, paid <date>/unpaid, total of <amount>. Payment by <method>
    intCCCount = 0
    intSatEveCount = 0
    intSunAmCount = 0
    intPaid = 0
    intToPay = 0
    intCount = 0
    strResult = u"""
<table>
    <tr>
        <td>&nbsp;</td>
        <td>Date</td>
        <td>Name</td>
        <td>Email</td>
        <td>CC</td>
        <td>Sat eve</td>
        <td>Sun am</td>
        <td>Paid</td>
        <td>To pay</td>
    </tr>
"""
    for objBooking in lstBookings:
        intCount += 1
        strEmailAddress = ToUnicode(objBooking.EmailAddress)
        if not strEmailAddress:
            strEmailAddress = "(unknown)"
        strResult += """
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td><a href=".?BookingId=%s">%s</a></td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>
""" % (intCount,
        objBooking.GetDateCreated().strftime(cnShortDateFormat),
        ToUnicode(objBooking.Name), objBooking.id,
        strEmailAddress,
        GetYN(objBooking.BookedForCC),
        GetYN(objBooking.BookedForSatEve), GetYN(objBooking.BookedForSunAm),
        HideZeros(objBooking.PaidAmount), HideZeros(objBooking.RemainingAmount))
        if objBooking.BookedForCC:
            intCCCount += 1
        if objBooking.BookedForSatEve:
            intSatEveCount += 1
        if objBooking.BookedForSunAm:
            intSunAmCount += 1
        intPaid += objBooking.PaidAmount
        intToPay += objBooking.RemainingAmount

        strEmailAddresses += ToUnicode(objBooking.EmailAddress) + "\n"
    strResult += """
<tr>
    <td colspan="4">&nbsp;</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>&nbsp;</td>
</tr>
</table>""" % (intCCCount, intSatEveCount, intSunAmCount, intPaid, intToPay)

    strResult += "<form><textarea>%s</textarea></form>" % strEmailAddresses
    return strResult

def CountOneBooking(objConf08Booking, intCCBookings, intSatEveBookings, intSunAmBookings, intPaidAmount, intRemainingAmount):
    if objConf08Booking.BookedForCC:
        intCCBookings += 1

    if objConf08Booking.BookedForSatEve:
        intSatEveBookings += 1

    if objConf08Booking.BookedForSunAm:
        intSunAmBookings += 1

    intPaidAmount += objConf08Booking.PaidAmount
    intRemainingAmount += objConf08Booking.RemainingAmount

    return (intCCBookings, intSatEveBookings, intSunAmBookings, intPaidAmount, intRemainingAmount)

def SendConfStatistics(objHere, objRegistration, intPaid, strBookedFor):
    intCCBookings = 0
    intSatEveBookings = 0
    intSunAmBookings = 0
    intPaidAmount = 0
    intRemainingAmount = 0
    objMembers = objHere.unrestrictedTraverse('/Data/E3/E3Members')
    for objBatch in objMembers.objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if "Events" in objMember.objectIds("Folder"):
                for objConf08Booking in objMember.Events.objectValues("E3Conf08Booking"):
                    (intCCBookings, intSatEveBookings, intSunAmBookings, intPaidAmount, intRemainingAmount) = CountOneBooking(objConf08Booking, intCCBookings, intSatEveBookings, intSunAmBookings, intPaidAmount, intRemainingAmount)
    for objConf08Booking in objHere.unrestrictedTraverse('/Data/E3/E3Conf08Booking').objectValues('E3Conf08Booking'):
        (intCCBookings, intSatEveBookings, intSunAmBookings, intPaidAmount, intRemainingAmount) = CountOneBooking(objConf08Booking, intCCBookings, intSatEveBookings, intSunAmBookings, intPaidAmount, intRemainingAmount)
    strResult = """Another booking :-)

Name: %s
Email address: %s
Amount paid: %s

Booked for: %s

Core Conference bookings: %s
Saturday evening: %s
Sunday morning: %s

Already paid: %s
Outstanding payments: %s
""" % (objRegistration.Name, objRegistration.EmailAddress, intPaid, strBookedFor, intCCBookings, intSatEveBookings, intSunAmBookings, intPaidAmount, intRemainingAmount)

    strResult = strResult.encode('ascii', 'ignore')
    SendEmail(objHere, strResult, "Another conference booking", "coen@coachcoen.com")

def StartConferencePayment(objHere, objRegistration, strDescription):

    intAmount = objRegistration.RemainingAmount
    strConfBookingId = objRegistration.id
    strEmailAddress = objRegistration.EmailAddress
    strCountry = objRegistration.Country
    strTelephone = objRegistration.Telephone
    strName = objRegistration.Name

    intCartId = GetNextCartId(objHere)
    objPayments = objHere.unrestrictedTraverse("/Data/Public/Payments")
    dodWorldPayCall = GetDOD(objHere, "E3WorldPayCall")
    objWorldPayCall = dodWorldPayCall.NewObject(objPayments)
    objWorldPayCall.SetDateCalled(datetime.date.today())
    objWorldPayCall.CartId = intCartId
    objWorldPayCall.Status = "Called"
    objWorldPayCall.PaymentType = strConfBookingId
    objWorldPayCall.Amount = intAmount
    Catalogue(objWorldPayCall)
    strResult = """
    <form action="https://select.worldpay.com/wcc/purchase" name="PaymentForm" method="post">
        <fieldset>
            <legend>Online payment</legend>
            <p>You should be automatically forwarded to the secure online payment system within a few seconds. However, if nothing happens, please click on the button below</p>
            <input type="hidden" name="instId" value="69595">
            <input type="hidden" name="cartId" value="%s">
            <input type="hidden" name="amount" value="%s">
            <input type="hidden" name="currency" value="GBP">
            <input type="hidden" name="desc" value="%s">
            <input type="hidden" name="testMode" value="0">
            <input type="hidden" name="email" value="%s">
            <input type="hidden" name="country" value="%s">
            <input type="hidden" name="name" value="%s">
            <input type="hidden" name="telephone" value="%s">
            <p><input type="submit" name="Submit" value="Continue to the payment system" class="btn"></p>
        </fieldset>
    </form>
    <script language="JavaScript">
    <!--
    PaymentForm.submit()
    //-->
    </script>
    """ % (intCartId, intAmount, strDescription, strEmailAddress, strCountry, strName, strTelephone)
    return strResult

def BuildFieldLine(strLabel, blnVerifyForm, strFormValue, strName):
    blnValid = True
    strResult = """<p><label>%s:</label><input type="text" name="%s" value="%s"></p>""" % (strLabel, strName, strFormValue)
#    print "BuildFieldLine |%s:%s|" % (strName, strFormValue)
    if blnVerifyForm:
        if not strFormValue:
            strResult = """<p class="MissingField"><label>%s:</label><input type="text" name="%s" value="%s"><br></p>""" % (strLabel, strName, strFormValue)
            blnValid = False
        elif "emailaddress" in strName.lower() and not ValidEmailAddress(strFormValue):
            strResult = """<p class="InvalidEmailAddress"><label>%s:</label><input type="text" name="%s" value="%s"><br></p>""" % (strLabel, strName, strFormValue)
            blnValid = False
    return (strResult, blnValid)

def GetPayNowAmount(objMember, strRegistrationType, blnPresentersRate):
    intFullAmount = cnConf08Price
    if datetime.date.today() <= cnConf08EBDate or blnPresentersRate:
        intFullAmount -= cnConf08EBDiscount
    intDeposit = cnConf08Deposit
    intRemainder = intFullAmount - intDeposit
    if (objMember and objMember.MembershipType == "Full") or blnPresentersRate:
        intFullAmount -= cnConf08MembersDiscount
    if strRegistrationType == "Deposit Only":
        intPayNowAmount = cnConf08Deposit
        intPayLaterAmount = intFullAmount - intPayNowAmount
    else:
        intPayLaterAmount = 0
        intPayNowAmount = intFullAmount
    return (intPayNowAmount, intPayLaterAmount, intFullAmount, intDeposit, intRemainder)

def BuildIntro():
    return """<p>Registration is now open for the Core Conference Programme, on Saturday 20th September 2008, in Bristol, United Kingdom</p>
<p>You will be sent an email when the rest of the programme is available</p>
<p>The Core Conference is &pound;%(Price)s, with a &pound;%(EBDiscount)s discount for registrations before %(EBDate)s and a &pound;%(MembersDiscount)s discount for Euro Coach List members. This includes lunch and refreshments</p>
""" % {'Price': cnConf08Price,
        'EBDiscount': cnConf08EBDiscount,
        'EBDate': cnConf08EBDate.strftime(cnShortDateFormat),
        'MembersDiscount': cnConf08MembersDiscount}

def BuildPresentersRateIntro():
    return """<p>Thanks again for agreeing to present or facilitate at the conference</p>
<p>Your presenter's rate is &pound;%s. This includes lunch and refreshments</p>
""" % (cnConf08Price - cnConf08EBDiscount - cnConf08MembersDiscount)

def GetMemberDiscountBlockForPresenters(objMember, strURL):
    strResult = ""
    if not objMember:
        strResult += """
<fieldset>
    <legend>Member log in</legend>
    <p>Log in now, to save re-typing your details. Or fill in your details in the 'Your details' box below</p>
	<form action="%(URL)s" method="post">
        <p>
            <input type="hidden" name="Action" value="LogIn">
			<input type="text" name="Username" value = "Username" class="txt"/>
	    </p>
	    <p>
			<input type="password" name="Password" value = "Password" class="txt"/>
	    </p>
        <p class="FormComment">
            <a href="%(URL)s?Action=PasswordReminder">(Forgot your password?)</a>
        </p>
		<p>
		    <input name="" type="submit" value="Log in" class="btn"/>
		</p>
	</form>
</fieldset>""" % {'URL': strURL}
    return strResult


def GetMemberDiscountBlock(objMember, strURL):
    strResult = ""
    if objMember:
        if objMember.MembershipType <> "Full":
            strResult += """
<fieldset>
    <legend>Membership expired</legend>
<p>Your membership has expired. If you wish to claim the &pound;%s discount member's discount, renew your membership first</p>
<p>To renew your membership, go to the <a href="/MyECL">MyECL page</a>, and click on the &quot;+&quot; in front of &quot;Payment and Membership Renewal&quot;</p>
</fieldset>""" % cnConf08MembersDiscount
    else:
        strResult += """
<fieldset>
    <legend>Member's Discount</legend>
    <p>Euro Coach List members get a &pound;%(MembersDiscount)s discount. Log in or join now to claim your discount</p>
    <h2>Join now</h2>
	<p>Free 3 months membership</p>
	<form action="/Membership/Welcome" method="post">
        <p>
			<input type="text" name="EmailAddress" value = "Email Address" class="txt"/>
            <input type="hidden" name="Action" value="JoinNow">
	    </p>
		<p>
		    <input name="" type="submit" value="Join" class="btn"/>
		</p>
	</form>
    <h2>Log in</h2>
	<form action="%(URL)s" method="post">
        <p>
            <input type="hidden" name="Action" value="LogIn">
			<input type="text" name="Username" value = "Username" class="txt"/>
	    </p>
	    <p>
			<input type="password" name="Password" value = "Password" class="txt"/>
	    </p>
        <p class="FormComment">
            <a href="%(URL)s?Action=PasswordReminder">(Forgot your password?)</a>
        </p>
		<p>
		    <input name="" type="submit" value="Log in" class="btn"/>
		</p>
	</form>
</fieldset>""" % {'MembersDiscount': cnConf08MembersDiscount,
	                'URL': strURL}
    return strResult

def BuildDetailsBlocks(strMemberName, strFormName, strMemberCountry, strFormCountry, strMemberTelephone, strFormTelephone, strMemberEmailAddress, strFormEmailAddress, blnVerifyForm, blnFullDetailsRequired):
    strRegisteredDetails = ""
    strAdditionalDetails = ""
    blnBlockValid = True
    if strMemberName:
        strRegisteredDetails += "<p><label>Name:</label>%s</p>\n" % strMemberName
    else:
        (strFieldLine, blnFieldValid) = BuildFieldLine("Name", blnVerifyForm, strFormName, "Name")
        strAdditionalDetails += strFieldLine
        if blnFullDetailsRequired and not blnFieldValid:
            blnBlockValid = False

    if strMemberCountry:
        strRegisteredDetails += "<p><label>Country:</label>%s</p>\n" % strMemberCountry
    else:
        strControl = SimpleBuildSelectControl("Country", cnCountryNames, "United Kingdom")
        strAdditionalDetails += """<p><label>Country:</label>%s</p>""" % strControl

    if strMemberTelephone:
        strRegisteredDetails += "<p><label>Telephone:</label>%s</p>\n" % strMemberTelephone
    else:
        strAdditionalDetails += """<p><label>Telephone:</label><input type="text" value="%s" name="Telephone"></p>""" % strFormTelephone

    if strMemberEmailAddress:
        strRegisteredDetails += "<p><label>Email:</label>%s</p>\n" % strMemberEmailAddress
    else:
        (strFieldLine, blnFieldValid) = BuildFieldLine("Email Address", blnVerifyForm, strFormEmailAddress, "EmailAddress")
        strAdditionalDetails += strFieldLine
        if not blnFieldValid:
            blnBlockValid = False

    return (strRegisteredDetails, strAdditionalDetails, blnBlockValid)

def BuildPaymentOptionsBlockOld(strFormRegistrationType, strFormPaymentMethod, intFullAmount, intDeposit, intRemainder):
    if not strFormRegistrationType or strFormRegistrationType == "Full Amount":
        strFullChecked = " checked "
        strDepositChecked = ""
    else:
        strFullChecked = ""
        strDepositChecked = " checked "

    strOnlineChecked = ""
    strPayPalChecked = ""
    strBankTransferChecked = ""
    strUKChequeChecked = ""

    if not strFormPaymentMethod or strFormPaymentMethod == "Online":
        strOnlineChecked = " checked "
    elif strFormPaymentMethod == "PayPal":
        strPayPalChecked = " checked "
    elif strFormPaymentMethod == "BankTransfer":
        strBankTransferChecked = " checked "
    elif strFormPaymentMethod == "UKCheque":
        strUKChequeChecked = " checked "

    strResult = """
        <input type="radio" name="RegistrationType" value="Full Amount" %s> the full amount of &pound;%s now<br>
        <input type="radio" name="RegistrationType" value="Deposit Only" %s> a deposit of &pound;%s now and the remainder of &pound;%s by %s<br>
    </p>
    <p>Payment method:<br>
        <input type="radio" name="PaymentMethod" value="Online" %s> Online credit/debit card<br>
        <input type="radio" name="PaymentMethod" value="PayPal" %s> PayPal<br>
        <input type="radio" name="PaymentMethod" value="BankTransfer" %s> Bank transfer to a UK bank account<br>
        <input type="radio" name="PaymentMethod" value="UKCheque" %s> UK cheque
    </p>
""" % (strFullChecked, intFullAmount, strDepositChecked, intDeposit, intRemainder, cnConf08FullPaymentDate.strftime(cnShortDateFormat), strOnlineChecked, strPayPalChecked, strBankTransferChecked, strUKChequeChecked)
    return strResult

def BuildPaymentOptionsBlock(strFormPaymentMethod):
    strOnlineChecked = ""
    strPayPalChecked = ""
    strBankTransferChecked = ""
    strUKChequeChecked = ""

    if not strFormPaymentMethod or strFormPaymentMethod == "Online":
        strOnlineChecked = " checked "
    elif strFormPaymentMethod == "PayPal":
        strPayPalChecked = " checked "
    elif strFormPaymentMethod == "BankTransfer":
        strBankTransferChecked = " checked "
    elif strFormPaymentMethod == "UKCheque":
        strUKChequeChecked = " checked "

    strResult = """
<fieldset>
    <legend>Payment method</legend>

        <p><input type="radio" name="PaymentMethod" value="Online" %s> Online credit/debit card</p>
        <p><input type="radio" name="PaymentMethod" value="PayPal" %s> PayPal</p>
        <p><input type="radio" name="PaymentMethod" value="BankTransfer" %s> Bank transfer to a UK bank account</p>
        <p><input type="radio" name="PaymentMethod" value="UKCheque" %s> UK cheque</p>
</fieldset>
""" % (strOnlineChecked, strPayPalChecked, strBankTransferChecked, strUKChequeChecked)
    return strResult

def GetTermsAndConditions():
    return """
<fieldset>
    <legend>Terms and Conditions</legend>
    <p>No VAT charged</p>
    <p>Substitutions: Substitutions can be made up to one week before the event. A &pound;15 administration fee will be charged for substitutions with less than one month notice</p>
    <p>Cancellation of a registration: Costs may be charged of up 35% of your payment if notified on or before 20/7/08 or up to 60% after 20/7/08. Any refund will be posted to you by 30/9/08</p>
</fieldset>"""

def BuildRegisterHTML(strFormAcceptTnC, strFormDetailsCorrect, blnVerifyForm):
    blnValid = True

    if blnVerifyForm and not strFormAcceptTnC:
        strMissingAcceptTnC = """ class="MissingField" """
        blnValid = False
    else:
        strMissingAcceptTnC = ""

    if blnVerifyForm and not strFormDetailsCorrect:
        strMissingDetailsCorrect = """ class="MissingField" """
    else:
        strMissingDetailsCorrect = ""

    if strFormAcceptTnC:
        strAcceptTnCChecked = " checked "
    else:
        strAcceptTnCChecked = ""

    if strFormDetailsCorrect:
        strDetailsCorrectChecked = " checked "
    else:
        strDetailsCorrectChecked = ""

    strResult = """
<fieldset>
    <legend>Register Now</legend>
    <p %s><input type="checkbox" name="AcceptTnC" %s>I accept the terms and conditions (see above)</p>
    <p %s><input type="checkbox" name="DetailsCorrect" %s>All details are correct</p>
    <p><input type="submit" value="Confirm and continue to payment page" class="btn"></p>
</fieldset>""" % (strMissingAcceptTnC, strAcceptTnCChecked, strMissingDetailsCorrect, strDetailsCorrectChecked)
    return (strResult, blnValid)

def ECLConf08ShowSpacesRemaining(objHere):
    intRemainingCount = CountConf08Spaces(objHere)
    if intRemainingCount == 1:
        strResult = "One space remaining. Sign up now"
    elif intRemainingCount > 0:
        strResult = "Only %s spaces remaining. Sign up now" % intRemainingCount
    else:
        strResult = "Fully booked. Join the waiting list"
    return strResult

def GetFirstBooking(objMember):
    objBookings = objMember.Events.objectValues("E3Conf08Booking")
    if objBookings:
        return objBookings[0]
    else:
        return None

def StatusBlock(objMember, blnPresentersRate):
    strResult = ""
    if not objMember and not blnPresenters:
        strResult = """<p>Note: You are not currently logged in. If you are a list member log in now to claim your discount, to see your current payments and to make any outstanding payments. Or join now for your free three month trial and to benefit from the member's discount</p>"""
    else:
        objBooking = GetFirstBooking(objMember)
#        if objBooking:


def GetFormValues(objHere, lstFieldNames):
    lstResult = []
    for strFieldName in lstFieldNames:
        lstResult.append(GetParameter(objHere.REQUEST, strFieldName))
#    print "Get form values: ", lstResult
    return lstResult

def AllRequiredEntered(*lstValues):
#    print lstValues
    for varValue in lstValues:
        if not varValue:
            return False
    return True

def GetRegistrationDetails(objHere, objMember):
    (strFormName, strFormCountry, strFormTelephone, strFormEmailAddress, strRegistrationType, strPaymentMethod) = GetFormValues(objHere, ("Name", "Country", "Telephone", "EmailAddress", "RegistrationType", "PaymentMethod"))
    if objMember:
        if objMember.Name:
            strName = objMember.Name
        else:
            strName = strFormName

        strEmailAddress = objMember.EmailDeliveryAddress

        if objMember.Country:
            strCountry = objMember.Country
        else:
            strCountry = strFormCountry

        if objMember.PhoneNumber:
            strTelephone = objMember.PhoneNumber
        else:
            strTelephone = strFormTelephone
    else:
        strName = strFormName
        strEmailAddress = strFormEmailAddress
        strCountry = strFormCountry
        strTelephone = strFormTelephone

    return (strName, strCountry, strTelephone, strEmailAddress, strRegistrationType, strPaymentMethod)

def PaymentPageDetails(objHere, objMember, blnPresentersRate):
    strRegistrationType = GetParameter(objHere.REQUEST, "RegistrationType")
    strFormEmailAddress = GetParameter(objHere.REQUEST, "EmailAddress")

    (intPayNowAmount, intPayLaterAmount, intFullAmount, intDeposit, intRemainder) = GetPayNowAmount(objMember, strRegistrationType, blnPresentersRate)

    dtmToday = datetime.date.today()
    strOneWeek = (dtmToday + datetime.timedelta(days=7)).strftime(cnShortDateFormat)
    strTwoWeeks = (dtmToday + datetime.timedelta(days=14)).strftime(cnShortDateFormat)

    if intPayLaterAmount:
        strPayLaterLine = "The remaining amount of �%s must be paid by %s" % (intPayLaterAmount, cnConf08FullPaymentDate.strftime(cnShortDateFormat))
    else:
        strPayLaterLine = ""

    return (strFormEmailAddress, strOneWeek, strTwoWeeks, intPayNowAmount, intPayLaterAmount, strPayLaterLine)

def GetWelcomeBlock(blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, objRegistration, blnYetToPay = True):
    lstNew = []
    lstAlready = []
    if blnNewCCBooking:
        lstNew.append("the Core Conference")
    elif objRegistration.BookedForCC:
        lstAlready.append("the Core Conference")

    if blnNewSatEveBooking:
        lstNew.append("the Saturday evening event")
    elif objRegistration.BookedForSatEve:
        lstAlready.append("the Saturday evening event")

    if blnNewSunAmBooking:
        lstNew.append("the Sunday morning workshop")
    elif objRegistration.BookedForSunAm:
        lstAlready.append("the Sunday morning workshop")

    strNew = ListToText(lstNew)
    if strNew:
        strNew = "<p>You are now registered for %s</p>" % strNew
    else:
        strNew = "<p>You were already registered. Perhaps you submitted the form twice</p>"

    strAlready = ListToText(lstAlready)
    if strAlready:
        strAlready = "<p>You were already registered for %s</p>" % strAlready

    if blnYetToPay:
        strNextStep = "<p>Please follow the payment instructions below</p>"
    else:
#        strNextStep = "Please use the form below to tell us about your preferences for the rest of the conference"
        strNextStep = ""
    return """
<fieldset>
    <legend>You are registered</legend>
    <h2>Welcome</h2>
    %s
    %s
    %s
</fieldset>
""" % (strNew, strAlready, strNextStep)

def PaymentInfo(objHere, objRegistration, strPaymentMethod):

    intRemainingAmount = objRegistration.RemainingAmount
    if not intRemainingAmount:
        return ("", "")

    strEmailAddress = objRegistration.EmailAddress

    if strPaymentMethod == "PayPal":
        strPaymentInfo = "Please send a payment for £%s using PayPal to coen@coachcoen.com now" % intRemainingAmount
    elif strPaymentMethod == "BankTransfer":
        strPaymentInfo = """Please transfer £%s now to:
Account name: Compass Mentis
Sort code: 83-15-26
Account Number:00683788
""" % intRemainingAmount
    elif strPaymentMethod == "UKCheque":
        strPaymentInfo = """Please send a UK cheque, payable to "Compass Mentis" for £%s now to:

Coen de Groot
56 Fairfield Road
Bristol  BS6 5JP

""" % intRemainingAmount

    strPaymentInfo += """
You may lose your registration if the money does not arrive by Wednesday 10th September"""

    strPaymentInfoHTML = InsertParagraphs(strPaymentInfo).replace('"', "&quot;").replace('£', "&pound;")

    strPaymentInfoHTML = """<fieldset>
    <legend>Your Payment</legend>
    <p>%s</p>
    <p>A reminder of this information has been emailed to %s</p>
</fieldset>""" % (strPaymentInfoHTML, strEmailAddress)

    strPaymentInfo = """Here is a reminder of the payment details:
-----------------------
%s
-----------------------
""" % strPaymentInfo

    return (strPaymentInfo, strPaymentInfoHTML)

def AddToRegistrationHistory(objRegistration, strInfo, strDate = ""):

    if not strDate:
        strDate = datetime.date.today().strftime(cnShortDateFormat)

    objRegistration.History = objRegistration.History + (strDate + ": " + strInfo, )

def RecordBasicConferenceRegistration(objHere, objMember):
    # What might this registration be:
        # 1. Payment promise
        # 2. Start of online payment

    # Already has a booking?
    objConfBooking = None
    strEmailAddress = GetParameter(objHere, "EmailAddress")

    if not objMember:
#        print "Searching for %s" % strEmailAddress
        objEmailAddress = SearchOne(objHere, "E3EmailAddress", "EmailAddressField", strEmailAddress)
        if objEmailAddress:
#            print "Found"
            objMember = objEmailAddress.unrestrictedTraverse("..")

    if objMember:
        objConfBooking = GetFirstBooking(objMember)

    if not objConfBooking:
        objConfBooking = GetRegistrationForEmailAddress(objHere, strEmailAddress)


#    if objConfBooking:
#        print "Booking found: ", objConfBooking.id
#        print "Stored in: ", objConfBooking.unrestrictedTraverse("..").id
#        print "Within: ", objConfBooking.unrestrictedTraverse("../..").id

    if not objConfBooking:
#        print "Member found: ", objMember.id
        dodConfBooking = GetDOD(objHere, "E3Conf08Booking")
        if objMember:
            objConfBooking = dodConfBooking.NewObject(objMember.Events)
        else:
            objConfBooking = dodConfBooking.NewObject()
        # Now fill in basic details

        (strName, strCountry, strTelephone, strEmailAddress, strRegistrationType, strPaymentMethod) = GetRegistrationDetails(objHere, objMember)

        objConfBooking.SetDateCreated(datetime.date.today())
        objConfBooking.Name = strName
        objConfBooking.Country = strCountry
        objConfBooking.Telephone = strTelephone
        objConfBooking.EmailAddress = strEmailAddress
        Catalogue(objConfBooking)
    return objConfBooking

def FiveChoices(strName):
    strResult = """
<input type="radio" name="%(Name)s" value="1"> 1 &nbsp;&nbsp;
<input type="radio" name="%(Name)s" value="2"> 2 &nbsp;&nbsp;
<input type="radio" name="%(Name)s" value="3" checked> 3 &nbsp;&nbsp;
<input type="radio" name="%(Name)s" value="4"> 4 &nbsp;&nbsp;
<input type="radio" name="%(Name)s" value="5"> 5 """ % {'Name': strName}
    return strResult

def ConferencePreferencesPage(objHere, strConfBookingId, strURL):
    strResult = """
<fieldset>
    <legend>Your Preferences</legend>
    <p>Now that you are registered for the Core Programme, <br><b>please tell us your preferences for the rest of the conference</b></p>
<form action="%s" method="post">
    <input type="hidden" name="ConfBookingId", value="%s"
    <fieldset>
        <legend>Friday Evening</legend>
        <p>Please score from 1 (no/won't come) to 5 (yes/will come)</p>
        <p><label>I'll be there</label> %s</p>
        <p><label>Informal meal</label> %s</p>
        <p><label>Other:</label> <input type="text" size="45" name="FriEveOther"></p>
    </fieldset>

    <fieldset>
        <legend>Saturday Evening</legend>
        <p>Please score from 1 (no/won't come) to 5 (yes/will come)</p>
        <p><label>I'll be there</label> %s</p>
        <p>Note: All of the following will include a meal before/after/during</p>
        <p><label>Ceilidh, barn dance</label> %s</p>
        <p><label>Leroc, Ceroc</label> %s</p>
        <p><label>Salsa</label> %s</p>
        <p><label>Ballroom dance</label> %s</p>
        <p><label>Quiz night</label> %s</p>
        <p><label>Music by delegates</label> %s</p>
        <p><label>Adventure walk</label> %s</p>
        <p><label>Other:</label> <input type="text" size="45" name="SatEveOther"></p>
    </fieldset>

    <fieldset>
        <legend>Sunday Morning</legend>
        <p>Please score from 1 (no/won't come) to 5 (yes/will come)</p>
        <p><label>I'll be there</label> %s</p>
        <p><label>Additional conference sessions</label> %s</p>
        <p><label>Other:</label> <input type="text" size="45" name="SunAmOther"></p>
    </fieldset>

    <fieldset>
        <legend>Sunday Lunch</legend>
        <p>Please score from 1 (no/won't come) to 5 (yes/will come)</p>
        <p><label>I'll be there</label> %s</p>
        <p><label>Informal meal</label> %s</p>
        <p><label>Other:</label> <input type="text" size="45" name="SunLunchOther"></p>
    </fieldset>

    <fieldset>
        <legend>Your comments</legend>
        <p><textarea name="Comments" cols="50" rows="5"></textarea></p>
    </fieldset>

    <input type="hidden" name="Action" value="SavePrefences">
    <input type="submit" value="Save my preferences" class="btn">
</form>
</fieldset>
    """ % (strURL, strConfBookingId,
        FiveChoices("FriEvePresence"),
        FiveChoices("FriEveInformalMeal"),
        FiveChoices("SatEvePresence"),
        FiveChoices("SatEveCeilidh"),
        FiveChoices("SatEveLeroc"),
        FiveChoices("SatEveSalsa"),
        FiveChoices("SatEveBallroom"),
        FiveChoices("SatEveQuiz"),
        FiveChoices("SatEveOwnMusic"),
        FiveChoices("SatEveAdvWalk"),
        FiveChoices("SunAmPresence"),
        FiveChoices("SunAmSessions"),
        FiveChoices("SunLunchPresence"),
        FiveChoices("SunLunchInformalMeal"))

    return strResult

def CreatePreferencesList(objHere):
    lstResult = []
    for strName in ("FriEvePresence", "FriEveInformalMeal", "FriEveOther", "SatEvePresence", "SatEveCeilidh", "SatEveLeroc", "SatEveSalsa", "SatEveBallroom", "SatEveQuiz", "SatEveOwnMusic", "SatEveAdvWalk", "SatEveOther", "SunAmPresence", "SunAmSessions", "SunAmOther", "SunLunchPresence", "SunLunchInformalMeal", "SunLunchOther"):
        strChoice = GetParameter(objHere.REQUEST, strName)
        lstResult.append("%s: %s" % (strName, strChoice))
    return lstResult

def RecordConferencePreferences(objHere, objMember):
    strConfBookingId = GetParameter(objHere.REQUEST, "ConfBookingId")
    objConfBooking = SearchOne(objHere, "E3Conf08Booking", "id", strConfBookingId)
    if objConfBooking:
        lstPreferences = CreatePreferencesList(objHere)
        objConfBooking.Preferences = lstPreferences
        objConfBooking.Comments = GetParameter(objHere.REQUEST, "Comments")
    else:
        print "Booking not found: %s" % strConfBookingId

def PreferencesSavedPage(objHere):
    return """<p>Thanks for telling us your preferences</p>
<p>We will keep you informed by email about the programme</p>"""

def SendRegistrationEmail(objHere, strPaymentInfo, strEmailAddress, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking):
    strBookedFor = GetBookedFor(blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking)
    if blnNewCCBooking or blnNewSatEveBooking:
        strDietaryReqs = """In the meantime, if you have any special dietary requirements, please let me know by Thursday 4th September"""
    else:
        strDietaryReqs = ""

    strMessage = """Thank you for registering for %s of the first Euro Coach List Conference

The conference will be held on Saturday and Sunday 20th and 21st September 2008, in Bristol, UK

We will send you more information later. %s

%s
All the best,

Coen""" % (strBookedFor, strDietaryReqs, strPaymentInfo.replace("£", "GBP"))
    strSubject = "Euro Coach List Conference Registration"

    SendEmail(objHere, strMessage, strSubject, strEmailAddress)

def SendAccommodationInfo(objHere, strEmailAddress):
    strMessage = u"""
We have negotiated a special rate at one of the local hotels, the Thistle Bristol Hotel

Information about this hotel, other local hotels and the local Youth Hostel, is at
http://www.eurocoachlist.com/Events/ECLConference08/Accommodation

Here is the information you need to book the accommodation at the special conference rates:

Thistle Bristol Hotel
* £75 BB per Standard Double/Twin Room (Sole occupancy)
* £95 BB per Deluxe Double Room (Sole Occupancy)
* To book call Sharon on 0117 930 3307 or Katie on 0117 930 3312, or email rbristol@thistle.co.uk. Reference: "Euro Coach List Conference"

Note: Rates quoted are for the nights of Friday 19th September and/or Saturday 20th September
"""

    strSubject = "Euro Coach List Conference Accommodation"

    SendEmail(objHere, strMessage, strSubject, strEmailAddress)

def AddToWaitingList(objHere, dictData):
    strMessage = """One more for the waiting list:
Name: %s
Email Address: %s
""" % (dictData["Name"], dictData["EmailAddress"])

    strSubject = "ECL Conference Waiting List"

    SendEmail(objHere, strMessage, strSubject, "coen@coachcoen.com")

    return """
<p>Thanks for your interest in the Euro Coach List conference</p>
<p>We will let you know when a space becomes available</p>
    """

def CountConf08Spaces(objHere):
    lstBookings = SearchMany(objHere, "E3Conf08Booking", "None", "")
    intBookings = 0
    for objBooking in lstBookings:
        if (objBooking.PaymentMethod <> "Online" or objBooking.InvoiceNumber) and objBooking.BookedForCC:
            intBookings += 1
#    intBookings = len(lstBookings)
    intReserved = objHere.unrestrictedTraverse('/Data/E3').Conf08Reserved
    return 100 - intBookings - intReserved

def ShowWaitingList(objHere, objMember, blnDoAdd):
    dictData = {}
    strErrors = ""
    strResult = ""

    lstFields = ("EmailAddress", "Name")

    if blnDoAdd:
        dictData = GetDataFromForm(objHere, objHere.REQUEST.form, lstFields)
        if not dictData["Name"] or not dictData["EmailAddress"]:
            strErrors = """<p class="ErrorMessage">One or both fields are missing. Please fill in all fields</p>\n"""
        elif not ValidEmailAddress(dictData["EmailAddress"]):
            strErrors = """<p class="ErrorMessage">Invalid email address. Please enter a valid email address and submit again</p>\n"""
    elif objMember:
        dictData["EmailAddress"] = objMember.PreferredEmailAddress()
        dictData["Name"] = objMember.Name
        if not dictData["Name"]:
            dictData["Name"] = objMember.Name

    if strErrors:
        strResult = strErrors
    elif blnDoAdd:
        dictErrors = CheckRequiredFields(dictData, lstFields)
        if not dictErrors:
            return AddToWaitingList(objHere, dictData)

    lstForm = (Fieldset("Waiting list", None,
                Paragraph(PureText("The conference is now full. Please use this form to be added to the waiting list")),
                Paragraph(TextControl("Name", "Name")),
                Paragraph(TextControl("Email Address", "EmailAddress")),
                Paragraph(SubmitControl("Add to waiting list"))),)

    strResult += CreateForm(objHere, lstForm, dictData, ".", {})

    return strResult

def DetermineBookingChanges(objHere, objRegistration, blnPresentersRate, objMember):
    (strBookForCC, strBookForSatEve, strBookForSunAm) = GetFormValues(objHere, ("BookForCC", "BookForSatEve", "BookForSunAm"))
    blnNewCCBooking = False
    blnNewSatEveBooking = False
    blnNewSunAmBooking = False
    blnClaimCCDiscount = False
    blnClaimSunAmDiscount = False

    if strBookForCC and not objRegistration.BookedForCC:
        blnNewCCBooking = True
        if not blnPresentersRate and objMember:
            blnClaimCCDiscount = True

    if strBookForSatEve and not objRegistration.BookedForSatEve:
        blnNewSatEveBooking = True

    if strBookForSunAm and not objRegistration.BookedForSunAm:
        blnNewSunAmBooking = True

    if blnNewSunAmBooking and (objRegistration.BookedForCC or blnNewCCBooking or objMember or blnPresentersRate):
        blnClaimSunAmDiscount = True

    if blnNewCCBooking and objRegistration.BookedForSunAm and not objMember:
        blnClaimSunAmDiscount = True

    return (blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, blnClaimCCDiscount, blnClaimSunAmDiscount)

def DetermineBookingAmounts(objRegistration, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, blnClaimCCDiscount, blnClaimSunAmDiscount, blnPresentersRate):
    intNewAmount = 0
    intDiscount = 0
    if blnNewCCBooking:
        if blnPresentersRate:
            intNewAmount += 74
        else:
            intNewAmount += 99

    if blnNewSatEveBooking:
        intNewAmount += 20

    if blnNewSunAmBooking:
        intNewAmount += 50

    if blnClaimCCDiscount:
        intDiscount += 10

    if blnClaimSunAmDiscount:
        intDiscount += 10

    intCurrentAmount = objRegistration.RemainingAmount + intNewAmount - intDiscount

    return (intNewAmount, intDiscount, intCurrentAmount)

def RecordBookingHistory(objRegistration, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, blnClaimCCDiscount, blnClaimSunAmDiscount, intNewAmount, intDiscount, intCurrentAmount, blnPresentersRate, strPaymentMethod):
    if blnNewCCBooking:
        if blnPresentersRate:
            AddToRegistrationHistory(objRegistration, "Booked for Core Conference, at GBP74 presenters rate")
        else:
            AddToRegistrationHistory(objRegistration, "Booked for Core Conference, at GBP99")

    if blnClaimSunAmDiscount:
        AddToRegistrationHistory(objRegistration, "Claimed GBP10 members' discount")

    if blnNewSatEveBooking:
        AddToRegistrationHistory(objRegistration, "Booked for Saturday evening event, at GBP20")

    if blnNewSunAmBooking:
        AddToRegistrationHistory(objRegistration, "Booked for Sunday morning event, at GBP50")
    if blnClaimSunAmDiscount:
        AddToRegistrationHistory(objRegistration, "Claimed GBP10 discount")

    if intNewAmount:
        AddToRegistrationHistory(objRegistration, "Total amount added: GBP%s" % (intNewAmount - intDiscount))

    if objRegistration.RemainingAmount:
        AddToRegistrationHistory(objRegistration, "Added to the remaining amount of GBP%s" % objRegistration.RemainingAmount)

    AddToRegistrationHistory(objRegistration, "Current amount outstanding: GBP%s" % intCurrentAmount)

    AddToRegistrationHistory(objRegistration, "Payment (promised) by %s" % strPaymentMethod)

    if blnNewCCBooking:
        objRegistration.BookedForCC = True

    if blnNewSatEveBooking:
        objRegistration.BookedForSatEve = True

    if blnNewSunAmBooking:
        objRegistration.BookedForSunAm = True

    objRegistration.RemainingAmount = intCurrentAmount

def SendBookingEmails(objHere, objRegistration, strFormPaymentMethod, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, intAmount):
    strEmailAddress = objRegistration.EmailAddress
    (strPaymentInfo, strPaymentInfoHTML) = PaymentInfo(objHere, objRegistration, strFormPaymentMethod)
    SendRegistrationEmail(objHere, strPaymentInfo, strEmailAddress, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking)
    SendAccommodationInfo(objHere, strEmailAddress)
    strBookedFor = GetBookedFor(blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking)
    SendConfStatistics(objHere, objRegistration, intAmount, strBookedFor)

def GetBookedFor(blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking):
    lstBookedFor = []

    if blnNewCCBooking:
        lstBookedFor.append("the Core Conference")
    if blnNewSatEveBooking:
        lstBookedFor.append("the Saturday evening event")
    if blnNewSunAmBooking:
        lstBookedFor.append("the Sunday morning workshop")
    strBookedFor = ListToText(lstBookedFor)
    return strBookedFor

def ProcessRegistrationRequest(objHere, objMember, blnPresentersRate):

    (strRegistrationForm, blnReadyToPay) = ConferenceRegistrationPage(objHere, objMember, True, blnPresentersRate)

    if blnReadyToPay:
        objRegistration = RecordBasicConferenceRegistration(objHere, objMember)

        strFormPaymentMethod = GetParameter(objHere, "PaymentMethod")

        (blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, blnClaimCCDiscount, blnClaimSunAmDiscount) = DetermineBookingChanges(objHere, objRegistration, blnPresentersRate, objMember)

        (intNewAmount, intDiscount, intCurrentAmount) = DetermineBookingAmounts(objRegistration, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, blnClaimCCDiscount, blnClaimSunAmDiscount, blnPresentersRate)

        RecordBookingHistory(objRegistration, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, blnClaimCCDiscount, blnClaimSunAmDiscount, intNewAmount, intDiscount, intCurrentAmount, blnPresentersRate, strFormPaymentMethod)

        if strFormPaymentMethod == "Online":
            # Create the WorldPay record,
            strDescription = "Euro Coach List Conference 2008"
            objRegistration.InProgressForCC = blnNewCCBooking
            objRegistration.InProgressForSatEve = blnNewSatEveBooking
            objRegistration.InProgressForSunAm = blnNewSunAmBooking
            return StartConferencePayment(objHere, objRegistration, strDescription)
        else:
            SendBookingEmails(objHere, objRegistration, strFormPaymentMethod, blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, intNewAmount - intDiscount)

            (strPaymentInfo, strPaymentInfoHTML) = PaymentInfo(objHere, objRegistration, strFormPaymentMethod)
            strResult = GetWelcomeBlock(blnNewCCBooking, blnNewSatEveBooking, blnNewSunAmBooking, objRegistration) + strPaymentInfoHTML
    else:
        strResult = strRegistrationForm

    return strResult

def GetEmailAddressForRegistration(objHere, strEmailAddress = ""):
    strResult = ""
    if strEmailAddress:
        strResult += """<p class="ErrorMessage">Incorrect email address. Please try again</p>"""
    strResult += """
<fieldset>
    <legend>Your email address</legend>
    <p>Please enter your email address, or log in (using the form in the left of the screen)</p>
    <form action = "/Events/ECLConference08/PayRemainder" method="post">
        <p>Email address <input type="text" name="EmailAddress" value="%s"></p>
        <p><input type="submit" value="Submit"></p>
    </form>
</fieldset>""" % strEmailAddress
    return strResult

def GetRegistrationForEmailAddress(objHere, strEmailAddress):
    strEmailAddress = strEmailAddress.lower()

    # Search 1: Any list members with this email address
    objEmailAddress = SearchOne(objHere, "E3EmailAddress", "EmailAddress", strEmailAddress)
    if objEmailAddress:
        objMember = objEmailAddress.unrestrictedTraverse("..")
        objBooking = GetFirstBooking(objMember)
        return objBooking

    # Search 2: Any member registrations with this email address
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objBooking in objMember.Events.objectValues("E3Conf08Booking"):
                if objBooking.EmailAddress == strEmailAddress:
                    return objBooking

    # Search 3: Any non-member registrations with this email address
    for objBooking in objHere.unrestrictedTraverse("/Data/E3/E3Conf08Booking").objectValues("E3Conf08Booking"):
        if objBooking.EmailAddress == strEmailAddress:
            return objBooking

    return None

def OutstandingPaymentsPage(objHere):
    # Member, has registration and has outstanding payments - go straight to WorldPay
    # Member, no registration - error message
    # Member, registration, no outstanding payments - error message
    # No member, no email address entered - error message
    # No member, email address entered (form or parameter) - go straight to WorldPay
    objMember = GetCurrentMember(objHere)
    if objMember:
        objRegistration = GetFirstBooking(objMember)
    else:
        strEmailAddress = GetParameter(objHere, "PaymentEmailAddress")
        if strEmailAddress:
            if ValidEmailAddress(strEmailAddress):
                objRegistration = GetRegistrationForEmailAddress(objHere, strEmailAddress)
            else:
                strResult = GetEmailAddressForRegistration(objHere, strEmailAddress)
                return strResult
        else:
            strResult = GetEmailAddressForRegistration(objHere)
            return strResult

    if not objRegistration:
        strResult = """<p>You are not registered for the Euro Coach List Conference and do not have any outstanding payments</p>
            <p>To register for the conference please go to <a href="/Events/ECLConference08/Register">Registration Page</a></p>"""
        return strResult

    if not objRegistration.RemainingAmount:
        strResult = """<p>You do not have any outstanding payments</p>"""
        if objMember:
            strResult += """<p>For more information about your conference registration please go to <a href="/Events/ECLConference08/Register">Registration Page</a></p>"""
        else:
            strResult += """<p>For any questions about your registration please <a href="/ContactDetails">contact the list owner</p>"""
        return strResult

    strDescription = "Euro Coach List Conference 2008 - Outstanding payment"
    strResult = StartConferencePayment(objHere, objRegistration, strDescription)
    return strResult

def OutstandingPaymentsBlock(objRegistration):
    strResult = """
<fieldset>
    <legend>Outstanding payment</legend>
    <p>You have an outstanding payment of &pound;%(Amount)s</p>
    <p>You can pay the outstanding amount when you register and pay for any additional parts of the conference. Or pay the outstanding amount online now on the <a href="/Events/ECLConference08/PayRemainder">payment page</a>, or see at the end of the page for <a href="#PaymentInstructions">payment instructions</a></p>
</fieldset>""" % {"Amount": objRegistration.RemainingAmount}
    return strResult

def OutstandingPaymentsBlock2(objRegistration):
    strResult = """
<fieldset>
    <a id="PaymentInstructions"></a>
    <legend>Payment Instructions</legend>
    <p>You have an outstanding payment of &pound;%(Amount)s</p>
    <p>Please pay now, as follows:
        <ul>
        <li>Online: Go to the <a href="/Events/ECLConference08/PayRemainder">online payment page</a>
        <li>PayPal: Send a payment for &pound;%(Amount)s using PayPal to coen@coachcoen.com</li>
        <li>UK bank transfer: Transfer &pound;%(Amount)s to:<br>
Account name: Compass Mentis<br>
Sort code: 83-15-26<br>
Account Number:00683788</li>
        <li>UK cheque: Send a UK cheque, payable to "Compass Mentis" for &pound;%(Amount)s  to:<br>
Coen de Groot<br>
56 Fairfield Road<br>
Bristol  BS6 5JP</li>
    </ul>
</fieldset>""" % {"Amount": objRegistration.RemainingAmount}
    return strResult

def ShortRegistrationBlock(objHere, objMember, blnPresentersRate, blnVerifyForm):
    blnRegistration = False
    blnWaitingList = False
    blnBlockValid = True
    strErrorMessage = ""

    (strBookForCC, strBookForSatEve, strBookForSunAm) = GetFormValues(objHere, ("BookForCC", "BookForSatEve", "BookForSunAm"))
    if blnVerifyForm and not (strBookForCC + strBookForSatEve + strBookForSunAm):
        blnBlockValid = False
        strErrorMessage = """<p class="ErrorMessage">Please select at least one event</p>"""

    if objMember:
        objRegistration = GetFirstBooking(objMember)
    else:
        objRegistration = None
    if objRegistration:
        blnBookedForCC = objRegistration.BookedForCC
        blnBookedForSatEve = objRegistration.BookedForSatEve
        blnBookedForSunAm = objRegistration.BookedForSunAm
    else:
        blnBookedForCC = False
        blnBookedForSatEve = False
        blnBookedForSunAm = False

    # options:
    # 1. Booked for all events
        # Just show info
    # 2. Not yet booked for CC, no spaces available, booked for both other events
        # Can only reserve, show CanBook, ask for email address and phone number only (if not logged in)
    # 3. Not yet booked for at least one event for which spaces are available
        # Normal registration

    strCanBook = ""

    if blnBookedForCC:
        strCanBook += """
<p><input type="checkbox" disabled name="BookForCC"><b>Core Conference</b> (already booked), Saturday 9am - 5.30pm</p>"""
    else:
        intRemainingCount = CountConf08Spaces(objHere)
        if blnPresentersRate or intRemainingCount > 0:
            blnRegistration = True
            strCanBook += """
<p><input type="checkbox" name="BookForCC" %s><b>Core Conference</b>, Saturday 9am - 5.30pm, including lunch and refreshments: &pound;99 full price, &pound;10 discount for Euro Coach List members</p>""" % ShowChecked(strBookForCC)
        else:
            blnWaitingList = True

    if blnBookedForSatEve:
        strCanBook += """
<p><input type="checkbox" disabled name="BookForSatEve"><b>Saturday evening dinner</b> (already booked)</p>"""
    else:
        blnRegistration = True
        strCanBook += """
<p><input type="checkbox" name="BookForSatEve" %s><b>Saturday evening dinner</b>: &pound;20</p>""" % ShowChecked(strBookForSatEve)

    if blnBookedForSunAm:
        strCanBook += """
<p><input type="checkbox" disabled name="BookForSunAm"><b>Sunday morning Coaching Master-Class</b> (already booked)</p>"""
    else:
        blnRegistration = True
        strCanBook += """
<p><input type="checkbox" name="BookForSunAm" %s><b>Sunday morning Coaching Master-Class</b>, including refreshments: &pound;50 full price, &pound;10 discount for Core Conference attendees and Euro Coach List members</p>""" % ShowChecked(strBookForSunAm)

    if blnRegistration and not objMember:
            strCanBook += """
<p>Already registered for any part of the conference? To claim your discount make sure to enter the same email address as for your previous registration. Or if you are a Euro Coach List member, just log in first</p>"""

    strResult = ""

    if blnWaitingList:
        strResult = """
<fieldset>
    <legend>Core Conference Waiting list</legend>
<p class="ErrorMessage">The Core Conference is now fully booked</p>
<p>To be put on the waiting list, please email <a href="mailto:coen@coachcoen.com">coen@coachcoen.com</a></p>
</fieldset"""

    if blnRegistration:
        strResult += """
<fieldset>
    <legend>Conference Sessions</legend>
    %s
    %s
</fieldset""" % (strErrorMessage, strCanBook)
    elif blnWaitingList:
        strResult += """
<fieldset>
    <legend>Registration complete</legend>
    <p>You are registered for the Saturday evening get-together and Sunday morning Coaching Master-Class</p>
</fieldset>"""
    else:
        strResult += """
<fieldset>
    <legend>Registration complete</legend>
    <p>You are registered for the Core Conference, Saturday evening get-together and Sunday morning Coaching Master-Class</p>
</fieldset>"""

    return (strResult, blnRegistration, blnWaitingList, blnBlockValid)

def PresentersRatesBlock():
    strResult = """
<fieldset>
    <legend>Presenter's rates<legend>
    <p>Presenters get the following rates:</p>
    <ul>
        <li>Core Conference: &pound;74</li>
        <li>Saturday evening dinner: &pound;20</li>
        <li>Sunday morning Coaching Master-Class: &pound;40</li>
    </ul>
    <p>No other discounts apply</p>
</fieldset>"""
    return strResult

def FormatBookingHistory(lstHistory):
    strHistory = ""
    for strLine in lstHistory:
        strHistory += "<p>%s</p>\n" % strLine

    strHistory = strHistory.replace("GBP", "&pound;")
    return strHistory


def GetBookingHistory(objMember):
    if not objMember:
        return ""

    objRegistration = GetFirstBooking(objMember)
    if not objRegistration:
        return ""

    if not objRegistration.History:
        return ""

    strHistory = FormatBookingHistory(objRegistration.History)

    return """
<fieldset>
    <legend>Your registration history</legend>
    %s
</fieldset>
""" % strHistory

def GetMemberDetails(objMember):
    if objMember:
        strMemberName = objMember.Name
        strMemberEmailAddress = objMember.PreferredEmailAddress()
        strMemberCountry = objMember.Country
        strMemberTelephone = objMember.PhoneNumber
    else:
        strMemberName = ""
        strMemberEmailAddress = ""
        strMemberCountry = ""
        strMemberTelephone = ""
    return (strMemberName, strMemberEmailAddress, strMemberCountry, strMemberTelephone)

def RegisteredDetailsBlock(objHere, objMember, blnVerifyForm, blnFullDetailsRequired):
    strResult = ""

    strFormName = ""
    strFormCountry = ""
    strFormTelephone = ""
    strEmailAddress = ""
    strRegistrationType = ""
    strFormPaymentMethod = ""

    strWarningMessage = ""

    blnReadyToPay = False

    (strMemberName, strMemberEmailAddress, strMemberCountry, strMemberTelephone) = GetMemberDetails(objMember)

    (strFormName, strFormCountry, strFormTelephone, strFormEmailAddress) = GetFormValues(objHere, ("Name", "Country", "Telephone", "EmailAddress"))

    (strRegisteredDetails, strAdditionalDetails, blnBlockValid) = BuildDetailsBlocks(strMemberName, strFormName, strMemberCountry, strFormCountry, strMemberTelephone, strFormTelephone, strMemberEmailAddress, strFormEmailAddress, blnVerifyForm, blnFullDetailsRequired)

    if strRegisteredDetails:
        strResult += """
<fieldset>
    <legend>Your registered details</legend>
    <p>You can change your details on your <a href="/MyECL/Profile">profile page</a></p>
    %s
</fieldset>""" % strRegisteredDetails
        strDetailsTitle = "Additional details"
    else:
        strDetailsTitle = "Your details"

    strResult += """
<fieldset>
    <legend>%s</legend>
        %s
</fieldset>""" % (strDetailsTitle, strAdditionalDetails)
    return (strResult, blnBlockValid)

def ConferenceRegistrationPage(objHere, objMember, blnVerifyForm, blnPresentersRate):
    strResult = ""
    blnPageCorrect = True
    blnOldPayments = False

    strResult += """
    <form action="." method="post">
        <input type="hidden" name="Action" value="ProcessRegistrationRequest">"""

    objRegistration = None
    if objMember:
        objRegistration = GetFirstBooking(objMember)

    if objRegistration:
        if objRegistration.RemainingAmount:
            blnOldPayments = True
            strResult += OutstandingPaymentsBlock(objRegistration)

    if blnPresentersRate:
        strResult += PresentersRatesBlock()

    (strRegistrationBlock, blnRegistration, blnWaitingList, blnBlockValid) = ShortRegistrationBlock(objHere, objMember, blnPresentersRate, blnVerifyForm)
    strResult += strRegistrationBlock
    if not blnRegistration:
        strResult += GetBookingHistory(objMember)
        if blnOldPayments:
            strResult += OutstandingPaymentsBlock2(objRegistration)
        return (strResult, True)
    if not blnBlockValid:
        blnPageCorrect = False

    if not objRegistration:
        (strBlock, blnBlockValid) = RegisteredDetailsBlock(objHere, objMember, blnVerifyForm, blnRegistration)
        strResult += strBlock
        if not blnBlockValid:
            blnPageCorrect = False

    (strRegistrationType, strFormPaymentMethod) = GetFormValues(objHere, ("RegistrationType", "PaymentMethod"))
    strResult += BuildPaymentOptionsBlock(strFormPaymentMethod)

    strResult += GetTermsAndConditions()

    (strFormAcceptTnC, strFormDetailsCorrect) = GetFormValues(objHere, ("AcceptTnC", "DetailsCorrect"))

    (strRegisterBlock, blnBlockValid) = BuildRegisterHTML(strFormAcceptTnC, strFormDetailsCorrect, blnVerifyForm)

    strResult += strRegisterBlock

    if not blnBlockValid:
        blnPageCorrect = False

    strResult += "\n</form>"

    strResult += GetBookingHistory(objMember)

    if blnOldPayments:
        strResult += OutstandingPaymentsBlock2(objRegistration)

    return (strResult, blnPageCorrect)

def ECLConf08Register(objHere, blnPresentersRate = False):
# When first, show full form
# Submit - check that all details have been filled in
# If details missing, show form again, with previous details there, plus message to show what went wrong
# Once all details are there, record the details, generate an payment id, create an automatic forward page to WorldPay
# WorldPay comes back - loading the Zope page, which then processes the payment

    strAction = GetParameter(objHere.REQUEST, "Action")

    objMember = GetCurrentMember(objHere)

    if strAction == "ProcessRegistrationRequest":
        return ProcessRegistrationRequest(objHere, objMember, blnPresentersRate)

    (strResult, blnDummy) = ConferenceRegistrationPage(objHere, objMember, False, blnPresentersRate)
    return strResult

#    if strAction == "AddToWaitingList":
#        strResult = AddToWaitingList(objHere, objMember)
#    elif strAction == "ConfirmRegistration":
#        strId = RecordConferenceRegistration(objHere, objMember, False, blnPresentersRate)
#        strResult = RegistrationConfirmedPage(objHere, objMember) + \
#            ConferenceRegistrationPage(objHere, objMember, False, blnPresentersRate)

#        strErrorMessage = ValidateRegistration(objHere, objMember, objRegistration)
#        if strErrorMessage:
#            strResult = strErrorMessage + ConferenceRegistrationPage(objHere, objMember, False, blnPresentersRate)
#        else:
            # if online payment
                # record the details
                # go to WorldPay page
            # if not online payment
                # record registration
                # show how to pay
                # send emails, etc
#        strResult = PayForRegistration(objHere, objMember, blnPresentersRate)

def CBARegister(objHere):
    pass

def GetCBAFormDetails(objHere):
    try:
        objForm = objHere.REQUEST.form
    except:
        return (False, "", "", "")

    if not objForm.has_key("Name") or not objForm.has_key("EmailAddress"):
        return (False, "", "", "")

    return (True, objForm["Name"], objForm["EmailAddress"])

def CheckCBA01GQForm(objHere, strName, strEmailAddress):
    if not strName:
        if not strEmailAddress:
            return (False, "Name and email address are missing. Please enter these required details")
        else:
            return (False, "Name is missing. Please enter the name")
    if not strEmailAddress:
        return (False, "Email address is missing. Please enter an email address")

    if not ValidEmailAddress(strEmailAddress):
        return (False, "Invalid email address. Please enter a valid email address")

    objRegistration = SearchOne(objHere, "E3EventRegistration", "EmailAddress", strEmailAddress)
    if objRegistration:
        return (False, "This email address is already registered")

    return (True, "")

def RebuildCBA01GQForm(objHere, strName, strEmailAddress, strMessage):
    strURL = objHere.REQUEST.VIRTUAL_URL
    strResult = """
<p class="ErrorMessage">%s</p>
<form action="%s" method="post">
	<fieldset>
		<legend>Sign up now</legend>
		<p>
			<label>Your name</label>
			<input type="text" name="Name" value="%s">
		</p>
		<p>
			<label>Your email address</label>
			<input type="text" name="EmailAddress" value="%s">
		</p>
		<p>
			<input type="submit" value="Sign up">
		</p>
	</fieldset>
</form>""" % (strMessage, strURL, strName, strEmailAddress)
    return strResult

def SendCBA01SilverRegistrationMessage(objHere, strEmailAddress):
    strMessage = """Welcome to the Coaching Business Accelerator

You will receive the first module on Monday 22nd October

All the best,

Coen

P.S. You can still upgrade to the Gold e-Workshop to receive expert support and join the learning community

For more information and to upgrade go to
http://www.EuroCoachList.com/Events/CoachingBusinessAccelerator/ToGold
"""
    strSubject = "Coaching Business Accelerator registration"
    SendEmail(objHere, strMessage, strSubject, strEmailAddress)

def SendCBA01GoldRegistrationMessage(objHere, strEmailAddress):
    strMessage = """Welcome to the Coaching Business Accelerator Gold e-Workshop

You will receive the first module on Monday 22nd October. You will also be signed up for the expert support and learning community by that date

For any questions, feel free to email me at this address (coen@coachcoen.com)

All the best,

Coen"""
    strSubject = "Coaching Business Accelerator registration"
    SendEmail(objHere, strMessage, strSubject, strEmailAddress)

def SendCBA01GoldUpgradeMessage(objHere, strEmailAddress):
    strMessage = """Welcome to the Coaching Business Accelerator Gold e-Workshop

You will receive the first module on Monday 22nd October. You will also be signed up for the expert support and learning community by that date

For any questions, feel free to email me at this address (coen@coachcoen.com)

All the best,

Coen"""
    strSubject = "Coaching Business Accelerator Upgrade to Gold e-Workshop"
    SendEmail(objHere, strMessage, strSubject, strEmailAddress)

def GetRegistrationCounts(objHere, strEvent):
    lstRegistrations = SearchMany(objHere, "E3EventRegistration", "Event", strEvent)
    if lstRegistrations:
        intSilverCount = 0
        intGoldCount = 0
        intARCount = 0
        for objRegistration in lstRegistrations:
            try:
                strRegistrationType = objRegistration.RegistrationType
                strVersion = strRegistrationType[5]
            except:
                strRegistrationType = ""
                strVersion = ""
            if strVersion == "S":
                intSilverCount += 1
            elif strVersion == "G":
                intGoldCount += 1
            elif strVersion == "A":
                intARCount += 1
        intRegistrationCount = len(lstRegistrations)
    else:
        intRegistrationCount = 0
    return (intRegistrationCount, intSilverCount, intGoldCount, intARCount)

def SendCBA01RegistrationNotification(objHere, strName, strEmailAddress):
    (intRegistrationCount, intSilverCount, intGoldCount, intARCount) = GetRegistrationCounts(objHere, "CBA01")

    strMessage = """New registration

Total registrations: %s
Gold: %s
Silver: %s
Auto responder: %s

Name: %s
Email address: %s
""" % (intRegistrationCount, intGoldCount, intSilverCount, intARCount, strName, strEmailAddress)
    strSubject = "Coaching Business Acceletor, new registration"
    SendEmail(objHere, strMessage, strSubject, "coen@coachcoen.com")

def SendCBA01UpgradeNotification(objHere, strName, strEmailAddress):
    (intRegistrationCount, intSilverCount, intGoldCount) = GetRegistrationCounts(objHere, "CBA01")

    strMessage = """Registration upgraded to Gold

Total registrations: %s
Gold: %s
Silver: %s

Name: %s
Email address: %s
""" % (intRegistrationCount, intGoldCount, intSilverCount, strName, strEmailAddress)
    strSubject = "Coaching Business Acceletor, registration upgrade"
    SendEmail(objHere, strMessage, strSubject, "coen@coachcoen.com")

def SendFailedUpgradeMessage(objHere, strRegistrationId):
    strMessage = """Upgrade failed, registration: %s""" % strRegistrationId
    strSubject = "CBA, upgrade failed"
    SendEmail(objHere, strMessage, strSubject, "coen@coachcoen.com")

def SendAlreadyGoldMessage(objHere, strRegistrationId, strPaymentId):
    strMessage = """A payment (id: %s) has just been made, to upgrade registration (id: %s) to the CBA Gold e-Workshop. However, the registration was already for a Gold e-Workshop""" % (strPaymentId, strRegistrationId)
    strSubject = "Urgent, CBA, payment to upgrade but already on Gold"
    SendEmail(objHere, strMessage, strSubject, "coen@coachcoen.com")

def CBASilverRegistrationSuccessMessage(strEmailAddress):
    strResult = """
<p>Thank you for joining the Coaching Business Accelerator Silver e-Workshops</p>
<p>You will start receiving the workshop material and exercises at your email address (%s) from Monday 22nd October</p>
<p>If you or your email host uses anti-spam software, please make sure to add the following email addresses to the software's white list:</p>
<ul>
    <li>coen@coachcoen.com</li>
    <li>CBA01Silver@forcoaches.com</li>
</ul>
<p>A confirmation email has been sent to %s. Please check your inbox. If you haven't received it, please check your spam or quarantine folder. If all else fails, <a href="/ContactDetails">contact the list owner</a></p>
""" % (strEmailAddress, strEmailAddress)
    return strResult

def CBAGoldRegistrationSuccessMessage(strEmailAddress):
    strResult = """
<p>Thank you for joining the Coaching Business Accelerator Gold e-Workshop</p>
<p>You will start receiving the workshop material and exercises at your email address (%s) from Monday 22nd October</p>
<p>Your membership of the learning community and expert support will also start on Monday 22nd October</p>
<p>If you or your email host uses anti-spam software, please make sure to add the following email addresses to the software's white list:</p>
<ul>
    <li>coen@coachcoen.com</li>
    <li>CBA01Gold@forcoaches.com</li>
</ul>
<p>A confirmation email has been sent to %s. Please check your inbox. If you haven't received it, please check your spam or quarantine folder. If all else fails, <a href="/ContactDetails">contact the list owner</a></p>""" % (strEmailAddress, strEmailAddress)
    return strResult

def CBAGoldUpgradeSuccessMessage(strEmailAddress):
    strResult = """
<p>Thank you for upgrading to the Gold e-Workshop</p>
<p>You will start receiving the workshop material and exercises at your email address (%s) from Monday 22nd October</p>
<p>Your membership of the learning community and expert support will also start on Monday 22nd October</p>
<p>If you or your email host uses anti-spam software, please make sure to add the following email addresses to the software's white list:</p>
<ul>
    <li>coen@coachcoen.com</li>
    <li>CBA01Gold@forcoaches.com</li>
</ul>
<p>A confirmation email has been sent to %s. Please check your inbox. If you haven't received it, please check your spam or quarantine folder. If all else fails, <a href="/ContactDetails">contact the list owner</a></p>""" % (strEmailAddress, strEmailAddress)
    return strResult

def CBA01ARRegistrationSuccessMessage(strEmailAddress):
    strResult = """
<p>Thank you for joining the Coaching Business Accelerator e-Workshop</p>
<p>The first email has been sent to %s. Please check your inbox. If you haven't received it, please check your spam or quarantine folder. If all else fails, <a href="/ContactDetails">contact the list owner</a></p>
<p>If you or your email host uses anti-spam software, please make sure to add coen@coachcoen.com to the software's white list</p>
"""
    return strResult

def CBA01GQRegister(objHere):
# Get name, email address, event and sign up type, and whether it is an upgrade
    (blnSuccess, strName, strEmailAddress) = GetCBAFormDetails(objHere)
    if not blnSuccess:
        return "Form called incorrectly. Please contact the list owner"

    (blnSuccess, strFailedMessage) = CheckCBA01GQForm(objHere, strName, strEmailAddress)
    if not blnSuccess:
        strResult = RebuildCBA01GQForm(objHere, strName, strEmailAddress, strFailedMessage)
        return strResult

    return RecordEventRegistration(objHere, "CBA01", "S", strEmailAddress, strName, "GQBonus", "CBA01SGQ")

def FindRegistrationForEmailAddress(objHere, strEmailAddress):
    print "Find registration for %s" % strEmailAddress
    strEmailAddress = strEmailAddress.lower()
    objRegistrations = objHere.unrestrictedTraverse("/Data/E3/E3EventRegistration")
    for objBatch in objRegistrations.objectValues("Folder"):
        for objRegistration in objBatch.objectValues("E3EventRegistration"):
            if objRegistration.EmailAddress.lower() == strEmailAddress:
                print "Found"
                return objRegistration
    print "Not found"
    return None

def AlreadyGoldErrorMessage():
    return """<p>There seems to be a problem with your payment. As far as the system can tell, you have already paid for the Gold e-Workshop</p>
<p>The list owner has been informed and will contact you as soon as possible</p>
<p>To contact the list owner, see the <a href="http://www.eurocoachlist.com/ContactDetails">Contact Details page</a></p>"""

cnGeneralReceipt = """Compass Mentis
Coen de Groot
56 Fairfield Road
Bristol BS6 5JP
Tel: +44 (0)117 955 0062
---------------------------------

Invoice Number: ECL%(InvoiceNumber)s
Invoice Date:   %(InvoiceDate)s
Invoice Due:    - Paid in full -


Receipt to:
%(Name)s
%(EmailAddress)s

Payment received for %(Description)s

Total %(Amount)s. No VAT charged

Payment received %(InvoiceDate)s, with thanks :-)

Any questions, please email me at coen@coachcoen.com

"""

from libConstants import cnGeneralReceipt
from libConstants import cnShortDateFormat
from datetime import date

def SendCBAReceipt(objHere, strEmailAddress, strName, strEvent, strPaymentId, intInvoiceNumber):
#    print "Id: ", strPaymentId
#    objWorldPayCall = SearchOne(objHere, "E3WorldPayCall", "id", strPaymentId)
    objWorldPayCall = objHere
    intAmount = objWorldPayCall.Amount
    strReceipt = cnGeneralReceipt % {'InvoiceNumber': intInvoiceNumber,
        'InvoiceDate': date.today().strftime(cnShortDateFormat),
        'Name': strName,
        'EmailAddress': strEmailAddress,
        'Description': "Coaching Business Accelerator e-Workshop",
        'Amount': "GBP%s" % intAmount}
    strSubject = "Coaching Business Accelerator Receipt"
    SendEmail(objHere, strReceipt, strSubject, strEmailAddress)

def RecordEventRegistration(objHere, strEvent, strVersion, strEmailAddress, strName, strPaymentId, strRegistrationType, strRegistrationToUpgrade = ""):

    from E3Payments import NextInvoiceNumber

    strUpgradeOffer = """<fieldset>
    <legend>Gold e-Workshop</legend>
<p>A small group of dedicated participants will be part of the interactive learning community. Join this select group and:</p>
<ul>
    <li>Discuss the materials with your fellow participants and with the workshop leaders</li>
    <li>Put your questions directly to the workshop leaders</li>
    <li>Receive support from your fellow participants during and after the workshop, and support them in return</li>
    <li>Buddy up with a fellow coach for regular extra support and encouragement</li>
    <li>Tap into the knowledge and expertise of your colleague coaches</li>
    <li>Join a group of people like yourself, who want to accelerate their success as professional coaches</li>
    <li>Create connections for you to tap into over the years to come</li>
</ul>
<p>Materials, expert support plus learning community. Usual price &pound;157. Materials, expert support plus learning community. Usual price &pound;157. Upgrade offer: &pound;132 (about &euro;191 or $269). Early bird upgrade offer: 10%% discount plus free 6 months' Euro Coach List membership by Wednesday 17th October. Offer price: &pound;116. Limited places.</p>
    <p><a href="/Events/CoachingBusinessAccelerator/Upgrade?id=%s"><input type="button" class="btn" value="Sign me up for the Gold e-Workshop"></a></p>
</fieldset>
"""
    if strRegistrationToUpgrade:
#        print "Registration to upgrade: %s" % strRegistrationToUpgrade
        if strRegistrationToUpgrade == "NotFound":
            objRegistration = None
        else:
            # See if we can find the email address
            objRegistration = SearchOne(objHere, "E3EventRegistration", "id", strRegistrationToUpgrade)


        if not objRegistration:
            objRegistration = FindRegistrationForEmailAddress(objHere, strEmailAddress)

        if objRegistration:
            if objRegistration.RegistrationType[5] == "G":
                SendAlreadyGoldMessage(objHere, objRegistration.id, strPaymentId)
                return AlreadyGoldErrorMessage()
        else:
            dodRegistration = GetDOD(objHere, "E3EventRegistration")
            objRegistration = dodRegistration.NewObject()
            objRegistration.Event = strEvent
            objRegistration.EmailAddress = strEmailAddress
            objRegistration.Name = strName
            objRegistration.title = "%s: %s (%s)" % (strEvent, strName, strEmailAddress)
            SendFailedUpgradeMessage(objHere, objRegistration.id)

        objRegistration.RegistrationType = "CBA01GUpgraded"
        objRegistration.PaymentId = strPaymentId
        Catalogue(objRegistration)
        SendCBA01GoldUpgradeMessage(objHere, strEmailAddress)
        strResult = CBAGoldUpgradeSuccessMessage(strEmailAddress)
        SendCBA01UpgradeNotification(objHere, strName, strEmailAddress)
        return strResult

    dodRegistration = GetDOD(objHere, "E3EventRegistration")
    objRegistration = dodRegistration.NewObject()
    objRegistration.Event = strEvent
    objRegistration.RegistrationType = strRegistrationType
    objRegistration.EmailAddress = strEmailAddress
    objRegistration.Name = strName
    objRegistration.title = "%s: %s (%s)" % (strEvent, strName, strEmailAddress)
    objRegistration.PaymentId = strPaymentId
    objRegistration.InvoiceNumber = NextInvoiceNumber(objHere)
    Catalogue(objRegistration)
    if strEvent == "CBA01":
        if strVersion == "S":
            SendCBA01SilverRegistrationMessage(objHere, strEmailAddress)
            strResult = CBASilverRegistrationSuccessMessage(strEmailAddress)
        elif strVersion == "A":
            # Auto responder version

            # Send receipt
            SendCBAReceipt(objHere, strEmailAddress, strName, strEvent, strPaymentId, objRegistration.InvoiceNumber)

            # Start auto responder
            StartEmailSequence(objHere, "CBA01", "", strEmailAddress)
            strResult = CBA01ARRegistrationSuccessMessage(strEmailAddress)
        else:
            SendCBA01GoldRegistrationMessage(objHere, strEmailAddress)
            strResult = CBAGoldRegistrationSuccessMessage(strEmailAddress)
        if strRegistrationType == "CBA01SGQ":
            strResult += strUpgradeOffer % objRegistration.id
    else:
        strResult = ""
    SendCBA01RegistrationNotification(objHere, strName, strEmailAddress)
    return strResult

def ConferenceAttendence(objHere):
    (dictAttendees, lstWillCome, intWillCome, lstMayCome, intMayCome) = GetAttendees(objHere)
    intComing = dictAttendees['Y']
    intMaybe = dictAttendees['M']
    strResult =  """<p><a href="/Events/ECLConference/Attendees">%s coming, %s may be coming</a></p>""" % (intComing, intMaybe)
    try:
        strResult = unicode(strResult, 'ascii', 'replace')
    except:
        pass
    return strResult

def ListAttendees(objHere):
    (dictAttendees, lstWillCome, intWillCome, lstMayCome, intMayCome) = GetAttendees(objHere)
    strResult = """
<fieldset>
    <legend>%s members said they want to come</legend>
    <p>%s</p>
</fieldset>
<fieldset>
    <legend>%s members said they may want to come</legend>
    <p>%s</p>
</fieldset>""" % (intWillCome, ", ".join(lstWillCome), intMayCome, ", ".join(lstMayCome))
    try:
        strResult = unicode(strResult, 'ascii', 'replace')
    except:
        pass
    return strResult

def GetAttendees(objHere):
    dictResult = {'Y': 0, 'N': 0, 'M': 0}
    lstWillCome = []
    intWillCome = 0
    lstMayCome = []
    intMayCome = 0
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if 'Events' in objMember.objectIds():
                strWillCome = objMember.Events.ECL07.WillCome
                if strWillCome:
                    dictResult[strWillCome] += 1
                    if strWillCome == 'Y':
                        intWillCome += 1
                        if objMember.Name:
                            lstWillCome.append(objMember.Name)
                    elif strWillCome == 'M':
                        intMayCome += 1
                        if objMember.Name:
                            lstMayCome.append(objMember.Name)
    lstWillCome.sort()
    lstMayCome.sort()
    return (dictResult, lstWillCome, intWillCome, lstMayCome, intMayCome)

def PreparePreferenceStorage(objMember):
    if not 'Events' in objMember.objectIds():
        objMember.manage_addFolder('Events')
    if not 'ECL07' in objMember.Events.objectIds():
        dodEventPreference = GetDOD(objMember, 'E3EventPreference')
        dodEventPreference.NewObject(objMember.Events, 'ECL07')

def GetLocationsSoFar(objMainMember):
    lstStartList = ("Milton Keyes", "Newquay", "Amsterdam", "London", "Bristol")
    dictResult = {}
    for strLocation in lstStartList:
        dictResult[strLocation] = 0

    objMembers = GetDataFolder(objMainMember, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if 'Events' in objMember.objectIds():
                if 'ECL07' in objMember.Events.objectIds():
                    for strLocation in objMember.Events.ECL07.Locations:
                        blnFound = False
                        for strOption in dictResult.keys():
                            if strOption.lower() == strLocation.lower():
                                blnFound = True
                                if dictResult[strOption] >= 0:
                                    dictResult[strOption] += 1
                                else:
                                    dictResult[strOption] -= 1
                                if objMember == objMainMember:
                                    dictResult[strOption] = -abs(dictResult[strOption])
                        if not blnFound:
                            if objMember == objMainMember:
                                dictResult[strLocation] = -1
                            else:
                                dictResult[strLocation] = 1
    return dictResult

def GetOtherLocations(lstMemberLocations, dictLocationsSoFar):
    strResult = ""
    for strLocation in lstMemberLocations:
        if not strLocation.lower() in lstLocationsLower:
            strResult += strLocation + "\n"
    return strResult

def BuildLocationDetails(dictLocationsSoFar):
    lstStartList = ("Milton Keyes", "Newquay", "Amsterdam", "London", "Bristol")
    lstLocations = dictLocationsSoFar.keys()
    lstLocations.sort()
    strCheckBoxes = ""
    lstOtherLocations = []
    for strLocation in lstLocations:
        if dictLocationsSoFar[strLocation] == -1 and not strLocation in lstStartList:
            lstOtherLocations.append(strLocation)
        else:
            intCount = dictLocationsSoFar[strLocation]
            if intCount < 0:
                strChecked = "checked"
            else:
                strChecked = ""
            strLocationId = strLocation.replace(" ", "~")
            intCount = abs(intCount)
            if intCount:
                strCount = " (%s)" % intCount
            else:
                strCount = ""
            strCheckBoxes += """<div class="LocationOption"><input type = "checkbox" name="Location-%s" id = "Location-%s" %s> <label for="Location-%s">%s%s</label></div>&nbsp; """ % (strLocationId, strLocationId, strChecked, strLocationId, strLocation, strCount)
    return (strCheckBoxes, "\n".join(lstOtherLocations))

def GetLocations(objMember):
    lstMemberLocations = objMember.Events.ECL07.Locations
    dictLocationsSoFar = GetLocationsSoFar(objMember)
    (strLocationsSoFar, strOtherLocations) = BuildLocationDetails(dictLocationsSoFar)
    return (strLocationsSoFar, strOtherLocations)

def ParseWeekday(strPart):
    dictWeekdays = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
    for strWeekday in dictWeekdays.keys():
        if strWeekday[:len(strPart)] == strPart:
            return (True, dictWeekdays[strWeekday])
    return (False, -1)

def ParseDate(strPart):
    lstParts = strPart.split(" ")
    if len(lstParts) <> 2:
        return (False, None)
    if lstParts[0].isdigit():
        intDate = int(lstParts[0])
        strMonth = lstParts[1]
    elif lstParts[1].isdigit():
        intDate = int(lstParts[1])
        strMonth = lstParts[0]
    else:
        return (False, None)
    if intDate < 1 or intDate > 31:
        return (False, None)
    dictMonths = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
    intMonth = 0
    for strMonthOption in dictMonths.keys():
        if strMonthOption[:len(strMonth)] == strMonth:
            intMonth = dictMonths[strMonthOption]
    if not intMonth:
        return (False, None)

    try:
        dtmDate = datetime.date(day = intDate, month = intMonth, year = 2007)
    except:
        return (False, None)

    dtmStartDate = datetime.date(year = 2007, month=9, day = 1)
    dtmEndDate = datetime.date(year = 2007, month = 11, day = 30)
    if dtmDate < dtmStartDate:
        return (False, None)

    if dtmDate > dtmEndDate:
        return (False, None)

    return (True, dtmDate)

def ParseAvailabilityInfo(strInfo):
    lstError = (False, [], [], [])
    strInfo = strInfo.strip().lower()
    if not strInfo:
        return lstError

    lstWeekdays = []
    lstDates = []
    lstRanges = []

    lstParts = strInfo.split(",")
    for strPart in lstParts:
        strPart = strPart.strip()
        if '-' in strPart:
            lstSubDates = strPart.split('-')
            if len(lstSubDates) <> 2:
                return lstError
            (blnCorrect, dtmFromDate) = ParseDate(lstSubDates[0].strip())
            if not blnCorrect:
                return lstError
            (blnCorrect, dtmToDate) = ParseDate(lstSubDates[1].strip())
            if not blnCorrect:
                return lstError
            if dtmFromDate > dtmToDate:
                return lstError
            lstRanges.append((dtmFromDate, dtmToDate))
        elif ' ' in strPart:
            (blnCorrect, dtmDate) = ParseDate(strPart)
            if not blnCorrect:
                return lstError
            lstDates.append(dtmDate)
        else:
            (blnCorrect, strWeekday) = ParseWeekday(strPart)
            if not blnCorrect:
                return lstError
            lstWeekdays.append(strWeekday)
    return (True, lstWeekdays, lstDates, lstRanges)

def BlankAvailabilityMap():
    dtmStartDate = datetime.date(year = 2007, month=9, day = 1)
    dtmEndDate = datetime.date(year = 2007, month = 11, day = 30)
    dictResult = {}
    dtmDate = dtmStartDate
    while dtmDate <= dtmEndDate:
        dictResult[dtmDate] = 'M'
        dtmDate = dtmDate + datetime.timedelta(days=1)
    return dictResult

def GetFullDates(lstWeekdays, lstDates, lstRanges):
    lstResult = lstDates

    dtmStartDate = datetime.date(year = 2007, month=9, day = 1)
    dtmEndDate = datetime.date(year = 2007, month = 11, day = 30)
    dtmDate = dtmStartDate
    while dtmDate <= dtmEndDate:
        if dtmDate.weekday() in lstWeekdays and not dtmDate in lstResult:
            lstResult.append(dtmDate)
        dtmDate = dtmDate + datetime.timedelta(days=1)

    for (dtmStartDate, dtmEndDate) in lstRanges:
        dtmDate = dtmStartDate
        while dtmDate <= dtmEndDate:
            if not dtmDate in lstResult:
                lstResult.append(dtmDate)
            dtmDate = dtmDate + datetime.timedelta(days=1)
    return lstResult

def NewAvailability(strOld, strNew):
    blnPreference = False
    if 'P' in strOld or 'P' in strNew:
        blnPreference = True
    strResult = strNew[0]
    if blnPreference:
        strResult += "P"
    return strResult

def ProcessAvailabilityStatement(dictMap, strType, lstWeekdays, lstDates, lstRanges):
    lstFullDates = GetFullDates(lstWeekdays, lstDates, lstRanges)
    for dtmDate in lstFullDates:
        dictMap[dtmDate] = NewAvailability(dictMap[dtmDate], strType)
    return dictMap

def GetAvailabilityMap(objPreferences):
    dictResult = BlankAvailabilityMap()
    for objStatement in objPreferences.objectValues('E3AvailabilityStatement'):
        (blnCorrect, lstWeekdays, lstDates, lstRanges) = ParseAvailabilityInfo(objStatement.Info)
        dictResult = ProcessAvailabilityStatement(dictResult, objStatement.Type, lstWeekdays, lstDates, lstRanges)
    return dictResult

def ValidAvailabilityStatement(objPreferences, strType, strInfo):
    # Valid type
    if not strType in ['Y', 'YP', 'MP', 'N', 'M']:
        SetMessage(objPreferences, "Incorrect type of availability: %s" % strType, "")
        return False

    # Valid info
    (blnCorrect, lstWeekdays, lstDates, lstRanges) = ParseAvailabilityInfo(strInfo)
    if not blnCorrect:
        SetMessage(objPreferences, "Incorrect availability information: %s" % strInfo, "")
        return False

    return True

def LastDayOfMonth(dtmDate):
    if (dtmDate + datetime.timedelta(days = 1)).day == 1:
        return True
    return False

def MonthStart(dtmDate):
    return """
<table border="1" cellspacing="0" style="float:left; margin-left:5px; margin-bottom: 5px">
    <tr>
        <td colspan="7" align="center">%s 2007</td>
    </tr>
    <tr>
        <td>Mo</td>
        <td>Tu</td>
        <td>We</td>
        <td>Th</td>
        <td>Fr</td>
        <td>Sa</td>
        <td>Su</td>
    </td>
<tr>%s""" % (MonthName(dtmDate.month), "<td>&nbsp;</td>" * dtmDate.weekday())

def MonthEnd(dtmDate):
    return """%s</tr>
</table>
""" % ("<td>&nbsp;</td>" * (6 - dtmDate.weekday()))

def WeekStart():
    return """<tr>\n"""

def WeekEnd():
    return """</tr>\n"""

def BuildCalendar(dictMap):
    strResult = ""
    dtmStartDate = datetime.date(year = 2007, month=9, day = 1)
    dtmEndDate = datetime.date(year = 2007, month = 11, day = 30)
    dtmDate = dtmStartDate
    while dtmDate <= dtmEndDate:
        if dtmDate.day == 1 or dtmDate == dtmStartDate:
            strResult += MonthStart(dtmDate)
        elif dtmDate.weekday() == 0:
            strResult += WeekStart()
        strInfo = dictMap[dtmDate]
        strShowInfo = strInfo[0]
        if strShowInfo == 'Y':
            pass
        if strShowInfo == 'M':
            strShowInfo = dtmDate.day
        elif strShowInfo == 'N':
            strShowInfo = 'n'
        strResult += """<td align="right" class="CalendarDate%s">%s</td>""" % (strInfo, strShowInfo)
        if LastDayOfMonth(dtmDate) or dtmDate == dtmEndDate:
            strResult += MonthEnd(dtmDate)
        elif dtmDate.weekday() == 6:
            strResult += WeekEnd()
        dtmDate = dtmDate + datetime.timedelta(days=1)
    return strResult

def OneStatement(objStatement):
    strType = {'Y': 'Yes',
            'N': 'No',
            'YP': 'Yes, prefered',
            'NP': 'No',
            'MP': 'Maybe, prefered',
            'M': 'Maybe'}[objStatement.Type]
    strResult = """
    <p><input type="checkbox" name="Delete-%(Id)s" value="Yes">
        %(Type)s: %(Info)s
    </p>""" % {
            'Id': objStatement.id,
            'Type': strType,
            'Info': objStatement.Info}
    return strResult

def GetStatementList(objPreferences):
    if not objPreferences:
        return ""

    strResult = """
<form action = %s>
    <input type="hidden" name="Action" value="DeleteAvailabilityStatements">
""" % objPreferences.REQUEST.ACTUAL_URL

    for objStatement in objPreferences.objectValues('E3AvailabilityStatement'):
        strResult += OneStatement(objStatement)
    strResult += """
    <p><input type="submit" value="Delete" class="btn"></p>
</form>"""
    return strResult

def GetFormDetails(objMember):
    objEventPreference = objMember.Events.ECL07
    dictResult = {}
    dictResult['URL'] = objMember.REQUEST.ACTUAL_URL
    dictResult['Name'] = objMember.Name
    for strWillCome in ['Yes', 'Maybe', 'No']:
        dictResult['WillCome' + strWillCome] = ''
        if objEventPreference.WillCome == strWillCome[0]:
            dictResult['WillCome' + strWillCome] = 'checked'
    (dictResult['LocationsSoFar'], dictResult['OtherLocations']) = GetLocations(objMember)

    dictMap = GetAvailabilityMap(objEventPreference)
    dictResult['Calendar'] = BuildCalendar(dictMap)

    dictResult['AvailabilityStatements'] = GetStatementList(objEventPreference)

    dictResult['PreparationOffers'] = objEventPreference.PreparationOffers
    dictResult['OnDayOffers'] = objEventPreference.OnDayOffers
    dictResult['Wishes'] = objEventPreference.Wishes
    dictResult['Comments'] = objEventPreference.Comments
    dictResult['DateOptions'] = GetDateOptions()
    return dictResult

def GetDateOptions():
    strResult = ""
    for intI in range(1, 32):
        strResult += "<option>%s</option>\n" % intI
    return strResult

def Template():
    return """
<fieldset>
    <legend>Would you like to come</legend>
    <form action="%(URL)s" method="post">
        <input type="hidden" name="Action" value="UpdateEventWillCome">
        <p><label>Your name</label><input type="text" value="%(Name)s" name="Name" size="30"></p>
        <p><input type="radio" name="WillCome" value="Yes" %(WillComeYes)s> Yes |
            <input type="radio" name="WillCome" value="Maybe" %(WillComeMaybe)s> Maybe |
            <input type="radio" name="WillCome" value="No" %(WillComeNo)s> No</p>
        <p><input type="submit" value="Update" class="btn"></p>
        <p>Note: A list of members who may be coming will be visible to all list members</p>
    </form>
</fieldset>
<fieldset>
    <legend>Where</legend>
    <p>Number of votes so far are shown in brackets</p>
    <form action="%(URL)s" method="post">
        <input type="hidden" name="Action" value="UpdateEventLocations">
        <p>%(LocationsSoFar)s</p>
        <p>Other location(s), one per line</p>
        <p><textarea name="OtherLocations" cols="30" class="FullWidth">%(OtherLocations)s</textarea></p>
        <p><input type="submit" value="Update" class="btn"></p>
    </form>
</fieldset>
<fieldset>
    <legend>When</legend>
    <p>Start with the big picture, such as "I can make all Saturdays" or "I cannot make 6th October - 14th October". Then add more specific rules, such as "I cannot make (Sat) 20th October"</p>
    <fieldset>
        <legend>Add a preference</legend>
        <form action="%(URL)s" method="post">
            <input type="hidden" name="Action" value="AddAvailabilityStatement">
            <p>
                <select name="AvailabilityType">
                    <option value="YP">I can make and prefer</option>
                    <option selected value="Y">I can make</option>
                    <option value="MP">I might be able to make and prefer</option>
                    <option value="M">I might be able to make</option>
                    <option value="N">I cannot make</option>
                </select>
            </p>

            <p>
                <label class="short">day:</label>
                <select name="Weekday">
                    <option value="Sat">Saturdays</option>
                    <option value="Sun">Sundays</option>
                    <option value="Mon">Mondays</option>
                    <option value="Tue">Tuesdays</option>
                    <option value="Wed">Wednesdays</option>
                    <option value="Thu">Thursdays</option>
                    <option value="Fri">Fridays</option>
                </select>
                <input type="submit" name="AddWeekday" value="Add" class="btn">
            </p>
            <p>
                <label class="short">date:</label>
                <select name="Month">
                    <option>Sept</option>
                    <option>Oct</option>
                    <option>Nov</option>
                </select>
                <select name="Date">
                    %(DateOptions)s
                </select>
                <input type="submit" name = "AddDate" value="Add" class="btn">
            </p>
            <p>
                <label class="short">period:</label>
                <select name="FromMonth">
                    <option>Sept</option>
                    <option>Oct</option>
                    <option>Nov</option>
                </select>
                <select name="FromDate">
                    %(DateOptions)s
                </select>
                to
                <select name="ToMonth">
                    <option>Sept</option>
                    <option>Oct</option>
                    <option>Nov</option>
                </select>
                <select name="ToDate">
                    %(DateOptions)s
                </select>
                <input type="submit" name="AddPeriod" value="Add" class="btn">
            </p>
        </form>
    </fieldset>
    <fieldset>
        <legend>Your availability</legend>
        %(Calendar)s
    </fieldset>
    <fieldset>
        <legend>Preferences already entered</legend>
        %(AvailabilityStatements)s
    </fieldset>
</fieldset>
<fieldset>
    <legend>Other preferences</legend>
    <form action="%(URL)s" method="post">
        <input type="hidden" name="Action" value="UpdateEventPreferences">
        <p>To help organise the event, I can ....</p>
        <p><textarea name="PreparationOffers" class="FullWidth">%(PreparationOffers)s</textarea></p>
        <p>During the event, I can ... (e.g. a workshop or presentation)</p>
        <p><textarea name="OnDayOffers" class="FullWidth">%(OnDayOffers)s</textarea></p>
        <p>This would make it a 'must attend event' for me</p>
        <p><textarea name="Wishes" class="FullWidth">%(Wishes)s</textarea></p>
        <p>Some final comments</p>
        <p><textarea name="Comments" class="FullWidth">%(Comments)s</textarea></p>
        <p><input type="submit" value="Update" class="btn"></p>
    </form>
</fieldset>"""

def PreferencesForm(objHere):
    objMember = GetCurrentMember(objHere)
    PreparePreferenceStorage(objMember)
    dictFormDetails = GetFormDetails(objMember)
    strResult = Template()
    strResult = strResult % dictFormDetails
    strResult = ToUnicode(strResult)
    return strResult

def AddLocation(dictLocations, strLocation, blnWillCome):
    if not dictLocations.has_key(strLocation.lower()):
        dictLocations[strLocation.lower()] = [strLocation, 0, 0]
    if blnWillCome:
        dictLocations[strLocation.lower()][1] += 1
    else:
        dictLocations[strLocation.lower()][2] += 1
    return dictLocations


def GetLocationScores(objHere):
    dictResult = {}
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if 'Events' in objMember.objectIds():
                lstLocations = objMember.Events.ECL07.Locations
                for strLocation in lstLocations:
                    dictResult = AddLocation(dictResult, strLocation, objMember.Events.ECL07.WillCome)
    return dictResult

def OneLocationScore(lstLocationDetails):
    (strLocation, intMayCome, intWillCome) = lstLocationDetails
    return """
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>""" % (strLocation, intMayCome, intWillCome, intMayCome + 2 * intWillCome)

def FormatLocationScores(dictScores):
    lstLocations = dictScores.keys()
    lstLocations.sort()
    strLocations = ""
    for strLocation in lstLocations:
        strLocations += OneLocationScore(dictScores[strLocation])
    strResult = """
<fieldset>
    <legend>Location preferences</legend>
    <table>
        <tr>
            <td>Location</td>
            <td>May come</td>
            <td>Will come</td>
            <td>Score</td>
        </tr>
    %s
    </table>
</fieldset>
""" % strLocations
    return strResult

def EventLocationScores(objHere):
    dictScores = GetLocationScores(objHere)
    return FormatLocationScores(dictScores)

def BlankDatePreferenceScores():
    dictResult = {}

    dtmStartDate = datetime.date(year = 2007, month=9, day = 1)
    dtmEndDate = datetime.date(year = 2007, month = 11, day = 30)
    dtmDate = dtmStartDate
    while dtmDate <= dtmEndDate:
        dictResult[dtmDate] = {'Y': 0, 'N': 0, 'M': 0, 'P': 0}
        dtmDate = dtmDate + datetime.timedelta(days=1)

    return dictResult

def AddDatePreferenceScores(dictScores, dictOneDiary):
    for dtmDate in dictOneDiary.keys():
        strAvailability = dictOneDiary[dtmDate]
        for strKey in ['P', 'Y', 'N', 'M']:
            if strKey in strAvailability:
                dictScores[dtmDate][strKey] += 1
    return dictScores

def GetDatePreferenceScores(objHere):
    dictResult = BlankDatePreferenceScores()
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if 'Events' in objMember.objectIds():
                dictOneDiary = GetAvailabilityMap(objMember.Events.ECL07)
                dictResult = AddDatePreferenceScores(dictResult, dictOneDiary)
    return dictResult

def FormatDatePreferenceScores(dictScores):
    strResult = ""
    dtmStartDate = datetime.date(year = 2007, month=9, day = 1)
    dtmEndDate = datetime.date(year = 2007, month = 11, day = 30)
    dtmDate = dtmStartDate
    while dtmDate <= dtmEndDate:
        if dtmDate.day == 1 or dtmDate == dtmStartDate:
            strResult += MonthStart(dtmDate)
        elif dtmDate.weekday() == 0:
            strResult += WeekStart()

        dictInfo = dictScores[dtmDate]
        strInfo = "%s: %s<br>%s-%s=<b>%s</b>" % (dtmDate.day, dictInfo['P'], dictInfo['Y'], dictInfo['N'], dictInfo['Y'] - dictInfo['N'])
        strResult += """<td>%s</td>""" % strInfo

        if LastDayOfMonth(dtmDate) or dtmDate == dtmEndDate:
            strResult += MonthEnd(dtmDate)
        elif dtmDate.weekday() == 6:
            strResult += WeekEnd()
        dtmDate = dtmDate + datetime.timedelta(days=1)
    return strResult

def DatePreferenceScores(objHere):
    dictScores = GetDatePreferenceScores(objHere)
    strResult = """
<fieldset>
    <legend>Date preferences</legend>
    <p>First line: Date: Number of attendees who prefer this date</p>
    <p>Second line: Can come - Cannot come = Score</p>
    %s
</fieldset>
    """ % FormatDatePreferenceScores(dictScores)
    return strResult

def AddOneComment(lstList, strComment, blnIsManager, strName, strUsername, strEmailAddress):
    if strComment:
        if blnIsManager:
            if strName:
                strComment = "%s, %s: %s" % (strName, strEmailAddress, strComment)
            else:
                strComment = "%s, %s: %s" % (strUsername, strEmailAddress, strComment)
        lstList.append(strComment)
    return lstList

def GetComments(objHere):
    (lstToHelp, lstDuring, lstMustAttend, lstComments) = ([], [], [], [])
    blnIsManager = ManagerLoggedIn(objHere)

    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if 'Events' in objMember.objectIds() and 'ECL07' in objMember.Events.objectIds():
                lstToHelp = AddOneComment(lstToHelp, objMember.Events.ECL07.PreparationOffers, blnIsManager, objMember.Name, objMember.Username, objMember.PreferredEmailAddress())
                lstDuring = AddOneComment(lstDuring, objMember.Events.ECL07.OnDayOffers, blnIsManager, objMember.Name, objMember.Username, objMember.PreferredEmailAddress())
                lstMustAttend = AddOneComment(lstMustAttend, objMember.Events.ECL07.Wishes, blnIsManager, objMember.Name, objMember.Username, objMember.PreferredEmailAddress())
                lstComments = AddOneComment(lstComments, objMember.Events.ECL07.Comments, blnIsManager, objMember.Name, objMember.Username, objMember.PreferredEmailAddress())
    return (lstToHelp, lstDuring, lstMustAttend, lstComments)

def ListComments(lstList):
    strResult = ""
    for strComment in lstList:
        strResult += "<p>%s</p>\n" % strComment
    return strResult

def SummariseComments(objHere):
    (lstToHelp, lstDuring, lstMustAttend, lstComments) = GetComments(objHere)
    strResult = """
<fieldset>
    <legend>To help organise the event, I can ...</legend>
    %s
</fieldset>
<fieldset>
    <legend>During the event, I can ... </legend>
    %s
</fieldset>
<fieldset>
    <legend>This would make it a 'must attend' event for me</legend>
    %s
</fieldset>
<fieldset>
    <legend>Some final comments</legend>
    %s
</fieldset>
""" % (ListComments(lstToHelp), ListComments(lstDuring), ListComments(lstMustAttend), ListComments(lstComments))
    return strResult

def EventSummary(objHere):
    try:
        strResult = unicode(ListAttendees(objHere), 'ascii', 'ignore')
    except:
        strResult = ListAttendees(objHere)

    try:
        strResult += unicode(EventLocationScores(objHere), 'ascii', 'ignore')
    except:
        strResult += EventLocationScores(objHere)

    try:
        strResult += unicode(DatePreferenceScores(objHere), 'ascii', 'ignore')
    except:
        strResult += DatePreferenceScores(objHere)

    try:
        strResult += unicode(SummariseComments(objHere), 'ascii', 'ignore')
    except:
        strResult += SummariseComments(objHere)

    return strResult
