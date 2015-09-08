import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
from libConstants import cnFirstZopeDate

# MultiOptionType can be one of the following:
#   Trial - start of trial period
#   LifetimeMember - member becomes a lifetime member
#   FreePeriod - start of a free period
#   Expiry - membership expired
#   WarningSent - Expiry due warning sent
#   BonusSent - Bonus message sent
#   ExpiryMessageSent - User just expired, message to user sent

class E3MultiOption(OFS.Folder.Folder):

    "E3MultiOption class"
    meta_type = 'E3MultiOption'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('FieldName', '', 'string')
        self.manage_addProperty('Option', '', 'ustring')
        self.manage_addProperty('OfferingsCount', 0, 'int')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3MultiOptionForm(self):
    "New E3MultiOption form"
    return GenericAddForm('E3MultiOption')

def addE3MultiOption(self, id):
    "New E3MultiOption action"
    objNewE3MultiOption = E3MultiOption(id)
    self._setObject(id, objNewE3MultiOption)
    
    return "New E3MultiOption created."
