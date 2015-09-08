import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
from libConstants import cnFirstZopeDate

class E3PlannedMessage(OFS.Folder.Folder):

    "E3PlannedMessage class"
    meta_type = 'E3PlannedMessage'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myPlannedDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('mySentDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('SourceMessagePath', '', 'string')

    def GetPlannedDate(self):
        return FromZopeDateTime(self.myPlannedDate)

    def SetPlannedDate(self, dtmDate):
        self.myPlannedDate = ToZopeDateTime(self, dtmDate)

    def GetSentDate(self):
        return FromZopeDateTime(self.mySentDate)

    def SetSentDate(self, dtmDate):
        self.mySentDate = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3PlannedMessageForm(self):
    "New E3PlannedMessage form"
    return GenericAddForm('E3PlannedMessage')

def addE3PlannedMessage(self, id):
    "New E3PlannedMessage action"
    objNewE3PlannedMessage = E3PlannedMessage(id)
    self._setObject(id, objNewE3PlannedMessage)
    
    return "New E3PlannedMessage created."
