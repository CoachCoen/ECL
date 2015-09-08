import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyDate

class MCIEnrolmentLog(OFS.Folder.Folder):
    "MCIEnrolmentLog class"
    meta_type = 'MCIEnrolmentLog'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('ParticipantName', '', 'string')
        self.manage_addProperty('DateEntered', cnEmptyDate, 'date')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('ClassIdList', '', 'string')
        self.manage_addProperty('SourceId', 0, 'long')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIEnrolmentLogForm(self):
    "New MCIEnrolmentLog form"
    return GenericAddForm('MCIEnrolmentLog')

def addMCIEnrolmentLog(self, id):
    "New MCIEnrolmentLog action"
    objNewMCIEnrolmentLog = MCIEnrolmentLog(id)
    self._setObject(id, objNewMCIEnrolmentLog)
    
    return "New MCIEnrolmentLog created."
