import OFS.Folder
import Globals
from Functions import *

class E3Role(OFS.Folder.Folder):
    "E3Role class"
    meta_type = 'E3Role'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('MemberId', '', 'string')
        self.manage_addProperty('ItemId', '', 'string')
        self.manage_addProperty('RoleType', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortRoleLine(self):
        return """<li><a href="/Role/ShowOne?Id=%s" onclick="return PopupRole('%s')">%s</a></li>""" % (self.RoleId, self.RoleId, self.title)

def addE3RoleForm(self):
    "New E3Role form"
    return GenericAddForm('E3Role')

def addE3Role(self, id):
    "New E3Role action"
    objNewE3Role = E3Role(id)
    self._setObject(id, objNewE3Role)
    
    return "New E3Role created."
