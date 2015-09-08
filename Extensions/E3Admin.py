# encoding: utf-8

"""Admin functions"""

from libDatabase import GetDataFolder
from libDatabase import SearchOne
from libDatabase import SearchMany
from libDatabase import GetDOD
from E3Members import CountMembers
from E3Members import NumberOfListMembers
from E3Members import GetMemberForId
from E3Digest import SendDailyDigests
from libConstants import cnFirstDate
from E3HTML import UpdateCacheItem
from E3Offerings import UpdateCounts
from libDatabase import GetWebsiteRoot
from libConstants import cnShortDateFormat
from libDate import MonthName
from libString import ToUnicode

import types
import datetime

def SetNoCommercialEmails(objHere):
    lstResult = []
    fileWho = open("/var/lib/zope/Extensions/ToUnsubscribe.txt")
    strWho = fileWho.read()
    lstWho = strWho.split()
    lstToUnsubscribe = []
    for strAddress in lstWho:
    	if strAddress:
            lstToUnsubscribe.append(strAddress.lower())
    for objBatch in objHere.unrestrictedTraverse("/Data/E3/E3Members").objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.EmailDeliveryAddress.lower() in lstToUnsubscribe:
#            if objMember.NoMail or objMember.NoCommercialEmails:
                lstResult.append(objMember.EmailDeliveryAddress)
                objMember.NoCommercialEmails = True

    strResult = "\n".join(lstResult)
    strResult = """<form>
    <textarea cols="80", rows="40">
%s</textarea>
</form>""" % strResult
    return strResult


def ListBounces(objHere):
    lstResult = []
    for objBatch in objHere.unrestrictedTraverse("/Data/E3/E3Members").objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            for objEmailAddress in objMember.objectValues("E3EmailAddress"):
                if objEmailAddress.Bouncing:
                    lstResult.append('<a href="http://issiegardner.com:8080/Data/E3/E3Members/%s/%s/%s">%s</a><br>\n' % (objBatch.id, objMember.id, objEmailAddress.id, objEmailAddress.EmailAddress))
    strResult = "".join(lstResult)
    strResult = """<h2>Bounced email addresses</h2>
<form>
    <textarea cols="80", rows="40">
    %s
    </textarea>
</form>""" % strResult
    return strResult

def EmailAddressesForNoMails(objHere):
    lstResult = []
    for objBatch in objHere.unrestrictedTraverse("/Data/E3/E3Members").objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.NoMail or objMember.NoCommercialEmails:
                lstResult.append(objMember.EmailDeliveryAddress)
    strResult = "\n".join(lstResult)
    strResult = """<h2>Members with NoMail or NoCommercialEmails set</h2>
<form>
    <textarea cols="80", rows="40">
%s</textarea>
</form>""" % strResult
    return strResult

def EmailAddressesForPastMembers(objHere):
    lstResult = []
    for objBatch in objHere.unrestrictedTraverse("/Data/E3/E3Members").objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if not (objMember.MembershipType in ["Cancelled", "Full"]) and not objMember.NoCommercialEmails and objMember.HasConfirmedEmailAddress:
                lstResult.append(objMember.EmailDeliveryAddress)
    strResult = "\n".join(lstResult)
    strResult = """<form>
    <textarea cols="80", rows="40">
%s</textarea>
</form>""" % strResult
    return strResult

def ListUnconfirmedMembers(objHere):
    lstAddresses = []
    lstMembershipTypes = []
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not objMember.MembershipType in lstMembershipTypes:
                lstMembershipTypes.append(objMember.MembershipType)

            if objMember.MembershipType == "Full" and not objMember.HasConfirmedEmailAddress:
                lstAddresses.append(objMember)

    strAddresses = ""
    for objMember in lstAddresses:
        strAddresses += '<li>%s (%s)</li>\n' % (objMember.EmailDeliveryAddress, objMember.id)

    strMembershipTypes = ""
    for strMembershipType in lstMembershipTypes:
        strMembershipTypes += "<li>%s</li>\n" % strMembershipType

    strResult = """
<h2>Membership types</h2>
<ol>
%s
</ol>
<h2>Members without confirmed email addresses</h2>
<ol>
%s
</ol>

""" % (strMembershipTypes, strAddresses)

    return strResult
# firstname, lastname, email

def EmailAddressesForLiveMembers(objHere):
    lstResult = []
    for objBatch in objHere.unrestrictedTraverse("/Data/E3/E3Members").objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if not (objMember.MembershipType in ["Cancelled", "None"]) and not objMember.NoCommercialEmails:
                lstResult.append(objMember.EmailDeliveryAddress)
    strResult = "\n".join(lstResult)
    strResult = """<form>
    <textarea cols="80", rows="40">
%s</textarea>
</form>""" % strResult
    return strResult

def ListAllEmailAddresses(objHere):
    lstAddresses = []
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == "Full":
                lstAddresses.append(objMember.EmailDeliveryAddress)
    strAddresses = ""
    for strAddress in lstAddresses:
        strAddresses += '"name","name","%s"\n' % strAddress
    strResult = """
<form>
    <textarea cols="80", rows="40">
"firstname","lastname","email"
%s</textarea>
</form>
""" % strAddresses
    return strResult
# firstname, lastname, email

def ListExpiredWithManyPayments(objHere):
    lstAddresses = []
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            intLen = len(objMember.Historic.objectValues("E3Payment"))
            strMembershipType = "%s" % objMember.MembershipType
            if intLen > 5:
                lstAddresses.append("%s: %s, %s<br>\n" % (objMember.EmailDeliveryAddress, intLen, strMembershipType))
    strAddresses = "".join(lstAddresses)
#    for strAddress in lstAddresses:
#        strAddresses += '"name","name","%s"\n' % strAddress
    strResult = """Expired members with many payments
<form>
    <textarea cols="80", rows="40">
"email"
%s</textarea>
</form>
""" % strAddresses
    return strResult


def TopPoster(lstPoster1, lstPoster2):
    return cmp(lstPoster2[1][0], lstPoster1[1][0])

def TopPostersForWholeYear(objHere, intYear):
    objArchive = GetDataFolder(objHere, 'E3Messages')
    dictResult = {}
    for intMonth in range(1, 13):
        try:
            objMonth = objArchive.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
        except:
            objMonth = None
        if objMonth:
            for objThread in objMonth.objectValues():
                strUserId = objThread.UserId
                strSubject = objThread.mailSubject.lower()
                if "[" in strSubject:
                    strSubject = strSubject[strSubject.find("["):]
                if not dictResult.has_key(strUserId):
                    dictResult[strUserId] = (0, 0)
                (intPlain, intAdv) = dictResult[strUserId]
                if "adv" in strSubject:
                    dictResult[strUserId] = (intPlain, intAdv + 1)
                else:
                    dictResult[strUserId] = (intPlain + 1, intAdv)

    lstResult = []

    for strUserId in dictResult.keys():
        lstResult.append((strUserId, dictResult[strUserId]))

    lstResult.sort(TopPoster)

    strResult = """<h1>Top posters for %s</h1>
    <ol>
    """ % intYear
    intDone = 0
    for (strUserId, (intCount, intAdverts)) in lstResult:
        objMember = GetMemberForId(objHere, strUserId)
        if objMember:
            strName = objMember.VisibleName(True)
            strEmail = objMember.EmailDeliveryAddress
            if objMember.MembershipType == None:
                strStatus = "Expired"
            else:
                strStatus = objMember.MembershipType
        else:
            strName = "unknown"
            strEmail = ""
            strStatus = ""
        strResult += """<li>%s posts (plus %s adverts) by %s (%s, %s, %s)</li>\n""" % (intCount, intAdverts, strName, strUserId, strEmail, strStatus)
        intDone += 1
        if intDone >= 20:
            strResult += "</ol>\n"
            return strResult
    strResult += "</ol>\n"
    return strResult


def TopPostersForMonth(objHere, intYear, intMonth):
    objArchive = GetDataFolder(objHere, 'E3Messages')
    dictResult = {}
    try:
        objMonth = objArchive.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
    except:
        return ""
    for objThread in objMonth.objectValues():
        strUserId = objThread.UserId
        strSubject = objThread.mailSubject.lower()
        if "[" in strSubject:
            strSubject = strSubject[strSubject.find("["):]
        if not dictResult.has_key(strUserId):
            dictResult[strUserId] = (0, 0)
        (intPlain, intAdv) = dictResult[strUserId]
        if "adv" in strSubject:
            dictResult[strUserId] = (intPlain, intAdv + 1)
        else:
            dictResult[strUserId] = (intPlain + 1, intAdv)
    lstResult = []

    for strUserId in dictResult.keys():
        lstResult.append((strUserId, dictResult[strUserId]))

    lstResult.sort(TopPoster)

    strResult = """<h1>Top posters for %s %s</h1>
    <ol>
    """ % (MonthName(intMonth), intYear)
    intDone = 0
    for (strUserId, (intCount, intAdverts)) in lstResult:
        objMember = GetMemberForId(objHere, strUserId)
        if objMember:
            strName = objMember.VisibleName(True)
        else:
            strName = "unknown"
        strResult += """<li>%s posts (plus %s adverts) by %s (%s)</li>\n""" % (intCount, intAdverts, strName, strUserId)
        intDone += 1
        if intDone >= 10:
            strResult += "</ol>\n"
            return strResult
    strResult += "</ol>\n"
    return strResult

def TopPostersForYear(objHere, intYear):
    strResult = ""
    for intMonth in range(1, 13):
        strResult += TopPostersForMonth(objHere, intYear, intMonth)
    return strResult

def ListOnePayment(objPayment):
    dtmDate = objPayment.GetDate()
    objMember = objPayment.unrestrictedTraverse("../..")
    if objMember.Name:
        strName = objMember.Name
    else:
        strName = "%s, %s" % (objMember.id, objMember.EmailDeliveryAddress)
    strResult = """<p>%s: %s, %s by <a href="http://www.EuroCoachList.com/MyECL?MemberId=%s">%s</a></p>""" % \
        (dtmDate.strftime(cnShortDateFormat), objPayment.PaymentType, ToUnicode(objPayment.Comments), objMember.id, ToUnicode(strName))
    return strResult
    # Date, payment type, description, member's name/link

def ListPayments(dictResult, lstDates):
    intDone = 0
    strResult = ""
    for dtmDate in lstDates:
        for objPayment in dictResult[dtmDate]:
            strResult += ListOnePayment(objPayment)
        intDone += 1
        if intDone >= 250:
            return strResult
    return strResult

def ListRecentPayments(objHere):
    dictResult = {}
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objPayment in objMember.Historic.objectValues("E3Payment"):
                dtmDate = objPayment.GetDate()
                if not dictResult.has_key(dtmDate):
                   dictResult[dtmDate] = []
                dictResult[dtmDate].append(objPayment)
    lstDates = dictResult.keys()
    lstDates.sort(reverse=True)
    strResult = ListPayments(dictResult, lstDates)
    return strResult

def ListOnHold(objHere):
    strResult = ""
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.OnHold:
                strResult += """<li><a href="/MyECL?MemberId=%s">%s - %s</a></li>\n""" % (objMember.id, objMember.id, objMember.Username)
    if strResult:
        strResult = "<ol>\n%s\n</ol>" % strResult
    else:
        strResult = "<p>No members on hold</p>"
    return strResult

def ExportEmailDeliverySettings(objHere):
    fileOutput = open("EmailDeliverySettings.txt", "w")
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            fileOutput.write("[%s]\n" % objMember.id)
            for objDeliveryMode in objMember.ListMemberships.objectValues("E3ListMembership"):
                fileOutput.write("%s: %s\n" % (objDeliveryMode.EmailAddress, objDeliveryMode.myDeliveryMode))
            fileOutput.write("-" * 10)
            fileOutput.write("\n")
            for objEmailAddress in objMember.objectValues("E3EmailAddress"):
                fileOutput.write(objEmailAddress.EmailAddress + "\n")
            fileOutput.write("-" * 10)
            fileOutput.write("\n")

def PreFixCheck(objHere):
    strResult = """<fieldset>
    <legend>Pre-fix check</legend>"""
    strResult += "<ol>\n"
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if "ListMemberships" in objMember.objectIds():
                if "ECL" in objMember.ListMemberships.objectIds():
                    strOldDeliveryMode = objMember.ListMemberships.ECL.myDeliveryMode
                    strOldDeliveryAddress = objMember.ListMemberships.ECL.EmailAddress
                    strDeliveryFrequency = objMember.EmailFrequency_ECL
                    strDigestMode = objMember.EmailDigestMode
                    strDeliveryAddress = objMember.EmailDeliveryAddress

                    if strOldDeliveryMode == "NoMail" and strDeliveryFrequency == "Direct" and strDigestMode == "StructuredDigest":
                        pass
                    elif strOldDeliveryMode == "Direct" and strDeliveryFrequency == "Direct" and strDigestMode == "StructuredDigest":
                        pass
                    elif strOldDeliveryMode in ["MIMEDigest", "TextDigest", "StructuredDigest", "TopicsList"] and strDeliveryFrequency == "Daily" and strDigestMode == strOldDeliveryMode:
                        pass
                    elif strOldDeliveryMode == "TopicsList" and strDigestMode == "StructuredDigest" and strDeliveryFrequency == "Direct":
                        pass
                    else:
                        strResult += "<li>%s, from %s to %s - %s</li>" % (objMember.id, strOldDeliveryMode, strDeliveryFrequency, strDigestMode)


    strResult += "</ol>\n"
    strResult += "</fieldset>"
    return strResult

def PostFixCheck(objHere):
    strResult = """<fieldset>
    <legend>Post-fix check</legend>"""

    strResult += "<ol>\n"
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if "ListMemberships" in objMember.objectIds():
                if "ECL" in objMember.ListMemberships.objectIds():
                    strOldDeliveryMode = objMember.ListMemberships.ECL.myDeliveryMode
                    strOldDeliveryAddress = objMember.ListMemberships.ECL.EmailAddress
                    strDeliveryFrequency = objMember.EmailFrequency_ECL
                    strDigestMode = objMember.EmailDigestMode
                    strDeliveryAddress = objMember.EmailDeliveryAddress

                    if strOldDeliveryMode == "NoMail" and strDeliveryFrequency == "Direct" and objMember.NoMail:
                        pass
                    elif strOldDeliveryMode == "Direct" and strDeliveryFrequency == "Direct" and strDigestMode == "StructuredDigest":
                        pass
                    elif strOldDeliveryMode in ["MIMEDigest", "TextDigest", "StructuredDigest", "TopicsList"] and strDeliveryFrequency == "Daily" and strDigestMode == strOldDeliveryMode:
                        pass
                    else:
                        strResult += "<li>%s, from %s to %s - %s</li>" % (objMember.id, strOldDeliveryMode, strDeliveryFrequency, strDigestMode)

    strResult += "</ol>\n"
    strResult += "</fieldset>"
    return strResult

def FixProblems(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if "ListMemberships" in objMember.objectIds():
                if "ECL" in objMember.ListMemberships.objectIds():
                    strOldDeliveryMode = objMember.ListMemberships.ECL.myDeliveryMode
                    strOldDeliveryAddress = objMember.ListMemberships.ECL.EmailAddress
                    strDeliveryFrequency = objMember.EmailFrequency_ECL
                    strDigestMode = objMember.EmailDigestMode
                    strDeliveryAddress = objMember.EmailDeliveryAddress

                    if strOldDeliveryMode == "NoMail" and strDeliveryFrequency == "Direct" and strDigestMode == "StructuredDigest":
                        objMember.NoMail = True
                    elif strOldDeliveryMode == "TopicsList" and strDigestMode == "StructuredDigest" and strDeliveryFrequency == "Direct":
                        objMember.EmailFrequency_ECL = "Daily"
                        objMember.EmailDigestMode = "TopicsList"

def CheckEmailDeliverySettings(objHere):
    strKnownProblems = """
<fieldset>
    <legend>Known problems, now filtered out in this test</legend>
    <ol>
        <li>Everyone on NoMail has been set to Direct, StructuredDigest</li>
        <li>From TopicsList to Direct, StructuredDigest</li>
    </ol>

    <p>To correct this, change following:</p>
    <ol>
        <li>Anyone who was on NoMail and is now Direct, StructuredDigest: Change objMember.NoMail to True</li>
        <li>Anyone who was on TopicsList and is now Direct, StructuredDigest: Change to Daily, TopicsList</li>
        <li>And then manually check against requests by email</li>
    </ol>

    <p>And the correct behaviour is (also being filtered out):
    <ol>
        <li>From Direct to Direct, StructuredDigest</li>
        <li>From (MIMEDigest, TextDigest, TopicsList, StructuredDigest) to Daily, ditto</li>
    </ol>
</fieldset>"""

    strResult = strKnownProblems
    strResult += PreFixCheck(objHere)
    FixProblems(objHere)
    strResult += PostFixCheck(objHere)
    return strResult

def ByFirstItem(lstItem1, lstItem2):
    return cmp(lstItem1[0], lstItem2[0])

def OneMapItem(objItem, blnLinkTo = True):
    strMapped = ""
    strMaySearch = ""
    if objItem.unrestrictedTraverse('Mapped'):
        strMapped = " Mapped "

    if objItem.unrestrictedTraverse('MaySearch'):
        strMaySearch = " MaySearch "

    return """<li><a href="%s">%s</a>%s%s</li>\n""" % (objItem.absolute_url(), objItem.title_or_id(), strMapped, strMaySearch)

def TravelWebsite(objFolder):
    lstResult = []
    for objItem in objFolder.objectValues('Folder'):
        lstResult.append((objItem.title, OneMapItem(objItem) + TravelWebsite(objItem)))
    strResult = ""
    if lstResult:
        lstResult.sort(ByFirstItem)
        for (strTitle, strHTML) in lstResult:
            strResult = strResult + strHTML
        strResult = "<ul>\n%s</ul>\n" % strResult
    return strResult

def PageMap(objHere):
    objStart = GetWebsiteRoot(objHere, 'E3')
    strResult = TravelWebsite(objStart)
    return strResult

def EmailAddressCheck(objHere):
    lstAddresses = SearchMany(objHere, "E3EmailAddress", "id", "E3EmailAddress04960")
    strResult = "<p>Found: %s</p>\n" % len(lstAddresses)
    for objAddress in lstAddresses:
        strResult += "<p>%s</p>\n" % objAddress.EmailAddress
    return strResult


def AlreadyDone(objMember, intNumber):
    strKey = str(intNumber).zfill(2) + ":"
    for strDone in objMember.DoLaterDone:
        if strKey in strDone:
            return True
    return False

def CheckRetrialMembers(objHere):
    strResult = ""
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if AlreadyDone(objMember, 1):
                if objMember.MembershipType == "None":
                    strResult += """<li><a href="http://www.eurocoachlist.com/MyECL?MemberId=%s">%s</a></li>""" % (objMember.id, objMember.id)
                else:
                    strResult += """<li>%s</li>""" % objMember.id
    if strResult:
        return "<ol>%s</ol>" % strResult
    else:
        return "<p>No one found</p>"

def FindTodaysWnE(objHere):
    dtmNow = datetime.date.today()
    strResult = ""
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objEvent in objMember.Historic.objectValues('E3Event'):
                print ".",
                if objEvent.GetDate() == dtmNow :
                    strResult += "%s; " % objMember.PreferredEmailAddress()
    print
    return strResult

def FindIncorrectPaymentFlags(objHere):
    strResult = ""
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.Historic.objectValues('E3Payment') and not objMember.HasPayments:
                strResult += """<p>%s</p>\n""" % objMember
            if objMember.HasPayments and not objMember.Historic.objectValues('E3Payment'):
                strResult += """<p>%s</p>\n""" % objMember
    return strResult

def ValidPrefix(strSubject):
    if not strSubject:
        return False
    for strPrefix in ['[ukcoach]', '[ec-l]', '[eurocoach-list]']:
        if strPrefix in strSubject.lower():
            return True
    return False

def FindPrivateMessages(objHere):
    strResult = "<ul>"
    objArchive = GetDataFolder(objHere, 'E3Messages')
    for objYear in objArchive.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            for objMessage in objMonth.objectValues('Folder'):
                if not ValidPrefix(objMessage.mailSubject):
                    strResult += """<a href="/Archive/ViewThread?ThreadId=%s"><li>%s</li></a>\n""" % (objMessage.id, objMessage.mailSubject)
    strResult += "</ul>"

def MessagesByMember(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    dictResult = {}
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            lstMessages = SearchMany(objHere, 'E3Messages', 'UserId', objMember.id)
            if lstMessages:
                intNum = len(lstMessages)
                if not dictResult.has_key(intNum):
                    dictResult[intNum] = []
                dictResult[intNum].append(objMember)
    lstNums = dictResult.keys()
    lstNums.sort()
    strResult = ""
    for intI in lstNums:
        strResult += """<p>%s messages: </p>
<ul>""" % intI
        for objMember in dictResult[intI]:
            strResult += "<li>%s, %s, %s, %s, %s</li>\n" % ( objMember.Name, objMember.id, objMember.MembershipType, objMember.GetNextExpiryDate(), objMember.ListEmailAddresses())
        strResult += "</ul>"
    return strResult

def ParkingAccounts(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.GetNextExpiryFromMailman() < cnFirstDate:
                if objMember.Name <> 'Unknown':
                    print objMember.Name

def UpdateAllMembers(objHere, blnCheckOnly = False):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            objMember.UpdateMembershipStatus(blnCheckOnly)
    return "Done"

def RemindToConfirm(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.VisitCount < 2:
                objMember.RemindToConfirm()
    return "Done"

def ExpiriesAndWarnings(objHere, blnReportOnly = False):
    """Daily function:
    - 3 months before expiry date, for a paid member, send out bonus message
    - 3 weeks before expiry due, send out a warning message
    - 3 weeks after warning message, if still not paid, expire membership"""
    objMembers = GetDataFolder(objHere, 'E3Member')
    strResult = "<ul>\n"
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            strStatus = objMember.CheckMembershipStatus(blnReportOnly)
            if strStatus:
                strResult += strStatus
    if blnReportOnly:
        strResult += "</ul>"
    else:
        strResult = "Done"
    return strResult

def EnWTest(objHere):
    objMe = SearchOne(objHere, 'E3Member', 'Username', 'ccoen@gotadsl.co.uk')
    if not objMe:
        objMe = SearchOne(objHere, 'E3Member', 'Username', 'CoachCoen')
    if objMe:
        objMe.CheckMembershipStatus()
        return "Done"
    else:
        return "Not found"

def CheckBounces(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            objMember.CheckExcessiveBouncing()

def RecordNumberOfMembers(objHere):
    intNumber = NumberOfListMembers(objHere)
    dodListStat = GetDOD(objHere, 'E3ListStat')
    objListStat = dodListStat.NewObject()
    objListStat.SetDateOfCount(datetime.date.today())
    objListStat.Count = intNumber
    return intNumber

def DailyFunctions(objHere):
    UpdateCounts(objHere)
    ExpiriesAndWarnings(objHere)
    CountMembers(objHere)
    intMembers = RecordNumberOfMembers(objHere)
    CheckBounces(objHere)
    SendDailyDigests(objHere)
    UpdateCacheItem(objHere, "HomePageContents")
    return "Success, members: %s" % intMembers

def UnicodeTest(objHere):
    objMember = SearchOne(objHere, 'E3Member', 'Username', 'CoachCoen')
    print "Name: ", objMember.Name
    print "Type: ", type(objMember.Name)
#    strName = objMember.Name
#    ucName = unicode(strName)
#    print ucName
#    print "Type: ", type(ucName)
#    objMember.Name = ucName
    print objMember.propertyMap()
    StringsToUnicode(objMember)

def StringsToUnicode(objObject):
    for dictProperty in objObject.propertyMap():
        if dictProperty['type'] == 'string':
            strName = dictProperty['id']
            strValue = objObject.getProperty(strName)
            print strName, type(strValue)
            if type(strValue) == types.StringType:
                strCommand = "objObject.%s = unicode(objObject.%s, 'ascii', 'replace')" % (strName, strName)
                exec strCommand
    for objSubObject in objObject.objectValues():
        StringsToUnicode(objSubObject)
