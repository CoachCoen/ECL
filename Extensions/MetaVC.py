import os
from LocalPaths import *

def ExportHeader(objItem, fileItem):
    fileItem.write("<type>%s</type>\n" % objItem.meta_type)

def ExportProperties(objItem, fileItem):
    fileItem.write("<properties>\n")
    try:
        lstMap = objItem.propertyMap()
    except:
        lstMap = None

    if lstMap:
        for dictProperty in lstMap:
            strType = dictProperty['type']
            strId = dictProperty['id']
            strLine = ""
            if strType in ['string', 'ustring', 'boolean', 'int']:
                strLine = """    <property type="%s" id="%s">%s</property>\n""" % (strType, strId, objItem.getProperty(strId))
            elif strType in ['text', 'lines', 'tokens', 'selection']:
                strLine = """    <property type="%s" id="%s">\n%s\n</property>\n""" % (strType, strId, objItem.getProperty(strId))
            else:
                print "Unknown type: %s" % strType
            if strLine:
                fileItem.write(strLine)

    fileItem.write("</properties>\n")

def ExportContents(objItem, fileItem):
    strType = objItem.meta_type.lower()

    fileItem.write("<contents>")
    strContents = GetContents(objItem)
#    try:
#    strContents = strContents.decode('ascii', 'replace')
#    except:
#        pass
    try:
        fileItem.write(strContents)
    except:
        fileItem.write("Contents could not be written")
    fileItem.write("</contents>\n")

def GetContents(objItem):
    strType = objItem.meta_type.lower()

    if strType == "external method":
        return "    <module>%s</module>\n<function>%s</function>\n" % (objItem.module(), objItem.function())
    elif strType == "file":
        return objItem.data
    elif strType in ["page template", 'dtml method', 'dtml document']:
        return objItem.document_src()
    elif strType == 'folder':
        return ""
    elif strType in ['standardpage', 'user folder', 'mail host', 'mail boxer']:
        return ""
    elif strType == 'image':
        return objItem.data

    print objItem.absolute_url, objItem.id, "Unknown type: ", strType
    return ""

def SetContents(objObject, strContents):
    strType = objObject.meta_type.lower()

    if strType == "external method":
        strModule = GetProperties(strContents, 'module')[0][1]
        strFunction = GetProperties(strContents, 'function')[0][1]
        objObject.manage_edit(objObject.title, strModule, strFunction)
    elif strType == 'file':
        objObject.data = strContents
    elif strType in ["dtml method", "dtml document"]:
        objObject.manage_edit(strContents, objObject.title)
    elif strType == "page template":
        try:
            objObject.pt_edit(strContents, 'text/html', 'utf-8')
        except:
            objContainer = objObject.unrestrictedTraverse('..')
            strObjectName = objObject.id
            objContainer.manage_delObjects(strObjectName)
            objObject = objContainer.manage_addProduct['PageTemplates'].manage_addPageTemplate(strObjectName)
            objObject.pt_edit(strContents, 'text/html', 'utf-8')

    elif strType == 'folder':
        pass
    elif strType in ['standardpage', 'user folder', 'mail host', 'mail boxer']:
        return ""
    elif strType == 'image':
        objContainer = objObject.unrestrictedTraverse('..')
        strId = objObject.id()
        objContainer.manage_delObjects(strId)
        objContainer.manage_addImage(strId, strContents) # Note: might need to save the contents in a file and then feed the filename instead of strContents

def ExportSubItems(objItem, strDestination):
    if objItem.objectValues():
        CreateFolders(strDestination)
    for objSubItem in objItem.objectValues():
        ExportItem(objSubItem, strDestination)

def ExportItem(objItem, strDestination):
    try:
        strId = objItem.id()
    except:
        strId = objItem.id
    strPath = "%s/%s" % (strDestination, strId)
    fileItem = open(strPath + ".exp", "w")
    ExportHeader(objItem, fileItem)
    ExportProperties(objItem, fileItem)
    ExportContents(objItem, fileItem)
    ExportSubItems(objItem, strPath)

def CreateOneFolder(strPath):
    if not os.path.exists(strPath):
        os.system('mkdir %s' % strPath)

def CreateFolders(strPath):
    lstPath = strPath.split("/")
    strFullPath = ""
    for strPath in lstPath:
        if strPath:
            strFullPath += "/" + strPath
            CreateOneFolder(strFullPath)

def ExportFolder(objFolder, strRoot, strFolder):
    strDestination = strRoot + "/" + strFolder + "/"
    CreateFolders(strDestination)

def ExportSite(objHere):
    objStart = objHere.unrestrictedTraverse('/')
#    strDestination = cnVCPath + strVersion
    strDestination = cnVCPath
    ExportItem(objStart.Meta, strDestination)
    ExportItem(objStart.Websites, strDestination)
#    ExportItem(objStart.XMLHttp, strDestination)

def ParseChunk(strChunk):
    intPosition = strChunk.find('>')
    strTag = strChunk[:intPosition + 1]
    strRemain = strChunk[intPosition + 1:]
    intPosition = strRemain.rfind('<')
    strContents = strRemain[:intPosition]

    strTag = strTag.replace('<', '').replace('>', '')
    lstRawProperties = strTag.split()[1:]
    dictProperties = {}
    for strProperty in lstRawProperties:
        (strName, strValue) = strProperty.split("=")
        strValue = strValue.replace('"', '')
        dictProperties[strName] = strValue
    return (dictProperties, strContents)

def GetProperties(strFile, strName):
    strRemain = strFile
    lstResult = []
    while strRemain:
        intStart = strRemain.find('<' + strName)
        if intStart >= 0 :
            intEnd = strRemain.find('</%s>' % strName)
            strChunk = strRemain[intStart:intEnd + len(strName) + 3]
            lstResult.append(ParseChunk(strChunk))
            strRemain = strRemain[intEnd + len(strName) + 3:]
        else:
            strRemain = ""
    return lstResult

def ParseImportFile(fileFile):
    strFile = fileFile.read()
    lstType = GetProperties(strFile, 'type')
    strType = lstType[0][1]
    lstProperties = GetProperties(strFile, 'property')
    lstContents = GetProperties(strFile, 'contents')
    strContents = lstContents[0][1]
    return (strType, lstProperties, strContents)

def GetPropertyValue(strType, strValue):
    if strType == 'int':
        return int(strValue)
    if strType == 'boolean':
        if strValue == '1' or strValue == 'True':
            return True
        else:
            return False
    if strType in ['text', 'lines', 'tokens', 'selection']:
        strResult = strValue[1:-1]
        try:
            exec 'strResult = ' + strResult
        except:
            pass
        return strResult
    return strValue

def DeleteProperty(objObject, strName):
    objObject.manage_delProperties((strName, ))

def ChangeProperty(objObject, strName, varNewContents):
    objObject.manage_changeProperties({strName:varNewContents})

def ChangePropertyType(objObject, strName, strNewType, varNewContents):
    objObject.manage_delProperties((strName, ))
    objObject.manage_addProperty(strName, varNewContents, strNewType)

def Exclude(strObject, lstExclude):
#    strObject = strObject[len(cnVCPath):]
#    print "Exclude |%s|?" % strObject
    if strObject.lower() in lstExclude:
#        print "Exclude: %s" % strObject
        return True
    if 'broken.exp' in strObject.lower():
        return True
    return False

def WriteLog(fileLog, strLine, blnExclude):
    if blnExclude:
        fileLog.write("Exclude: ")
    fileLog.write(strLine + "\n")

def CompareOneProperty(fileLog, dictOldProperty, varOldContents, lstNewProperties, strObjectType, objObject,  blnCommit, strPath, lstExclude):
    strName = dictOldProperty['id']
    try:
        strObjectId = objObject.id()
    except:
        strObjectId = objObject.id
    for (dictNewProperty, strNewContents) in lstNewProperties:
        blnExclude = Exclude(strPath + "/" + strObjectId + "/" + strName, lstExclude)
        if dictNewProperty['id'] == strName:
            if dictNewProperty['type'] <> dictOldProperty['type']:
                WriteLog(fileLog, "Property '%s', type changed from %s to %s" % (strName, dictOldProperty['type'], dictNewProperty['type']), blnExclude)
                if blnCommit and not blnExclude:
                    ChangePropertyType(objObject, strName, dictNewProperty['type'], varNewContents)
                return
            varNewContents = GetPropertyValue(dictNewProperty['type'], strNewContents)
            if  varNewContents <> varOldContents:
                if strObjectType == 'Image' and str(varOldContents) == str(varNewContents):
                    pass
                else:
                    WriteLog(fileLog, "Property '%s', contents changed from '%s' (%s) to '%s' (%s)" % (strName, varOldContents, type(varOldContents), varNewContents, type(varNewContents)), blnExclude)
                    if blnCommit and not blnExclude:
                        ChangeProperty(objObject, strName, varNewContents)
            return
    WriteLog(fileLog, "Property %s deleted" % dictOldProperty['id'], blnExclude)
    if blnCommit and not blnExclude:
        DeleteProperty(objObject, strName)

def GetId(objObject):
    try:
        strId = objObject.id()
    except:
        strId = objObject.id
    return strId

def CompareContents(fileLog, objOldObject, strNewContents, blnCommit, strPath, lstExclude):
    strOldContents = GetContents(objOldObject)
    strId = GetId(objOldObject)
    try:
        if str(strOldContents).strip() <> str(strNewContents).strip():
            blnExclude = Exclude(strPath + "/" + strId, lstExclude)
            WriteLog(fileLog, 'Contents changed', blnExclude)
#        WriteLog(fileLog, 'From\n|%s|\nTo\n|%s|' % (strOldContents, strNewContents), blnExclude)
            if blnCommit and not blnExclude:
                SetContents(objOldObject, strNewContents)
    except:
        WriteLog(fileLog, 'Failed to compare', objOldObject.id)

def RemoveAllProperties(objObject):
    try:
        lstMap = objObject.propertyMap()
    except:
        lstMap = ()
    for dictProperty in lstMap:
        objObject.manage_delProperties(dictProperty['id'])

def SetProperties(objObject, lstNewProperties):
    for (dictProperty, strNewContents) in lstNewProperties:
        AddProperty(objObject, dictProperty, strNewContents)

def AddProperty(objObject, dictNewProperty, strNewContents):
    strId = dictNewProperty['id']
    strType = dictNewProperty['type']
    objObject.manage_addProperty(strId, GetPropertyValue(strType, strNewContents), strType)

def CompareProperties(fileLog, objOldObject, lstNewProperties, blnCommit, strPath, lstExclude):
    try:
        lstMap = objOldObject.propertyMap()
    except:
        lstMap = None
    strId = GetId(objOldObject)
    blnExclude = Exclude(strPath + "/" + strId, lstExclude)
    if lstMap and not lstNewProperties:
        WriteLog(fileLog, "All properties gone", blnExclude)
        if blnCommit and not blnExclude:
            RemoveAllProperties(objOldObject)
    elif not lstMap and lstNewProperties:
        WriteLog(fileLog, "All new properties", blnExclude)
        if blnCommit and not blnExclude:
            SetProperties(objOldObject, lstNewProperties)
    elif lstMap and lstNewProperties:
        for dictProperty in lstMap:
            CompareOneProperty(fileLog, dictProperty, objOldObject.getProperty(dictProperty['id']), lstNewProperties, objOldObject.meta_type, objOldObject, blnCommit, strPath, lstExclude)
        for (dictNewProperty, strNewContents) in lstNewProperties:
            if not dictNewProperty['id'] in objOldObject.propertyIds():
                blnExclude = Exclude(strPath + "/" + objOldObject.id + "/" + dictNewProperty['id'], lstExclude)
                WriteLog(fileLog, "New property %s" % dictNewProperty['id'], blnExclude)
                if blnCommit and not blnExclude:
                    AddProperty(objOldObject, dictNewProperty, strNewContents)

def UpdateObject(fileLog, fileFile, objContainer, strObjectName, blnCommit, strPath, lstExclude):
    (strMetaType, lstProperties, strContents) = ParseImportFile(fileFile)
    objOldObject = objContainer.unrestrictedTraverse(strObjectName)
    
    if objOldObject.meta_type <> strMetaType:
        blnExclude = Exclude(strPath + "/" + strObjectName, lstExclude)
        WriteLog(fileLog, "Type changed from %s to %s, creating a new object" % (objOldObject.meta_type, strMetaType), blnExclude)
        if blnCommit and not blnExclude:
            objContainer.manage_delObjects(objOldObject.id)
            NewObject(fileFile, objContainer, strObjectName, strPath)
    else:
        CompareProperties(fileLog, objOldObject, lstProperties, blnCommit, strPath, lstExclude)
        CompareContents(fileLog, objOldObject, strContents, blnCommit, strPath, lstExclude)

def NewObject(fileFile, objContainer, strObjectName, strPath):
    (strType, lstProperties, strContents) = ParseImportFile(fileFile)
    strType = strType.lower()
    
    if strType == "external method":
#        if 'External' in strPath:
#            strPath = strPath[strPath.find('External') + 8:]
#            print "Path: |%s|" % strPath
#        elif 'Products' in strPath:
#            strPath = strPath[strPath.find('Products'):]
#            print "Path: |%s|" % strPath
#        else:
#            print "Path: |%s|" % strPath
        strModule = GetProperties(strContents, 'module')[0][1]
        strFunction = GetProperties(strContents, 'function')[0][1]
        objContainer.manage_addProduct['ExternalMethod'].manage_addExternalMethod(strObjectName, "", strModule, strFunction)
    elif strType == 'file':
        objContainer.manage_addFile(strObjectName, strContents)
    elif strType == "dtml method":
        objContainer.manage_addDTMLMethod(strObjectName, "")
        objObject = objContainer.unrestrictedTraverse(strObjectName)
        objObject.manage_edit(strContents, "")
    elif strType == "dtml document":
        objContainer.manage_addDTMLDocument(strObjectName, "")
        objObject = objContainer.unrestrictedTraverse(strObjectName)
        objObject.manage_edit(strContents, "")
    elif strType == "page template":
        objObject = objContainer.manage_addProduct['PageTemplates'].manage_addPageTemplate(strObjectName)
        objObject.pt_edit(strContents, "")
    elif strType == 'folder':
        objContainer.manage_addFolder(strObjectName)
    elif strType in ['standardpage', 'user folder', 'mail host', 'mail boxer']:
        print "New %s, but no code to import it" % strType
        return ""
    elif strType == 'image':
        objContainer.manage_addImage(strObjectName, strContents)
    else:
        print "Unknown object type: %s" % strType

def ImportFile(fileLog, strPath, strFile, objContainer, blnCommit, lstExclude):
    strFullname = strPath + "/" + strFile
    fileFile = open(strFullname, "r")
    lstObjectName = strFile.split('.')[:-1]
    strObjectName = '.'.join(lstObjectName)
    fileLog.write('Importing %s\n' % strFullname)
#    print strFullname
    if strObjectName in objContainer.objectIds():
        UpdateObject(fileLog, fileFile, objContainer, strObjectName, blnCommit, strPath, lstExclude)
    else:
        blnExclude = Exclude(strPath + "/" + strObjectName, lstExclude)
        WriteLog(fileLog, "New object: %s" % strObjectName, blnExclude)
        
        if blnCommit and not blnExclude:
            NewObject(fileFile, objContainer, strObjectName, strPath)
    fileLog.write("\n")

def CreateShortLog(strLog, strShortLog):
    fileSource = open(strLog, "r")
    lstSource = fileSource.readlines()
    fileSource.close()
    fileTarget = open(strShortLog, "w")
    blnWriteMode = False
    strName = ""
    intLine = 0
    for strLine in lstSource:
        if strLine.strip():
            intLine += 1
            if intLine == 1:
                strName = strLine
            elif intLine == 2:
                fileTarget.write(strName)
            if intLine > 1:
                fileTarget.write(strLine)
        else:
            if intLine > 1:
                fileTarget.write("\n")
            intLine = 0
    fileTarget.close()
    fileTarget = open(strShortLog, "r")
    return fileTarget.read().replace("\n", "<br>\n")

def ReadExclusionFile():
    fileExclude = open(cnLocalPath + "VCExclude.dat", "r")
    lstLines = fileExclude.readlines()
    lstResult = []
    for strLine in lstLines:
        lstResult.append(cnVCPath.lower() + "/" + strLine.lower()[:-1])
    print "\n".join(lstResult)
    return lstResult

def ImportSite(objHere, blnCommit = False):
    lstExclude = ReadExclusionFile()
    objStart = objHere.unrestrictedTraverse('/')
#    strSource = cnVCPath + cnVersion
    strSource = cnVCPath
    strLog = cnVCLogPath  + "VC.log"
    strShortLog = cnVCLogPath + "VCShort.log"
    fileLog = open(strLog, "w")
    intDone = 0
    for (strPath, lstDirs, lstFiles) in os.walk(strSource):
        if len(lstFiles) > 0 and not ".svn" in strPath and not "broken.exp" in strPath:
            print strPath
            strObjectPath = "/" + strPath[len(strSource):]
            strObjectPath = strObjectPath.replace('//', '/')
            print "Objectpath: ", strObjectPath
            objContainer = objStart.unrestrictedTraverse(strObjectPath)
            for strFile in lstFiles:
                if not 'broken.exp' in strFile:
                    ImportFile(fileLog, strPath, strFile, objContainer, blnCommit, lstExclude)
                intDone += 1
#                if intDone > 10:
#                    return
    fileLog.close()
    return CreateShortLog(strLog, strShortLog)
