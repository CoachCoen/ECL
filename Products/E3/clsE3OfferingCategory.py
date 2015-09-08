import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyDate
from libConstants import cnEmptyZopeDate
import DateTime

class E3OfferingCategory(OFS.Folder.Folder):
    "E3OfferingCategory class"
    meta_type = 'E3OfferingCategory'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Category', '', 'string')
        self.manage_addProperty('CategoryCount', 0, 'int')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3OfferingCategoryForm(self):
    "New E3OfferingCategory form"
    return GenericAddForm('E3OfferingCategory')

def addE3OfferingCategory(self, id):
    "New E3OfferingCategory action"
    objNewE3OfferingCategory = E3OfferingCategory(id)
    self._setObject(id, objNewE3OfferingCategory)
    
    return "New E3OfferingCategory created."
