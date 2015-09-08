# encoding: utf-8

"""Functions for sending emails"""

from libDatabase import GetDataFolder
import random
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMessage import MIMEMessage
from libString import ToUnicode

from email import Encoders

def ExtractToAddress(strTo):
    if '<' in strTo:
        strResult = strTo[strTo.find('<') + 1:]
        strResult = strResult[:strResult.find('>')]
    else:
        strResult = strTo
    return strResult

def RandomSpoolName():
    intMailId = random.randint(1, 100000)
    strName = "OutgoingEmail%s" % str(intMailId).zfill(5)
    return strName

def FileExists(strPath, strName):
    lstFiles = os.listdir(strPath)
    if strName in lstFiles:
        return True
    return False

def SendEmailWithAttachments(objHere, strMessage, strSubject, strTo, strFromName, strFromAddress, lstAttachments):
    objMessage = MIMEMultipart()
    objMessage['Subject'] = strSubject
    objMessage['To'] = strTo
    strFrom = "%s <%s>" % (strFromName, strFromAddress)
    objMessage['From'] = strFrom

    objMailBody = MIMEText(strMessage)
    objMessage.attach(objMailBody)

    for objAttachment in lstAttachments:
        lstPath = objAttachment.getPhysicalPath()
        strFileName = lstPath[-1]
        strContents = str(objAttachment.data)
        strContentType = objAttachment.content_type
        (strMainType, strSubType) = strContentType.split('/')
        objAttachedFile = MIMEBase(strMainType, strSubType)
        objAttachedFile.set_payload(strContents)
        Encoders.encode_base64(objAttachedFile)
        objAttachedFile.add_header('Content-Disposition', 'attachment', filename = strFileName)
        objMessage.attach(objAttachedFile)

    objMailHost = objHere.unrestrictedTraverse('/Websites/ECLv3/MailHost')
    strMessage = objMessage.as_string()
    objMailHost.send(strMessage, strTo, strFrom, strSubject)

def SendHTMLEmail(objHere, strHTML, strSubject, strTo, strFrom = "coen@coachcoen.com"):

    objDigest = MIMEMultipart()

    objDigest.preamble = strSubject
#    objDigest['Reply-to'] = 'noreply-eurocoach-list@forcoaches.com'
    objHTML = MIMEText(strHTML, 'html')
    objDigest.attach(objHTML)

    strMessage = objDigest.as_string()

    objMailHost = objHere.unrestrictedTraverse('/Websites/ECLv3/MailHost')
    try:
        objMailHost.send(strMessage, strTo, strFrom, strSubject)
        return True
    except:
        return False

def SendEmail(objHere, strMessage, strSubject, strTo, strFrom = "coen@coachcoen.com", blnMIME = False):
    if not strTo:
        return

    if not blnMIME:
        strMessage = """To: %s
From: %s

%s""" % (strTo, strFrom, strMessage)

    objMailHost = objHere.unrestrictedTraverse('/Websites/ECLv3/MailHost')
    if blnMIME:
        try:
            objMailHost.send(strMessage, strTo, strFrom, strSubject)
            return True
        except:
            return False
    else:
        try:
            strMessage = strMessage.encode("ascii", "ignore")
        except:
            strMessage = strMessage.decode("ascii", "ignore")
            strMessage = strMessage.encode("ascii", "ignore")
        strTo = strTo.encode("ascii", "ignore")

        try:
            objMailHost.send(strMessage, strTo, strFrom, strSubject, "quoted-printable")
            return True
        except:
            return False

def SendAnyEmail(objHere, strMessage, strSubject, strTo, strFrom = "coen@coachcoen.com", blnMIME = False):
    if "<p>" in strMessage:
        return SendHTMLEmail(objHere, strMessage, strSubject, strTo, strFrom)
    else:
        return SendEmail(objHere, strMessage, strSubject, strTo, strFrom, blnMIME)

def SendEmailOld(strMessage, strSubject, strTo, strFrom = "coen@coachcoen.com", blnMIME = False):

    """Send an email by writing a file into the MailDropHost spool directory"""
    strName = RandomSpoolName()
    strPath = "/tmp/maildrop/spool/"
    while FileExists(strPath, strName):
        strName = RandomSpoolName()

    strToAddress = ExtractToAddress(strTo)
    if strSubject:
        strSubject = "Subject: %s\n\n" % strSubject
    if blnMIME:
        strFile = """##To:%s
##From: %s
%s
""" % (strToAddress, strFrom, strMessage)
    else:
        strFile = """##To:%s
##From: %s
From: %s
To: %s
%s
%s
""" % (strToAddress, strFrom, strFrom, strTo, strSubject, strMessage)
    fileMail = open(strPath + strName, 'w')
    fileMail.write(strFile)

def FormatForEmail(strMessage):
    """Replaces relative URLs with absolute URLs
        and =" with =3D" """
    strResult = strMessage

    lstParts = strResult.split('href="/')
    strResult = string.join(lstParts, 'href="http://www.MentorCoaches.com/')

    lstParts = strResult.split('="')
    strResult = string.join(lstParts, '=3D"')
    return strResult

def SendErrorEmail(objHere, strErrorMessage):
    """Sends an error message to coen@coachcoen.com"""
    print "Error message sent: %s" % strErrorMessage
    strMessage = """System error:
%s
""" % strErrorMessage
    strTo = "coen@coachcoen.com"
    strFrom = "zope@EuroCoachList.com"
    strSubject = "ECL Payment system error"
    objMailHost = objHere.unrestrictedTraverse('/ECLv3/MailHost')
    objMailHost.send(strMessage, strTo, strFrom, strSubject)

import smtplib
from email.MIMEText import MIMEText

def SendSimpleEmail(strToAddress, strFromAddress, strFromName, strMessage, strSubject):
    """Send an email"""
    objSMTP = smtplib.SMTP()
    objMsg = MIMEText(strMessage)

    objMsg['Subject'] = strSubject
    objMsg['From'] = strFromAddress
    objMsg['To'] = strToAddress

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    objSMTP = smtplib.SMTP()
    objSMTP.connect()
    objSMTP.sendmail(strFromAddress, [strToAddress], objMsg.as_string())
    objSMTP.close()
