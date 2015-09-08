import OFS.Folder
import Globals
from Functions import *

class MCIEnrolment(OFS.Folder.Folder):
    "MCIEnrolment class"
    meta_type = 'MCIEnrolment'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('ParticipantId', '', 'string')
        self.manage_addProperty('ClassId', '', 'string')
        self.manage_addProperty('WelcomeMessageSent', False, 'boolean')
        self.manage_addProperty('InstructionsSent', False, 'boolean')
        self.manage_addProperty('SourceId', 0, 'long')
        self.manage_addProperty('Removed', False, 'boolean')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIEnrolmentForm(self):
    "New MCIEnrolment form"
    return GenericAddForm('MCIEnrolment')

def addMCIEnrolment(self, id):
    "New MCIEnrolment action"
    objNewMCIEnrolment = MCIEnrolment(id)
    self._setObject(id, objNewMCIEnrolment)
    
    return "New MCIEnrolment created."
