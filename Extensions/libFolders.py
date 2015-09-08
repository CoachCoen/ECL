# encoding: utf-8

"""Functions for deleting and creating folders and"""

def DeleteObject(objObject):
    """Deletes a folder or object within a folder"""
    objFolder = objObject.unrestrictedTraverse('..')
    objFolder.manage_delObjects(objObject.id)

def AddFolder(objTarget, strName):
    """Creates a new folder, called strName, within objTarget
        Returns the new folder"""
    try:
        objTarget.manage_addFolder(strName)
    except:
        pass
    return objTarget.unrestrictedTraverse(strName)

