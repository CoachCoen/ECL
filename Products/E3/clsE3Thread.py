import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate
from libConstants import cnFirstDate
from libConstants import cnLastDate
from libDatabase import SearchMany

# ThreadType can be one of the following:
#   Trial - start of trial period
#   LifetimeMember - member becomes a lifetime member
#   FreePeriod - start of a free period
#   Expiry - membership expired
#   WarningSent - Expiry due warning sent
#   BonusSent - Bonus message sent
#   ExpiryMessageSent - User just expired, message to user sent

class E3Thread(OFS.Folder.Folder):

    "E3Thread class"
    meta_type = 'E3Thread'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('TopicId', '', 'string')
        self.manage_addProperty('Subject', '', 'string')
        self.manage_addProperty('Summary', '', 'text')
        self.manage_addProperty('myFirstMessageDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('myLastMessageDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('Publish', False, 'boolean')
        self.manage_addProperty('Move', False, 'boolean')
        self.manage_addProperty('Deleted', False, 'boolean')

    def GetFirstMessageDate(self):
        if self.myFirstMessageDate.year() == 1901:
            self.SetMessageDates()
        return FromZopeDateTime(self.myFirstMessageDate)

    def SetFirstMessageDate(self, dtmDate):
        self.myFirstMessageDate = ToZopeDateTime(self, dtmDate)

    def GetLastMessageDate(self):
        if self.myLastMessageDate.year() == 1901:
            self.SetMessageDates()
        return FromZopeDateTime(self.myLastMessageDate)

    def SetLastMessageDate(self, dtmDate):
        self.myLastMessageDate = ToZopeDateTime(self, dtmDate)

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def SetMessageDates(self):
        lstMessages = SearchMany(self, 'E3Messages', 'ThreadId', self.id)
        if len(lstMessages) > 100:
            print "Too many messages: %s" % len(lstMessages)
            return
        dtmFirstDate = cnLastDate
        dtmLastDate = cnFirstDate
        for objMessage in lstMessages:
            dtmMessageDate = FromZopeDateTime(objMessage.mailDate)
            if dtmMessageDate < dtmFirstDate:
                dtmFirstDate = dtmMessageDate
            if dtmMessageDate > dtmLastDate:
                dtmLastDate = dtmMessageDate
        self.SetFirstMessageDate(dtmFirstDate)
        self.SetLastMessageDate(dtmLastDate)

def addE3ThreadForm(self):
    "New E3Thread form"
    return GenericAddForm('E3Thread')

def addE3Thread(self, id):
    "New E3Thread action"
    objNewE3Thread = E3Thread(id)
    self._setObject(id, objNewE3Thread)

    return "New E3Thread created."
