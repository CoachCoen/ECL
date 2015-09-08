# encoding: utf-8

# import datetime

"""Various database functions"""

def ConvertToList(lstItems):
    lstResult = []
    for objItem in lstItems:
        lstResult.append(objItem)
    return lstResult
    
def NextInvoiceNumber(objHere):
    objE3 = GetDataFolder(objHere, 'E3Data')
    intNextInvoiceNumber = objE3.LatestInvoiceNumber + 1
    objE3.LatestInvoiceNumber = intNextInvoiceNumber
    return intNextInvoiceNumber

def Catalogue(objObject):
    strType = objObject.meta_type
    objDataFolder = GetDataFolder(objObject, strType)     
    if "Catalogue" in objDataFolder.objectIds():
        objCatalogue = objDataFolder.Catalogue
        objCatalogue.catalog_object(objObject)

def VisitDataFolder(objFolder, strItemType, funAction, lstParameters):
    for objItem in objFolder.objectValues():
        if objItem.meta_type == strItemType:
            funAction(objItem)
        VisitDataFolder(objItem, strItemType, funAction, lstParameters)

def VisitData(objHere, strItemType, funAction, lstParameters = ()):
    objFolder = GetDataFolder(objHere, strItemType)
    VisitDataFolder(objFolder, strItemType, funAction, lstParameters)

def GetWebsiteRoot(objHere, strWebsite):
    if strWebsite == 'E3':
        return objHere.unrestrictedTraverse('/Websites/ECLv3')
    elif strWebsite == 'MCI':
        return objHere.unrestrictedTraverse('/Websites/MCI')
    else:
        print "Website root not found for %s" % strWebsite
        return None

def GetDataFolder(objHere, strContents):
    """Returns the folder that this type of contents lives in
        strContents can either be a Data Object Type 
        or 'DataDefinitions'"""
    strPath = ''
    if strContents in objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions').objectIds():
        objDataObjectDefinition = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions/%s' % strContents)
    else:
        objDataObjectDefinition = None

    if objDataObjectDefinition:
        return objHere.unrestrictedTraverse('/Data/%s/%s' % (objDataObjectDefinition.Category, objDataObjectDefinition.Location))

    if strContents == 'DataObjectDefinitions':
        strPath = '/Data/Meta/DataObjectDefinitions'
    if strContents == 'MCIData':
        strPath = '/Data/MCI'
    if strContents == 'E3Data':
        strPath = '/Data/E3'
    if strContents == 'MetaData':
        strPath = '/Data/Meta'
    if strContents == 'MainDataFolder':
        strPath = '/Data'
    if strContents == 'MailBoxer':
        strPath = '/Websites/ECLv3/MailBoxer'
    if strContents == 'E3Messages':
#        strPath = '/Data/E3Messages/Messages'
#        strPath = '/Websites/ECLv3/MailBoxer/Archive'
        strPath = '/Data/E3Messages'
    if strPath:
        return objHere.unrestrictedTraverse(strPath)
    print "GetDataFolder, unknown contents type: %s" % strContents
    return None

def GetDOD(objHere, strDataObjectType):
    return GetDataFolder(objHere, 'DataObjectDefinitions').unrestrictedTraverse(strDataObjectType)

def SearchOne(objHere, strDataObjectType, strKey, strValue):
    """Searches for a single object of type strDataObjectType,
        where strKey = strValue
        returns None if more or less than 1 objects are found"""
    lstResult = SearchMany(objHere, strDataObjectType, strKey, strValue)
    if lstResult and len(lstResult) == 1:
        return lstResult[0]
    else:
        return None

def SearchMany(objHere, strDataObjectType, strKey, strValue):
    """Searches for objects of type strDataObjectType,
        where strKey = strValue"""
    objCatalogue = None
    objCatalogue = GetDataFolder(objHere, strDataObjectType).Catalogue
#    dtmNow = datetime.datetime.today()
#    print dtmNow, "SearchMany start"
    if objCatalogue:            
        dictCriteria = {strKey: strValue}
        lstResult = []
        lstBrains = objCatalogue.searchResults(dictCriteria)
#        dtmNow = datetime.datetime.today()
#        print dtmNow, "SearchMany, searchResults found"
        for objBrain in lstBrains:
            try:
                lstResult.append(objBrain.getObject())
            except:
                pass
        return lstResult
    return []

def SearchManyBrains(objHere, strDataObjectType, strKey, strValue):
    """Searches for objects of type strDataObjectType,
        where strKey = strValue
        Return Brains, rather than the actual objects"""
    objCatalogue = None
    objCatalogue = GetDataFolder(objHere, strDataObjectType).Catalogue
    if objCatalogue:            
        dictCriteria = {strKey: strValue}
        lstResult = objCatalogue.searchResults(dictCriteria)
        lstResult = ConvertToList(lstResult)
        return lstResult
    return []

#results=zcat(population_count={
#                 'query': [ 5, 10 ],
#                 'range': 'minmax'}
#            )
#
#results=zcat(population_count={
#                 'query' : 5,
#                 'range': 'min'}
#            )


def SearchDateRange(objHere, strDataObjectType, strKey, dtmFrom, dtmTo):
    objCatalogue = GetDataFolder(objHere, strDataObjectType).Catalogue
    if objCatalogue:
        if dtmFrom:
            if dtmTo:
                dictCriteria = {strKey: {'query': [dtmFrom, dtmTo]},
                                'range': 'minmax'}
            else:
                dictCriteria = {strKey: {'query': dtmFrom},
                                'range': 'min'}
        else:
            if dtmTo:
                dictCriteria = {strKey: {'query': dtmTo},
                                'range': 'max'}
            else:
                return None
        lstResult = []
        print "dictCriteria: %s" % dictCriteria
        lstBrains = objCatalogue.searchResults(dictCriteria)
        for objBrain in lstBrains:
            try:
                lstResult.append(objBrain.getObject())
            except:
                pass
        return lstResult
    return None        
    

def VisitMembers(objHere, strType, funAction):
    for objBatch in GetDataFolder(objHere, 'E3Member').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objItem in objMember.objectValues(strType):
                funAction(objItem)

def ReindexOne(objHere, strType):
    objDataObjectDefinition = GetDOD(objHere, strType)
    if objDataObjectDefinition.HasCatalogue:
        objDataFolder = GetDataFolder(objHere, strType)
        objCatalogue = objDataFolder.Catalogue
        if strType in ['E3EmailAddress']:
            VisitMembers(objHere, strType, objCatalogue.catalog_object)
        else:
            VisitData(objHere, strType, objCatalogue.catalog_object)
