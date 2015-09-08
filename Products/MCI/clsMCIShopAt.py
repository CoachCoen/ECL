import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyDate

class MCIShopAt(OFS.Folder.Folder):
    "MCIShopAt class"
    meta_type = 'MCIShopAt'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('BookId', '', 'string')
        self.manage_addProperty('Date', cnEmptyDate, 'date')
        self.manage_addProperty('ShopId', '', 'string')
        self.manage_addProperty('SourceId', 0, 'long')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIShopAtForm(self):
    "New MCIShopAt form"
    return GenericAddForm('MCIShopAt')

def addMCIShopAt(self, id):
    "New MCIShopAt action"
    objNewMCIShopAt = MCIShopAt(id)
    self._setObject(id, objNewMCIShopAt)
    
    return "New MCIShopAt created."
