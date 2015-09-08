import OFS.Folder
import Globals
from Functions import *
from libConstants import cnReceipt
import datetime

from libConstants import cnEmptyZopeDate

class E3Invoice(OFS.Folder.Folder):
    "E3Invoice class"
    meta_type = 'E3Invoice'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('InvoiceNumber', 0, 'int')
        self.manage_addProperty('myDateSent', cnEmptyZopeDate, 'date')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('Subject', '', 'string')
        self.manage_addProperty('Message', '', 'string')

    def GetDateSent(self):
        return FromZopeDateTime(self.myDateSent)

    def SetDateSent(self, dtmDate):
        self.myDateSent = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def Send(self):
        dtmNow = datetime.date.today()
        strReceipt = cnReceipt % (self.InvoiceNumber, dtmNow)
        
        print "Sending invoice - not yet implemented"

def addE3InvoiceForm(self):
    "New E3Invoice form"
    return GenericAddForm('E3Invoice')

def addE3Invoice(self, id):
    "New E3Invoice action"
    objNewE3Invoice = E3Invoice(id)
    self._setObject(id, objNewE3Invoice)
    
    return "New E3Invoice created."
