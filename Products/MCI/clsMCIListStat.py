import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyDate

class MCIListStat(OFS.Folder.Folder):
    "MCIListStat class"
    meta_type = 'MCIListStat'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('List', '', 'string')
        self.manage_addProperty('Count', 0, 'int')
        self.manage_addProperty('Date', cnEmptyDate, 'date')
        self.manage_addProperty('SourceId', 0, 'long')
        self.manage_addProperty('ListId', 0, 'long')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIListStatForm(self):
    "New MCIListStat form"
    return GenericAddForm('MCIListStat')

def addMCIListStat(self, id):
    "New MCIListStat action"
    objNewMCIListStat = MCIListStat(id)
    self._setObject(id, objNewMCIListStat)
    
    return "New MCIListStat created."
