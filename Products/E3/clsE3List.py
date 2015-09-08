import OFS.Folder
import Globals
from Functions import *
from libConstants import cnDeliveryModes
from libConstants import cnEmptyZopeDate
from libConstants import cnDeliveryModes
from libDatabase import GetDOD
from libDatabase import GetDataFolder
import datetime

class E3List(OFS.Folder.Folder):
    "E3List class"
    meta_type = 'E3List'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('ListName', '', 'string')
        self.manage_addProperty('LastUpdate', DateTime(), 'date')

    def CreateMailBoxerMembers(self):
        dodMailBoxerMembers = GetDOD(self, 'E3MailBoxerMembers')
        for strDeliveryMode in cnDeliveryModes:
            objMailBoxerMembers = dodMailBoxerMembers.NewObject(self)
            objMailBoxerMembers.DeliveryMode = strDeliveryMode

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def GetMailingLists(self):
        """
        Can send if:
        * Is a full member
        * Email address confirmed
    
        Will receive if:
        * Is a full member
        * Email address confirmed
    
        * Not on bouncing
        * Member not on holiday mode (Member.NoMail)
        * On Direct, TextDigest, MIMEDigest
        """
        dictResult = {}
        for strDeliveryMode in cnDeliveryModes:
#            print strDeliveryMode
            dictResult[strDeliveryMode] = []
        objMembers = GetDataFolder(self, 'E3Member')
        for objBatch in objMembers.objectValues('Folder'):
            for objMember in objBatch.objectValues('E3Member'):
                if objMember.MembershipType == 'Full':
                    for objEmailAddress in objMember.objectValues('E3EmailAddress'):
                        strAdvDeliveryMode = ""
                        if objEmailAddress.Confirmed:
                            strEmailAddress = objEmailAddress.EmailAddress
                            if strEmailAddress == objMember.EmailDeliveryAddress:
                                if "Adv" in self.unrestrictedTraverse('..').id:
                                    strDeliveryMode = objMember.GetEmailFrequency("ECL", True)
                                else:
                                    strDeliveryMode = objMember.GetEmailFrequency("ECL", False)
                                if strDeliveryMode != "Direct":
                                    strDeliveryMode = objMember.EmailDigestMode
                            else:
                                strDeliveryMode = "NoMail"
                            if strDeliveryMode in cnDeliveryModes and not objMember.NoMail and not objEmailAddress.Bouncing:
                                dictResult[strDeliveryMode].append(strEmailAddress)
                            else:
                                dictResult['NoMail'].append(strEmailAddress)
        return dictResult

    def Update(self, blnForce = False):
        dtmLastUpdate = self.LastUpdate
        fltSince = DateTime() - dtmLastUpdate
        fltOneSecond = 1/float(24*60*60)
        intSeconds = int(fltSince/fltOneSecond)
        intMinutes = int(intSeconds/60)
#        print "Time passed from %s to %s: %s seconds" % (self.LastUpdate, DateTime(), intSeconds)
        if not blnForce and intSeconds < 5:
            return
        dictMembers = self.GetMailingLists()
        for objMailBoxerMembers in self.objectValues('E3MailBoxerMembers'):
            if objMailBoxerMembers.DeliveryMode in cnDeliveryModes:
                objMailBoxerMembers.Members = dictMembers[objMailBoxerMembers.DeliveryMode]
            else:
                print "Unknown delivery mode: ", objMailBoxerMembers.DeliveryMode
        self.LastUpdate = DateTime()

    def GetMailBoxerMembers(self, strDeliveryMode):
        self.Update()
        for objMailBoxerMembers in self.objectValues('E3MailBoxerMembers'):
            if objMailBoxerMembers.DeliveryMode == strDeliveryMode:
                return objMailBoxerMembers.Members
        return []

    def AllMailBoxerMembers(self):
        self.Update()
        lstResult = []
        for objMailBoxerMembers in self.objectValues('E3MailBoxerMembers'):
            lstResult += objMailBoxerMembers.Members
        return lstResult

def addE3ListForm(self):
    "New E3List form"
    return GenericAddForm('E3List')

def addE3List(self, id):
    "New E3List action"
    objNewE3List = E3List(id)
    self._setObject(id, objNewE3List)
    
    return "New E3List created."

