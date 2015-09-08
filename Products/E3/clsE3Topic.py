import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
from libConstants import cnFirstZopeDate

# TopicType can be one of the following:
#   Trial - start of trial period
#   LifetimeMember - member becomes a lifetime member
#   FreePeriod - start of a free period
#   Expiry - membership expired
#   WarningSent - Expiry due warning sent
#   BonusSent - Bonus message sent
#   ExpiryMessageSent - User just expired, message to user sent

class E3Topic(OFS.Folder.Folder):

    "E3Topic class"
    meta_type = 'E3Topic'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Order', 0, 'int')
        self.manage_addProperty('ShortTitle', '', 'string')
        self.manage_addProperty('ThreadCount', 0, 'int')
        self.manage_addProperty('MessageCount', 0, 'int')

    def GetDate(self):
        return FromZopeDateTime(self.myDate)

    def SetDate(self, dtmDate):
        self.myDate = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3TopicForm(self):
    "New E3Topic form"
    return GenericAddForm('E3Topic')

def addE3Topic(self, id):
    "New E3Topic action"
    objNewE3Topic = E3Topic(id)
    self._setObject(id, objNewE3Topic)
    
    return "New E3Topic created."
