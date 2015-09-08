import OFS.Folder
import Globals
from Functions import *

class MCIPerson(OFS.Folder.Folder):
    "MCIPerson class"
    meta_type = 'MCIPerson'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('PersonName', '', 'string')
        self.manage_addProperty('WebPage', '', 'string')
        self.manage_addProperty('WebSite', '', 'string')
        self.manage_addProperty('ShortBio', '', 'text')
        self.manage_addProperty('MCIPartner', False, 'boolean')
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('PersonId', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def NamePlusLink(self):
        strTarget = ""
        if self.WebPage:
            strLink = self.WebPage
        else:
            if self.WebSite:
                strLink = "http://" + self.WebSite
                strTarget = """ target="_blank" """
            else:
                strLink = "mailto:" + self.EmailAddress
    
        strResult = '<a href="%s"%s>%s</a>' % (strLink, strTarget, self.PersonName)
        return strResult
    
def addMCIPersonForm(self):
    "New MCIPerson form"
    return GenericAddForm('MCIPerson')

def addMCIPerson(self, id):
    "New MCIPerson action"
    objNewMCIPerson = MCIPerson(id)
    self._setObject(id, objNewMCIPerson)
    
    return "New MCIPerson created."
