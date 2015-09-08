import OFS.Folder
import Globals
from Functions import *
import random
import string
from libDatabase import SearchOne
from libDatabase import Catalogue

class E3UnclaimedEmailAddress(OFS.Folder.Folder):
    "E3UnclaimedEmailAddress class"
    meta_type = 'E3UnclaimedEmailAddress'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('EmailAddress', '', 'string')
        self.manage_addProperty('Key', '', 'string')

    def SetRandomKey(self):
        self.Key = self.RandomKey()
        Catalogue(self)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def RandomKey(self):
        strResult = RandomString()
        while SearchOne(self, 'E3UnclaimedEmailAddress', 'Key', strResult):
            strResult = RandomString()
        return strResult

def RandomString():
    strResult = ""
    strRange = string.ascii_letters + string.digits
    for intI in range(0, 10):
        strResult += random.choice(strRange)
    return strResult

def addE3UnclaimedEmailAddressForm(self):
    "New E3UnclaimedEmailAddress form"
    return GenericAddForm('E3UnclaimedEmailAddress')

def addE3UnclaimedEmailAddress(self, id):
    "New E3UnclaimedEmailAddress action"
    objNewE3UnclaimedEmailAddress = E3UnclaimedEmailAddress(id)
    self._setObject(id, objNewE3UnclaimedEmailAddress)
    
    return "New E3UnclaimedEmailAddress created."
