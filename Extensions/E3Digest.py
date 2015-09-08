# encoding: utf-8

from libDatabase import GetDataFolder
from libDatabase import SearchOne
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
#from email.MIMEBase import MIMEBase
from email.MIMEMessage import MIMEMessage
import email
#from email.header import Header
#from email.charset import Charset

from E3Messages import GetSenderIdentification
from E3Messages import ClearSubjectHeader
from libConstants import cnShortDateFormat
from libConstants import cnFullDateFormat
from libEmail import SendEmail
from libString import PrepareMessageText
#from E3Offerings import BuildOfferingMessage
from E3Offerings import CreateOfferingEmail
from libString import ToUnicode

import datetime

cnLine = "-" * 50
cnStandardFooter = """%s
Do not forward this email or any part thereof
For support, to subscribe or unsubscribe go to www.EuroCoachList.com""" % cnLine
cnStandardFooterHTML = """Do not forward this email or any part thereof<br>
For support, to subscribe or unsubscribe go to <a href="http://www.EuroCoachList.com">www.EuroCoachList.com</a>"""

cnDigestIntro = """When replying remove "noreply-" from the email address and please edit your Subject line so it is more specific than "Re: Euro Coach List Digest" """

def ExtractName(strEmailAddress):
    if '<' in strEmailAddress:
        strResult = strEmailAddress[:strEmailAddress.find('<')] + strEmailAddress[(strEmailAddress.find('>') + 1):]
    else:
        strResult = strEmailAddress
    strResult = strResult.replace('"', '').strip()
    return strResult

def GetHTMLHeader():
    return """
    <div style="float:left; border-width:1px; border-style:solid; border-color:black; background:#EEEEEE; font-family:sans-serif; width:100%%">
        <div style="float:left;padding:0px; padding-top:0px; padding-bottom:0px">
            <div style="background: #F9A01B; color:white; font-size:300%%; font-weight:bold; ">
                [ec-l]
            </div>
            <div style="color:grey; font-weight:bold; font-size:80%%; text-align:right">
                Website links:
            </div>
        </div>
        <div style="float:left; margin-left:5px;">
            <div style="color:grey; font-size: 200%%; font-weight:bold; margin-bottom:0px; padding-bottom:0px">
                Euro Coach List
            </div>
            <div style="color:#F9A01B; font-weight:bold; margin-top:-10px; margin-bottom:10px; padding-top:0px">
                A Working Community of Professional Coaches
            </div>
            <div style="margin-bottom:5px; color:grey; font-weight:bold; font-size:80%%"><a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com">Home page</a> |
                <a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com/Membership">Membership</a> |
                <a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com/Rules">Rules</a> |
                <a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com/MyECL">MyECL</a> |
                <a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com/Archive">Archive</a>
            </div>
        </div>
    </div>
"""

# Search option temporarily disabled because there was a problem when not logged in
# When re-enabling, put "</form>" at end for GetHTMLFooter()
def GetHTMLHeaderWithSearch():
    return """<form action="http://www.EuroCoachList.com/Archive/ViewSearchResults" method="post">
    <div style="float:left; border-width:1px; border-style:solid; border-color:black; background:#EEEEEE; font-family:sans-serif; width:100%%">
        <div style="float:left;padding:0px; padding-top:0px; padding-bottom:0px">
            <div style="background: #F9A01B; color:white; font-size:300%%; font-weight:bold; ">
                [ec-l]
            </div>
            <div style="color:grey; font-weight:bold; font-size:80%%; text-align:right">
                Website links:
            </div>
        </div>
        <div style="float:left; margin-left:5px;">
            <div style="color:grey; font-size: 200%%; font-weight:bold; margin-bottom:0px; padding-bottom:0px">
                Euro Coach List
            </div>
            <div style="color:#F9A01B; font-weight:bold; margin-top:-10px; margin-bottom:10px; padding-top:0px">
                A Working Community of Professional Coaches
            </div>
            <div style="margin-bottom:5px; color:grey; font-weight:bold; font-size:80%%"><a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com">Home page</a> |
                <a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com/Membership">Membership</a> |
                <a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com/Rules">Rules</a> |
                <a style="text-decoration:none; color:grey" href="http://www.EuroCoachList.com/MyECL">MyECL</a>
                <input type="text" name="SearchBoth" style="color: #404040;	border: 1px inset #00008B; display:inline; margin-left:10px; "><input type="Submit" style="color: #404040; background-color:#FEEACE; border: 1px outset #00008B; font-weight:bold;" value="Archive Search">
            </div>
        </div>
    </div>
"""

def GetHTMLTopics():
    return """<div style="margin-top:10px; padding:0px; margin-right: 10px; float:left; border-width:1px; border-left-style:solid; border-top-style:solid; border-color:grey; width: 100%%; font-family:sans-serif; font-size:80%%">
        <div style="padding-left: 10px">
            <p style="font-size:120%%; font-weight:bold; color:#F9A01B">%(Title)s, %(Date)s</p>
            <a name="Topics"></a><p>Today's Topics</p>
            %(Topics)s
        </div>
    </div>
"""

def GetHTMLFooter():
    return  """   <div style="margin-top: 10px; float:left; border-width:1px; border-style:solid; border-color:black; background:#EEEEEE; font-family:sans-serif; font-size:80%%%%; width:100%%%%">
        <div style="padding: 0px; padding-left: 10px">

            <p>%s</p>
        </div>
    </div>
""" % cnStandardFooterHTML

def IdToLink(objHere, strId):
    if "Offer" in strId:
        objOffering = SearchOne(objHere, "E3Offering", "id", strId)
        strLink = "Offerings?Id=%s" % strId
        if objOffering:
            if objOffering.Type == "Event":
                strLink = "Events?EventIdId=%s" % strId
    else:
        strLink = "Archive/ViewThread?ThreadId=%s" % strId
#    print "Id to link, from %s to %s" % (strId, strLink)
    return strLink

def OneStructuredDigest(objHere, strId, strDate, strSender, strBody, strSubject, intMessageNumber):

    strTemplate = u"""
    <div style="margin-top:10px; padding:0px; float:left; border-width:1px; border-left-style:solid; border-top-style:solid; border-color:grey; width: 100%%; font-family:sans-serif; font-size:80%%">
        <div style="padding-left: 10px">
            <p><a name="Message%(MessageNumber)s"></a><a style="display:inline; font-size: 110%%; font-weight:bold; color:#F9A01B; text-decoration:none" href="http://www.EuroCoachList.com/%(Link)s">%(Subject)s</a><br>
            Message %(MessageNumber)s, posted %(MessageDate)s by %(Sender)s</p>
            <p>
                %(MessageText)s<br>
                <div style="color:grey; display:inline">%(Shortened)s </div>
                <a href="http://www.EuroCoachList.com/%(Link)s" style="color:grey">Original Message</a>
                <a href="#Topics" style="color:grey">Back to Topics List</a>
                %(ReplyToSender)s
                <a href="mailto:eurocoach-list@forcoaches.com?subject=Re: [ec-l] %(Subject)s">Reply to all (list members)</a>
            </p>
        </div>
    </div>
"""

    strLink = IdToLink(objHere, strId)

    strSenderEmail = ExtractEmailFromSender(strSender)
    if strSenderEmail:
        strReplyToSender = """<a href="mailto:%s?subject=Re: [ec-l] %s">Reply (to sender)</a>""" % (strSenderEmail, strSubject)
    else:
        strReplyToSender = ""

    if strId.isdigit():
        (blnShortened, strMessageText) = PrepareMessageText(strBody)
    else:
        blnShortened = ""
        strMessageText = strBody

    if blnShortened:
        strShortened = "(cut off after 500 words) ...<br>"
    else:
        strShortened = ""

    strSubject = SafeToUnicode(strSubject)

    strMessageText = strMessageText.encode('utf-8', 'replace')
    strMessageText = ToUnicode(strMessageText)

    try:
        strSender = strSender.encode('utf-8', 'replace')
    except:
        strSender = ToUnicode(strSender)

    strSender = SenderToHTML(strSender)
    strSender = ToUnicode(strSender)
    strReplyToSender = ToUnicode(strReplyToSender)
    strSubject = ToUnicode(strSubject)
    strLink = ToUnicode(strLink)

    strResult = strTemplate % {'Link': strLink,
            'Subject': strSubject,
            'MessageDate': strDate,
            'MessageNumber': intMessageNumber,
            'Sender': strSender,
            'ReplyToSender': strReplyToSender,
            'MessageText': strMessageText,
            'Shortened': strShortened}
    try:
        strResult = unicode(strResult, 'ascii', 'ignore')
    except:
        pass
    return strResult

def ExtractEmailFromSender(strSender):
    lstSender = strSender.split()
    strResult = ""
    for strPart in lstSender:
        strPart = strPart.replace('"', '')
        if '@' in strPart:
            strPart = strPart.replace(">", "").replace("<", "")
            return strPart
    return ""

def SenderToHTML(strSender):
    lstSender = strSender.split()
    strResult = ""
    for strPart in lstSender:
        strPart = strPart.replace('"', '')
        if '@' in strPart:
            strPart = """<a href="mailto:%s">%s</a>""" % (strPart.replace('<', '').replace('>', ''), strPart.replace('<', '&lt;').replace('>', '&gt;'))
        strResult += strPart + " "
    return strResult

def HTMLTopicList(objHere, lstDigestInfo, strTemplate):
    strResult = ""
    intMessageNumber = 1
    for (strMessageId, strMessageDate, strSender, strName, strSubject, strPlainText, strSource, strHTMLText) in lstDigestInfo:
        strMySender = SenderToHTML(strSender)

        strLink = IdToLink(objHere, strMessageId)

        try:
            strSubject = strSubject.encode('ascii', 'xmlcharrefreplace')
        except:
            strSubject = strSubject.decode('ascii', 'ignore')
            strSubject = strSubject.encode('ascii', 'ignore')

        strResult +=  strTemplate % {'MessageNumber': intMessageNumber,
                            'Subject': strSubject,
                            'Sender': strMySender,
                            'Date': strMessageDate,
                            'MessageId': strMessageId,
                            'Link': strLink}

        intMessageNumber += 1
    return strResult

def HTMLMessageList(objHere, lstDigestInfo):
    strResult = ""
    intMessageNumber = 1
    for (strMessageId, strMessageDate, strSender, strName, strSubject, strPlainText, strSource, strHTMLText) in lstDigestInfo:
        strResult += OneStructuredDigest(objHere, strMessageId, strMessageDate, strSender, strHTMLText, strSubject, intMessageNumber)
        intMessageNumber += 1
    return strResult

def StructuredDigestHTML(objHere, strDate, lstDigestInfo, blnAdverts):
    strTemplate =  GetHTMLHeader() + GetHTMLTopics() + "%(Messages)s" + GetHTMLFooter()

    if blnAdverts:
        strTitle = "Daily Adverts Digest"
    else:
        strTitle = "Daily Messages Digest"

    strTopics = HTMLTopicList(objHere, lstDigestInfo, """<li>%(Date)s - <a href="#Message%(MessageNumber)s">%(Subject)s</a> by %(Sender)s</li>""")
    strMessages = HTMLMessageList(objHere, lstDigestInfo)

#    strTopics = strTopics.encode('utf-8', 'replace')
#    strTopics = ToUnicode(strTopics)
#    strTemplate = ToUnicode(strTemplate)
#    strTemplate = strTemplate.encode('utf-8', 'replace')
#    strMessages = strMessages.encode('utf-8', 'replace')
    strMessages = strMessages.encode('ascii', 'xmlcharrefreplace')
#    print "Topics, type: ", type(strTopics)
#    print "Template, type: ", type(strTemplate)
#    print "Messages, type: ", type(strMessages)

    strResult = strTemplate % {'Date': strDate,
                                'Topics': strTopics,
                                'Messages': strMessages,
                                "Title": strTitle}
    return strResult

def CreateStructuredDigest(objHere, lstDigestInfo, strDate, blnAdverts):
    strHTML = StructuredDigestHTML(objHere, strDate, lstDigestInfo, blnAdverts)
    strEmail = HTMLEmail(strHTML, blnAdverts)
    return strEmail

def OneTopic(strSubject, strName, intMessageNumber):
    return u"""%s. %s (%s)\t
""" % (intMessageNumber, ToUnicode(strSubject), ToUnicode(strName))

def SafeToUnicode(strString):
    try:
        strString = strString.encode('utf-8', 'replace')
    except:
        strString = strString.decode('ascii', 'ignore')
        strString = strString.encode('utf-8', 'replace')
    return strString

def OneTextDigest(strDate, strSender, strSubject, strBody, intMessageNumber):
    strSubject = SafeToUnicode(strSubject)

    # strBody = strBody.encode('utf-8', 'replace')
    strBody = ToUnicode(strBody)
    strSender = ToUnicode(strSender)
    strSubject = ToUnicode(strSubject)

#    print type(strSubject), type(strBody), type(strSender), type(strDate)
    strResult = """
%s\t
Message: %s\t
Date: %s\t
From: %s\t
Subject: %s\t
%s""" % (cnLine, intMessageNumber, strDate, strSender, strSubject, strBody)

#    print intMessageNumber, type(strResult)
    strResult = SafeToUnicode(strResult)
    return strResult

def TextTopicsList(lstDigestInfo):
    strTopics = u""
    intMessageNumber = 1
    for (strMessageId, strMessageDate, strSender, strName, strSubject, strPlainText, strSource, strHTMLText) in lstDigestInfo:
#        print "Subject: %s" % strSubject
#        print "Subject, type = ", type(strSubject)
        try:
            strSubject = strSubject.encode('utf-8', 'replace')
        except:
            strSubject = strSubject.decode('ascii', 'ignore')
            strSubject = strSubject.encode('utf-8', 'replace')
#        print "Subject, post utf-8 en/decode: %s" % strSubject
        strOneTopic = OneTopic(strSubject, strSender, intMessageNumber)
#        print "strTopics, type = ", type(strTopics)
#        print "strOneTopic, type = ", type(strOneTopic)
        strTopics = strTopics + strOneTopic
        intMessageNumber += 1
    return strTopics

def TextMessageList(lstDigestInfo):
    intMessageNumber = 1
    strMessages = ""
    for (strMessageId, strMessageDate, strSender, strName, strSubject, strPlainText, strSource, strHTMLText) in lstDigestInfo:
        strMessages += OneTextDigest(strMessageDate, strSender, strSubject, strPlainText, intMessageNumber)
        intMessageNumber += 1
    return strMessages

def CreateTextDigest(lstDigestInfo, strDate, blnAdverts):
#    strTopics = TextTopicsList(lstDigestInfo)
    intMessageNumber = 1
    strMessages = TextMessageList(lstDigestInfo)
    strTopics = TextTopicsList(lstDigestInfo)

    if blnAdverts:
        strIntro = ""
        strType = "Adverts"
    else:
        strIntro = cnDigestIntro
        strType = "Messages"

    strTemplate = """%(Intro)s\t

Euro Coach List %(Type)s Digest, %(Date)s\t

Today's Topics:\t
%(Topics)s
%(Messages)s

%(Footer)s
"""
    strMessage = strTemplate % {'Intro': strIntro,
        'Date': strDate,
        'Topics': ToUnicode(strTopics),
        'Messages': ToUnicode(strMessages),
        "Type": strType,
        'Footer': cnStandardFooter}

    strMessage = strMessage.encode('ascii', 'ignore')
    objDigest = MIMEText(strMessage, 'plain', 'utf-8')

    if blnAdverts:
        objDigest['Subject'] = "Euro Coach List Adverts Digest"
    else:
        objDigest['Subject'] = "Euro Coach List Messages Digest"
    objDigest['From'] = 'eurocoach-list@forcoaches.com'
    objDigest['Reply-to'] = 'noreply-eurocoach-list@forcoaches.com'
#    objDigest .. Charset('utf-8')

    return objDigest.as_string()

def CreateTextDigestOld(lstDigestInfo, strDate):
#    strTopics = TextTopicsList(lstDigestInfo)
    intMessageNumber = 1
    strMessages = TextMessageList(lstDigestInfo)
    strTopics = TextTopicsList(lstDigestInfo)

    strTemplate = """%(Intro)s\t

Euro Coach List Digest, %(Date)s\t

Today's Topics:\t
%(Topics)s
%(Messages)s

%(Footer)s
"""
    strResult = strTemplate % {'Intro': cnDigestIntro,
        'Date': strDate,
        'Topics': strTopics,
        'Messages': strMessages,
        'Footer': cnStandardFooter}

    return strResult

def TopicsListHTML(objHere, lstDigestInfo, strDate, blnAdverts):
    strTopics = ""
    strTemplate = GetHTMLHeader() + GetHTMLTopics() + GetHTMLFooter()

    if blnAdverts:
        strTitle = "Daily Adverts Digest"
    else:
        strTitle = "Daily Messages Digest"

    strTopics = HTMLTopicList(objHere, lstDigestInfo, """<li>%(Date)s - <a href="http://www.eurocoachlist.com/%(Link)s">%(Subject)s</a> by %(Sender)s</li>
""")

    strResult = strTemplate % {'Date': strDate, 'Topics': strTopics, "Title": strTitle}

    return strResult

def CreateTopicsList(objHere, lstDigestInfo, strDate, blnAdverts):
    strHTML = TopicsListHTML(objHere, lstDigestInfo, strDate, blnAdverts)
    strEmail = HTMLEmail(strHTML, blnAdverts)
    return strEmail

def DigestMessageList(lstDigestInfo):
    lstResult = []
    for (strMessageId, strMessageDate, strSender, strName, strSubject, strPlainText, strSource, strHTMLText) in lstDigestInfo:
        if strSource:
            objMail = email.message_from_string(strSource)
            objPart = MIMEMessage(objMail)
            lstResult.append(objPart)
    return lstResult

def CreateMIMEDigest(lstDigestInfo, strDate, blnAdverts):
    objDigest = MIMEMultipart()
    if blnAdverts:
        objDigest['Subject'] = "Euro Coach List Message Digest"
        strType = "Adverts"
    else:
        objDigest['Subject'] = "Euro Coach List Adverts Digest"
        strType = "Messages"
    objDigest['From'] = 'eurocoach-list@forcoaches.com'
    objDigest['Reply-to'] = 'noreply-eurocoach-list@forcoaches.com'
#    objDigest['Content-type'] = "text/plain; charset=utf-8"
#    objDigest['To'] = 'eurocoach-list@forcoaches.com'
    objDigest.preamble = 'Here is the MIME digest'

    strTopics = TextTopicsList(lstDigestInfo)
    lstMessageObjects = DigestMessageList(lstDigestInfo)

    strBody = """%s\t

Euro Coach List %s Digest, %s\t

Today's topics:\t
%s

%s""" % (cnDigestIntro, strType, strDate, strTopics, cnStandardFooter)

    strBody = strBody.encode('ascii', 'ignore')
    objMailBody = MIMEText(strBody, 'plain', 'utf-8')
    objDigest.attach(objMailBody)

    for objMessageObject in lstMessageObjects:
        objDigest.attach(objMessageObject)

    return objDigest.as_string()

def SimpleHTMLToText(strHTML):
    strResult = strHTML
    strResult = strResult.replace("<br>", "\n")
    strResult = strResult.replace("<p>", "")
    strResult = strResult.replace("</p>", "\n")
    return strResult

def GetOfferingInfo(objHere, strOfferingId):
    objOffering = SearchOne(objHere, "E3Offering", "id", strOfferingId)
    if not objOffering:
        return None

    strFrom = objOffering.GetFromAddress()
    strSubject = objOffering.AdvertSubjectHeader()
    (strMessage, strPlainMessage) = objOffering.AdvertDetails(False, blnForDigest = True)

#   (strSender, strSubject, strMessage, strPlainMessage) = BuildOfferingMessage(objOffering)
    strSender = objOffering.GetFromAddress()
    strName = ExtractName(strSender)
#    strName = objOffering.unrestrictedTraverse("../..").VisibleName(True)
    strDate = objOffering.GetFirstAnnouncementDate().strftime("%d %b %Y, %H:%M")
#    strPlainText = strPlainMessage.encode('ascii', 'replace')
    strHTMLText = ToUnicode(strMessage).encode('ascii', 'xmlcharrefreplace')
    strSource = CreateOfferingEmail(strSender, strSubject.encode('utf-8', 'replace'), ToUnicode(strMessage).encode('ascii', 'xmlcharrefreplace'), strOfferingId)
    return((strOfferingId, strDate, strSender.encode('ascii', 'replace'), strName.encode('ascii', 'replace'), strSubject, strPlainMessage, strSource, strHTMLText))

def GetMessageInfo(objHere, strMessageId):
    objMessage = SearchOne(objHere, "E3Messages", "id", strMessageId)

    if not objMessage:
        return None

    strDate = objMessage.mailDate.strftime("%d %b %Y, %H:%M")
    strText = objMessage.mailBody.strip().decode('ascii', 'ignore')
    strSubject = ClearSubjectHeader(objMessage.mailSubject).strip()
#    strSender = GetSenderIdentification(objMessage, True)
    strSender = objMessage.mailFrom
    strName = ExtractName(objMessage.mailFrom)
    try:
        strSource = objMessage.mailSource
    except:
        strSource = ""
    return((strMessageId, strDate, strSender, strName, strSubject, strText, strSource, strText))

def GetDigestInfo(objHere, lstMessageList = None, blnAdverts = False):
    objData = GetDataFolder(objHere, 'E3Data')
    if not lstMessageList:
        lstMessageList = objData.DigestList
    lstResult = []
    for strMessageId in lstMessageList:
        lstDetails = None
        if "E3Offering" in strMessageId:
            if blnAdverts:
                lstDetails = GetOfferingInfo(objHere, strMessageId)
        else:
            if not blnAdverts:
                lstDetails = GetMessageInfo(objHere, strMessageId)

        if lstDetails:
            lstResult.append(lstDetails)
    return lstResult

def CreateDigest(objHere, lstDigestInfo, strDate, strDeliveryMode, blnAdverts):
    strDigestContent = ""
    strReturnAddress = ""
    if strDeliveryMode == "MIMEDigest":
        strDigestContent = CreateMIMEDigest(lstDigestInfo, strDate, blnAdverts)
        strReturnAddress = "Euro Coach List <noreply-eurocoach-list@forcoaches.com>"

    elif strDeliveryMode == "TextDigest":
        strDigestContent = CreateTextDigest(lstDigestInfo, strDate, blnAdverts)
        strReturnAddress = "Euro Coach List <noreply-eurocoach-list@forcoaches.com>"

    elif strDeliveryMode == "StructuredDigest":
        strDigestContent = CreateStructuredDigest(objHere, lstDigestInfo, strDate, blnAdverts)
        strReturnAddress = "Euro Coach List <noreply-eurocoach-list@forcoaches.com>"

    elif strDeliveryMode == "TopicsList":
        strDigestContent = CreateTopicsList(objHere, lstDigestInfo, strDate, blnAdverts)
        strReturnAddress = "Euro Coach List <noreply-eurocoach-list@forcoaches.com>"

    return (strDigestContent, strReturnAddress)

def EmailDigest(objHere, lstAddresses, strContent, strFrom, blnMIME, blnAdverts):
    if blnAdverts:
        strType = "Adverts"
    else:
        strType = "Messages"
    SendEmail(objHere, strContent, "Euro Coach List %s Digest" % strType, "coen@coachcoen.com", strFrom, blnMIME)
    for strAddress in lstAddresses:
        if strAddress:
            SendEmail(objHere, strContent, "Euro Coach List %s Digest" % strType, strAddress, strFrom, blnMIME)

def SendOneSetOfDailyDigests(objHere, blnAdverts):
    lstDigestInfo = GetDigestInfo(objHere, blnAdverts = blnAdverts)
    if not lstDigestInfo:
        return
    strDate = datetime.datetime.today().strftime("%d %b %Y")
    if blnAdverts:
        objECL = GetDataFolder(objHere, "E3List").ECL_Adv
        dictMailingLists = objECL.GetMailingLists()
    else:
        objECLAdv = GetDataFolder(objHere, "E3List").ECL
        dictMailingLists = objECLAdv.GetMailingLists()
#    print dictMailingLists
    for strDeliveryMode in ("MIMEDigest", "TextDigest", "StructuredDigest", "TopicsList"):
        if strDeliveryMode in ['MIMEDigest', 'StructuredDigest', 'TopicsList', 'TextDigest']:
            blnMIME = True
        else:
            blnMIME = False
        (strDigestContent, strFrom) = CreateDigest(objHere, lstDigestInfo, strDate, strDeliveryMode, blnAdverts)
        EmailDigest(objHere, dictMailingLists[strDeliveryMode], strDigestContent, strFrom, blnMIME, blnAdverts)

def SendDailyDigests(objHere):
    SendOneSetOfDailyDigests(objHere, False)
    SendOneSetOfDailyDigests(objHere, True)
    objData = GetDataFolder(objHere, 'E3Data')
    objData.DigestList = ()

def SendOneFinalDigest(objHere, strDeliveryMode, strEmailAddress):
#    print "SendOneFinalDigest"
    lstDigestInfo = GetDigestInfo(objHere)
    strDate = datetime.datetime.today().strftime("%d %b %Y")
    (strDigestContent, strFrom) = CreateDigest(objHere, lstDigestInfo, strDate, strDeliveryMode)
    strSubject = "Euro Coach List Digest"
    blnMIME = False
    if strDeliveryMode in ['MIMEDigest', 'StructuredDigest', 'TopicsList']:
        blnMIME = True
    SendEmail(objHere, strDigestContent, strSubject, strEmailAddress, strFrom, blnMIME)
#    print "Email sent to %s" % strEmailAddress

def TestStructuredDigest(objHere):
    return CreateStructuredDigest(objHere, ('1110191693000', '1163435823000', '1146566680000', '1146566681000', '1146566681001', '1146566681002'))

def TextEmail(strTo, strToName, strBCC, strFrom, strFromName, strSubject, strBody):
    strTemplate = """To: %(ToName)s <%(To)s>
From: %(FromName)s <%(From)s>
Subject: %(Subject)s
%(BCC)s

%(Body)s

"""
    if strBCC:
        strBCC = "BCC: %s" % strBCC
    return strTemplate % {'To': strTo,
                            'ToName': strToName,
                            'From': strFrom,
                            'FromName': strFromName,
                            'BCC': strBCC,
                            'Subject': strSubject,
                            'Body': strBody}

def HTMLEmail(strHTML, blnAdvert):
    objDigest = MIMEMultipart()
    if blnAdvert:
        strSubject = "Euro Coach List Adverts Digest"
    else:
        strSubject = "Euro Coach List Messages Digest"
    objDigest.preamble = strSubject
#    objDigest['Subject'] = strSubject
#    objDigest['From'] = 'eurocoach-list@forcoaches.com'
    objDigest['Reply-to'] = 'noreply-eurocoach-list@forcoaches.com'
#    objDigest['To'] = 'eurocoach-list@forcoaches.com'
    objHTML = MIMEText(strHTML, 'html')
    objDigest.attach(objHTML)

    return objDigest.as_string()

def MIMEEmail(strTo, strToName, strBCC, strFrom, strFromName, strSubject, strBody, lstAttachments):
    pass

