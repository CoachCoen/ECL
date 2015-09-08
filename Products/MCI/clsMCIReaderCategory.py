import OFS.Folder
import Globals
from Functions import *

class MCIReaderCategory(OFS.Folder.Folder):
    "MCIReaderCategory class"
    meta_type = 'MCIReaderCategory'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('CategoryName', '', 'string')
        self.manage_addProperty('DisplayOrder', 0, 'int')
        self.manage_addProperty('SourceId', 0, 'long')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIReaderCategoryForm(self):
    "New MCIReaderCategory form"
    return GenericAddForm('MCIReaderCategory')

def addMCIReaderCategory(self, id):
    "New MCIReaderCategory action"
    objNewMCIReaderCategory = MCIReaderCategory(id)
    self._setObject(id, objNewMCIReaderCategory)
    
    return "New MCIReaderCategory created."
