import OFS.Folder
import Globals
from Functions import *

class E3Help(OFS.Folder.Folder):
    "E3Help class"
    meta_type = 'E3Help'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('HelpId', '', 'string')
        self.manage_addProperty('Lines', [], 'lines')
        self.manage_addProperty('Type', '', 'string')
        self.manage_addProperty('Categories', '', 'string')
        self.manage_addProperty('CanExpand', False, 'boolean')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortHelpLine(self):
        return """<li><a href="/Help/ShowOne?Id=%s" onclick="return PopupHelp('%s')">%s</a></li>""" % (self.HelpId, self.HelpId, self.title)

def addE3HelpForm(self):
    "New E3Help form"
    return GenericAddForm('E3Help')

def addE3Help(self, id):
    "New E3Help action"
    objNewE3Help = E3Help(id)
    self._setObject(id, objNewE3Help)
    
    return "New E3Help created."
