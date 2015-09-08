from libDatabase import GetDOD
from libDatabase import GetDataFolder
import datetime
from libConstants import cnEmptyDate
from libEmail import SendEmailWithAttachments
from libBuildHTML import InsertBrs

def SendOnePlannedMessage(objPlannedMessage):
    objStandardMessage = objPlannedMessage.unrestrictedTraverse(objPlannedMessage.SourceMessagePath)
    strSubject = objStandardMessage.EmailSubject
    strMessage = objStandardMessage.Message
    strSentFromName = objStandardMessage.unrestrictedTraverse('..').SentFromAddress
    strSentFromAddress = objStandardMessage.unrestrictedTraverse('..').SentFromAddress
    objSequence = objPlannedMessage.unrestrictedTraverse('..')
    strToAddress = objSequence.EmailAddress
    lstAttachments = []
    for fileAttachment in objStandardMessage.objectValues():
        lstAttachments.append(fileAttachment)
    SendEmailWithAttachments(objPlannedMessage, strMessage, strSubject, strToAddress, strSentFromName, strSentFromAddress, lstAttachments)
    objPlannedMessage.SetSentDate(datetime.date.today())

def SendTodaysMessages(objSequence):
    dtmNow = datetime.date.today()
    for objPlannedMessage in objSequence.PlannedMessages.objectValues('E3PlannedMessage'):
        if objPlannedMessage.GetPlannedDate() <= dtmNow:
            if objPlannedMessage.GetSentDate() == datetime.date(1901, 1, 1):
                SendOnePlannedMessage(objPlannedMessage)

def SendAutoEmails(objHere):
    for objBatch in GetDataFolder(objHere, "E3SequenceInProgress").objectValues('Folder'):
        for objSequence in objBatch.objectValues("E3SequenceInProgress"):
            if objSequence.Active:
                SendTodaysMessages(objSequence)

def AddNewAutoEmails(objHere):
    dodPlannedMessage = GetDOD(objHere, "E3PlannedMessage")
    for objBatch in GetDataFolder(objHere, "E3SequenceInProgress").objectValues('Folder'):
        for objSequence in objBatch.objectValues("E3SequenceInProgress"):
            print "Checking sequence for %s" % objSequence.title
            strSequenceName = objSequence.SequenceName
            objStandardSequence = objSequence.unrestrictedTraverse('/Data/E3/StandardMessageSequences/%s' % objSequence.SequenceName)
            lstPlannedMessages = []
            for objPlannedMessage in objSequence.PlannedMessages.objectValues("E3PlannedMessage"):
                lstPlannedMessages.append(objPlannedMessage.SourceMessagePath)
            for objStandardMessage in objStandardSequence.objectValues('Folder'):
                if not objStandardMessage.getPhysicalPath() in lstPlannedMessages:
                    AddOnePlannedMessage(objSequence, objStandardMessage, dodPlannedMessage)
                    print "Added: %s" % objStandardMessage.title
                else:
                    print "Found: %s" % objStandardMessage.title

def StartEmailSequence(objHere, strName, strMemberId = "", strEmailAddress = ""):
# 1.Create the E3SequenceInProgress object
# 2.Create the E3PlannedMessage objects within the Planned messages folder
#   1.PlannedDate = <current date> + DaysDelay
#   2.SentDate = blank

    dodSequence = GetDOD(objHere, 'E3SequenceInProgress')
    objSequence = dodSequence.NewObject()
    objSequence.title = '%s: %s' % (strName, strMemberId + strEmailAddress)
    objSequence.SequenceName = strName
    objSequence.SetStartDate(datetime.date.today())
    objSequence.MemberId = strMemberId
    if strMemberId and not strEmailAddress:
        objMember = SearchOne(objHere, "E3Member", "id", strMemberId)
        if objMember:
            strEmailAddress = objMember.PreferredEmailAddress()

    objSequence.EmailAddress = strEmailAddress
    objSequence.Active = True
    GeneratePlannedMessages(objSequence)
    SendTodaysMessages(objSequence)

def GeneratePlannedMessages(objSequence):
    dodPlannedMessage = GetDOD(objSequence, "E3PlannedMessage")
    objStandardSequence = objSequence.unrestrictedTraverse('/Data/E3/StandardMessageSequences/%s' % objSequence.SequenceName)
    for objStandardMessage in objStandardSequence.objectValues('Folder'):
        AddOnePlannedMessage(objSequence, objStandardMessage, dodPlannedMessage)

def AddOnePlannedMessage(objSequence, objStandardMessage, dodPlannedMessage):
    objMessage = dodPlannedMessage.NewObject(objSequence.PlannedMessages)
    dtmPlannedDate = objSequence.GetStartDate() + datetime.timedelta(days = objStandardMessage.DaysDelay)
    objMessage.SetPlannedDate(dtmPlannedDate)
    objMessage.title = "%s: %s" % (dtmPlannedDate, objStandardMessage.EmailSubject)
    objMessage.SourceMessagePath = objStandardMessage.getPhysicalPath()

def TestAutoEmails(objHere):
    StartEmailSequence(objHere, 'CBA01', '', 'coen@coachcoen.com')

def ValidLine(strText):
    return "<p>%s</p>" % strText

def ErrorLine(strText):
    return """<p style="colour:red">%s</p>""" % strText

def CheckFields(objObject, lstFieldList):
    strResult = ""
    for strFieldName in lstFieldList:
        if not objObject.hasProperty(strFieldName):
            strResult += ErrorLine("Missing field: %s" % strFieldName)
        elif not objObject.getProperty(strFieldName):
            strResult += ErrorLine("Blank field: %s" % strFieldName)
        else:
            strText = objObject.getProperty(strFieldName)
            if strFieldName == 'Message':
                strText = InsertBrs(strText)
            strResult += ValidLine("%s: %s" % (strFieldName, strText))
    return strResult

def CheckStandardMessage(objStandardMessage):
    strResult = "<h3>Checking message: %s</h3>" % objStandardMessage.id
    strResult += CheckFields(objStandardMessage, ('DaysDelay', 'EmailSubject', 'Message'))
    for objFile in objStandardMessage.objectValues():
        strResult += ValidLine("Attachment: %s" % objFile.absolute_url())
    return strResult

def VerifyOneAutoEmail(objStandardSequence):
    strDetails = CheckFields(objStandardSequence, ('title', 'SentFromAddress', 'SentFromName'))
    
    strResult = """<fieldset>
    <legend>Verifying message sequence: %s</legend>
%s
</fieldset>""" % (objStandardSequence.id, strDetails)
    for objStandardMessage in objStandardSequence.objectValues('Folder'):
        strResult += CheckStandardMessage(objStandardMessage)
    return strResult

def VerifyAutoEmails(objHere):
    strResult = ""
    for objStandardSequence in objHere.unrestrictedTraverse('/Data/E3/StandardMessageSequences').objectValues('Folder'):
        strResult += VerifyOneAutoEmail(objStandardSequence)
    return strResult

