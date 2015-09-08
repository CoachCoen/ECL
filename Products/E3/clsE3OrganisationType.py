import OFS.Folder
import Globals
from Functions import *

class E3OrganisationType(OFS.Folder.Folder):
    "E3OrganisationType class"
    meta_type = 'E3OrganisationType'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Type', '', 'ustring')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortOrganisationTypeLine(self):
        return """<li><a href="/OrganisationType/ShowOne?Id=%s" onclick="return PopupOrganisationType('%s')">%s</a></li>""" % (self.OrganisationTypeId, self.OrganisationTypeId, self.title)

def addE3OrganisationTypeForm(self):
    "New E3OrganisationType form"
    return GenericAddForm('E3OrganisationType')

def addE3OrganisationType(self, id):
    "New E3OrganisationType action"
    objNewE3OrganisationType = E3OrganisationType(id)
    self._setObject(id, objNewE3OrganisationType)
    
    return "New E3OrganisationType created."
