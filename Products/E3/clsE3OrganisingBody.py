import OFS.Folder
import Globals
from Functions import *

class E3OrganisingBody(OFS.Folder.Folder):
    "E3OrganisingBody class"
    meta_type = 'E3OrganisingBody'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('CreatedBy', '', 'string')
        self.manage_addProperty('OrganisationId', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortOrganisingBodyLine(self):
        return """<li><a href="/OrganisingBody/ShowOne?Id=%s" onclick="return PopupOrganisingBody('%s')">%s</a></li>""" % (self.OrganisingBodyId, self.OrganisingBodyId, self.title)

def addE3OrganisingBodyForm(self):
    "New E3OrganisingBody form"
    return GenericAddForm('E3OrganisingBody')

def addE3OrganisingBody(self, id):
    "New E3OrganisingBody action"
    objNewE3OrganisingBody = E3OrganisingBody(id)
    self._setObject(id, objNewE3OrganisingBody)
    
    return "New E3OrganisingBody created."
