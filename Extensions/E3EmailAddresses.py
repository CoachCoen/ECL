# encoding: utf-8

import LocalPaths
reload(LocalPaths)

import datetime

from libDatabase import GetDOD
from libDatabase import GetDataFolder
from libString import ExtractAddress
from E3StartStop import RandomPassword
from libDatabase import SearchOne
from libGeneral import GetParameter
#from Mailman import MailList
from libConstants import cnSignature
from libEmail import SendEmail

"""Extract all email addreses, stored in /Archive/ECLArchive/*/*/<id>/mailFrom
Format: "Jilly Shaul" <lifematters@btinternet.com>

Check whether this email address already exists, i.e. Datastore/Members/Member<id>/EmailAddress#/EmailAddress = (address)
If it doesn't exist, create a new entry under Datastore/Members/Unknown/EmailAddress(next#)

This ties it all together, for searches, etc"""

def GetAllEmailAddresses(objMembers, objEmailCatalogue):
    """Gets all email addresses for all members, for quick checking"""
    dictResult = {}
    for objBatch in objMembers.objectValues():
        for objMember in objBatch.objectValues():
            for objEmailAddress in objMember.objectValues('E3EmailAddress'):
                objEmailCatalogue.catalog_object(objEmailAddress)
                strEmailAddress = objEmailAddress.EmailAddress.lower()
                dictResult[strEmailAddress] = objMember
    return dictResult
    
def ExtractOneAddress(objMessage, dictAllEmailAddresses, dodMember, dodEmailAddress):
    """Processes one message"""
    (strEmailAddress, strName) = ExtractAddress(objMessage.mailFrom)
    if not strEmailAddress.lower() in dictAllEmailAddresses.keys():
        objMember = dodMember.NewObject()
        objMember.Name = 'Unknown'
        objMember.Username = objMember.id
        objMember.Status = 'NoMember'
        objMember.Password = RandomPassword()
        objEmailAddress = dodEmailAddress.NewObject(objMember)
        objEmailAddress.EmailAddress = strEmailAddress
        objEmailAddress.Confirmed = False
        objEmailAddress.ConfirmationString = ''
        dictAllEmailAddresses[strEmailAddress] = objMember
    else:
        strOldName = dictAllEmailAddresses[strEmailAddress].Name
        if not strOldName or strOldName == 'Name unknown':
            dictAllEmailAddresses[strEmailAddress].Name = strName

    strUserId = dictAllEmailAddresses[strEmailAddress].id
    try:
        objMessage.manage_addProperty('UserId', strUserId, 'string')
    except:
        objMessage.UserId = strUserId

    return dictAllEmailAddresses

def ExtractEmailAddresses(objHere):
    """Processes all messages"""
#    objUnknownMember = SearchOne(objHere, 'E3Member', 'Username', 'Unknown')
#    if not objUnknownMember:
#        objDataObjectDefinition = GetDataFolder(objHere, 'DataObjectDefinitions').E3Member
#        objUnknownMember = objDataObjectDefinition.NewObject()
#        objUnknownMember.Username = 'Unknown'
    objArchive = GetDataFolder(objHere, 'E3Messages')
    objEmailAddresses = GetDataFolder(objHere, 'E3EmailAddress')
    objMembers = GetDataFolder(objHere, 'E3Member')

    dictAllEmailAddresses = GetAllEmailAddresses(objMembers, objEmailAddresses.Catalogue)
    dodMember = GetDOD(objHere, 'E3Member')
    dodEmailAddress = GetDOD(objHere, 'E3EmailAddress')
    intDone = 0
    for objYear in objArchive.objectValues():
        for objMonth in objYear.objectValues():
            for objThread in objMonth.objectValues():
                dictAllEmailAddresses = ExtractOneAddress(objThread, dictAllEmailAddresses, dodMember, dodEmailAddress)
                intDone = intDone + 1
#                if intDone > 100:
#                    return "done"
                for objMessage in objThread.objectValues('Folder'):
                    intDone = intDone + 1
                    dictAllEmailAddresses = ExtractOneAddress(objMessage, dictAllEmailAddresses, dodMember, dodEmailAddress)
    return "%s done" % intDone

def ConfirmEmailAddress(objHere):
    strId = GetParameter(objHere.REQUEST, 'Id')
#    print "ConfirmEmailAddress, id = ", strId
    strId = strId.replace('"', '')
    if not strId:
        return "<p>No confirmation string specified. Confirmation failed. Please try again</p>"
    objEmailAddress = SearchOne(objHere, 'E3EmailAddress', 'ConfirmationString', strId)
    if not objEmailAddress:
        return "<p>Confirmation string incorrect. Confirmation failed. Please try again</p>"
    dtmConfirmationSent = objEmailAddress.GetConfirmationStringSent()
    objEmailAddress.Confirm()
    strConfirmationMessage = """
<p>Email address %s confirmed</p>
<p>You can now use this email address to send and receive Euro Coach List messages</p>""" % objEmailAddress.EmailAddress
    return strConfirmationMessage

def AddAddress(dictAddresses, strMailFrom):
    strEmailAddress = ExtractAddress(strMailFrom)[0].lower()
    if not dictAddresses.has_key(strEmailAddress):
        dictAddresses[strEmailAddress] = 0
    dictAddresses[strEmailAddress] += 1

def UnclaimedEmailAddresses(objHere):
    dodUnclaimedEmailAddress = GetDOD(objHere, 'E3UnclaimedEmailAddress')
    dictAddresses = {}
    objMessages = GetDataFolder(objHere, 'E3Messages')
    for objYear in objMessages.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            for objThread in objMonth.objectValues('Folder'):
                if objThread.UserId == 'unknown':
                    AddAddress(dictAddresses, objThread.mailFrom)
                for objMessage in objThread.objectValues('Folder'):
                    if objMessage.UserId == 'unknown':
                        AddAddress(dictAddresses, objMessage.mailFrom)

    dodUnclaimedEmailAddress = GetDOD(objHere, 'E3UnclaimedEmailAddress')
    for strAddress in dictAddresses.keys():
        objUnclaimed = dodUnclaimedEmailAddress.NewObject()
        objUnclaimed.EmailAddress = strAddress
        objUnclaimed.SetRandomKey()

#def EnableMailing(objEmailAddress):
#    objMember = objEmailAddress.unrestrictedTraverse('..')
#    for objListMembership in objMember.objectValues('E3ListMembership'):
#        if objListMembership.EmailAddress == objEmailAddress.EmailAddress:
#            return
#    dodListMembership = GetDOD(objEmailAddress, 'E3ListMembership')
#    objListMembership = dodListMembership.NewObject(objMember)
#    objListMembership.ValuesForNew(objEmailAddress.EmailAddress, 'NoMail')

#def ProcessPostingOnlyAddresses(objHere):
#    objECL = MailList.MailList('eurocoach-list', lock=0)
#    lstPostingOnly = objECL.accept_these_nonmembers
#    for strEmailAddress in lstPostingOnly:
#        strEmailAddress = strEmailAddress.lower()
#        objEmailAddress = SearchOne(objHere, 'E3EmailAddress', 'EmailAddress', strEmailAddress)
#        if objEmailAddress:
#            EnableMailing(objEmailAddress)
#        else:
#            print "Posting only, not found: ", strEmailAddress

