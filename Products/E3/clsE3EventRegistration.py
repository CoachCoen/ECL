import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
import DateTime

# EventRegistrationType can be one of the following:
#   Trial - start of trial period
#   LifetimeMember - member becomes a lifetime member
#   FreePeriod - start of a free period
#   Expiry - membership expired
#   WarningSent - Expiry due warning sent
#   BonusSent - Bonus message sent
#   ExpiryMessageSent - User just expired, message to user sent

class E3EventRegistration(OFS.Folder.Folder):

    "E3EventRegistration class"
    meta_type = 'E3EventRegistration'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myDate', DateTime.DateTime(), 'date')
        self.manage_addProperty('Event', '', 'string')
        self.manage_addProperty('RegistrationType', '', 'string')
        self.manage_addProperty('Name', '', 'string')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('PaymentId', '', 'string')
        self.manage_addProperty('InvoiceNumber', '', 'string')

    def GetDate(self):
        return FromZopeDateTime(self.myDate)

    def SetDate(self, dtmDate):
        self.myDate = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3EventRegistrationForm(self):
    "New E3EventRegistration form"
    return GenericAddForm('E3EventRegistration')

def addE3EventRegistration(self, id):
    "New E3EventRegistration action"
    objNewE3EventRegistration = E3EventRegistration(id)
    self._setObject(id, objNewE3EventRegistration)
    
    return "New E3EventRegistration created."
