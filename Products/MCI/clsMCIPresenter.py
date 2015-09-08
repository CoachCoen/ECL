import OFS.Folder
import Globals
from Functions import *

class MCIPresenter(OFS.Folder.Folder):
    "MCIPresenter class"
    meta_type = 'MCIPresenter'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('PresenterName', '', 'string')
        self.manage_addProperty('PresenterTitle', '', 'string')
        self.manage_addProperty('Bio', '', 'text')
        self.manage_addProperty('Website', '', 'string')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('MCIPartner', False, 'boolean')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addMCIPresenterForm(self):
    "New MCIPresenter form"
    return GenericAddForm('MCIPresenter')

def addMCIPresenter(self, id):
    "New MCIPresenter action"
    objNewMCIPresenter = MCIPresenter(id)
    self._setObject(id, objNewMCIPresenter)
    
    return "New MCIPresenter created."
