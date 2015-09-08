# encoding: utf-8

from E3Messages import ClearSender
from libGeneral import GetParameter
from libConstants import cnShortDateFormat
from libDatabase import SearchOne
from E3Messages import ClearSubjectHeader
from libBuildHTML import InsertBrs
from E3Members import GetCurrentMember
from E3HTML import FullURL
import base64
from E3Messages import GetSenderIdentification
from E3Members import IsFullMember
from libString import ToUnicode

def GetThreads(objMessage, intThreadId, intMessageId):
    if objMessage.objectValues('Folder'):
        strResult = "<p>\n"
        strLink = "/Archive/ViewThread?Year=%s&Month=%s&ThreadId=%s" % (objMessage.mailDate.year(), objMessage.mailDate.month(), objMessage.id)
        strSender = ClearSender(objMessage.mailFrom)
        strMessageTime = objMessage.mailDate.strftime(cnShortDateFormat + " %H:%M")

        strResult = "%s by %s" % (strMessageTime, strSender)
        if intMessageId:
            strResult = strResult + """<a href="%s">%s</a>""" % (strLink, strResult)
        strResult = "<p>%s</p>\n" % strResult
        strReplies = ""
        for objM in objMessage.objectValues('Folder'):
            strLink = "/Archive/ViewThread?Year=%s&Month=%s&ThreadId=%s&MessageId=%s" % (objM.mailDate.year(), objM.mailDate.month(), objMessage.id, objM.id)
            strSender = ClearSender(objM.mailFrom)
            strMessageTime = objM.mailDate.strftime(cnShortDateFormat + " %H:%M")
            if int(objM.id) == intMessageId:
                strReplies += "<li>%s by %s</li>" % (strMessageTime, strSender)
            else:
                strReplies += """<li><a href="%s">%s by %s</a></li>""" % (strLink, strMessageTime, strSender)

        if strReplies:
            strResult += "<ul>%s</ul>" % strReplies
    else:
        strResult = ""
    return strResult

def CleanMessageId(varId):
    strId = str(varId)
    if 'bound' in strId:
        strId = strId[strId.rfind('/') + 1:]
        strId = strId.replace('%3E', '')
        strId = strId.replace('>', '')
    return strId

def ViewAttachment(objHere):
#    print "View attachment"
    strThreadId = GetParameter(objHere.REQUEST, 'ThreadId')
    strMessageId = GetParameter(objHere.REQUEST, 'MessageId')
    if strMessageId:
        objMessage = SearchOne(objHere, 'E3Messages', 'id', strMessageId)
    else:
        objMessage = SearchOne(objHere, 'E3Messages', 'id', strThreadId)
    strAttachmentId = GetParameter(objHere.REQUEST, 'Attachment')
#    print strAttachmentId
    objAttachment = objMessage.unrestrictedTraverse(strAttachmentId)
    if 'image' in objAttachment.content_type:
        return "Can't show images yet"
#        return objAttachment.__call__(objAttachment)
#        return objAttachment
#    print dir(objAttachment)
#    return objAttachment.content_type
#    print dir(objHere.REQUEST.response.headers)
#    objHere.REQUEST.Response.content-encoding = objAttachment.content_type
#    print "content type:", objAttachment.content_type
    objHere.REQUEST.response.setHeader('content-type', """%s; name="%s" """ % (objAttachment.content_type, objAttachment.title))
#    objHere.REQUEST.response.setHeader('content-type', """%s""" % objAttachment.content_type)
    objHere.REQUEST.response.setHeader('content-length', len(objAttachment.data))
    objHere.REQUEST.response.setHeader('Accept-Ranges', 'bytes')
    if "image" in objAttachment.content_type:
        return objAttachment
#        objHere.REQUEST.response.setHeader('content-transfer-encoding', 'base64')
#        return base64.encodestring(objAttachment)
#        return base64.encodestring(objAttachment.data)
    return objAttachment.data

def ListAttachments(objMessage, intThreadId, intMessageId = 0):
    strResult = ""
    strLink = "/Archive/ViewThread?Year=%s&Month=%s&ThreadId=%s" % (objMessage.mailDate.year(), objMessage.mailDate.month(), intThreadId)
    strAttachmentLink = "/Archive/ViewAttachment?Year=%s&Month=%s&ThreadId=%s" % (objMessage.mailDate.year(), objMessage.mailDate.month(), intThreadId)
    if intMessageId:
        strLink = strLink + "&MessageId=%s" % CleanMessageId(objMessage.id)
        strAttachmentLink = strAttachmentLink + "&MessageId=%s" % CleanMessageId(objMessage.id)

    for objAttachment in objMessage.objectValues('File'):
        strId = CleanMessageId(objAttachment.id)
        if not '.html' in strId and not '.txt' in strId:
#            strFullLink = '%s&Attachment=%s' % (strAttachmentLink, strId)
            strFullLink = objAttachment.absolute_url()
            strResult += """<li><a href="%s">%s</a></li>""" % (strFullLink,   objAttachment.title)

    if strResult:
        strResult = """<h2>Attachment(s)</h2>
        <ul>
            %s
        </ul>""" % strResult
    return strResult

def GetHTML(objMessage):
    for objAttachment in objMessage.objectValues('File'):
        if '.html' in str(objAttachment.id):
            return objAttachment.data
    return ""

def IsThreadPublic(objHere, objRequest):
    intThreadId = str(GetParameter(objRequest, 'ThreadId'))
    intMonth = str(GetParameter(objRequest, 'Month'))
    intYear = str(GetParameter(objRequest, 'Year'))
    strMessageId = GetParameter(objRequest, 'MessageId')
    if strMessageId:
        intMessageId = int(strMessageId)
    else:
        intMessageId = 0

    strThreadId = GetParameter(objRequest, 'ThreadId')
    objThread = SearchOne(objHere, 'E3Messages', 'id', strThreadId)
    if not objThread:
        return False
    if intMessageId:
        strMessageId = GetParameter(objRequest, 'MessageId')
        objMessage = SearchOne(objHere, 'E3Messages', 'id', strMessageId)
    else:
        objMessage = objThread
    if objMessage.Private:
        return False
    return True

def ViewThreadContents(objHere, objRequest):
#    print "Request: ", objRequest.REQUEST
    intThreadId = str(GetParameter(objRequest, 'ThreadId'))
    intMonth = str(GetParameter(objRequest, 'Month'))
    intYear = str(GetParameter(objRequest, 'Year'))
#    print "Thread: ", intThreadId
#    print "Month: ", intMonth
#    print "Year: ", intYear
    strAttachment = GetParameter(objRequest, 'Attachment')
    strMessageId = GetParameter(objRequest, 'MessageId')
    if strMessageId:
        intMessageId = int(strMessageId)
    else:
        intMessageId = 0

    strThreadId = GetParameter(objRequest, 'ThreadId')
    objThread = SearchOne(objHere, 'E3Messages', 'id', strThreadId)
    if intMessageId:
        strMessageId = GetParameter(objRequest, 'MessageId')
        objMessage = SearchOne(objHere, 'E3Messages', 'id', strMessageId)
    else:
        objMessage = objThread
    
    if not objThread:
        return "<p>Message not found. Please contact the list owner</p>"

    if strAttachment:
        objAttachment = objMessage.unrestrictedTraverse(strAttachment)
        return objMessage.unrestrictedTraverse(strAttachment)
    strSubject = ClearSubjectHeader(objMessage.mailSubject)
#    strThreads = GetThreads(objThread, intThreadId, intMessageId)
    strThreads = ""
    strDate = objMessage.mailDate.strftime(cnShortDateFormat + " %H:%M")
    objMember = GetCurrentMember(objHere)
#    if objMessage.Private and not objMember:


    strSender = GetSenderIdentification(objThread, IsFullMember(objHere))
#    else:
#        strSender = ClearSender(objMessage.mailFrom)
    strHTML = GetHTML(objMessage)
    objMember = GetCurrentMember(objHere)
    strPrivatePublic = ""
    if objMember:
        if objMember.id == objMessage.UserId:
            if objMessage.Private:
                strPrivatePublic = """<p>For list members only. <a href="%s&Action=SetPublic">Click here to make this a public message</a>. Note: Only make a message public if you have personally written the whole message</p>"""
            else:
                strPrivatePublic = """<p>Public message, visible to anyone. <a href="%s&Action=SetPrivate">Click here to make this a private message, visible to list members only</a></p>"""
            strPrivatePublic = strPrivatePublic % FullURL(objHere)
        
    if strHTML:
        strBody = strHTML
    else:
        strBody = InsertBrs(objMessage.mailBody)
    strAttachments = ListAttachments(objMessage, intThreadId, intMessageId)

    strAttachments = ToUnicode(strAttachments)
    strSubject = ToUnicode(strSubject)
    strSender = ToUnicode(strSender)
    strBody = ToUnicode(strBody)
    strThreads = ToUnicode(strThreads)
    strAttachments = ToUnicode(strAttachments)    

    strResult = u"""
<fieldset>
    <legend>%s by %s</legend>
""" % (strDate, strSender)

    strResult += u"<h2>%s</h2>\n" % strSubject
    strResult += strPrivatePublic + "\n"
    strResult += strThreads + "\n"
    strResult += strAttachments + "\n"
    strResult += u"""</fieldset>
<fieldset>
    <legend>Message</legend>
    <p>%s</p>
</fieldset>
""" % strBody

#    strResult = u"""    
#
#				<fieldset>
#					<legend>%(Date)s by %(Sender)s</legend>
#					<h2>%(Subject)s</h2>
#                    %(PrivatePublic)s
#                    %(Threads)s
#                    %(Attachments)s
#				</fieldset>
#				<fieldset>
#					<legend>Message</legend>
#					<p>%(Body)s</p>
#				</fieldset>""" % {'Subject': strSubject,
#                'Threads': strThreads,
#                'Date': strDate,
#                'Sender': strSender,
#                'Body': strBody,
#                'PrivatePublic': strPrivatePublic,
#                'Attachments': strAttachments}
#    strResult = unicode(strResult, 'ascii', 'replace')
    return strResult
