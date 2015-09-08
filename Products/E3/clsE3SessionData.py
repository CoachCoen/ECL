import OFS.Folder
import Globals
from Functions import *

class E3SessionData(OFS.Folder.Folder):
    "E3SessionData class"
    meta_type = 'E3SessionData'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Username', '', 'string')
        self.manage_addProperty('ErrorScreen', '', 'string')
        self.manage_addProperty('PlainMessage', '', 'string')
        self.manage_addProperty('ErrorMessage', '', 'string')
        self.manage_addProperty('PageTitle', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3SessionDataForm(self):
    "New E3SessionData form"
    return GenericAddForm('E3SessionData')

def addE3SessionData(self, id):
    "New E3SessionData action"
    objNewE3SessionData = E3SessionData(id)
    self._setObject(id, objNewE3SessionData)
    
    return "New E3SessionData created."
