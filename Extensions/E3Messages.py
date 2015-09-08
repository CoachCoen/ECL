# encoding: utf-8

"""Functions related to list messages, including functions to display messages"""

import datetime
import math

from libDatabase import GetDataFolder
from libDatabase import SearchOne
from libGeneral import GetParameter
from libBuildHTML import GetDateDropdown
from libBuildHTML import GetMonthDropdown
from libBuildHTML import GetYearDropdown
from libBuildHTML import IsPlural
from libBuildHTML import BuildPagingList
from libConstants import cnShortDateFormat
from E3TempData import IsLoggedIn
from E3Members import IsFullMember
from libDatabase import GetDOD
from email.Header import decode_header
from libString import ClearSubjectHeader
from libString import ToUnicode

def PageTitleForMessage(objHere):
    strThreadId = GetParameter(objHere.REQUEST, "ThreadId")
    if strThreadId:
        objMessage = SearchOne(objHere, 'E3Messages', 'id', strThreadId)
    else:
        objMessage = None

    strTitle = "Discussion List Message"
    if objMessage:
        if not objMessage.Private or IsFullMember(objHere):
            strTitle = "Message: %s" % ClearSubjectHeader(objMessage.mailSubject)

    return strTitle

def ChangeMonthCount(objHere, intYear, intMonth, intIncrease = 1, blnPublicCount = False):
    objE3Messages = GetDataFolder(objHere, 'E3Messages')
    if blnPublicCount:
        lstMessageCount = objE3Messages.PublicMessageCount
    else:
        lstMessageCount = objE3Messages.MessageCount
    blnFound = False
    lstResult = []
    for strYearLine in lstMessageCount:
        if not blnFound and strYearLine[:4] == str(intYear):
            blnFound = True
            lstCounts = strYearLine.split()
            lstCounts[intMonth] = str(int(lstCounts[intMonth]) + intIncrease)
            strYearLine = " ".join(lstCounts)
        lstResult.append(strYearLine)
    if not blnFound:
        lstCounts = []
        for intI in range(0, 13):
            lstCounts.append("0")
        lstCounts[intMonth] = str(intIncrease)
        lstCounts[0] = str(intYear)
        lstResult.append(" ".join(lstCounts))
    if blnPublicCount:
        objE3Messages.PublicMessageCount = lstResult
    else:
        objE3Messages.MessageCount = lstResult

def GetWhen(objRequest):
    strMonth = GetParameter(objRequest, 'Month')
    strYear = GetParameter(objRequest, 'Year')
    strDate = GetParameter(objRequest, 'Date')

    if strMonth and strYear and strMonth.isdigit() and strYear.isdigit():
        intMonth = int(strMonth)
        intYear = int(strYear)
        if strDate:
            intDate = int(strDate)
        else:
            intDate = 0
    else:
        intMonth = 0
        intYear = 0
        intDate = 0
    return (intYear, intMonth, intDate)

def GetOffset(objRequest):
    strOffset = GetParameter(objRequest, 'Offset')
    if strOffset:
        intOffset = int(strOffset)
    else:
        intOffset = 0
    return intOffset

def SelectDateForm(strTitle, intYear = 0, intMonth = 0, intDate = 0):
    strResult = """
                <form id="form1" name="form1" method="post" action="/Archive/ViewMonth">
                    <fieldset>
                        <legend>%(Title)s</legend>
                        <p>Choose month %(MonthDropdown)s %(YearDropdown)s
                        %(SelectDate)s
                        <input type="submit" name="Submit" value="Go" class="btn"/></p>
                    </fieldset>
                </form>"""

    strMonthDropdown = GetMonthDropdown(intMonth)
    strYearDropdown = GetYearDropdown(intYear)

    if intMonth:
        strDateDropdown = GetDateDropdown(intYear, intMonth, intDate)
        strSelectDate = """<br>Choose a specific date %s""" % strDateDropdown
    else:
        strSelectDate = ""

    strResult = strResult % {'MonthDropdown': strMonthDropdown,
                            'YearDropdown': strYearDropdown,
                            'SelectDate': strSelectDate,
                            'Title': strTitle}
    return strResult

def ViewMonthPageContents(objHere, objRequest):
    """Generate contents of /Archive/ViewMonth"""
    blnFullMember = IsFullMember(objHere)
    strResult = """%(Intro)s<form action="/Archive/ViewSearchResults" method="post">
                    <fieldset>
                        <legend>Search the archive</legend>
                        <p><label>Search for</label>
                            <input type="text" name="SearchBoth" class="txt"/>
                        <input name="Input" type="submit" value="Search" />	                    </p>

						<p>%(AdvancedSearch)s</p>
                    </fieldset>
			    </form>"""

    if blnFullMember:
        strIntro = ""
        strAdvancedSearch = """Or go to the <a href="/Archive/AdvancedSearch">advanced search form</a>"""
    else:
        strIntro = """<p>Non list members only get limited access to the archive. Some message are private and can only be read by list members. Public messages can be read by anyone. Membership is free for the first 3 months. <a href="/Membership">Join Now</a></p>"""
        strAdvancedSearch = "(List members also get access to an advanced search facility)"

    strResult = strResult % {'AdvancedSearch': strAdvancedSearch,
                            'Intro': strIntro}

    (intYear, intMonth, intDate) = GetWhen(objRequest)
    intOffset = GetOffset(objRequest)

    if intMonth:
        strDateDropdown = GetDateDropdown(intYear, intMonth, intDate)
        strMonthList = GetListForMonth(objHere, intYear, intMonth, intDate, intOffset)
        strSelectDate = """<p>Choose a specific date %s</p>""" % strDateDropdown
    else:
        strSelectDate = ""
        strMonthList = """<p>No month or year selected</p>"""

    strResult += SelectDateForm("Change your selection", intYear, intMonth, intDate)

    if intMonth:
        strMonthList = GetListForMonth(objHere, intYear, intMonth, intDate, intOffset)
    else:
        strMonthList = """<p>No month or year selected</p>"""

    strResult += """<p>&nbsp;</p>%s""" % strMonthList

    return strResult

def GetSenderIdentification(objMessage, blnFullMember, blnWithLink = True):
    # Order to show this in:
    # if user exists:
        # Name, if filled in
        # Username, if no @ in username or if blnFullMember
        # Blank, otherwise
    # Blank, otherwise
    objMember = SearchOne(objMessage, "E3Member", "id", objMessage.UserId)
    strResult = ""
    if objMember:
        if objMember.Name and objMember.Name <> 'Unknown':
            strResult = objMember.Name
        if not strResult:
            if objMember.ShowFullName == 'Showtoall':
                strResult = objMember.FullName
            elif objMember.ShowFullName == 'Members' and blnFullMember:
                strResult = objMember.FullName
        if not strResult and objMember.Username:
            if (not '@' in objMember.Username or blnFullMember) and not 'E3Member' in objMember.Username:
                strResult = objMember.Username
        if blnFullMember and not strResult:
            strResult = ClearSender(objMessage.mailFrom)
    if strResult:
        if blnWithLink:
            return """<a href="/Members/ViewProfile?MemberId=%s">%s</a>""" % (objMember.id, strResult)
        else:
            return strResult
    return "(anonymous)"

def FormatOneThread(objThread, blnEvenRow, blnFullMember):
    """Show one thread in nicely formatted HTML, in row format"""
    if blnEvenRow:
        intBoxId = 'MessageBox1'
    else:
        intBoxId = 'MessageBox2'

    strSender = GetSenderIdentification(objThread, blnFullMember, False)
    strSender = ToUnicode(strSender)
#    strSender = ClearSender(objThread.mailFrom)

    strMessageTime = objThread.mailDate.strftime(cnShortDateFormat + " %H:%M")
    intReplyCount = len(objThread.objectValues('Folder'))
    if intReplyCount == 0:
        strReplyCount = ""
    elif intReplyCount == 1:
        strReplyCount = " (1 reply)"
    else:
        strReplyCount = " (%s replies)" % intReplyCount

    intMonth = objThread.mailDate.month()
    intYear = objThread.mailDate.year()
    intThreadId = objThread.id

    strSubjectHeader = ClearSubjectHeader(objThread.mailSubject)
    strSubjectHeader = ToUnicode(strSubjectHeader)

    strLink = "/Archive/ViewThread?Year=%s&Month=%s&ThreadId=%s" % (intYear, intMonth, intThreadId)
    strResult = """<a href="%(Link)s"><div id="%(BoxId)s">
					<p>%(MessageTime)s by %(Sender)s%(ReplyCount)s</p>
					<p>%(SubjectHeader)s</p>
				</div></a>
""" % {'MessageTime': strMessageTime,
        'ReplyCount': strReplyCount,
        'SubjectHeader': strSubjectHeader,
        'Link': strLink,
        'Sender': strSender,
        'BoxId': intBoxId}
    return strResult

def GetListForMonth(objHere, intYear, intMonth, intDate, intOffset, intMaxMessages = 20):
    """Get a list of messages, nicely formatted in row format,
        for the specified intYear/intMonth and optionally intDate"""
    blnFullMember = IsFullMember(objHere)
    strResult = ""
    objArchive = GetDataFolder(objHere, 'E3Messages')
    try:
        objMonth = objArchive.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
    except:
        return "<p>No messages found for this month</p>"

    dictThreads = {}
    intMessages = 0
    intPublicMessages = 0
    for objThread in objMonth.objectValues():
        if not intDate or objThread.mailDate.day() == intDate:
            intPublicMessages += 1
            if blnFullMember or not objThread.Private:
                dictThreads[objThread.mailDate] = objThread
        for objMessage in objThread.objectValues('Folder'):
            if not intDate or objMessage.mailDate.day() == intDate:
                intPublicMessages += 1
                if blnFullMember or not objMessage.Private:
                    dictThreads[objThread.mailDate] = objMessage

    strURL = '/Archive/ViewMonth'
    intThreads = len(dictThreads)
#    intThreads = len(dictThreads.keys())
    if blnFullMember:
        strPublic = ""
    else:
        strPublic = " public "
    if intThreads == 0:
        return """<p class="Message">No %s messages found</p>""" % strPublic
#    if not intDate:
#        intMessages = MessageCountForMonth(objHere, intYear, intMonth)
    intFirstThread = intOffset + 1
    intLastThread = intOffset + intMaxMessages
    if intLastThread > intThreads:
        intLastThread = intThreads
#    strNavigation = """<p>%(Messages)s message%(MessagesPlural)s found in %(Threads)s thread%(ThreadsPlural)s""" % {'Messages': intMessages,
#            'MessagesPlural': IsPlural(intMessages),
#            'Threads': intThreads,
#            'ThreadsPlural': IsPlural(intThreads)}

    strNavigation = """<p>%(Messages)s %(Public)s message%(MessagesPlural)s found""" % {'Messages': intThreads,
        'MessagesPlural': IsPlural(intThreads),
        'Public': strPublic}

    if intMaxMessages < intThreads:
        strLink = strURL + "?Year=%s&Month=%s" % (intYear, intMonth)
        if intDate:
            strLink = strLink + "&Date=%s" % intDate
        strLink = strLink + "&Offset=%s"

        strNavigation = strNavigation + "<br />" + BuildPagingList(intMaxMessages, intThreads, intFirstThread, intLastThread, strLink, intOffset)

    strNavigation = strNavigation + "</p>"

    lstDates = dictThreads.keys()
    lstDates.sort()

    blnEvenRow = False
    for intI in range(intOffset, intOffset + intMaxMessages + 1):
        if intI < len(lstDates):
            strOneThread = FormatOneThread(dictThreads[lstDates[intI]], blnEvenRow, blnFullMember)
            strOneThread = ToUnicode(strOneThread)
            strResult = strResult + strOneThread
            blnEvenRow = not blnEvenRow

    strResult = strNavigation + strResult + "<p>%s</p>" % strNavigation
    strResult = ToUnicode(strResult)
    return strResult

def CountAllMessages(objHere):
    """Counts number of messages by month/year, stores in E3Messages.MessageCount"""
    dtmNow = datetime.datetime.today()
    objMessages = GetDataFolder(objHere, 'E3Messages')
    lstLines = []
    for intYear in range(dtmNow.year, 1996, -1):
        strLine = str(intYear)
        for intMonth in range(1, 13):
            intCount = 0
            try:
                objMonth = objMessages.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
            except:
                objMonth = None
            if objMonth:
                for objThread in objMonth.objectValues():
                    intCount = intCount + 1 + len(objThread.objectValues('Folder'))

            strLine = strLine + " " + str(intCount)
        lstLines.append(strLine)
    objMessages.MessageCount = lstLines

def CountPublicMessages(objHere):
    """Counts number of public messages by month/year, stores in E3Messages.PublicMessageCount"""
    dtmNow = datetime.datetime.today()
    objMessages = GetDataFolder(objHere, 'E3Messages')
    lstLines = []
    for intYear in range(dtmNow.year, 1996, -1):
        strLine = str(intYear)
        for intMonth in range(1, 13):
            intCount = 0
            try:
                objMonth = objMessages.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
            except:
                objMonth = None
            if objMonth:
                for objThread in objMonth.objectValues():
                    if not objThread.Private:
                        intCount += 1
                    for objMessage in objThread.objectValues('Folder'):
                        if not objMessage.Private:
                            intCount += 1

            strLine = strLine + " " + str(intCount)
        lstLines.append(strLine)
    objMessages.PublicMessageCount = lstLines

def CountMessages(objHere):
    CountAllMessages(objHere)
    CountPublicMessages(objHere)

def MessageCountForMonth(objHere, intYear, intMonth):
    """Gets number of messages sent in intYear/intMonth"""
    lstCountList = GetDataFolder(objHere, 'E3Messages').MessageCount

    for strLine in lstCountList:
        lstCounts = strLine.split()
        if int(lstCounts[0]) == intYear:
            return int(lstCounts[intMonth])
    return 0

def CreateCountList(lstCountList):
    """Turn list of counts (messages by year/month) into a nice dictionary of lists
        for direct access to the counts"""
    dictResult = {}
    for intI in range(1990, 2050):
        dictResult[intI] = ("0 " * 12).split()
    for strLine in lstCountList:
        lstLine = strLine.split()
        dictResult[int(lstLine[0])] = lstLine[1:]
    return dictResult

def ArchiveCalendar(objHere):
    """Creates a calendar (list of month/year)
        complete with number of messages for each month/year
        plus links to page showing messages for that month/year"""
    blnFullMember = IsFullMember(objHere)

    strMonthList = """<th scope="col">&nbsp;</th>\n"""
    for strMonth in ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'):
        strMonthList = strMonthList + """<th scope="col">%s</th>\n""" % strMonth
    strHeader = "<tr>%s</tr>\n" % strMonthList

    lstCountList = GetDataFolder(objHere, 'E3Messages').MessageCount
    dictCountList = CreateCountList(lstCountList)
    dictPublicCountList = CreateCountList(GetDataFolder(objHere, 'E3Messages').PublicMessageCount)

    dtmNow = datetime.datetime.today()
    strRows = ""
    blnDark = True
    for intYear in range(dtmNow.year, 1998, -1):
        if blnDark:
            strBG = """bgcolor="#F0F0F0" """
            blnDark = False
        else:
            strBG = ""
            blnDark = True
        strRows = strRows + """<tr>
                        <th scope="row">%s</th>
        """ % (intYear)
        for intMonth in range(1, 13):
            intMessageCount = int(dictCountList[intYear][intMonth - 1])
            intPublicCount = int(dictPublicCountList[intYear][intMonth - 1])
            if intMessageCount or intPublicCount:
                if blnFullMember:
                    strContent = """<td align="right" bgcolor="#F0F0F0"><a href="/Archive/ViewMonth?Year=%s&Month=%s">%s</a></td>\n""" % (intYear, intMonth, intMessageCount)
                else:
                    strContent = """
<td align="right" bgcolor="#F0F0F0">
    <a href="/Archive/ViewMonth?Year=%s&Month=%s">%s</a><br>
    (%s)
</td>\n""" % (intYear, intMonth, intPublicCount, intMessageCount)
            else:
                strContent = """<td>&nbsp;</td>\n"""
            strRows = strRows + strContent
        strRows = strRows + "</tr>\n"

    strResult = """<table class="MonthList">%s</table>""" % (strHeader + strRows)
    return strResult

def GetDiscussionsForMonth(objMonth, blnFullMember):
    """Returns all discussions (not advert, at least 2 sub-messages)
        within the given month"""
    lstResult = []
    for objThread in objMonth.objectValues():
        if len(objThread.objectValues('Folder')) >= 2 and not 'adv' in objThread.mailSubject.lower() and (blnFullMember or not objThread.Private):
            lstResult.append(objThread)
    return lstResult

def GetMessagesForMonth(objMonth, blnFullMember):
    """Returns all messages (not advert, maximum of 1 sub-message)
        within the given month"""
    lstResult = []
    for objMessage in objMonth.objectValues():
        if len(objMessage.objectValues('Folder')) < 2 and not 'adv' in objMessage.mailSubject.lower()and (blnFullMember or not objMessage.Private):
            lstResult.append(objMessage)
    return lstResult

def GetAdvertsForMonth(objMonth, blnFullMember):
    """Returns all adverts within the given month"""
    lstResult = []
    for objMessage in objMonth.objectValues():
        if 'adv' in objMessage.mailSubject.lower() and (blnFullMember or not objMessage.Private):
            lstResult.append(objMessage)
    return lstResult

def ShortFormatMessage(objMessage):
    """Turns message into short format html chunk"""
    strSubject = ClearSubjectHeader(objMessage.mailSubject)
    strLink = "/Archive/ViewThread?Year=%s&Month=%s&ThreadId=%s" % (objMessage.mailDate.year(), objMessage.mailDate.month(), objMessage.id)
    return """<li><a href="%s">%s</a></li>""" % (strLink, strSubject)

def ReverseSort(varA, varB):
    """Returns true if varB comes before varA, used for sorted in reverse order"""
    return cmp(varB, varA)

def ListRecent(objHere, intCount, fnFunction, blnLongFormat = False):
    """Returns most <intCount> most recent messages, either
        - Discussion (not advert, at least 2 sub-messages)
        - Message (not advert, maximum 1 sub-message)
        - Advert
        Either in long format (used within the page contents) or
        in short format (used in side bar)"""
    # Any message which has at least 2 replies
#    if intCount > 3:
#        if not IsLoggedIn(objHere):
#            return "<p>Members only</p>"
#        if not IsFullMember(objHere):
#            return "<p>Current members only</p>"
    lstFound = []
    dtmNow = datetime.datetime.today()
    intMonth = dtmNow.month
    intYear = dtmNow.year
    objMessages = GetDataFolder(objHere, 'E3Messages')
    if not objMessages:
        return "Message folder not found"
    # They might not come out in order, so instead just grab whole month's worth of messages until at least enough, then sort
    if not blnLongFormat:
        blnFullMember = True
    else:
        blnFullMember = IsFullMember(objHere)
    while len(lstFound) < intCount * 3 and intYear > 1996:
        try:
            objMonth = objMessages.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
        except:
            objMonth = None
#            print "Not found", intYear, intMonth
        if objMonth:
            lstFound = lstFound + fnFunction(objMonth, blnFullMember)
        intMonth = intMonth - 1
        if intMonth == 0:
            intMonth = 12
            intYear = intYear - 1

    dictFound = {}
    for objThread in lstFound:
        dictFound[objThread.mailDate] = objThread

    lstDates = dictFound.keys()

    lstDates.sort(ReverseSort)

    intDone = 0
    if blnLongFormat:
        strResult = u""
    else:
        strResult = u"<ul>\n"

    blnEvenRow = False
    for dtmDate in lstDates:
        objThread = dictFound[dtmDate]
        if intDone < intCount:
            if blnLongFormat:
                strToAdd = FormatOneThread(objThread, blnEvenRow, blnFullMember)
                blnEvenRow = not blnEvenRow
            else:
                strToAdd = ShortFormatMessage(objThread)
            strToAdd = ToUnicode(strToAdd)
            strResult += strToAdd
        intDone = intDone + 1

    if not blnLongFormat:
        strResult = strResult + u"</ul>\n"

    strResult = ToUnicode(strResult)
    return strResult

def ListRecentDiscussions(objHere, intCount = 3, blnLongFormat = False):
    """Returns <intCount> most recent discussions"""
    return "<p>Not now</p>"
#    return ListRecent(objHere, intCount, GetDiscussionsForMonth, blnLongFormat)

def ListRecentMessages(objHere, intCount = 3, blnLongFormat = False):
    """Returns <intCount> most recent messages"""
    return ListRecent(objHere, intCount, GetMessagesForMonth, blnLongFormat)

def ListRecentAdverts(objHere, intCount = 3):
    """Returns <intCount> most recent adverts"""
    return ListRecent(objHere, intCount, GetAdvertsForMonth)

def CountPastMessages(objHere):
    """Returns total number of past messages"""
    lstCountList = GetDataFolder(objHere, 'E3Messages').MessageCount
    intResult = 0
    for strCount in lstCountList:
        lstCount = strCount.split()
        for strOne in lstCount[1:]:
            intResult = intResult + int(strOne)
    return intResult

def ClearSender(strSender):
    """Returns name part of mailSender
        i.e. either between double quotes
        or with < and > removed"""
    if '"' in strSender:
        strSender = strSender[strSender.find('"')+1:]
    if '"' in strSender:
        strSender = strSender[:strSender.find('"')]
    strSender = strSender.replace('<', '').replace('>', '')
    (strSender, strEncoding) = decode_header(strSender)[0]
    strSender = strSender.replace('"', '')
    return strSender

def MoveThreads(objHere):
    objMessages = GetDataFolder(objHere, 'E3Messages')
#    intDone = 0
    for objYear in objMessages.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            print
            print objMonth.id
            for objThread in objMonth.objectValues('Folder'):
                if objThread.objectValues('Folder'):
                    print objThread.title
                print "|",
                for objMessage in objThread.objectValues('Folder'):
                    strNewId = str(objMessage.id)
                    while strNewId in objMonth.objectIds():
                        strNewId = str(long(strNewId) + 1)
                    objMonth.manage_clone(objMessage, strNewId)
                    objThread.manage_delObjects(objMessage.id)
                    print "-",

def PurgeDay(objMonth, lstThreads):
    for objThread in lstThreads:
        if objThread.mailFrom <> 'ToDelete':
            for objThread2 in lstThreads:
                if objThread <> objThread2 and objThread2.mailFrom <> 'ToDelete':
                    if objThread2.mailDate == objThread.mailDate and objThread2.title == objThread.title and objThread2.mailSubject == objThread.mailSubject:
                        objThread2.mailFrom = 'ToDelete'
                        print objThread2.id, objThread2.title
    for objThread in lstThreads:
        if objThread.mailFrom == 'ToDelete':
            objMonth.manage_delObjects(objThread.id)


def PurgeMonth(objMonth):
    dictDates = {}
    for intDate in range(1, 32):
        dictDates[intDate] = []
    for objThread in objMonth.objectValues('Folder'):
        if objThread.objectValues('Folder'):
            print "Still has sub-messages: %s" % objThread.id
        else:
            dtmDate = objThread.mailDate
            intDate = dtmDate.day()
            dictDates[intDate].append(objThread)
    for intI in range(1, 32):
        PurgeDay(objMonth, dictDates[intI])

def RemoveDuplicates(objHere):
    objMessages = GetDataFolder(objHere, 'E3Messages')
    for objYear in objMessages.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            print objMonth.id
            PurgeMonth(objMonth)

