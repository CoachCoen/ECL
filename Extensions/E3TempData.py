# encoding: utf-8

import thread

from libDatabase import GetDataFolder
from libDatabase import GetDOD

def GetThreadId():
    intId = abs(thread.get_ident())
    strId = 'Thread%s' % intId
    return strId

def StoreTempData(objHere, strUsername, strErrorScreen, strPageTitle):
    strId = GetThreadId()
    objFolder = GetDataFolder(objHere, 'E3SessionData')
    dodTempData = GetDOD(objHere, 'E3SessionData')
    objTempData = dodTempData.NewObject(objFolder, strId)
    objTempData.Username = strUsername
    objTempData.ErrorScreen = strErrorScreen
    objTempData.PageTitle = strPageTitle

def SetErrorScreen(objHere, strErrorScreen):
    objTempData = GetTempData(objHere)
    objTempData.ErrorScreen = strErrorScreen

def SetPageTitle(objHere, strPageTitle):
    objTempData = GetTempData(objHere)
    objTempData.PageTitle = strPageTitle

def GetPageTitle(objHere):
    objTempData = GetTempData(objHere)
    return objTempData.PageTitle

def RemoveTempData(objHere):
    strId = GetThreadId()
    objFolder = GetDataFolder(objHere, 'E3SessionData')
    objFolder._delObject(strId)
    return 'Done'

def GetTempData(objHere):
    return GetDataFolder(objHere, 'E3SessionData').unrestrictedTraverse(GetThreadId())

def GetUsername(objHere):
    return GetTempData(objHere).Username

def GetErrorScreen(objHere):
    return GetTempData(objHere).ErrorScreen

def IsLoggedIn(objHere):
    if GetUsername(objHere):
        return True
    return False

def SetMessage(objHere, strErrorMessage = '', strPlainMessage = ''):
    strId = GetThreadId()
    objTempData = GetTempData(objHere)
    if strErrorMessage:
        if objTempData.ErrorMessage:
            objTempData.ErrorMessage += "<br>\n"
        objTempData.ErrorMessage += strErrorMessage
    if strPlainMessage:
        if objTempData.PlainMessage:
            objTempData.PlainMessage += "<br>\n"
        objTempData.PlainMessage += strPlainMessage

def GetMessages(objHere):
    strId = GetThreadId()
    objTempData = GetTempData(objHere)
    if objTempData.ErrorMessage:
        return (objTempData.ErrorMessage, "")
    else:
        return ("", objTempData.PlainMessage)
