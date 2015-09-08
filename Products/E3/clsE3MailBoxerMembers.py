import OFS.Folder
import Globals
from Functions import *

class E3MailBoxerMembers(OFS.Folder.Folder):
    "E3MailBoxerMembers class"
    meta_type = 'E3MailBoxerMembers'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('DeliveryMode', '', 'string')
        self.manage_addProperty('Members', [], 'lines')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3MailBoxerMembersForm(self):
    "New E3MailBoxerMembers form"
    return GenericAddForm('E3MailBoxerMembers')

def addE3MailBoxerMembers(self, id):
    "New E3MailBoxerMembers action"
    objNewE3MailBoxerMembers = E3MailBoxerMembers(id)
    self._setObject(id, objNewE3MailBoxerMembers)
    
    return "New E3MailBoxerMembers created."
