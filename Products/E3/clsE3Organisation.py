import OFS.Folder
import Globals
from Functions import *

class E3Organisation(OFS.Folder.Folder):
    "E3Organisation class"
    meta_type = 'E3Organisation'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('CreatedBy', '', 'string')
        self.manage_addProperty('Name', '', 'ustring')
        self.manage_addProperty('OrganisationType', '', 'string')
        self.manage_addProperty('Description', '', 'utext')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def ShortOrganisationLine(self):
        return """<li><a href="/Organisation/ShowOne?Id=%s" onclick="return PopupOrganisation('%s')">%s</a></li>""" % (self.OrganisationId, self.OrganisationId, self.title)

    def DetailsBlock(self, strTitle):
        if strTitle:
            strTitle = "<legend>%s</legend>" % strTitle

        strName = self.Name
        if self.OrganisationType:
            strName += " (%s)" % self.OrganisationType

        if self.Description:
            strDescription = "<p>%s</p>" % self.Description
        else:
            strDescription = ""

        strResult = """<fieldset>
%s
<p><a href="/Organisations?OrganisationId=%s">%s</a></p>
%s
</fieldset>""" % (strTitle, self.id, strName, strDescription)
        return strResult

def addE3OrganisationForm(self):
    "New E3Organisation form"
    return GenericAddForm('E3Organisation')

def addE3Organisation(self, id):
    "New E3Organisation action"
    objNewE3Organisation = E3Organisation(id)
    self._setObject(id, objNewE3Organisation)

    return "New E3Organisation created."
