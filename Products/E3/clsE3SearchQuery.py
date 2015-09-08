import OFS.Folder
import Globals
from Functions import *

class E3SearchQuery(OFS.Folder.Folder):
    "E3SearchQuery class"
    meta_type = 'E3SearchQuery'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('SearchQueryId', '', 'string')
        self.manage_addProperty('TableName', '', 'string')
        self.manage_addProperty('CriteriaDescription', '', 'string')
        self.manage_addProperty('ObjectIds', [], 'lines')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortSearchQueryLine(self):
        return """<li><a href="/SearchQuery/ShowOne?Id=%s" onclick="return PopupSearchQuery('%s')">%s</a></li>""" % (self.SearchQueryId, self.SearchQueryId, self.title)

def addE3SearchQueryForm(self):
    "New E3SearchQuery form"
    return GenericAddForm('E3SearchQuery')

def addE3SearchQuery(self, id):
    "New E3SearchQuery action"
    objNewE3SearchQuery = E3SearchQuery(id)
    self._setObject(id, objNewE3SearchQuery)
    
    return "New E3SearchQuery created."
