# encoding: utf-8

import LocalPaths
reload(LocalPaths)

import sys
import string
import datetime
import random

from Mailman import MailList
from Mailman import Message
from Mailman import mm_cfg
from Mailman.MemberAdaptor import ENABLED
from Mailman.MemberAdaptor import BYBOUNCE

from E3Security import RandomPassword
from libDatabase import GetDOD
from libDatabase import Catalogue
from libDatabase import ReindexOne
from libDatabase import GetDataFolder
from libDatabase import SearchOne
from libConstants import cnFirstDate
from libConstants import cnLastDate
from libConstants import cnEmptyDate
from libConstants import cnMailmanEmptyDate
from libConstants import cnMailmanFirstDate
from libConstants import cnMailmanLastDate
from libConstants import cnListNameECL
from libConstants import cnSignature
from E3Members import CountMembers
from MetaHelp import BuildRules
from MetaHelp import ReadHelp
from MetaStart import CreateDataObjectDefinitions
from libEmail import SendEmail
from libFolders import AddFolder

def GetEmailAddresses(objAdmin, intMemberId):
    """Get all email addresses from Mailman for this intMemberId"""
    lstResult = []
    
    for strEmailAddress in objAdmin.admMemberEmailAddress.keys():
        if objAdmin.admMemberEmailAddress[strEmailAddress] == intMemberId:
            lstResult.append(strEmailAddress)
    return lstResult

def GetMemberDetails(objAdmin, objECL, intMemberId):
    """Get Name, Username, Password and OnHold status from Mailman for this intMemberId"""

    blnOnHold = False
    if objAdmin.admOnHold.has_key(intMemberId):
        if objAdmin.admOnHold[intMemberId]:
            blnOnHold = True

    strName = 'Name unknown'
    strPassword = RandomPassword()
    strUsername = ''
    strBackupName = ''
    lstEmailAddresses = GetEmailAddresses(objAdmin, intMemberId)
    for strEmailAddress in lstEmailAddresses:
        if objECL.passwords.has_key(strEmailAddress):
            strPassword = objECL.passwords[strEmailAddress]
        if objECL.usernames.has_key(strEmailAddress):
            strName = objECL.usernames[strEmailAddress]
        if objECL.members.has_key(strEmailAddress) or objECL.digest_members.has_key(strEmailAddress):
            strUsername = strEmailAddress
        strBackupName = strEmailAddress
    if not strUsername:
        strUsername = strBackupName

    return (strName, strUsername, strPassword, blnOnHold)

def ValidDate(lstDate):
    """Checks (intDate, intMonth, intYear) is a valid date
        If not, corrects it"""
    (intDate, intMonth, intYear) = lstDate
    if intDate == 31 and (intMonth in [4, 6, 9, 11]):
        intDate = 30
    if intDate > 28 and intMonth == 2:
        if intYear in [2000, 2004, 2008]:
            intDate = 29
        else:
            intDate = 28
    if (intYear, intMonth, intDate) == (0, 0, 0):
        return cnFirstDate
    dtmDate = datetime.date(intYear, intMonth, intDate)
    return dtmDate

def CalculateFreeMonths(dtmStartDate, dtmEndDate):
    deltaPeriod = dtmEndDate - dtmStartDate
    intResult = int((deltaPeriod.days / 30) + 0.5)
    return intResult

def ImportPeriods(objMember, objAdmin, intMemberId):
    """Reads periods from Mailman for this intMemberId and 
        creates new Period objects within objMember"""
                    
    dodPeriod = GetDOD(objMember, 'E3Period')
    dtmLastDate = cnFirstDate
    if objAdmin.admPeriod.has_key(intMemberId):
        for (strPeriodType, lstStartDate, lstEndDate) in objAdmin.admPeriod[intMemberId]:
            dtmStartDate = ValidDate(lstStartDate)
            dtmEndDate = ValidDate(lstEndDate)
            deltaDuration = dtmEndDate - dtmStartDate
            intDays = deltaDuration.days + 1

            dtmLastDate = max(dtmLastDate, dtmEndDate)
            if lstEndDate == cnMailmanEmptyDate:
                objMember.GiveLifetimeMembership(dtmStartDate)
            elif strPeriodType in ['f', 't']:
                objMember.GiveFreeMembershipPeriod(dtmStartDate, intDays, False)
            elif not strPeriodType in ['t', 'p', 'b']:
                print "Unknown period type: ", strPeriodType
            objPeriod = dodPeriod.NewObject(objMember.FromMailman)
            objPeriod.SetStartDate(dtmStartDate)
            objPeriod.SetEndDate(dtmEndDate)
            objPeriod.PeriodType = {'f': 'Free', 
                                    't': 'Trial',
                                    'p': 'Paid',
                                    'b': 'Bonus'}[strPeriodType]
    return dtmLastDate

def GetDeliveryMode(objECL, strEmailAddress):
    """Works out whether <strEmailAddress> is in TextDigest, MIMEDigest or Direct mode"""
    if objECL.digest_members.has_key(strEmailAddress):
        if objECL.getMemberOption(strEmailAddress, mm_cfg.DisableMime):
            return 'TextDigest'
        else:
            return 'MIMEDigest'

    if objECL.members.has_key(strEmailAddress):
        return 'Direct'
    return ''

def ImportListMembership(objEmailAddress, objECL, intMemberId, strEmailAddress):
    """Import all list memberships for <intMemberId> and <strEmailAddress> from Mailman"""
    strDeliveryMode = GetDeliveryMode(objECL, strEmailAddress)
    if not strDeliveryMode:
        strDeliveryMode = 'NoMail'
    else:
        intDeliveryStatus = objECL.getDeliveryStatus(strEmailAddress)
        blnNoMail = (intDeliveryStatus <> ENABLED)
        if blnNoMail:
            strDeliveryMode = 'NoMail'
            if intDeliveryStatus == BYBOUNCE:
                objEmailAddress.Bouncing = True
                print "Bouncing: ", objEmailAddress.id, objEmailAddress.EmailAddress
    dodListMembership = GetDOD(objEmailAddress, 'E3ListMembership')
    objListMembership = dodListMembership.NewObject(objEmailAddress)
    objListMembership.ListName = cnListNameECL
    objListMembership.SetDeliveryMode(strDeliveryMode)
    Catalogue(objListMembership)

def ImportEmailAddresses(objMember, objAdmin, objECL, intMemberId):
    """Import all email addresses for <intMemberId> from Mailman"""
    lstEmailAddresses = GetEmailAddresses(objAdmin, intMemberId)
    dodEmailAddress = GetDOD(objMember, 'E3EmailAddress')
    for strEmailAddress in lstEmailAddresses:
        objEmailAddress = dodEmailAddress.NewObject(objMember)
        objEmailAddress.EmailAddress = strEmailAddress
        objEmailAddress.Confirmed = True
        objEmailAddress.ConfirmationString = ''
        ImportListMembership(objEmailAddress, objECL, intMemberId, strEmailAddress)
        Catalogue(objEmailAddress)

def ImportOnePayment(objMember, intMemberId, lstPayment):
    """Stores payment within objMember"""
    dictPaymentTypes = {'WorldPay': 'WorldPay',
                        'Cheque': 'Cheque',
                        'Bank': 'Bank',
                        '2CO': '2Checkout',
                        '2Checkout': '2Checkout',
                        '2CO\r\n': '2Checkout',
                        'payment method unknown': 'Unknown',
                        'Cash': 'Cash',
                        'FF': 'Friday Forum',
                        'FF\r\n': 'Friday Forum'}
    dictCurrency = {'GBP': 'GBP',
                    'USD': 'USD',
                    'EUR': 'EUR',
                    '\xa3': 'GBP',
                    '?': 'Unknown',
                    '\x80': 'Unknown',
                    '': 'Unknown'}
    (strEmailAddress, strName, lstDate, strPaymentType, intMonths) = lstPayment[:5]
    if len(lstPayment) > 5:
        (strCurrency, fltAmount, strComments) = lstPayment[5:8]
    else:
        (strCurrency, fltAmount, strComments) = ('', 0.0, '')

    if len(lstPayment) > 8:
        intInvoiceNumber = lstPayment[8]
    else:
        intInvoiceNumber = 0
    strCurrency = dictCurrency[strCurrency]
    (intDay, intMonth, intYear) = lstDate
    if intYear < 1900:
        intYear += 2000
    dtmDate = datetime.date(intYear, intMonth, intDay)
    strPaymentType = dictPaymentTypes[strPaymentType]
    dodPayment = GetDOD(objMember, 'E3Payment')
    objPayment = dodPayment.NewObject(objMember.Historic)
    objPayment.SetDate(dtmDate)
    objPayment.PaymentType = strPaymentType
    objPayment.Name = strName
    objPayment.EmailAddress = strEmailAddress
    objPayment.Amount = fltAmount
    objPayment.Currency = strCurrency
    objPayment.Comments = strComments
    objPayment.Months = intMonths
    objPayment.InvoiceNumber = intInvoiceNumber
    Catalogue(objPayment)

def ImportPayments(objMember, objAdmin, intMemberId):
    """Import all payments for <intMemberId> from Mailman"""
    if objAdmin.admPayment.has_key(intMemberId):
        for lstPayment in objAdmin.admPayment[intMemberId]:
            ImportOnePayment(objMember, intMemberId, lstPayment)
            objMember.HasPayments = True

def ImportEvents(objMember, objAdmin, intMemberId):
    """Import all events for <intMemberId> from Mailman"""
    dodEvent = GetDOD(objMember, 'E3Event')
    if objAdmin.admBonusSent.has_key(intMemberId):
        for lstDate in objAdmin.admBonusSent[intMemberId]:
            dtmDate = datetime.date(lstDate[2], lstDate[1], lstDate[0])
            objEvent = dodEvent.NewObject(objMember.Historic)
            objEvent.EventType = 'BonusSent'
            objEvent.SetDate(dtmDate)
            Catalogue(objEvent)

    if objAdmin.admWarningSent.has_key(intMemberId):
        for lstDate in objAdmin.admWarningSent[intMemberId]:
            dtmDate = datetime.date(lstDate[2], lstDate[1], lstDate[0])
            objEvent = dodEvent.NewObject(objMember.Historic)
            objEvent.EventType = 'WarningSent'
            objEvent.SetDate(dtmDate)
            Catalogue(objEvent)
    
    for strEmailAddress in objAdmin.admExpiry.keys():
        if objAdmin.admMemberEmailAddress[strEmailAddress] == intMemberId:
            for lstDate in objAdmin.admExpiry[strEmailAddress]:
                dtmDate = datetime.date(lstDate[2], lstDate[1], lstDate[0])
            objEvent = dodEvent.NewObject(objMember.Historic)
            objEvent.EventType = 'Expiry'
            objEvent.SetDate(dtmDate)
            objEvent.EmailAddress = strEmailAddress
            Catalogue(objEvent)


def ImportOneMember(objHere, objAdmin, objECL, intMemberId, fileErrors, intDone):
    """Imports one member, including full details, from Mailman"""
    (strName, strUsername, strPassword, blnOnHold) = GetMemberDetails(objAdmin, objECL, intMemberId)
    dodMember = GetDOD(objHere, 'E3Member')
    objMember = dodMember.NewObject()
    objMember.Name = strName
    objMember.OnHold = blnOnHold
    objMember.ImportedFromMailman = True
    if strUsername:
        objMember.Username = strUsername
    else:
        objMember.Username = objMember.id
    print "%s - New member: %s, id: %s" % (intDone, objMember.Username, objMember.id)
    objMember.Password = strPassword
    AddFolder(objMember, 'FromMailman')

    dtmLastDate = ImportPeriods(objMember, objAdmin, intMemberId)
    deltaOneDay = datetime.timedelta(days = 1)
    dtmNextExpiryDate = dtmLastDate + deltaOneDay
    objMember.SetNextExpiryFromMailman(dtmNextExpiryDate)
    objMember.SetNextExpiryDate(dtmNextExpiryDate)

    ImportEmailAddresses(objMember, objAdmin, objECL, intMemberId)
    ImportPayments(objMember, objAdmin, intMemberId)
    ImportEvents(objMember, objAdmin, intMemberId)

    objMember.UpdateMembershipStatus()
#    if not objMember.LifetimeMember:
#        objMember.MembershipType = ExpiryStatusAtImport(objMember)
    Catalogue(objMember)
    return objMember

def TooLong(dtmDate1, dtmDate2):
    if dtmDate1 == cnLastDate:
        return False
    if dtmDate2 == cnLastDate:
        return False
    deltaPeriod = dtmDate1 - dtmDate2
    if abs(deltaPeriod.days) > 3:
        return True
    return False

def DateTest(objHere):
    print "-" * 30
    objMembers = GetDataFolder(objHere, 'E3Member')
    objMember = objMembers.Batch023.E3Member023067
    objPayment = objMember.Historic.E3Payment01430
    print type(objPayment.GetDate())
    objPayment.SetDate(objPayment.GetDate() + datetime.timedelta(days = 1))
    print "Plus one day: ", type(objPayment.GetDate())
    print "And the new one:"
    dodMember = GetDOD(objHere, 'E3Member')
    objMember = dodMember.NewObject()
    dodPayment = GetDOD(objHere, 'E3Payment')
    objPayment = dodPayment.NewObject(objMember.Historic)
    print objPayment.GetDate(), type(objPayment.GetDate())
    objPayment.Date = datetime.date.today()
    print type(objPayment.Date)
    print objPayment.Date > datetime.date.today()
    objPayment.Date = datetime.datetime.today()
    print type(objPayment.Date)
    print objPayment.Date > datetime.date.today()
    print objPayment.Date > datetime.datetime.today()
    print datetime.datetime.today() > objPayment.Date
    print datetime.date.today() > objPayment.Date
    objPayment.Date = datetime.date.today()
    print type(objPayment.Date)
    print objMember.id, objPayment.id
    print "-" * 30

def ImportMembers(objHere, objAdmin, objECL, intMaxMembers):
#    DateTest(objHere)
#    return

#def Dummy():
    """Imports all members, including full details, from Mailman"""
    intDone = 0
    fileErrors = open('/var/lib/zope/log/errors.log', 'w')
#    objMember = ImportOneMember(objHere, objAdmin, objECL, 988, fileErrors) # Was 72
    if True:
        for intMemberId in objAdmin.admMember.keys():
            if intMemberId <> 858:
                intDone = intDone + 1
                if intDone <= intMaxMembers:
#                    try:
                        objMember = ImportOneMember(objHere, objAdmin, objECL, intMemberId, fileErrors, intDone)
                        Catalogue(objMember)
#                    except:
#                        fileErrors.write('Error processing member: %s\n' % intMemberId)
    return "<p>Members imported</p>"

def CheckExpiryDates(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not objMember.LifetimeMember:
                print objMember.id
                dtmOldExpiryDate = objMember.GetNextExpiryDate()
                dtmNewExpiryDate = objMember.UpdateMembershipStatus()
                if dtmOldExpiryDate <> dtmNewExpiryDate:
                    print "Mismatch for %s" % objMember.id
                    return

def ImportWorldPayResults(objWorldPayCall, dictResults):
    """Import WorldPayResults for this WorldPayCall"""
    dodWorldPayResult = GetDOD(objWorldPayCall, 'E3WorldPayResult')
    for strKey in dictResults.keys():
        objWorldPayResult = dodWorldPayResult.NewObject(objWorldPayCall)
        objWorldPayResult.AttributeName = strKey
        objWorldPayResult.AttributeValue = dictResults[strKey]

def ImportOneWorldPayCall(objHere, objAdmin, intCallId):
    """Import one WorldPayCall from Mailman"""
    (strPaymentAddress, strMembershipAddress) = objAdmin.admWorldPayCalls[intCallId]
    dtmDateCalled = cnFirstDate
    if objAdmin.admWorldPayResults.has_key(intCallId):
        if objAdmin.admWorldPayResults[intCallId]['transStatus'] == 'Y':
            strStatus = 'Success'
        elif objAdmin.admWorldPayResults[intCallId]['transStatus'] == 'N':
            strStatus = 'Failed'
        else:
            strStatus = 'Unknown'
    else:
        strStatus = 'Called'
    dodWorldPayCall = GetDOD(objHere, 'E3WorldPayCall')
    objWorldPayCall = dodWorldPayCall.NewObject()
    objWorldPayCall.SetDateCalled(dtmDateCalled)
    objWorldPayCall.Status = strStatus
    if objAdmin.admWorldPayResults.has_key(intCallId):
        ImportWorldPayResults(objWorldPayCall, objAdmin.admWorldPayResults[intCallId])

def ImportWorldPayCalls(objHere, objAdmin, intMaxCalls):
    """Import all WorldPayCalls"""
    intDone = 0
    for intCallId in objAdmin.admWorldPayCalls.keys():
        intDone = intDone + 1
        if intDone <= intMaxCalls:
            ImportOneWorldPayCall(objHere, objAdmin, intCallId)
    return '<p>WorldPay calls imported</p>'

def GetLatestInvoiceNumber(objHere):
    intLatest = 0
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objPayment in objMember.Historic.objectValues('E3Payment'):
                intLatest = max(objPayment.InvoiceNumber, intLatest)
    objData = GetDataFolder(objHere, 'E3Data')
    objData.LatestInvoiceNumber = intLatest

def BuildList(objHere, strListName):
    dodList = GetDOD(objHere, 'E3List')
    objList = dodList.NewObject(None, strListName)
    objList.ListName = strListName
    objList.CreateMailBoxerMembers()

def ImportStaticData(objHere):
    print "Creating data object definitions"
    CreateDataObjectDefinitions(objHere, 'E3')
    print "Reading help file"
    ReadHelp(objHere)
    print "Reindexing help objects"
    ReindexOne(objHere, 'E3Help')
    print "Building help pages"
    BuildRules(objHere)
    print "Done"
    BuildList(objHere, cnListNameECL)
    
def ExpirePast2Months(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == 'Full' and not objMember.OnHold:
                if objMember.GetNextExpiryDate() <= datetime.date.today():
                    dtmDelta = datetime.date.today() - objMember.GetNextExpiryDate()
                    if dtmDelta.days > 60:
                        objMember.SetMembershipType('None')

def TellOnePostingOnly(strEmailAddress, intNumberOfAddresses):
    strMessage = """(If you are no longer a member of the Euro Coach List, please ignore this message)

As you know, the Euro Coach List is currently moving to a new system

On the old system there was a single list of non-registered email addresses which were allowed to post messages. On the new system each member can have their own list of posting only email addresses

Unfortunately I have no way of telling which email address belongs to which member, other than laboriously going through all %(Count)s such addresses

If this (%(Address)s) is an email address which you might use to send a message from then please do the following:
1. Go to http://www.EuroCoachList.com/MyECL
2. Log in
3. Go down to "Email Addresses, Advanced"
4. Enter this address (%(Address)s) as a new address and set it to "Posting only"
5. Click on "Update email addresses"

You should have received your log in details in a separate email. If not, please contact me

Thanks

""" % {'Address': strEmailAddress,
        'Count': intNumberOfAddresses}
    strMessage += cnSignature
    strSubject = "Euro Coach List - your %s email address" % strEmailAddress
    SendEmail(strMessage, strSubject, strEmailAddress)    

def InformPostingOnlyAddresses(objHere):
    objECL = MailList.MailList('eurocoach-list', lock=0)
    lstAccept = objECL.accept_these_nonmembers
    lstUnknown = []
    for strEmailAddress in lstAccept:
        if not SearchOne(objHere, 'E3EmailAddress', 'EmailAddress', strEmailAddress.lower()):
            lstUnknown.append(strEmailAddress)
    for strEmailAddress in lstUnknown:
        TellOnePostingOnly(strEmailAddress, len(lstUnknown))
#    print "Started with: %s, now: %s" % (len(lstAccept), len(lstUnknown))

def ImportMembersData(objHere):
    """Main import routine"""
    print "Loading data from Mailman"
    objAdmin = MailList.MailList('admin', lock=0)
    objECL = MailList.MailList('eurocoach-list', lock=0)
    intLimitImport = 100000
    print "Importing members"
    ImportMembers(objHere, objAdmin, objECL, intLimitImport)
    print "Getting latest invoice number"
    GetLatestInvoiceNumber(objHere)
    print "Removing members who should have expired 2 months ago"
    ExpirePast2Months(objHere)
    print "Counting members"
    CountMembers(objHere)
    print "Done"

def E3Reindex(objHere):
    for strType in ('E3Member', 'E3EmailAddress', 'E3ListMembership', 'E3Help'):
        ReindexOne(objHere, strType)
