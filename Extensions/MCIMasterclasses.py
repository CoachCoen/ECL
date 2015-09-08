import datetime
import DateTime

from libDatabase import GetDataFolder
from libDatabase import SearchOne
from libGeneral import GetParameter

from libConstants import cnMCIRoot

def ListPastMasterclasses(objHere):
    objMasterclasses = GetDataFolder(objHere, "MCIMasterclass")
    dictMasterclasses = {}
    for objMasterclass in objMasterclasses.objectValues('MCIMasterclass'):
        if objMasterclass.ClassDate <= DateTime.DateTime() and objMasterclass.ClassDate > DateTime.DateTime('1 Jan 2000') and objMasterclass.ReadyToPublish:
            dictMasterclasses[objMasterclass.ClassDate] = objMasterclass

    lstDates = dictMasterclasses.keys()
    lstDates.sort()

    strList = ""
    for dtmDate in lstDates:
        strList += dictMasterclasses[dtmDate].BlockForPastList()
    strResult = """<table width="100%%" border="0" cellspacing="0" cellpadding="5" class="TableWithBorder">
    <tr><td>
        <table width="100%%" border="0" cellspacing="0" cellpadding="0" class="MainText">
            %s
        </table>
    </td></tr>
</table>""" % strList
    strResult = unicode(strResult, 'ascii', 'replace')
    return strResult

def RecentMasterclasses(objClass1, objClass2):
    if objClass1.ClassDate > objClass2.ClassDate:
        return -1
    return 1

def ShowMasterclass(objHere):
    strId = GetParameter(objHere.REQUEST, 'Id')
    objMasterclass = SearchOne(objHere, 'MCIMasterclass', 'id', strId)
    if not objMasterclass:
        return """<p>This Masterclass does not exist. Please go back to the <a href="http://www.mcilocal.com/Masterclasses">list of Masterclasses</a></p>"""
    strResult = objMasterclass.ShowFullDetails()
    try:
        strResult = unicode(strResult, 'ISO-8859-1', 'replace')
    except:
        pass
    return strResult

def ShowMasterclassTitle(objHere):
    strId = GetParameter(objHere.REQUEST, 'Id')
    objMasterclass = SearchOne(objHere, 'MCIMasterclass', 'id', strId)
    if not objMasterclass:
        return "Unknown Masterclass"
    return objMasterclass.ClassTitle

def ShowMasterclassPresenters(objHere):
    strId = GetParameter(objHere.REQUEST, 'Id')
    objMasterclass = SearchOne(objHere, 'MCIMasterclass', 'id', strId)
    if not objMasterclass:
        return ""
    strResult = objMasterclass.PlainPresentersList()
    try:
        strResult = unicode(strResult, 'ISO-8859-1', 'replace')
    except:
        pass
    return strResult

def ListOneComingMasterclass(objComing):
    return """<li><a href="http://%s/Masterclasses/%s" target="_blank">%s</a></li>""" % (cnMCIRoot, objComing.id, objComing.ClassTitle)

def ListOneRecording(objPast):
    return """<li><a href="http://%s/Masterclasses/ShowMasterclass?Id=%s" target="_blank">%s</a></li>""" % (cnMCIRoot, objPast.id, objPast.ClassTitle)

def ListOneNotes(objPast):
    return """<li><a href="http://%s/Masterclasses/ShowMasterclass?Id=%s" target="_blank">%s</a></li>""" % (cnMCIRoot, objPast.id, objPast.ClassTitle)

def HasFutureMasterclasses(objHere):
    objMasterclasses = GetDataFolder(objHere, 'MCIMasterclass')
    dtmNow = datetime.datetime.today()
    for objMasterclass in objMasterclasses.objectValues('MCIMasterclass'):
        if not objMasterclass.Cancelled:
            dtmClassDate = datetime.datetime(year = objMasterclass.ClassDate.year(), month = objMasterclass.ClassDate.month(), day = objMasterclass.ClassDate.day())
            if dtmClassDate >= dtmNow:
                return True
    return False

def ECLMasterclassesSideBar(objHere):
    objMasterclasses = GetDataFolder(objHere, 'MCIMasterclass')
    dtmNow = datetime.datetime.today()
    lstComing = []
    lstPast = []
    for objMasterclass in objMasterclasses.objectValues('MCIMasterclass'):
        if not objMasterclass.Cancelled:
            dtmClassDate = datetime.datetime(year = objMasterclass.ClassDate.year(), month = objMasterclass.ClassDate.month(), day = objMasterclass.ClassDate.day())
            if dtmClassDate >= dtmNow:
                lstComing.append(objMasterclass)
            else:
                lstPast.append(objMasterclass)
    if lstComing:
        lstComing.sort(RecentMasterclasses)
        strComing = ""
        for objComing in lstComing:
            strComing = strComing + ListOneComingMasterclass(objComing)
        strComing = """<ul>
                        %s
                        </ul>""" % strComing
    else:
        strComing = """<p>By <a href = "http://www.MentorCoaches.com">Mentor Coaches International</a></p>"""
    intRecordings = 0
    strRecordings = ""
    intNotes = 0
    strNotes = ""
    lstPast.sort(RecentMasterclasses)
    for objPast in lstPast:
        if objPast.ClassRecording:
            if intRecordings < 3:
                strRecordings = strRecordings + ListOneRecording(objPast)
            intRecordings = intRecordings + 1
        if objPast.Notes:
            if intNotes < 3:
                strNotes = strNotes + ListOneNotes(objPast)
            intNotes = intNotes + 1
    strResult = """
				<h1>Masterclasses</h1>
                %(Coming)s
                <h2>Recordings</h2>
                <ul>
                %(Recordings)s
                </ul>
                <p><a href="http://%(Root)s/Masterclasses/Past" target="_blank">More ...</a></p>
                <h2>Notes</h2>
                <ul>
                %(Notes)s
                </ul>
                <p><a href="http://%(Root)s/Masterclasses/Past" target="_blank">More ...</a></p>
                """ % {'Coming': strComing,
                    'RecordingsCount': intRecordings,
                    'Recordings': strRecordings,
                    'NotesCount': intNotes,
                    'Notes': strNotes,
                    'Root': cnMCIRoot}
    return strResult

def CountMasterclassRecordings(objHere):
    return 0

def CountMasterclassNotes(objHere):
    return 0

def CountPastMasterclasses(objHere):
    return 0
