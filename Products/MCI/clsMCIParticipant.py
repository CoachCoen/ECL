import OFS.Folder
import Globals
from Functions import *

class MCIParticipant(OFS.Folder.Folder):
    "MCIParticipant class"
    meta_type = 'MCIParticipant'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('ParticipantName', '', 'string')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('NoMailings', False, 'boolean')
        self.manage_addProperty('SourceId', 0, 'long')
        self.manage_addProperty('Removed', False, 'boolean')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIParticipantForm(self):
    "New MCIParticipant form"
    return GenericAddForm('MCIParticipant')

def addMCIParticipant(self, id):
    "New MCIParticipant action"
    objNewMCIParticipant = MCIParticipant(id)
    self._setObject(id, objNewMCIParticipant)
    
    return "New MCIParticipant created."
