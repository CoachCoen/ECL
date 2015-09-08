import OFS.Folder
import Globals
from Functions import *

class MCIBookCategory(OFS.Folder.Folder):
    "MCIBookCategory class"
    meta_type = 'MCIBookCategory'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('SubCategoryOf', '', 'string')
        self.manage_addProperty('CategoryName', '', 'string')
        self.manage_addProperty('DisplayOrder', 0, 'int')
        self.manage_addProperty('SourceId', 0, 'long')
        self.manage_addProperty('SubCategoryOfCategoryId', 0, 'long')
        self.manage_addProperty('BooksInCategory', 0, 'int')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIBookCategoryForm(self):
    "New MCIBookCategory form"
    return GenericAddForm('MCIBookCategory')

def addMCIBookCategory(self, id):
    "New MCIBookCategory action"
    objNewMCIBookCategory = MCIBookCategory(id)
    self._setObject(id, objNewMCIBookCategory)
    
    return "New MCIBookCategory created."
