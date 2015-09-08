import OFS.Folder
import Globals
from Functions import *
from E3MailingList import GetList
from E3Digest import SendOneFinalDigest
from libDatabase import GetDataFolder
from libDatabase import SearchOne

class E3ListMembership(OFS.Folder.Folder):
    "E3ListMembership class"
    meta_type = 'E3ListMembership'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myDeliveryMode', '', 'string')
        self.manage_addProperty('EmailAddress', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def FinalDigest(self, strDigestType):
#        print "Final digest"
        objListMembership = self.unrestrictedTraverse('..').ListMemberships.ECL
        strEmailAddress = objListMembership.EmailAddress
        objEmailAddress = SearchOne(self, "E3EmailAddress", "EmailAddress", strEmailAddress)
        if not objEmailAddress.IsLive():
            return
        SendOneFinalDigest(self, strDigestType, objEmailAddress.EmailAddress)

    def SetDeliveryMode(self, strDeliveryMode):
        if self.myDeliveryMode <> strDeliveryMode:
            if strDeliveryMode == 'Direct' and self.myDeliveryMode in ['MIMEDigest', 'TextDigest', 'StructuredDigest', 'TopicsList']:
                self.FinalDigest(self.myDeliveryMode)
            self.myDeliveryMode = strDeliveryMode

    def GetDeliveryMode(self):
        return self.myDeliveryMode

def addE3ListMembershipForm(self):
    "New E3ListMembership form"
    return GenericAddForm('E3ListMembership')

def addE3ListMembership(self, id):
    "New E3ListMembership action"
    objNewE3ListMembership = E3ListMembership(id)
    self._setObject(id, objNewE3ListMembership)
    
    return "New E3ListMembership created."
