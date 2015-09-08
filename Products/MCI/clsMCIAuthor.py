import OFS.Folder
import Globals
from Functions import *

class MCIAuthor(OFS.Folder.Folder):
    "MCIAuthor class"
    meta_type = 'MCIAuthor'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Name', '', 'string')
        self.manage_addProperty('SourceId', 0, 'long')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIAuthorForm(self):
    "New MCIAuthor form"
    return GenericAddForm('MCIAuthor')

def addMCIAuthor(self, id):
    "New MCIAuthor action"
    objNewMCIAuthor = MCIAuthor(id)
    self._setObject(id, objNewMCIAuthor)
    
    return "New MCIAuthor created."
