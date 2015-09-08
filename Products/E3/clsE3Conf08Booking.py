import OFS.Folder
import Globals
import DateTime
from Functions import *

from libConstants import cnEmptyZopeDate

class E3Conf08Booking(OFS.Folder.Folder):
    "E3Conf08Booking class"
    meta_type = 'E3Conf08Booking'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myDateCreated', cnEmptyZopeDate, 'date')
        self.manage_addProperty('Name', '', 'ustring')
        self.manage_addProperty('Country', '', 'string')
        self.manage_addProperty('Telephone', '', 'ustring')
        self.manage_addProperty('EmailAddress', '', 'ustring')
        self.manage_addProperty('RegistrationType', '', 'string')
        self.manage_addProperty('EarlyBird', False, 'boolean')
        self.manage_addProperty('PaymentMethod', '', 'string')
        self.manage_addProperty('PayNowAmount', 0, 'int')
        self.manage_addProperty('PayLaterAmount', 0, 'int')
        self.manage_addProperty('Status', '', 'string')
        self.manage_addProperty('CartId', '', 'string')
        self.manage_addProperty('Preferences', '', 'ulines')
        self.manage_addProperty('Comments', '', 'utext')
        self.manage_addProperty('myDepositPaid', cnEmptyZopeDate, 'date')
        self.manage_addProperty('myRemainderPaid', cnEmptyZopeDate, 'date')
        self.manage_addProperty('InvoiceNumber', '', 'string')        
        self.manage_addProperty("BookedForCC", False, "boolean")
        self.manage_addProperty("BookedForSatEve", False, "boolean")
        self.manage_addProperty("BookedForSunAm", False, "boolean")
        self.manage_addProperty("InProgressForCC", False, "boolean")
        self.manage_addProperty("InProgressForSatEve", False, "boolean")
        self.manage_addProperty("InProgressForSunAm", False, "boolean")
        self.manage_addProperty("History", [], "lines")
        self.manage_addProperty("PaidAmount", 0, "int")
        self.manage_addProperty("RemainingAmount", 0, "int")
        
    def GetDateCreated(self):
        return FromZopeDateTime(self.myDateCreated)

    def SetDateCreated(self, dtmDate):
        self.myDateCreated = ToZopeDateTime(self, dtmDate)

    def GetDepositPaid(self):
        return FromZopeDateTime(self.myDepositPaid)

    def SetDepositPaid(self, dtmDate):
        self.myDepositPaid = ToZopeDateTime(self, dtmDate)

    def GetRemainderPaid(self):
        return FromZopeDateTime(self.myRemainderPaid)

    def SetRemainderPaid(self, dtmDate):
        self.myRemainderPaid = ToZopeDateTime(self, dtmDate)

    def HasDepositPaid(self):
        if self.myDepositPaid > DateTime("1 Jan 1950"):
            return True
        return False
    
    def HasRemainderPaid(self):
        if self.myRemainderPaid > DateTime("1 Jan 1950"):
            return True
        return False

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3Conf08BookingForm(self):
    "New E3Conf08Booking form"
    return GenericAddForm('E3Conf08Booking')

def addE3Conf08Booking(self, id):
    "New E3Conf08Booking action"
    objNewE3Conf08Booking = E3Conf08Booking(id)
    self._setObject(id, objNewE3Conf08Booking)
    
    return "New E3Conf08Booking created."
