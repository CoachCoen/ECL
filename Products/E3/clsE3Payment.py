import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
from libConstants import cnReceipt
from libConstants import cnShortDateFormat
from libConstants import cnSignature
from libEmail import SendEmail
import datetime

class E3Payment(OFS.Folder.Folder):
    "E3Payment class"
    meta_type = 'E3Payment'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('PaymentType', '', 'string')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('Amount', 0, 'float')
        self.manage_addProperty('Currency', '', 'string')
        self.manage_addProperty('ChequeNumber', '', 'string')
        self.manage_addProperty('myPaidInDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('Comments', '', 'string')
        self.manage_addProperty('Name', '', 'string')
        self.manage_addProperty('Months', 0, 'int')
        self.manage_addProperty('BonusDays', 0, 'int')
        self.manage_addProperty('RefreshExpiry', True, 'boolean')
        self.manage_addProperty('RefreshExpiryOverride', False, 'boolean')
        self.manage_addProperty('InvoiceNumber', 0, 'int')

    def GetDate(self):
        return FromZopeDateTime(self.myDate)

    def SetDate(self, dtmDate):
        self.myDate = ToZopeDateTime(self, dtmDate)

    def GetPaidInDate(self):
        return FromZopeDateTime(self.myPaidInDate)

    def SetPaidInDate(self, dtmDate):
        self.myPaidInDate = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def SendReceipt(self):
        objMember = self.unrestrictedTraverse('../..')
        dtmEndOfMembershipDate = objMember.GetNextExpiryDate() - datetime.timedelta(days=1)
        strEmailAddress = self.EmailAddress
        if not strEmailAddress:
            objMember = self.unrestrictedTraverse('../..')
            strEmaiLAddress = objMember.PreferredEmailAddress()
        strReceipt = cnReceipt % {'InvoiceNumber': self.InvoiceNumber,
            'InvoiceDate': self.GetDate().strftime(cnShortDateFormat), 
            'EndOfMembershipDate': dtmEndOfMembershipDate.strftime(cnShortDateFormat),
            'Amount': "%s %.2f" % (self.Currency, self.Amount),
            'Name': objMember.Name,
            'EmailAddress': self.EmailAddress}
        strReceipt += cnSignature
        SendEmail(self, strReceipt, "Thanks for your payment", strEmailAddress)

def addE3PaymentForm(self):
    "New E3Payment form"
    return GenericAddForm('E3Payment')

def addE3Payment(self, id):
    "New E3Payment action"
    objNewE3Payment = E3Payment(id)
    self._setObject(id, objNewE3Payment)
    
    return "New E3Payment created."
