import OFS.Folder
import Globals
from Functions import *

class MCILink(OFS.Folder.Folder):
    "MCILink class"
    meta_type = 'MCILink'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('TableName', '', 'string')
        self.manage_addProperty('FromId', 0, 'long')
        self.manage_addProperty('ToId', 0, 'long')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCILinkForm(self):
    "New MCILink form"
    return GenericAddForm('MCILink')

def addMCILink(self, id):
    "New MCILink action"
    objNewMCILink = MCILink(id)
    self._setObject(id, objNewMCILink)
    
    return "New MCILink created."
