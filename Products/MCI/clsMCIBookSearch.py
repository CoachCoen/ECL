import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyDate

class MCIBookSearch(OFS.Folder.Folder):
    "MCIBookSearch class"
    meta_type = 'MCIBookSearch'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('BookId', '', 'string')
        self.manage_addProperty('Date', cnEmptyDate, 'date')
        self.manage_addProperty('SearchLine', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIBookSearchForm(self):
    "New MCIBookSearch form"
    return GenericAddForm('MCIBookSearch')

def addMCIBookSearch(self, id):
    "New MCIBookSearch action"
    objNewMCIBookSearch = MCIBookSearch(id)
    self._setObject(id, objNewMCIBookSearch)
    
    return "New MCIBookSearch created."
