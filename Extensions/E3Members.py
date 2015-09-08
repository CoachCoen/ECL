# encoding: utf-8

"""Members related functions"""

from E3TempData import GetUsername
from libDatabase import SearchOne
from libDatabase import GetDataFolder
from libGeneral import GetParameter
from libDatabase import SearchMany
from libConstants import cnShortDateFormat
from libConstants import cnLastZopeDate
import datetime
import random
from libString import ClearSubjectHeader
from libString import PrepareMessageText
from libString import RemoveHTMLCodes
from libString import ToUnicode

#def CompareNameWithFullName(objHere):
#    strResult = u""
#    objMembers = GetDataFolder(objHere, 'E3Member')
#    for objBatch in objMembers.objectValues('Folder'):
#        for objMember in objBatch.objectValues('E3Member'):
#            if objMember.Name <> "Name unknown" and objMember.FullName and objMember.Name and objMember.FullName <> objMember.Name:
#                strResult += "<p>%s - %s</p>" % (ToUnicode(objMember.Name), ToUnicode(objMember.FullName))
#    return strResult

def CreateEventFolders(objHere):
    intAdded = 0
    intAll = 0
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            intAll += 1
            if not 'Events' in objMember.objectIds():
                objMember.manage_addFolder('Events')
                intAdded += 1
    return """
<p>Done</p>
<p>Total: %s</p>
<p>Folders added: %s</p>""" % (intAll, intAdded)

def UsernameInUse(objMember, strUsername):
    # Check that no one uses the same username, even if they have a different case (upper/lower/etc)
    # For this we have to go through all users
#    print "Username: ", strUsername
    strUsername = strUsername.lower()
    objMembers = GetDataFolder(objMember, "E3Member")
    for objBatch in objMembers.objectValues("Folder"):
        for objCheckMember in objBatch.objectValues("E3Member"):
#            print type(objCheckMember.Username), type(strUsername)

            if objCheckMember <> objMember and objCheckMember.Username.lower() == strUsername:
                return True
    return False

def ShowFeaturedMember(objHere, blnForHomePage = False):
    lstIntroThreads = SearchMany(objHere, "E3Thread", "TopicId", "E3Topic00336")
    lstPublicThreads = []
    for objThread in lstIntroThreads:
        lstOneSet = []
        lstMessages = SearchMany(objHere, "E3Messages", "ThreadId", objThread.id)
        dictMessages = {}
        intPublicCount = 0
        for objMessage in lstMessages:
            dictMessages[objMessage.mailDate] = objMessage
            if not objMessage.Private:
                intPublicCount += 1

        lstDates = dictMessages.keys()
        if len(lstDates) > 0:
            lstDates.sort()

            objFirstMessage = dictMessages[lstDates[0]]
            blnFirstMessagePublic = not objFirstMessage.Private

            if intPublicCount > 0 and blnFirstMessagePublic:
                lstPublicThreads.append((objFirstMessage, objThread.id, intPublicCount > 1))

    # We've got the threads, now choose one at random
    (objFirstMessage, strThreadId, blnMultipleMessages) = random.choice(lstPublicThreads)

    # Show the first message in the thread

    strName = ClearSubjectHeader(objFirstMessage.mailSubject).replace("Introduction", "").replace("introduction", "").replace(":", "").strip()

    strText = objFirstMessage.mailBody.strip().decode('ascii', 'ignore')
    strText = RemoveHTMLCodes(strText)
    (blnShortened, strText) = PrepareMessageText(strText, 120, False)
    if blnShortened:
        strText += " (More...)"

    if blnMultipleMessages:
        strURL = "/Forum/ShowThread?ThreadId=%s" % strThreadId
    else:
        strURL = "/Archive/ViewThread?ThreadId=%s" % objFirstMessage.id

    strResult = """<a href="%s">
    <h2>%s</h2>
    <p>%s</p>
</a>
""" % (strURL, strName, strText)
    return strResult

def ExpirePast2Months(objHere):
    print "Obsolete function called: ExpirePast2Months"

def NumberOfListMembers(objHere):
    """Return number of current members
        i.e. all MCIMember objects which are Live()"""
    return GetDataFolder(objHere, 'E3Member').MembersCount

def GetCurrentMember(objHere):
    """Return current member"""
    strUsername = GetUsername(objHere)
    if strUsername:
        return SearchOne(objHere, 'E3Member', 'Username', strUsername)
    return None

def IsFullMember(objHere):
    objMember = GetCurrentMember(objHere)
    if objMember and objMember.MembershipType == 'Full':
        return True
    return False

def GetMemberForId(objHere, strMemberId):
    objMembers = GetDataFolder(objHere, 'E3Member')
    strBatchId = strMemberId[8:11]
    try:
        return objMembers.unrestrictedTraverse('Batch%s/%s' % (strBatchId, strMemberId))
    except:
        return None

def CountMembers(objHere):
    intResult = 0
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.Live() and not objMember.ParkingMember():
                intResult = intResult + 1
    objData = GetDataFolder(objHere, 'E3Data')
    objData.MembersCount = intResult

def ManagerLoggedIn(objHere):
    objMember = GetCurrentMember(objHere)
    if objMember:
        return objMember.Manager
    return False

def MergeResultLists(lstMembersByUsername, lstMembersByName, lstMembersByEmailAddress):
    lstResult = []
    for objMember in lstMembersByUsername + lstMembersByName:
        if not objMember in lstResult:
            lstResult.append(objMember)

    for objEmailAddress in lstMembersByEmailAddress:
        objMember = objEmailAddress.unrestrictedTraverse('..')
        if not objMember in lstResult:
            lstResult.append(objMember)

    return lstResult

def ExtensiveMembersSearch(objHere, strSearchFor):
    lstResult = []
    strSearchFor = strSearchFor.lower()
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.ContainsString(strSearchFor):
                lstResult.append(objMember)
    return lstResult

def ListMembersForManager(objHere):
    strSearchFor = GetParameter(objHere.REQUEST, 'SearchFor')
    strExtensiveSearch = GetParameter(objHere.REQUEST, 'ExtensiveSearch')
    blnExtensiveSearch = (strExtensiveSearch == 'Yes')
#    if blnExtensiveSearch:
#        print "Extensive please"
    if not strSearchFor:
        return "No search string specified"
    if blnExtensiveSearch:
        lstResult = ExtensiveMembersSearch(objHere, strSearchFor)
    else:
        lstMembersByUsername = SearchMany(objHere, 'E3Member', 'Username', strSearchFor)
        lstMembersByName = SearchMany(objHere, 'E3Member', 'Name', strSearchFor)
        lstMembersByEmailAddress = SearchMany(objHere, 'E3EmailAddress', 'EmailAddress', strSearchFor)
        lstResult = MergeResultLists(lstMembersByUsername, lstMembersByName, lstMembersByEmailAddress)

    if not lstResult:
        return "No one found for %s" % strSearchFor

    strMembers = ""
    for objMember in lstResult:
        strMembers += """<p><a href="/MyECL?MemberId=%s">%s, %s, %s, %s</a><br>%s</p>""" % (objMember.id, objMember.Username, objMember.Name, objMember.MembershipType, objMember.GetNextExpiryDate(), objMember.ListEmailAddresses())

    strResult = "<h2>Members for %s</h2>%s" % (strSearchFor, strMembers)

#    strResult = ToUnicode(strResult)

    return strResult

#def ToUnicode(strHTML):
#    strResult = strHTML.encode('iso-8859-1', 'replace')
#    return strResult


