import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
from libConstants import cnFirstZopeDate

class E3SequenceInProgress(OFS.Folder.Folder):

    "E3SequenceInProgress class"
    meta_type = 'E3SequenceInProgress'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('SequenceName', '', 'string')
        self.manage_addProperty('myStartDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('MemberId', '', 'string')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('Active', True, 'boolean')
        self.manage_addFolder('PlannedMessages')

    def GetStartDate(self):
        return FromZopeDateTime(self.myStartDate)

    def SetStartDate(self, dtmDate):
        self.myStartDate = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3SequenceInProgressForm(self):
    "New E3SequenceInProgress form"
    return GenericAddForm('E3SequenceInProgress')

def addE3SequenceInProgress(self, id):
    "New E3SequenceInProgress action"
    objNewE3SequenceInProgress = E3SequenceInProgress(id)
    self._setObject(id, objNewE3SequenceInProgress)
    
    return "New E3SequenceInProgress created."
