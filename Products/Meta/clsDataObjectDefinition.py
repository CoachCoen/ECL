import OFS.Folder
import Globals
from Functions import *

from libDatabase import GetDataFolder
from libFolders import AddFolder

class DataObjectDefinition(OFS.Folder.Folder):
    "DataObjectDefinition class"
    meta_type = 'M3DataObjectDefinition'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Category', 'Meta', 'string')
        self.manage_addProperty('Batched', False, 'boolean')
        self.manage_addProperty('SubObject', False, 'boolean')
        self.manage_addProperty('BatchSize', 100, 'int')
        self.manage_addProperty('CurrentBatch', 1, 'int')
        self.manage_addProperty('CurrentId', 0, 'int')
        self.manage_addProperty('Location', '', 'string')
        self.manage_addProperty('HasCatalogue', False, 'boolean')
        self.manage_addProperty('Indexes', [], 'lines')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def NextId(self, objParent = None):
        if self.SubObject:
            intId = 1
            for objChild in objParent.objectValues(self.id):
                strId = objChild.id
                strId = strId[len(self.id):]
                if int(strId) > intId:
                    intId = int(strId)
            return self.id + str(intId).zfill(4)
        else:
            self.CurrentId = self.CurrentId + 1
            if self.Batched:
                if self.CurrentId > self.BatchSize:
                    self.CurrentBatch = self.CurrentBatch + 1
                    self.CurrentId = 1

            return self.BuildId()

    def BuildId(self, intBatch = 0, intId = 0):
        if not intBatch:
            intBatch = self.CurrentBatch

        if not intId:
            intId = self.CurrentId
        if self.Batched:
            return '%s%s%s' % (self.id, str(intBatch).zfill(3), str(intId).zfill(3))
        else:
            return '%s%s' % (self.id, str(intId).zfill(5))

    def BlankDictionary(self):
        dictResult = {}
        if self.Batched:
            for intBatch in range(1, self.CurrentBatch + 1):
                for intI in range(1, self.BatchSize + 1):
                    if not (intBatch == self.CurrentBatch and intI > self.CurrentId):
                        strId = self.BuildId(intBatch, intI)
                        dictResult[strId] = 0
        else:
            for intI in range(1, self.CurrentId + 1):
                strId = self.BuildId(0, intI)
                dictResult[strId] = 0
        return dictResult

    def GetNextSubId(self, objFolder):
        strType = self.id
        intLastNumber = 0
        for strId in objFolder.objectIds(strType):
            strNumber = strId[len(strType):]
            intNumber = int(strNumber)
            if intNumber > intLastNumber:
                intLastNumber = intNumber
        strResult = strType + str(intLastNumber + 1).zfill(3)
        return strResult

    def NewObject(self, objTarget = None, strId = ''):
        if not strId:
            strId = self.NextId()
        if not objTarget:
            objTarget = GetDataFolder(self, self.id)
            if self.Batched:
                strBatchName = 'Batch%s' % str(self.CurrentBatch).zfill(3)
                try:
                    objTarget = objTarget.unrestrictedTraverse(strBatchName)
                except:
                    objTarget = AddFolder(objTarget, strBatchName)
        AddFunction = eval("objTarget.manage_addProduct['%s'].add%s" % (self.Category, self.id))
        AddFunction(strId)
#        print "Created %s in %s with id %s" % (self.id, objTarget.id, strId)
        objObject = objTarget.unrestrictedTraverse(strId)

#        if self.HasCatalogue:
#            objCatalogue = GetDataFolder(self, self.id).Catalogue
#            objCatalogue.catalog_object(objObject)

        return objObject

def addDataObjectDefinitionForm(self):
    "New DataObjectDefinition form"
    return GenericAddForm('DataObjectDefinition')

def addDataObjectDefinition(self, id):
    "New DataObjectDefinition action"
    objNewDataObjectDefinition = DataObjectDefinition(id)
    self._setObject(id, objNewDataObjectDefinition)
    
    return "New DataObjectDefinition created."
