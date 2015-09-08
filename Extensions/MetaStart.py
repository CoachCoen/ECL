# encoding: utf-8
"""Boots trapping process,
    1. Create empty directories
    2. Create Data Object Definitions
    3. Import data"""
import LocalPaths

from libFolders import DeleteObject
from libFolders import AddFolder
from libDatabase import GetDataFolder
from libDatabase import GetDOD

def RemoveOldFolders(objHere, strWebsites):

    objMainDataFolder = GetDataFolder(objHere, 'MainDataFolder')

    if 'E3' in strWebsites:
        try:
            objMainDataFolder.manage_delObjects('E3')
        except:
            print "/Data/E3 not found, no need to delete"

    if 'MCI' in strWebsites:
        try:
            objMainDataFolder.manage_delObjects('MCI')
        except:
            print "/Data/MCI not found, no need to delete"

#    try:
#        objMainDataFolder.manage_delObjects('Meta')
#    except:
#        print "/Data/Meta not found, no need to delete"

def CreateNewFolders(objHere, strWebsites):
    objRootFolder = objHere.unrestrictedTraverse('/')
    objDataFolder = AddFolder(objRootFolder, 'Data')
    objMetaFolder = AddFolder(objDataFolder, 'Meta')
    AddFolder(objMetaFolder, 'DataObjectDefinitions')
    AddFolder(objDataFolder, 'MCI')
    AddFolder(objDataFolder, 'E3')

def NewCatalogue(objTarget):
    objTarget.manage_addProduct['ZCatalog'].manage_addZCatalog('Catalogue', 'Catalog')
    return objTarget.unrestrictedTraverse('Catalogue')
        
def NewZCTextIndex(objDataFolder, strField, strName):
    class Extra:
        """ Just a dummy to build records for the Lexicon.
        """
        pass

    wordSplitter = Extra()
    wordSplitter.group = 'Word Splitter'
    wordSplitter.name = 'Whitespace splitter'

    caseNormalizer = Extra()
    caseNormalizer.group = 'Case Normalizer'
    caseNormalizer.name = 'Case Normalizer'

    objDataFolder.Catalogue.manage_addProduct['ZCTextIndex'].manage_addLexicon('%sLexicon' % strField, '%sLexicon' % strField,(wordSplitter, caseNormalizer))

    extra = Extra()
    extra.index_type = 'Okapi BM25 Rank'
    extra.lexicon_id = '%sLexicon' % strField
    extra.name = strName

    objDataFolder.Catalogue.addIndex(strField, 'ZCTextIndex', extra)
 
def NewFieldIndex(objDataFolder, strName, strField):
    class Extra:
        """ Just a dummy to build records for the Lexicon.
        """
        pass
    extra = Extra()
    extra.indexed_attrs = strField
    objDataFolder.Catalogue.addIndex(strName, 'FieldIndex', extra)
    print "New field index: %s, %s" % (strField, strName)

def NewDateIndex(objDataFolder, strField):
    objDataFolder.Catalogue.addIndex(strField, 'DateIndex')

def CreateCatalogues(objDataFolder, dictCatalogue):
    if 'Catalogue' in objDataFolder.objectIds():
        objDataFolder.manage_delObjects('Catalogue')

    objCatalogue = NewCatalogue(objDataFolder)

    for strField in dictCatalogue.keys():
        strType = dictCatalogue[strField]
        lstType = strType.split('/')
        if len(lstType) > 1:
            strType = lstType[0]
            strName = lstType[1]
        else:
            strName = strField
        if strType == 'Text':
            NewZCTextIndex(objDataFolder, strField, strName)
        else:
            NewFieldIndex(objDataFolder, strField, strName)

def AddDataObjectDefinition(objDefs, strDataObjectType, blnBatched, intBatchSize, strLocation, strCategory, dictCatalogues):
    if strDataObjectType in objDefs.objectIds():
        objDefs.manage_delObjects(strDataObjectType)
    objDefs.manage_addProduct['Meta'].addDataObjectDefinition(strDataObjectType)
    objDataObjectDefinition = objDefs.unrestrictedTraverse(strDataObjectType)
    objDataObjectDefinition.Category = strCategory
    objDataObjectDefinition.Batched = blnBatched
    objDataObjectDefinition.BatchSize = intBatchSize
    objDataObjectDefinition.Location = strLocation
    objMainDataFolder = GetDataFolder(objDefs, strCategory + "Data")
    if strLocation:
        objDataFolder = AddFolder(objMainDataFolder, strLocation)

    if dictCatalogues:
        CreateCatalogues(objDataFolder, dictCatalogues)
        objDataObjectDefinition.HasCatalogue = True

def AddEventDefinitions(objHere):
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    AddDataObjectDefinition(objDefs, 'E3EventPreference', False, 0, 'E3EventPreferences', 'E3', None)
    AddDataObjectDefinition(objDefs, 'E3AvailabilityStatement', False, 0, 'E3AvailabilityStatements', 'E3', None)
    return "Done"

def AddEventRegistrationDefinitions(objHere):
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    AddDataObjectDefinition(objDefs, 'E3EventRegistration', True, 100, 'E3EventRegistration', 'E3', {'Event': 'Field', 'Name': 'Text', 'EmailAddress': 'Text', 'id': 'Field'})
    return "EventRegistration definitions added"

def AddThreadDefinitions(objHere):
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    AddDataObjectDefinition(objDefs, 'E3Thread', True, 100, 'E3Threads', 'E3', {'id': 'Field', 'TopicId': 'Field'})
    AddDataObjectDefinition(objDefs, 'E3Topic', False, 0, 'E3Topics', 'E3', {'id': 'Field'})

def CreateDataObjectDefinitions(objHere, strWebsites):
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    # Note: Only those objects which have their own data directory
    # and/or which have a ZCatalogue
    lstMCI = ( \
        ('MCIAuthor', True, 100, 'MCIAuthors', 'MCI', 
            {'id':'Field',
            'SourceId': 'Field'}),
        ('MCIBookCategory', False, 0, 'MCIBookCategories', 'MCI', 
            {'id':'Field',
            'SourceId': 'Field'}),
        ('MCIBook', True, 100, 'MCIBooks', 'MCI',
            {'id': 'Field',
            'ISBN': 'Field',
            'Review': 'Field',
            'Title': 'Text',
            'SubTitle': 'Text',
            'Authors': 'Text',
            'Categories': 'Text',
            'ReaderCategories': 'Text',
            'SourceId': 'Field'}),
        ('MCIBookReview', True, 100, 'MCIBookReviews', 'MCI', 
            {'id': 'Field',
            'ReviewId': 'Field'}),
        ('MCIBookSearch', True, 100, 'MCIBookSearches', 'MCI', {}),
        ('MCIEnrolmentLog', True, 100, 'MCIEnrolmentLogs', 'MCI', {}),
        ('MCIEnrolment', True, 100, 'MCIEnrolments', 'MCI', {'MasterclassId': 'Field'}),
        ('MCIListStat', True, 100, 'MCIListStats', 'MCI', {}),
        ('MCILink', True, 100, 'MCILinks', 'MCI', {}),
        ('MCIMasterclass', False, 0, 'MCIMasterclasses', 'MCI', 
            {'SourceId': 'Field', 
            'id': 'Field'}),
        ('MCINewsletter', False, 0, 'MCINewsletters', 'MCI', {'id': 'Field'}),
        ('MCIParticipant', True, 100, 'MCIParticipants', 'MCI', 
            {'id':'Field',
            'ParticipantName': 'Text',
            'SourceId': 'Field'}),
        ('MCIPerson', False, 0, 'MCIPerson', 'MCI', 
            {'PersonId': 'Field',
                'id': 'Field'}),
        ('MCIPresenter', False, 0, 'MCIPresenters', 'MCI', {}),
        ('MCIReaderCategory', False, 0, 'MCIReaderCategories', 'MCI', 
            {'SourceId': 'Field',
            'id': 'Field'}),
        ('MCIShopAt', True, 100, 'MCIShopAt', 'MCI', {})
        )

    lstE3 = ( \
        ('E3List', False, 0, 'E3Lists', 'E3', {}),
        ('E3ListStat', True, 100, 'E3ListStats', 'E3', {}),
        ('E3Member', True, 100, 'E3Members', 'E3', 
            {'Username': 'Field',
            'id': 'Field',
            'EmailAddress': 'Text',
            'Name': 'Text'}),
        ('E3SessionData', True, 100, 'E3SessionData', 'E3', {}),
        ('E3WorldPayCall', False, 0, 'E3WorldPayCalls', 'E3', {'CartId': 'Field'}),
        ('E3WorldPayResult', False, 0, '', 'E3', {}),
        ('E3EmailAddress', False, 0, 'E3EmailAddresses', 'E3', {'EmailAddress': 'Text',
            'EmailAddressField': 'Field/EmailAddress',
            'id': 'Field', 
            'ConfirmationString': 'Field'}),
        ('E3Event', False, 0, '', 'E3', {}),
        ('E3Invoice', False, 0, '', 'E3', {}),
        ('E3MailBoxerMembers', False, 0, '', 'E3', {}),
        ('E3ListMembership', False, 0, '', 'E3', {}),
        ('E3Payment', False, 0, '', 'E3', {}),
        ('E3Period', False, 0, '', 'E3', {}),
        ('E3Help', False, 0, 'E3Help', 'E3', {'Categories': 'Text',
                                        'id': 'Field',
                                        'HelpId': 'Field'}),
        ('E3Search', 'False', 0, '', 'E3', {}),
        ('E3SearchBlock', 'False', 0, '', 'E3', {}),
        ('E3UnclaimedEmailAddress', 'True', 100, 'E3UnclaimedEmailAddresses', 'E3', {'Key': 'Field'})
        )

    if 'E3' in strWebsites:
        if 'MCI' in strWebsites:
            lstList = lstE3 + lstMCI
        else:
            lstList = lstE3
    else:
        lstList = lstMCI


    for (strDataObjectType, blnBatched, intBatchSize, strLocation, strCategory, dictCatalogues) in lstList:
        AddDataObjectDefinition(objDefs, strDataObjectType, blnBatched, intBatchSize, strLocation, strCategory, dictCatalogues)

def CreateAdditionalProperties(objHere):
    """Any properties that haven't been done by the other code"""
    objMessages = GetDataFolder(objHere, "E3Messages")
    print objMessages.MessageCount
    try:
        objMessages.manage_delObjects('MessageCount')
    except:
        print "Couldn't delete MessageCount, probably didn't exist"

    try:
        objMessages.manage_addProperty('MessageCount', [], 'lines')
    except:
        print "E3Messages.MessageCount already defined. No need to add property"

    try:
        objMessages.manage_addProperty('MembersCount', 0, 'int')
    except:
        print "E3Messages.MembersCount already defined. No need to add property"

    objE3 = GetDataFolder(objHere, "E3Data")
    try:
        objE3.manage_addProperty('LatestInvoiceNumber', 0, 'int')
    except:
        print "E3Data.LatestInvoiceNumber already defined. No need to add property"

    for strProperty in ('DirectListMembers', 'TextDigestMembers', 'MIMEDigestMembers', 'NoMailMembers', 'DigestList'):
        try:
            objE3.manage_addProperty(strProperty, [], 'lines')
        except:
            print "E3Data.%s already defined. No need to add property" % strProperty

    for strProperty in ('DigestLength', 'LatestCartId', 'MembersCount'):
        try:
            objE3.manage_addProperty(strProperty, 0, 'int')
        except:
            print "E3Data.%s already defined. No need to add property" % strProperty

        objE3.LatestCartId = 1

def AddCatalogue(objHere):
    CreateCatalogues(GetDataFolder(objHere, 'MCIReaderCategory'), {'id': 'Field'})
#    dodMCIReview = GetDOD(objHere, 'MCIBookReview')
#    dodMCIReview.HasCatalogue = True

def BuildE3MessageCatalogue(objMessages):
    objCatalogue = NewCatalogue(objMessages)
    NewFieldIndex(objMessages, 'id')
    NewZCTextIndex(objMessages, 'title')
    NewZCTextIndex(objMessages, 'mailFrom')
    NewZCTextIndex(objMessages, 'mailSubject')
    NewZCTextIndex(objMessages, 'mailBody')
    NewFieldIndex(objMessages, 'UserId')
    NewDateIndex(objMessages, 'mailDate')

def CreateE3MessageIndex(objHere):
    intDone = 0
    objMessages = GetDataFolder(objHere, 'E3Messages')
    if not 'Catalogue' in objMessages.objectIds():
        BuildE3MessageCatalogue(objMessages)
    for objYear in objMessages.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            print
            print objMonth.id
            for objThread in objMonth.objectValues('Folder'):
                objMessages.Catalogue.catalog_object(objThread)
                print "|",
                intDone += 1
                for objMessage in objThread.objectValues('Folder'):
                    objMessages.Catalogue.catalog_object(objMessage)
                    print "-",
                    intDone += 1
    print
    print "Done: %s" % intDone

def SetupSystems(objHere):
    """The boots trapping process"""
    blnRecreateFolders = True
    blnE3Import = False
    blnMCIImport = False
    blnE3MessageIndex = False

    blnRecreateFolders = True
#    blnE3Import = True
#    blnMCIImport = True
#    blnE3MessageIndex = True

#    CreateDataObjectDefinitions(objHere)

    strWebsites = 'E3'
#    strWebsites = 'MCI'
#    strWebsites = 'E3MCI'
#    CreateAdditionalProperties(objHere)
    if blnRecreateFolders:
#        RemoveOldFolders(objHere, strWebsites)
#        CreateNewFolders(objHere, strWebsites)
        CreateDataObjectDefinitions(objHere, strWebsites)
#        if 'E3' in strWebsites:
#            CreateAdditionalProperties(objHere)
    return "All done"
