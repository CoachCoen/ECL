import OFS.Folder
import Globals
from Functions import *

from libConstants import cnEmptyZopeDate

class E3ListStat(OFS.Folder.Folder):
    "E3ListStat class"
    meta_type = 'E3ListStat'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('ListId', '', 'string')
        self.manage_addProperty('myDateOfCount', cnEmptyZopeDate, 'date')
        
#        self.manage_addProperty('Count', 0, 'int')
#        self.manage_addProperty('Events', {}, 'dict')
#        self.manage_addProperty('Status', {}, 'dict')

    def GetDateOfCount(self):
        return FromZopeDateTime(self.myDateOfCount)

    def SetDateOfCount(self, dtmDate):
        self.myDateOfCount = ToZopeDateTime(self, dtmDate)

    def SetStats(self, dictStatistics):
        for strKey in dictStatistics.keys():
            self.manage_addProperty(strKey, dictStatistics[strKey], 'int')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3ListStatForm(self):
    "New E3ListStat form"
    return GenericAddForm('E3ListStat')

def addE3ListStat(self, id):
    "New E3ListStat action"
    objNewE3ListStat = E3ListStat(id)
    self._setObject(id, objNewE3ListStat)
    
    return "New E3ListStat created."
