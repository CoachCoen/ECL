import OFS.Folder
import Globals
from Functions import *

class E3SearchBlock(OFS.Folder.Folder):
    "E3SearchBlock class"
    meta_type = 'E3SearchBlock'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Criteria', [], 'lines')
        self.manage_addProperty('FromPrevious', '', 'string')
        self.manage_addProperty('Sequence', 0, 'int')
        self.manage_addProperty('MessagesFound', 0, 'int')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3SearchBlockForm(self):
    "New E3SearchBlock form"
    return GenericAddForm('E3SearchBlock')

def addE3SearchBlock(self, id):
    "New E3SearchBlock action"
    objNewE3SearchBlock = E3SearchBlock(id)
    self._setObject(id, objNewE3SearchBlock)
    
    return "New E3SearchBlock created."
