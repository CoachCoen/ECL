import OFS.Folder
import Globals
from Functions import *

class E3RoleType(OFS.Folder.Folder):
    "E3RoleType class"
    meta_type = 'E3RoleType'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Type', '', 'ustring')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortRoleTypeLine(self):
        return """<li><a href="/RoleType/ShowOne?Id=%s" onclick="return PopupRoleType('%s')">%s</a></li>""" % (self.RoleTypeId, self.RoleTypeId, self.title)

def addE3RoleTypeForm(self):
    "New E3RoleType form"
    return GenericAddForm('E3RoleType')

def addE3RoleType(self, id):
    "New E3RoleType action"
    objNewE3RoleType = E3RoleType(id)
    self._setObject(id, objNewE3RoleType)
    
    return "New E3RoleType created."
