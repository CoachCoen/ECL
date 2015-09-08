import datetime
import random
from libConstants import cnShortDateFormat
from libConstants import cnLastDate
from libEmail import SendEmail

from libDatabase import SearchOne
from libGeneral import GetParameter

cnCypher = 'GzHYjfJ9CURd652PqBouxy4IDVOMcX0vgwlAKiEQ7kbmW8eZtpLraN1TSF3snh'

#ActionId consists of following parts:
#MemberId - 17 digits (note: current member id only has 6 digits, but we may need more)
#Type of action (sequential number, calling bespoke code, 4 digits)
#Expiry date (if any, 6 digits - yymmdd or 000000)
#ActionId is encoded, with check sum
#3 digit check sum, to give a 1 in 1000 chance of creating a valid action id at random (note: chances are worse, since member id probably won't exist, nor will the action type or the expiry date)

def GetSubKey(strKey, intStart):
    strResult = ""
    intLocation = intStart
    while intLocation < len(strKey):
        strResult += strKey[intLocation]
        intLocation += 3
    return strResult

def GenerateChecksum(strKey):
# Key is 20 digits long, then generate 4 digit check sum
# 1. Split key into 3 numbers, by taking 1st, 4th, 7th, etc digits for first number, etc. This will give 7, 7, 6 digits
# Note: to simplify this, add "4" to end of key
# 2. For each number, work out the remainder after dividing by a 4 digit prime
# 3. Add up the 4 remainders, drop the 5th digit, keep the rest

    intResult = 0
    for intI in range(0, 3):
        strSubKey = GetSubKey(strKey, intI)
        intSubKey = int(strSubKey)
        (intDummy, intRemainder) = divmod(intSubKey, 719)
        intResult += intRemainder
    strResult = str(intRemainder).zfill(5)[2:]
    return strResult

def EncodeKey(strKey):
# strKey is 27 digits long, plus 3 digit checksum = 30 digits
# Go from 30 digits (0 - 9) to 30 characters in 'A'-'Z', 'a'-'z', '0' - '9'
# Shuffle them, to create a fixed cypher

#    print "Encode key, from |%s|, %s digits" % (strKey, len(strKey))
    strResult = ""
    intTotal = 0
    for strDigit in strKey:
        intDigit = int(strDigit)
        intTotal += intDigit + 3
        (intDummy, intTotal) = divmod(intTotal, 62)
#        print intTotal,
        strResult += cnCypher[intTotal]
#    print
    return strResult

def GenerateActionKey(strId, intAction, dtmExpiryDate):
# First two digits determine what type of item this is
# Last 15 digits are the actual id
    if "E3Member" in strId:
        intId = int(strId[8:])
        intType = 1
    elif strId.isDigit(): # Message
        intId = int(strId)
        intType = 2
        
    strFullId = str(intType).zfill(2) + str(intId).zfill(15) # 17 chars
    strAction = str(intAction).zfill(4) # 4 chars
    strDate = str(dtmExpiryDate.year)[2:] + str(dtmExpiryDate.month).zfill(2) + str(dtmExpiryDate.day).zfill(2) # 6 chars

#    print "Individual elements: %s - %s - %s, length: %s, %s, %s" % (strFullId, strAction, strDate, len(strFullId), len(strAction), len(strDate))
    strRawKey = strFullId + strAction + strDate # 17 + 4 + 6 = 27 chars
#    print "Raw key: %s, %s characters" % (strRawKey, len(strRawKey))
    strChecksum = GenerateChecksum(strRawKey)
#    print "Check sum: %s" % strChecksum
    strRawKey += strChecksum
    strResult = EncodeKey(strRawKey)
    return strResult
    
def DecodeActionKey(strKey):
    strResult = ""
    intPrev = 0
    for strChar in strKey:
        intChar = cnCypher.find(strChar)
        intResult = intChar - intPrev
        if intResult < 0:
            intResult += 62
        intPrev = intChar
#        (intDummy, intResult) = divmod(intResult, 62)
        strResult += str(intResult - 3)
#        intTotal += intChar
#        (intDummy, intTotal) = divmod(intTotal, 62)
#        print intTotal,
#    print
    return strResult

def GetObjectFromUniversalId(objHere, strObjectId):
    strType = strObjectId[:2]
    strId = strObjectId[2:]
    intType = int(strType)
    if intType == 1: # Member
        intId = int(strId)
        strMemberId = "E3Member" + str(intId).zfill(6)
        objMember = SearchOne(objHere, "E3Member", "id", strMemberId)
        return objMember
    elif intType == 2: # Message
        objMessage = SearchOne(objHere, "E3Message", "id", strId)
        return objMessage
    return None

def ValidateActionKey(objHere, strKey):
    # Correct length
    if len(strKey) <> 30:
#        print "Length: %s" % len(strKey)
        return (False, None, None, 0)
        
    # Check sum correct
    strChecksum = strKey[27:]
    strKey = strKey[:27]
    if strChecksum <> GenerateChecksum(strKey):
#        print "Checksum incorrect: |%s|" % strChecksum
        return (False, False, None, 0)
        
    strObjectId = strKey[:17]
    strAction = strKey[18:21]
    strDate = strKey[21:]
    
#    print "ObjectId: |%s|" % strObjectId
#    print "Action: |%s|" % strAction
#    print "Date: |%s|" % strDate
    
    strYear = "20" + strDate[:2]
    strMonth = strDate[2:4]
    strDay = strDate[4:]
#    print "Year: %s" % strYear
#    print "Month: %s" % strMonth
#    print "Day: %s" % strDay
    try:
        dtmExpiryDate = datetime.date(year = int(strYear), month = int(strMonth), day = int(strDay))
    except:
        return (False, False, None, 0)
#        print "Incorrect date"

#    print "Date: %s" % dtmExpiryDate

    if not strAction.isdigit():
        return (False, False, None, 0)
        
    intAction = int(strAction)
        
    objObject = GetObjectFromUniversalId(objHere, strObjectId)

    if not objObject:
        return (False, False, None, 0)
        
#    print "Object exists"
    
    dtmNow = datetime.date.today()
    blnExpired = (dtmExpiryDate < dtmNow)
        
    return (True, blnExpired, objObject, intAction)
    
def TestActionKeys(objHere):
    print "-" * 50
    strMessage = """
<p>Start of message</p>
<p><a href="{1}">Link 1</a></p>
<p><a href="{2}">Link 2</a></p>
<p><a href="{3}">Link 3</a></p>
"""
    
    objMember = objHere.unrestrictedTraverse("/Data/E3/E3Members/Batch006/E3Member006060")
    dtmExpiryDate = datetime.date.today()
    intAction = 10
    strKey = GenerateActionKey(objMember.id, intAction, dtmExpiryDate)
    print "Key: |%s|, %s digits" % (strKey, len(strKey))
    strOriginal = DecodeActionKey(strKey)
    print "Original: |%s|, %s digits" % (strOriginal, len(strOriginal))
    
    ValidateActionKey(objHere, strOriginal)
    
    strMessage = InsertActionKeys(strMessage, objMember.id)
    return strMessage
    
def AlreadyDone(objMember, intAction, blnDoNow = False):
    strAction = str(intAction).zfill(2) + ":"

    for strDone in objMember.DoLaterDone:
        if strAction in strDone:
            return True

    if blnDoNow:
        objMember.DoLaterDone = objMember.DoLaterDone + ("%s %s" % (strAction, datetime.date.today()), )
    return False
    
def InfoOwnerAboutNewEmailAddress(objHere):
    strId = GetParameter(objHere.REQUEST, "MemberId")
    strNewEmailAddress = GetParameter(objHere.REQUEST, "EmailAddress")
    strMessage = "Member with id %s would like to switch to the following email address: %s" % (strId, strNewEmailAddress)
    strSubject = "Email change request from ECL website"
    SendEmail(objHere, strMessage, strSubject, "coen@coachcoen.com")
    return """
<fieldset>
    <legend>Your request</legend>
    <p>The list owner has been notified of your request to use a new email address</p>
    <p>This will probably be done during the next working day</p>
</fieldset>"""

def ClaimAdditionalTrialPeriod(objMember, intAction):
    objMember.SendPasswordReminder()
    strExtraInfo = """
<fieldset>
    <legend>For your information</legend>
    <p>An email with your username and password has been emailed to your registered address(es)</p>
    <p>In case none of these addresses work anymore, please enter your current email address below, so the list owner can sort this out for you</p>
    <fieldset>
        <form action="." method="get">
            <p>
                <label>Email address</label>
                <input type="text" name="EmailAddress">
                <input type="hidden" name="MemberId" value="%s">
                <input type="hidden" name="Action" value="InfoOwnerAboutNewEmailAddress">
            </p>
            <p>
                <input type="submit" name="SubmitButton" value="Submit" class="btn">
            </p>
        </form>
    </fieldset>
    <p>If you want to change your email address go to <a href="/MyECL">MyECL</a>. Note: You will need your username and password for this</p>
    <p>Also, to help you manage the volume of list messages I suggest you try out the new Structured Digest. To change to the Structured Digest go to <a href="/MyECL">MyECL</a>. Also see the page on <a href="/About/Manage">managing the list messages</a></p>
</fieldset>""" % objMember.id
        
    if AlreadyDone(objMember, intAction, True):
        return """
<fieldset>
    <legend>Action already done</legend>
    <p>You have already extended your membership with the extra trial period</p>
    <p>If you have any questions, please <a href="/ContactDetails">contact the list owner</a></p>
    
</fieldset>""" + strExtraInfo

    objMember.CreateAdditionalTrialPeriod(31)
    strResult = """
<fieldset>
    <legend>New trial period</legend>
    <p>Welcome to your extra trial period</p>
    <p>Your membership now runs until %s</p>
</fieldset>
""" % objMember.GetNextExpiryDate().strftime(cnShortDateFormat)
    return strResult + strExtraInfo

def NoMoreCommercialEmails(objMember, intAction):
    objMember.NoCommercialEmails = True
    return """
<fieldset>
    <legend>No more emails</legend>
    <p>Your request to stop receiving information about the Euro Coach List has been recorded</p>
</fieldset>"""

def MultipleRegistrations(objMember, intAction):
    objMember.DuplicateMembership = True
    
    return """
<fieldset>
    <legend>Multiple list membership</legend>
    <p>Thanks for letting me know about this duplicate membership</p>
</fieldset>"""

def ProcessDoLaterRequest(objHere):

    strIncorrectAction = """
<fieldset>
    <legend>Incorrect action</legend>
    <p>The action you have requested seems to be incorrect</p>
    <p>Please <a href="/ContactDetails">contact the list owner</a> or try again</p>
</fieldset>
"""
    strAction = GetParameter(objHere.REQUEST, "Action")
    if strAction == "InfoOwnerAboutNewEmailAddress":
        return InfoOwnerAboutNewEmailAddress(objHere)

    strRequestId = GetParameter(objHere.REQUEST, "RequestId")
    
    if not strRequestId:
        return strIncorrectAction

    strOriginal = DecodeActionKey(strRequestId)
#    print "Original key: %s" % strOriginal
    (blnValidKey, blnExpired, objObject, intAction) = ValidateActionKey(objHere, strOriginal)
    if not blnValidKey:
        return strIncorrectAction
        
    if blnExpired:
        return """
<fieldset>
    <legend>Action expired</legend>
    <p>The action you have requested is no longer valid</p>
</fieldset>
"""
    
    if intAction == 1:
        return ClaimAdditionalTrialPeriod(objObject, intAction)
        
    elif intAction == 2:
        return NoMoreCommercialEmails(objObject, intAction)
        
    elif intAction == 3:
        return MultipleRegistrations(objObject, intAction)
        
    return strIncorrectAction

def InsertOneActionKey(intAction, strId):
    dtmDate = datetime.date(day=1, month=1, year=2099)

    if intAction == 1: # Claim additional trial period - valid for 6 months
        dtmDate = datetime.date.today() + datetime.timedelta(days=183)
        
    if intAction in [1, 2, 3]:
        strKey = GenerateActionKey(strId, intAction, dtmDate)
#        print "Key: |%s|, %s chars" % (strKey, len(strKey))
        return strKey
        
    return ""

def InsertActionKeys(strMessage, strMemberId):
#    print "Insert action keys for %s" % strMemberId
    # Replace all {1}, etc, with correct URL
    strResult = ""
    lstParts = strMessage.split('"{')
    strResult = lstParts[0]
    for strPart in lstParts[1:]:
        strNewPart = '"{' + strPart
        intPosition = strPart.find("}")
        if intPosition >= 0:
            strId = strPart[:intPosition]
            strPart = strPart[intPosition+1:]
            if strId.isdigit():
                strNewPart = """"http:/www.EuroCoachList.com/MyECL/Request?RequestId=%s%s""" % (InsertOneActionKey(int(strId), strMemberId), strPart)
        strResult += strNewPart
            
    return strResult
    
