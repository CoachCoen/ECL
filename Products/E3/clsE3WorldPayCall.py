import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate

class E3WorldPayCall(OFS.Folder.Folder):
    "E3WorldPayCall class"
    meta_type = 'E3WorldPayCall'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myDateCalled', cnEmptyZopeDate, 'date')
        self.manage_addProperty('Status', '', 'string')
        self.manage_addProperty('CartId', '', 'string')
        self.manage_addProperty('PaymentType', '', 'string')
        self.manage_addProperty('Amount', 0, 'int')
        self.manage_addProperty('RegistrationToUpgrade', '', 'string')

    def GetDateCalled(self):
        return FromZopeDateTime(self.myDateCalled)

    def SetDateCalled(self, dtmDate):
        self.myDateCalled = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3WorldPayCallForm(self):
    "New E3WorldPayCall form"
    return GenericAddForm('E3WorldPayCall')

def addE3WorldPayCall(self, id):
    "New E3WorldPayCall action"
    objNewE3WorldPayCall = E3WorldPayCall(id)
    self._setObject(id, objNewE3WorldPayCall)
    
    return "New E3WorldPayCall created."
