import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyDate
from libConstants import cnEmptyZopeDate
import DateTime

class E3Period(OFS.Folder.Folder):
    "E3Period class"
    meta_type = 'E3Period'

    def mymyinitmymy(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myStartDate', DateTime.DateTime(cnEmptyZopeDate), 'date')
        self.manage_addProperty('myEndDate', DateTime.DateTime(cnEmptyZopeDate), 'date')
        self.manage_addProperty('PeriodType', '', 'string')

    def GetStartDate(self):
        return FromZopeDateTime(self.myStartDate)

    def SetStartDate(self, dtmDate):
        self.myStartDate = ToZopeDateTime(self, dtmDate)

    def GetEndDate(self):
        return FromZopeDateTime(self.myEndDate)

    def SetEndDate(self, dtmDate):
        self.myEndDate = ToZopeDateTime(self, dtmDate)

    def indexmyhtml(self):
        "Show details"
        return ShowFullDetails(self)

def addE3PeriodForm(self):
    "New E3Period form"
    return GenericAddForm('E3Period')

def addE3Period(self, id):
    "New E3Period action"
    objNewE3Period = E3Period(id)
    self._setObject(id, objNewE3Period)
    
    return "New E3Period created."
