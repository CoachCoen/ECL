import OFS.Folder
import Globals
from Functions import *

class E3EventPreference(OFS.Folder.Folder):

    "E3EventPreference class"
    meta_type = 'E3EventPreference'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('EventId', '', 'string')
        self.manage_addProperty('WillCome', '', 'string')
        self.manage_addProperty('Locations', [], 'lines')
        self.manage_addProperty('OnDayOffers', '', 'text')
        self.manage_addProperty('PreparationOffers', '', 'text')
        self.manage_addProperty('OrganisationTeamRoles', '', 'text')
        self.manage_addProperty('Wishes', '', 'text')
        self.manage_addProperty('Comments', '', 'text')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3EventPreferenceForm(self):
    "New E3EventPreference form"
    return GenericAddForm('E3EventPreference')

def addE3EventPreference(self, id):
    "New E3EventPreference action"
    objNewE3EventPreference = E3EventPreference(id)
    self._setObject(id, objNewE3EventPreference)
    
    return "New E3EventPreference created."
