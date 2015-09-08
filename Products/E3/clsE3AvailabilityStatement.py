import OFS.Folder
import Globals
from Functions import *

class E3AvailabilityStatement(OFS.Folder.Folder):

    "E3AvailabilityStatement class"
    meta_type = 'E3AvailabilityStatement'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Type', '', 'string')
        self.manage_addProperty('Info', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3AvailabilityStatementForm(self):
    "New E3AvailabilityStatement form"
    return GenericAddForm('E3AvailabilityStatement')

def addE3AvailabilityStatement(self, id):
    "New E3AvailabilityStatement action"
    objNewE3AvailabilityStatement = E3AvailabilityStatement(id)
    self._setObject(id, objNewE3AvailabilityStatement)
    
    return "New E3AvailabilityStatement created."
