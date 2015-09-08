import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
from libConstants import cnFirstZopeDate

# EventType can be one of the following:
#   Trial - start of trial period
#   LifetimeMember - member becomes a lifetime member
#   FreePeriod - start of a free period
#   Expiry - membership expired
#   WarningSent - Expiry due warning sent
#   BonusSent - Bonus message sent
#   ExpiryMessageSent - User just expired, message to user sent

class E3Event(OFS.Folder.Folder):

    "E3Event class"
    meta_type = 'E3Event'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('EventType', '', 'string')
        self.manage_addProperty('myDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('Comments', '', 'string')
        self.manage_addProperty('Days', 0, 'int')

    def GetDate(self):
        return FromZopeDateTime(self.myDate)

    def SetDate(self, dtmDate):
        self.myDate = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3EventForm(self):
    "New E3Event form"
    return GenericAddForm('E3Event')

def addE3Event(self, id):
    "New E3Event action"
    objNewE3Event = E3Event(id)
    self._setObject(id, objNewE3Event)
    
    return "New E3Event created."
