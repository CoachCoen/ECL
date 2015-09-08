from libGeneral import GetParameter
from libGeneral import GetDataFolder
from libDatabase import SearchOne
from E3DoLater import InsertActionKeys
from libEmail import SendEmail
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMessage import MIMEMessage
import datetime
from libConstants import cnShortDateFormat

#For starters, keep it simple, i.e. bespoke code for this promotion:
#Message stored in /Data/E3/EmailsToMembers
#Subfolders (e.g. ../Message1, ../Message2)
#Property: Message
#Property: Sent to (lines, all email addresses)
#Options:
#Send test message (i.e. just to me)
#Show what has already been sent

def ListOneMessage(objMessage):
    strResult = """
<fieldset>
    <legend>Details for message %s</legend>
    <form>
        <p><label>Name:</label> %s</p>
        <p><label>Subject:</label> %s</p>
        <p><label>Number sent:</label> %s</p>
    </form>
</fieldset>
<fieldset>
    <legend>Actions</legend>
    <form method ="post" action=".">
        <input type="hidden" name="Action" value="SendBatchEmails">
        <input type="hidden" name="MessageName" value="%s">
        <p><label>Membership type:</label> 
            <input type="radio" name="MembershipType" value="All"> All members &nbsp;&nbsp;&nbsp; 
            <input type="radio" name="MembershipType" value="Live" checked> Live members &nbsp;&nbsp;&nbsp;
            <input type="radio" name="MembershipType" value="Expired"> Expired members </p>
        <p><label>Delivery type:</label>
            <input type="radio" name="DeliveryType" value="All" checked> All types &nbsp;&nbsp;&nbsp;
            <input type="radio" name="DeliveryType" value="Digest"> Digest mode &nbsp;&nbsp;&nbsp;
            <input type="radio" name="DeliveryType" value="TextDigest"> Text digest &nbsp;&nbsp;&nbsp;
            <input type="radio" name="DeliveryType" value="StructuredDigest"> Structured digest &nbsp;&nbsp;&nbsp;
            <input type="radio" name="DeliveryType" value="TopicsList"> Topics only &nbsp;&nbsp;&nbsp;
            <input type="radio" name="DeliveryType" value="MIMEDigest"> MIME Digest &nbsp;&nbsp;&nbsp;
            <input type="radio" name="DeliveryType" value="Direct"> Direct</p>
        <p><label>Holiday mode:</label>
            <input type="radio" name="HolidayMode" value="All" checked> All &nbsp;&nbsp;&nbsp;
            <input type="radio" name="HolidayMode" value="OnHoliday"> On holiday &nbsp;&nbsp;&nbsp;
            <input type="radio" name="HolidayMode" value="NotOnHoliday"> Not on holiday </p>
        <p><label>Numbers:</label>
            <input type="radio" name="Numbers" value="100"> First/next 100 &nbsp;&nbsp;&nbsp;
            <input type="radio" name="Numbers" value="JustMe" checked> Just me &nbsp;&nbsp;&nbsp;
            <input type="radio" name="Numbers" value="All"> All</p>
        <p><input type="submit" class="btn" value="Send"></p>
    </form>
</fieldset>
""" % (objMessage.id, objMessage.id, objMessage.Subject, len(objMessage.AlreadyDone), objMessage.id)
    return strResult
    
def MatchesCriteria(objMember, strMembershipType, strDeliveryType, strHolidayMode):
    if strMembershipType == "Live" and objMember.MembershipType <> "Full":
        return False

    if strMembershipType == "Expired" and objMember.MembershipType <> "None":
        return False

    if strDeliveryType == "Digest" and not objMember.EmailFrequency_ECL == "Daily":
        return False
        
    if strDeliveryType in ["MIMEDigest", "TopicsOnly", "StructuredDigest", "TextDigest", "Direct"]:
        if not objMember.EmailFrequency_ECL == "Daily":
            return False
        if not objMember.EmailDigestMode == strDeliveryType:
            return False
        
    if strHolidayMode == "OnHoliday" and not objMember.NoMail:
        return False
        
    if strHolidayMode == "NotOnHoliday" and objMember.NoMail:
        return False
        
    return True

def GetMemberList(objMessage, strMembershipType, strDeliveryType, strHolidayMode):
    lstResult = []
    for objBatch in GetDataFolder(objMessage, "E3Member").objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if not objMember.ParkingMember() and \
                not objMember.id in objMessage.AlreadyDone and \
                not objMember.DuplicateMembership and \
                not objMember.NoCommercialEmails:
                if MatchesCriteria(objMember, strMembershipType, strDeliveryType, strHolidayMode):
                    if objMember.PreferredEmailAddress():
                        lstResult.append(objMember)
    return lstResult

def FormatList(lstMembers):
    strResult = ""
    for objMember in lstMembers:
        strEmailAddress = objMember.EmailDeliveryAddress
        strName = objMember.Name
        if "unknown" in strName.lower():
            strName = ""
        if strName:
            strName = ", %s" % strName
        strResult += "%s (%s%s)\n" % (strEmailAddress, objMember.id, strName)
    return strResult

def FormatIdList(objHere, lstMemberIds):
    lstMembers = []
    for strId in lstMemberIds:
        objMember = SearchOne(objHere, "E3Member", "id", strId)
        if objMember:
            lstMembers.append(objMember)
    return FormatList(lstMembers)

def InsertVariableText(strMessage, objMember):
    return InsertActionKeys(strMessage, objMember.id)

def SendOneOne(objMember, strMessage, strSubject):
    strMessage = InsertVariableText(strMessage, objMember)
    strMessage = strMessage.encode('ascii', 'xmlcharrefreplace')        
    strSubject = InsertVariableText(strSubject, objMember)
    strEmailAddress = objMember.PreferredEmailAddress()
#    strEmailAddress = "coen@coachcoen.com"
    strFrom = "Coen de Groot <coen@coachcoen.com>"
    objEmail = MIMEMultipart()
    objEmail['Reply-to'] = 'coen@coachcoen.com'
    objEmail.preamble = strSubject
    objHTML = MIMEText(strMessage, 'html')
    objEmail.attach(objHTML)

    SendEmail(objMember, objEmail.as_string(), strSubject, strEmailAddress, strFrom, True)


def SendNow(objMessage):
    strConfirmed = GetParameter(objMessage.REQUEST, "Confirmation")
    if not strConfirmed or strConfirmed <> "Yes":
        return "<p>Not sent - please confirm and try again</p>"
        
    strMembershipType = GetParameter(objMessage.REQUEST, "MembershipType")
    strDeliveryType = GetParameter(objMessage.REQUEST, "DeliveryType")
    strHolidayMode = GetParameter(objMessage.REQUEST, "HolidayMode")
    strNumbers = GetParameter(objMessage.REQUEST, "Numbers")
    lstMembers = GetMemberList(objMessage, strMembershipType, strDeliveryType, strHolidayMode)

    if strNumbers == "All":
        lstMembersNow = lstMembers
    elif strNumbers == "JustMe":
        intNumberToSendTo = 1
        objMe = SearchOne(objMessage, "E3Member", "Username", "CoachCoen")
        if objMe:
            lstMembersNow = [objMe, ]
        else:
            lstMembersNow = []
    elif strNumbers == "100":
        intNumberToSendTo = min(len(lstMembers), 100)
        lstMembersNow = lstMembers[:100]
    else:
        intNumberToSendTo = 0
        return "<p>Incorrect strNumbers: %s</p>" % strNumbers
    strMessage = objMessage.Message
    strSubject = objMessage.Subject
    objMessage.AlreadyDone = objMessage.AlreadyDone + ("%s: %s, %s, %s, %s" % (datetime.date.today().strftime(cnShortDateFormat), strMembershipType, strDeliveryType, strHolidayMode, strNumbers), )
    for objMember in lstMembersNow:
        SendOneOne(objMember, strMessage, strSubject)
        objMessage.AlreadyDone = objMessage.AlreadyDone + (objMember.id, )
    return "<p>Sent</p>"

def AskConfirmation(objMessage):
    strMembershipType = GetParameter(objMessage.REQUEST, "MembershipType")
    strDeliveryType = GetParameter(objMessage.REQUEST, "DeliveryType")
    strHolidayMode = GetParameter(objMessage.REQUEST, "HolidayMode")
    strNumbers = GetParameter(objMessage.REQUEST, "Numbers")
    lstMembers = GetMemberList(objMessage, strMembershipType, strDeliveryType, strHolidayMode)
    if strNumbers == "All":
        intNumberToSendTo = len(lstMembers)
        lstMembersNow = lstMembers
    elif strNumbers == "JustMe":
        intNumberToSendTo = 1
        objMe = SearchOne(objMessage, "E3Member", "Username", "CoachCoen")
        if objMe:
            lstMembersNow = [objMe, ]
        else:
            lstMembersNow = []
    elif strNumbers == "100":
        intNumberToSendTo = min(len(lstMembers), 100)
        lstMembersNow = lstMembers[:100]
    else:
        intNumberToSendTo = 0
        print "Incorrect strNumbers: %s" % strNumbers
    strResult = """
<fieldset>
    <legend>Your selection</legend>
    <p>Send your emails to the following list members:</p>
    <form>
        <p><label>Membership</label> %s</p>
        <p><label>Delivery</label> %s</p>
        <p><label>Holiday</label> %s</p>
        <p><label>Numbers</label> %s</p>
        <p><b>Found %s member(s)</b></p>
        <p>Already sent to %s member(s)</p>
        <p><b>Yet to be sent to %s member(s)</b></p>
    </form>
</fieldset>
<fieldset>
    <legend>To be sent to</legend>
    <p>To be sent to the following members:</p>
    <textarea rows="10" cols="100">%s</textarea>
</fieldset>
<fieldset>
    <legend>Already sent to </legend>
    <p>Already sent to the following members:</p>
    <textarea rows="10" cols="100">%s</textarea>
</fieldset>
<fieldset>
    <legend>Confirmation</legend>
    <form action="." method="post">
        <p><input type="checkbox" name="Confirmation" value="Yes"> Yes, send this message to these %s member(s)</p>
        <input type="hidden" name="Action" value="ConfirmedSendNow">
        <input type="hidden" name="MessageName" value="%s">
        <input type="hidden" name="MembershipType" value="%s">
        <input type="hidden" name="DeliveryType" value="%s">
        <input type="hidden" name="HolidayMode" value="%s">
        <input type="hidden" name="Numbers" value="%s">
        <p><input type="submit" value="Send now" class="btn"></p>
    </form>
</fieldset>
""" % (strMembershipType, strDeliveryType, strHolidayMode, strNumbers, len(lstMembers) +  len(objMessage.AlreadyDone), len(objMessage.AlreadyDone), len(lstMembers), FormatList(lstMembersNow), FormatIdList(objMessage, objMessage.AlreadyDone), intNumberToSendTo, objMessage.id, strMembershipType, strDeliveryType, strHolidayMode, strNumbers)
    # Get choices
    # Show choices
    # Build list
    # Show list
    # Ask for confirmation
    return strResult

def ListMessages(objHere):
    objE3Data = objHere.unrestrictedTraverse("/Data/E3")
    strMessageName = GetParameter(objHere.REQUEST, "MessageName")
    if strMessageName and strMessageName in objE3Data.EmailsToMembers.objectIds():
        objMessage = objE3Data.EmailsToMembers.unrestrictedTraverse(strMessageName)
        strAction = GetParameter(objHere.REQUEST, "Action")
        if strAction == "SendBatchEmails":
            return AskConfirmation(objMessage)
        elif strAction == "ConfirmedSendNow":
            SendNow(objMessage)
        return ListOneMessage(objMessage)
        
    strResult = "<ul>\n"
    for objFolder in objE3Data.EmailsToMembers.objectValues():
        strResult += """<li><a href=".?MessageName=%s">%s: &quot;%s&quot;, sent to %s member(s)</a></li>\n""" % (objFolder.id, objFolder.id, objFolder.Subject, len(objFolder.AlreadyDone))
    strResult += "</ul>\n"
    return strResult
    

