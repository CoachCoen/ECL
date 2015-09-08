import OFS.Folder
import Globals
from Functions import *

class E3EventSeries(OFS.Folder.Folder):
    "E3EventSeries class"
    meta_type = 'E3EventSeries'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('CreatedBy', '', 'string')
        self.manage_addProperty('OrganisationId', '', 'string')
        self.manage_addProperty('Title', '', 'ustring')
        self.manage_addProperty('Description', '', 'utext')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortEventSeriesLine(self):
        return """<li><a href="/EventSeries/ShowOne?Id=%s" onclick="return PopupEventSeries('%s')">%s</a></li>""" % (self.EventSeriesId, self.EventSeriesId, self.title)

def addE3EventSeriesForm(self):
    "New E3EventSeries form"
    return GenericAddForm('E3EventSeries')

def addE3EventSeries(self, id):
    "New E3EventSeries action"
    objNewE3EventSeries = E3EventSeries(id)
    self._setObject(id, objNewE3EventSeries)
    
    return "New E3EventSeries created."
