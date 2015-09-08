# import OFS.SimpleItem
import OFS.Folder
import Globals
from Functions import *

#class WorldPayResult(OFS.SimpleItem.SimpleItem):
class E3WorldPayResult(OFS.Folder.Folder):
    "WorldPayResult class"
    meta_type = 'E3WorldPayResult'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('AttributeName', '', 'string')
        self.manage_addProperty('AttributeValue', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3WorldPayResultForm(self):
    "New WorldPayResult form"
    return GenericAddForm('E3WorldPayResult')

def addE3WorldPayResult(self, id):
    "New WorldPayResult action"
    objNewWorldPayResult = E3WorldPayResult(id)
    self._setObject(id, objNewWorldPayResult)
    
    return "New E3WorldPayResult created."
