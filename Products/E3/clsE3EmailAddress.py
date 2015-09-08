import OFS.Folder
import Globals
from Functions import *
from libConstants import cnEmptyZopeDate
from libConstants import cnFirstDate
from libConstants import cnSignature
from libConstants import cnListNameECL
from libString import GetMessage
import datetime
from libEmail import SendEmail
from libEmail import SendAnyEmail
import string
import random
from libDatabase import SearchOne
from libDatabase import Catalogue
from libConstants import cnECLRoot
from E3Messages import CountPastMessages
from libDatabase import GetDataFolder

class E3EmailAddress(OFS.Folder.Folder):
    "E3EmailAddress class"
    meta_type = 'E3EmailAddress'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('Confirmed', False, 'boolean')
        self.manage_addProperty('ConfirmationString', '', 'string')
        self.manage_addProperty('myConfirmationStringSent', cnEmptyZopeDate, 'date')
        self.manage_addProperty('myConfirmationReminderSent', cnEmptyZopeDate, 'date')
        self.manage_addProperty('BounceDay1', 0, 'int')
        self.manage_addProperty('BounceDay2', 0, 'int')
        self.manage_addProperty('BounceDay3', 0, 'int')
        self.manage_addProperty('Bouncing', False, 'boolean')
        self.manage_addProperty('ChangeToThisOne', False, 'boolean')

    def RecordBounce(self):
        if not self.Bouncing:
            self.BounceDay1 += 1

    def MoveBounces(self):
        self.BounceDay3 = self.BounceDay2
        self.BounceDay2 = self.BounceDay1
        self.BounceDay1 = 0

    def CheckExcessiveBouncing(self):
        if self.Bouncing:
            return
        if self.BounceDay1 > 2 and self.BounceDay2 > 2 and self.BounceDay3 > 2:
            self.SetBouncing(True)
            strMessage = """There seems to be a problem with your email address (%s). Three or more list messages a day sent to this address have bounced back over the last three days

This email address has now been disabled. No more emails will be sent to this address. You will still be able to send messages from this address

To re-enable the email address please go to the MyECL page at %s/MyECL

""" % (self.EmailAddress, cnECLRoot)
            strMessage += cnSignature
            strSubject = "Euro Coach List email address disabled due to excessive bouncing"
            SendEmail(self, strMessage, strSubject, self.EmailAddress)
        self.MoveBounces()

    def SetBouncing(self, blnBouncing):
        if blnBouncing <> self.Bouncing:
            self.Bouncing = blnBouncing
            self.BounceDay1 = 0
            self.BounceDay2 = 0
            self.BounceDay3 = 0

#    def GetListMembership(self, strListName = cnListNameECL):
#        for objListMembership in self.objectValues('E3ListMembership'):
#            if objListMembership.ListName == strListName:
#            return objListMembership
#        return None

    def IsLive(self, blnMemberIsLive = None):
        if self.Bouncing:
            return False
        if not self.Confirmed:
            return False
        if blnMemberIsLive == None:
            objMember = self.unrestrictedTraverse('..')
            if objMember.MembershipType <> 'Full':
                return False
        else:
            return blnMemberIsLive
        return True

    def BeyondConfirmation(self):
        if self.Confirmed:
            return False
        dtmReminder = self.GetConfirmationReminderSent()
        print "dtmReminder: %s" % dtmReminder
        if (not dtmReminder) or dtmReminder < cnFirstDate:
            return False
        dtmNow = datetime.date.today()
        deltaSinceReminder = dtmNow - dtmReminder
        if deltaSinceReminder.days < 14:
            return False
        return True

    def TimeToRemind(self):
        if self.Confirmed:
            return False
        dtmReminder = self.GetConfirmationReminderSent()
        if (dtmReminder) and dtmReminder > cnFirstDate:
            return False
        dtmNow = datetime.date.today()
        deltaSinceFirst = dtmNow - self.GetConfirmationStringSent()
        if deltaSinceFirst.days > 7 and deltaSinceFirst.days < 10:
            return True
        return False

    def SendConfirmationReminder(self):
#        print "Confirmation reminder sent"
        self.SetConfirmationReminderSent(datetime.date.today())
        strConfirmationString = self.ConfirmationString
        strConfirmationMessage = """About a week ago someone, presumably you, subscribed %s to the Euro Coach List. A confirmation request was sent to you, which you don't seem to have responded to

This means that you won't be receiving list messages to %s, nor will you be able to send messages to the Euro Coach List from that address

To confirm your email address, do one of the following:
* Reply to this email. Make sure the code still shows in the email subject
* Go to the following website address:
http://www.EuroCoachList.com/Membership/Confirm?Id=%s

""" % (self.EmailAddress, self.EmailAddress, strConfirmationString)
        strConfirmationMessage += cnSignature
        strSubject = "Euro Coach List confirmation, #%s#" % strConfirmationString
        strListAddress = GetDataFolder(self, 'MailBoxer').mailto
        SendEmail(self, strConfirmationMessage, strSubject, self.EmailAddress, strListAddress)

    def CheckConfirmations(self):
        if self.Confirmed:
            return
        dtmNow = datetime.date.today()
        dtmReminder = self.GetConfirmationReminderSent()
        if not dtmReminder or dtmReminder < cnFirstDate:
            deltaSinceRegistration = dtmNow - self.GetConfirmationStringSent()
            if deltaSinceRegistration.days > 14:
                self.SendConfirmationReminder()

    def GetConfirmationReminderSent(self):
        return FromZopeDateTime(self.myConfirmationReminderSent)

    def SetConfirmationReminderSent(self, dtmDate):
        self.myConfirmationReminderSent = ToZopeDateTime(self, dtmDate)

    def GetConfirmationStringSent(self):
        return FromZopeDateTime(self.myConfirmationStringSent)

    def SetConfirmationStringSent(self, dtmDate):
        self.myConfirmationStringSent = ToZopeDateTime(self, dtmDate)

    def SendConfirmationMessage(self):
        strConfirmationMessage = GetMessage(self, "ConfirmationMessage") % {"EmailAddress": self.EmailAddress}
        strConfirmationMessage += cnSignature
        strSubject = "Euro Coach List email address confirmed"
        SendAnyEmail(self, strConfirmationMessage, strSubject, self.EmailAddress)

    def SendChangedMessage(self, strOldAddress):
        strConfirmationMessage = """Your email address (%s) has now been confirmed

Your list messages will now go to this address, instead of the old address (%s)

You can use both your old and your new address to send messages to the Euro Coach List

""" % (self.EmailAddress, strOldAddress)
        strConfirmationMessage += cnSignature
        strSubject = "Euro Coach List email address confirmed"
        SendEmail(self, strConfirmationMessage, strSubject, self.EmailAddress)

    def Confirm(self):
        self.Confirmed = True
        self.ConfirmationString = ""
        objMember = self.unrestrictedTraverse("..")
        objMember.Confirm()
        Catalogue(self)
        if self.ChangeToThisOne:
            objMember = self.unrestrictedTraverse('..')
            strOldAddress = objMember.EmailDeliveryAddress
            objMember.EmailDeliveryAddress = self.EmailAddress
            self.SendChangedMessage(strOldAddress)
        else:
            self.SendConfirmationMessage()

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def RandomConfirmationString(self):
        strResult = RandomString()
        while SearchOne(self, 'E3EmailAddress', 'ConfirmationString', strResult):
            strResult = RandomString()
        return strResult

    def RequestConfirmation(self):
        strConfirmationString = self.RandomConfirmationString()
        self.ConfirmationString = strConfirmationString
        self.SetConfirmationStringSent(datetime.date.today())
        Catalogue(self)
        strConfirmationMessage = """Someone, presumably you, has just subscribed %s to the Euro Coach List.

To make sure that an email address can only be subscribed to the Euro Coach List by its owner, you need to confirm the subscription request

To confirm your email address, do one of the following:
* Reply to this email. Make sure the code still shows in the email subject
* Go to the following website address:
http://www.EuroCoachList.com/Membership/Confirm?Id=%s

""" % (self.EmailAddress, strConfirmationString)
        strConfirmationMessage += cnSignature
        strSubject = "Euro Coach List confirmation, #%s#" % strConfirmationString
        strListAddress = GetDataFolder(self, 'MailBoxer').mailto
        SendEmail(self, strConfirmationMessage, strSubject, self.EmailAddress, strListAddress)

def RandomString():
    strResult = ""
    strRange = string.ascii_letters + string.digits
    for intI in range(0, 10):
        strResult += random.choice(strRange)
    return strResult

def addE3EmailAddressForm(self):
    "New E3EmailAddress form"
    return GenericAddForm('E3EmailAddress')

def addE3EmailAddress(self, id):
    "New E3EmailAddress action"
    objNewE3EmailAddress = E3EmailAddress(id)
    self._setObject(id, objNewE3EmailAddress)

    return "New E3EmailAddress created."
