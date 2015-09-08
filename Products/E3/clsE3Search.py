import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate

class E3Search(OFS.Folder.Folder):
    "E3Search class"
    meta_type = 'E3Search'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myLastExecuted', cnEmptyZopeDate, 'date')

    def GetLastExecuted(self):
        return FromZopeDateTime(self.myLastExecuted)

    def SetLastExecuted(self, dtmDate):
        self.myLastExecuted = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3SearchForm(self):
    "New E3Search form"
    return GenericAddForm('E3Search')

def addE3Search(self, id):
    "New E3Search action"
    objNewE3Search = E3Search(id)
    self._setObject(id, objNewE3Search)
    
    return "New E3Search created."
