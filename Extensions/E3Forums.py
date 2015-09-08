from E3Messages import ClearSubjectHeader
from E3Members import GetCurrentMember
import datetime
from libDatabase import GetDataFolder
from types import *
from libDatabase import GetDOD
from libDatabase import SearchOne
from libDatabase import SearchMany
from libDatabase import Catalogue
from libDate import ShortMonthName
from libConstants import cnShortDateFormat
from libConstants import cnEmptyZopeDate
from libConstants import cnTopTopics
from E3Messages import CountPastMessages
from libGeneral import GetParameter
from E3TempData import SetMessage
from E3Messages import GetSenderIdentification
from E3Messages import ClearSubjectHeader
from E3Digest import PrepareMessageText
from E3Digest import ExtractName
from E3Members import ManagerLoggedIn
from E3HTML import UpdateCacheItem
from libString import ToUnicode
from E3Members import IsFullMember
from libBuildHTML import IsPlural
from libBuildHTML import InsertBrs

cnTextBlockLength = 500

strStyles = """
<STYLE>
    .MessageToBeDone, .MessageInProgress, .MessageDone {border-width: 1px; border-style: solid; padding: 2px; margin-bottom: 5px; width:600px; background-color: #F7F7F7; font-family: verdana, tahoma, arial; cursor:pointer;}

    .BlankSpace {display:inline; margin-right: 10px; float:left;}

    .MessageToBeDone, .MessageDone {font-size:12px;}

    .MessageToBeDone {border-color: #00E0E0;}

    .MessageDone {border-color: #000000; color: #808080}

    .MessageInProgress {border-color: #FF0000; font-size: 12px}

    .MessageArea {border: 1px solid #808080; width: 656px; padding: 3px; float:left; height: 750px; clip:auto; overflow: auto;}

    .MessageDate, .MessageSubject, .MessageText {display: inline}

    .MessageSubject {font-weight:bold}

    .TopicsArea, .OneTopic, .TopicHeader, .NewTopic, .TopicThreads {
        margin: 3px; margin-left: 10px;
        font-family: verdana, tahoma, arial;
        font-size: 12px;}

    .TopicsArea {width: 400px; float:left; border: 1px solid #808080;}

    .OneTopic {width: 100%}

    .TopicHeader {width:500px; cursor: pointer}

    .NewTopic {width: 250px; float: left;}

    .NewTopicWide {width: 400px; float: left;}

    .NewTopicButton {cursor: pointer}

    .TopicThreads {width: 100%; clear:both; max-height: 100px; overflow:auto;}

    .OneTopicThread {cursor:pointer;}

    .NavigationArea {clear:both}

    .MonthBox, .YearBox {border: 1px solid #808080; padding: 3px; float:left; margin: 5px}

    .YearBox {clear:both}

</STYLE>
"""

strScripts = """
<script type=text/javascript>
    var objCurrentMessage = null;
    var intNewTopic = 0;

    function SelectThisMessage(objMessage){
        SetMessageClasses();
        objMessage.className = "MessageInProgress";
        objCurrentMessage = objMessage;
    }

    function SetMessageClasses(){
        objMessageArea = document.getElementById('MessageArea');
        lstMessages = objMessageArea.childNodes;
        for (var intI=0; intI<lstMessages.length; intI++){
            objMessage = lstMessages[intI]
            if (objMessage.nodeName == 'DIV'){
                objMessage.className = "Message" + objMessage.getAttribute("status")
            }
        }
    }

    function SelectFirstMessage(){
        lstMessages = document.getElementById('MessageArea').childNodes;
        var intI = 0;
        while ((lstMessages[intI].nodeName!='DIV') || (lstMessages[intI].getAttribute("status")=="Done"))
            intI++
        SelectThisMessage(lstMessages[intI]);
    }

    function MarkMessageAsDone(objMessage){
        objMessage.setAttribute('status', 'Done')
        SetMessageClasses()
//        SelectFirstMessage()
    }

    function SetMessageTopic(objMessage, strTopic, intTopicId){
        lstChildren = objMessage.childNodes
        for (var intI=0; intI<lstChildren.length; intI++)
        {
            objSibling = lstChildren[intI];
            if (objSibling.nodeName=='INPUT')
                objSibling.value = intTopicId
            if (objSibling.className == 'MessageTopic')
                objSibling.firstChild.nodeValue = strTopic
        }
    }

    function GetMessageProperty(objMessage, strProperty){
        lstChildren = objMessage.childNodes
        for (var intI=0; intI<lstChildren.length; intI++)
        {
            objSibling = lstChildren[intI];
            if (objSibling.className == strProperty)
                return objSibling.firstChild.nodeValue
        }
    }

    function oldNewThreadForTopic(objTopic){
        SetMessageTopic(objCurrentMessage, objTopic.firstChild.nodeValue, objTopic.id)
        MarkMessageAsDone(objCurrentMessage)
    }

    function RemoveCrLf(strString)
    {
        intLength = strString.length
        strLastChar = strString.charAt(intLength - 1)
        if (strLastChar == "\\n")
            strString = strString.substr(0, intLength - 1)
        return strString
    }

    function ZopeNewThread(strTopicId, strSubject)
    {
        xhr = new XMLHttpRequest()
        xhr.open("post", "/XMLHttp/NewThread", false)
        xhr.setRequestHeader("TopicId", strTopicId)
        xhr.setRequestHeader("Subject", strSubject)
        xhr.send(null)
        strResult = RemoveCrLf(xhr.responseText)
        return strResult
    }

    function ZopeSetThreadId(strMessageId, strThreadId)
    {
        xhr = new XMLHttpRequest()
        xhr.open("post", "/XMLHttp/SetThreadId", false)
        xhr.setRequestHeader("MessageId", strMessageId)
        xhr.setRequestHeader("ThreadId", strThreadId)
        xhr.send(null)
    }

    function ZopeNewTopic(strTopic, strSubTopicOfTopicId)
    {
        xhr = new XMLHttpRequest()
        xhr.open("post", "/XMLHttp/NewTopic", false)
        xhr.setRequestHeader("Topic", strTopic)
        xhr.setRequestHeader("SubTopicOfTopicId", strSubTopicOfTopicId)
        xhr.send(null)
        strResult = RemoveCrLf(xhr.responseText)
        return strResult
    }

    function GetThreadBox(objTopic)
    {
        lstChildren = objTopic.childNodes
        for (var intI=0; intI<lstChildren.length; intI++)
        {
            objSibling = lstChildren[intI];
            if (objSibling.className == "TopicThreads")
                return objSibling
        }
        return 0
    }

    function AddMessageToThread(objThread)
    {
        // Zope: Assign current message to ThreadId
        strThreadId = objThread.id
        strMessageId = objCurrentMessage.id
        ZopeSetThreadId(strMessageId, strThreadId)
        strSubject = objThread.firstChild.nodeValue

        // Mark message with thread
        objTopicHeader = objThread.parentNode.parentNode.parentNode.childNodes[1]
        SetMessageTopic(objCurrentMessage, objTopicHeader.firstChild.nodeValue + ": " + strSubject)
        MarkMessageAsDone(objCurrentMessage)
    }

    function InsertBeforeSubTopics(objTopic, objBox)
    {
        lstChildren = objTopic.childNodes
        intFirstSubTopics = -1
        for (var intI=0; intI<lstChildren.length; intI++)
            if ((intFirstSubTopics == -1) && (lstChildren[intI].className=="OneTopic"))
                intFirstSubTopics = intI
        if (intFirstSubTopics == -1)
            objTopic.insertBefore(objBox, null)
        else
            objTopic.insertBefore(objBox, lstChildren[intFirstSubTopics])
    }

    function CreateThreadBox(objTopic)
    {
        var objList = document.createElement("ul")
        objList.className = "ThreadList"
        var objBox = document.createElement("div")
        objBox.className = "TopicThreads"
        objBox.appendChild(objList)
        InsertBeforeSubTopics(objTopic, objBox)
        return objBox
    }

    function AddThreadToThreadBox(objBox, strSubject, strThreadId)
    {
        var lstChildren = objBox.childNodes
        var objList
        for (var intI=0; intI<lstChildren.length; intI++)
            if (lstChildren[intI].className == 'ThreadList')
                objList = lstChildren[intI]
//        var objList = objBox.firstChild
        var objItem = document.createElement("li")
        objItem.className = "OneTopicThread"
        objItem.setAttribute("onClick", "AddMessageToThread(this)")
        objItem.id = strThreadId
        var strText = document.createTextNode(strSubject)
        objItem.appendChild(strText)
        objList.appendChild(objItem)
    }

    function NewThreadForTopic(objTopicHeader){
        objTopic = objTopicHeader.parentNode

        // Zope: Create a new thread for this topic, return ThreadId
        strSubject = GetMessageProperty(objCurrentMessage, "MessageSubject")
        strThreadId = ZopeNewThread(objTopic.id, strSubject)

        // Zope: Assign current message to new ThreadId
        strMessageId = objCurrentMessage.id
        ZopeSetThreadId(strMessageId, strThreadId)

        // If 1st thread against this topic, show thread box
        objBox = GetThreadBox(objTopic)
        if (objBox == 0)
            objBox = CreateThreadBox(objTopic)

        // Show thread in box
        AddThreadToThreadBox(objBox, strSubject, strThreadId)

        // Mark message as done
        SetMessageTopic(objCurrentMessage, objTopicHeader.firstChild.nodeValue + ": " + strSubject)
        MarkMessageAsDone(objCurrentMessage)
    }

    function GetTopicString(objNewTopicBox)
    {
        lstChildren = objNewTopicBox.parentNode.childNodes
        for (var intI=0; intI<lstChildren.length; intI++)
        {
            objSibling = lstChildren[intI]
            if (objSibling.className == "NewTopicInput")
                return objSibling.value
        }
        return ""
    }

    function NewSubTopic(objNewTopicBox)
    {
        strTopic = GetTopicString(objNewTopicBox)

        // If input box blank, pass
        if (strTopic == "")
            return

        // Add a new subtopic at the end of the OneTopic box which contains this button,
        // with subtopic as per the input box
        objOneTopicBox = objNewTopicBox
        while ((objOneTopicBox.className != "OneTopic") && (objOneTopicBox.className != "TopicsArea"))
            objOneTopicBox = objOneTopicBox.parentNode

        strTopicId = ZopeNewTopic(strTopic, objOneTopicBox.id)

        objNewTopic = document.createElement("div")
        objNewTopic.className = "OneTopic"
        objNewTopic.setAttribute("id", strTopicId)

        objNewTopic.innerHTML = '<div class="TopicHeader" onClick="NewThreadForTopic(this)">' + strTopic + '</div> \
                   <div class="NewTopic"> \
                       <input type="text" class="NewTopicInput"> \
                       <input type="button"  onClick = "NewSubTopic(this)" value="New" class="NewTopicButton"> \
                   </div>'

       objOneTopicBox.appendChild(objNewTopic)



    }

    window.onload = function(){
        SetMessageClasses();
        SelectFirstMessage();
}

</script>
"""


def CreateInitialTopics(objHere):
    dodTopic = GetDOD(objHere, 'E3Topic')
    lstTopics = (('Discussions', 'disc'),
        ('Client situations', 'clnt sttns'),
        ('Building Your Coaching Practice', 'devt n mktg'),
        ('Training, Supervision and Mentoring for Coaches', 'tng, svsn, mntrng'))
    intOrder = 10
    for lstItem in lstTopics:
        objTopic = dodTopic.NewObject()
        objTopic.title = lstItem[0]
        objTopic.ShortTitle = lstItem[1]
        objTopic.Order = intOrder
        intOrder += 10
        for lstSubItem in lstItem[2:]:
            objSubTopic = dodTopic.NewObject(objTopic)
            objSubTopic.title = lstSubItem[0]
            objSubTopic.ShortTitle = lstSubItem[1]
            objSubTopic.Order = intOrder
            intOrder += 10
            Catalogue(objSubTopic)
        Catalogue(objTopic)

def ThreadsBlockForTopic(objTopic, intYear, intMonth):
#    return ""

    strTopicId = objTopic.id
    lstThreads = SearchMany(objTopic, "E3Thread", "TopicId", strTopicId)
    if not lstThreads:
        return ""
    strResult = """
<div class="TopicThreads">
    <ul class="ThreadList">
"""
    dictThreads = {}
    for objThread in lstThreads:
        dtmDate = objThread.GetLastMessageDate()
        intMonths = 12 * (intYear - dtmDate.year) + (intMonth - dtmDate.month)
        print intYear, dtmDate.year, intMonth, dtmDate.month, intMonths
        if intMonths <= 3:
            if not dictThreads.has_key(dtmDate):
                dictThreads[dtmDate] = []
            dictThreads[dtmDate].append(objThread)

    lstDates = dictThreads.keys()
    lstDates.sort()

    for dtmDate in lstDates:
        for objThread in dictThreads[dtmDate]:
            strResult += """<li onClick="AddMessageToThread(this)" class="OneTopicThread" id="%s">%s</li>\n""" % (objThread.id, objThread.Subject)

    strResult += "   </ul>\n</div>"
    return strResult

def OneTopicBlock(objTopic, intYear, intMonth):
    strThreads = ThreadsBlockForTopic(objTopic, intYear, intMonth)
    strOldTemplate =  """
<div class="OneTopic" id="%(Id)s">
                <div class="TopicHeader" onClick="NewThreadForTopic(this)">%(Topic)s</div>
                <div class="NewTopic">
                    <input type="text" class="NewTopicInput">
                    <input type="button"  onClick = "NewSubTopic(this)" value="New" class="NewTopicButton">
                </div>
                %(Threads)s
"""
    strTemplate =  """
<div class="OneTopic" id="%(Id)s">
                <div class="TopicHeader" onClick="NewThreadForTopic(this)">%(Topic)s</div>
                %(Threads)s
"""

    return strTemplate % {'Id': objTopic.id,
    'Topic': objTopic.title,
    'Threads': strThreads
}



def LoadTopics(objContainer):
    dictResult = {}
    for objTopic in objContainer.objectValues('E3Topic'):
        if objTopic.title <> "Dummy":
            intOrder = objTopic.Order
            if not intOrder in dictResult.keys():
                dictResult[intOrder] = []
            dictResult[intOrder].append(objTopic)
    return dictResult

def CreateTopicsBlocks(objHere, intYear, intMonth):
    print "Create topics block for year = %s, month = %s" % (intYear, intMonth)
    # 2 levels only
    dictTopics = LoadTopics(GetDataFolder(objHere, "E3Topic"))
    lstOrder = dictTopics.keys()
    lstOrder.sort()
    strResult1 = ""
    strResult2 = ""
    for intOrder in lstOrder:
        for objTopic in dictTopics[intOrder]:
            strOneTopic = OneTopicBlock(objTopic, intYear, intMonth)
            dictSubTopics = LoadTopics(objTopic)
            if dictSubTopics:
                lstSubOrder = dictSubTopics.keys()
                lstSubOrder.sort()
                for intSubOrder in lstSubOrder:
                    for objSubTopic in dictSubTopics[intSubOrder]:
                        strOneTopic += OneTopicBlock(objSubTopic, intYear, intMonth) + "</div>"
            strOneTopic += "</div>"
            if objTopic.id in ['E3Topic00330', 'E3Topic00333']:
                strResult1 += strOneTopic
            else:
                strResult2 += strOneTopic
    return (strResult1, strResult2)

def CreateTextBlock(objMessage):
    strDate = objMessage.mailDate.strftime("%d/%m/%y %H:%M")
    strSubject = ClearSubjectHeader(objMessage.mailSubject)
    strResult = "%s <b>%s</b>" % (strDate, strSubject)
    strBody = objMessage.mailBody.strip()
    strBody = strBody[:cnTextBlockLength - len(strResult)]
    strResult = strResult + " " + strBody
    return strResult

def IsAdvert(objMessage):
    if 'adv' in objMessage.mailSubject.lower():
        return True
    return False

def GetNextBatch(objHere, intYear, intMonth):
    # Find the next 100 messages to organise
    intMaxThreads = 30
    dtmNow = datetime.datetime.today()
    objMessages = GetDataFolder(objHere, 'E3Messages')
    dictResult = {}
    try:
        objMonth = objMessages.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
    except:
        objMonth = None
    intDone = 0
    intAdvert = 0
    intToDo = 0
    if objMonth:
        for objMessage in objMonth.objectValues():
            if objMessage.ThreadId:
                intDone += 1
            elif IsAdvert(objMessage):
                intAdvert += 1
            else:
                dictResult[objMessage.mailDate] = objMessage
                intToDo += 1
    return (dictResult, intDone, intAdvert, intToDo)

def OneMessageLine(objMessage):
    strTemplate = """
            <div id="%(MessageId)s" status="ToBeDone" onclick="SelectThisMessage(this)">
                <div class="MessageDate">%(Date)s</div>
                <div class="MessageSubject">%(Subject)s</div>
                <div class="MessageText">%(Body)s</div>
                <div class="MessageTopic">(unclassified)</div>
            </div>
"""

    strDate = objMessage.mailDate.strftime("%d/%m/%y %H:%M")
    strSubject = ClearSubjectHeader(objMessage.mailSubject)
    strMessageLine = "%s <b>%s</b>" % (strDate, strSubject)
    strBody = objMessage.mailBody.strip()
    strBody = strBody[:cnTextBlockLength - len(strSubject) - len(strDate)]
    strBody = strBody.decode('ascii', 'ignore') + "</b></i></a>"

    return strTemplate % {'MessageId': objMessage.id,
        'Date': strDate,
        'Subject': strSubject.decode('ascii', 'ignore'),
        'Body': strBody}

def ProcessForm(objHere):
    objForm = objHere.REQUEST.form
    for strKey in objForm.keys():
        if strKey[:8] == 'TopicFor' and objForm[strKey]:
            print "Value set for %s: %s" % (strKey, objForm[strKey])

def YearBox(intYear):
    return """<div class="YearBox">%s</div>""" % intYear

def MonthBox(intYear, intMonth):
    return """<a href="/admin/E3ForumIndexingScreen?Month=%s&Year=%s"><div class="MonthBox">%s</div></a>""" % (intMonth, intYear, ShortMonthName(intMonth))

def MonthBoxes():
    strResult = ""
    for intYear in range(2009, 2005, -1):
        strResult += YearBox(intYear)
        for intMonth in range(1, 13):
            strResult += MonthBox(intYear, intMonth)
    strResult += """<a href="/admin/E3ForumIndexingScreen?ToMove"><div class="YearBox">Messages to Move</div></a>"""
    return strResult

def GetMessagesForMonth(objHere, intYear, intMonth):
    (dictThreads, intDone, intAdverts, intToDo) = GetNextBatch(objHere, intYear, intMonth)
    lstDates = dictThreads.keys()
    lstDates.sort()
    strMessages = ""
    for dtmDate in lstDates:
        objMessage = dictThreads[dtmDate]
        strMessages += OneMessageLine(objMessage)
    return (strMessages, intDone, intAdverts, intToDo)

def GetMessagesToMove(objHere):
    lstMessages = objHere.unrestrictedTraverse('/Data/E3').ToMove
    strResult = ""
    print "To move: ", lstMessages
    for strMessageId in lstMessages:
        objMessage = SearchOne(objHere, "E3Messages", "id", strMessageId)
        if objMessage:
            strResult += OneMessageLine(objMessage)
        else:
            print "Message not found: %s" % strMessageId
    return (strResult, 0, 0, len(lstMessages))

def ForumIndexingScreen(objHere):
    objRequest = objHere.REQUEST
    if objRequest.has_key("ToMove"):
        (strMessages, intDone, intAdverts, intToDo) = GetMessagesToMove(objHere)
    else:
        strMonth = GetParameter(objRequest, "Month")
        strYear = GetParameter(objRequest, "Year")
        dtmNow = datetime.date.today()
        if strMonth:
            intMonth = int(strMonth)
        else:
            intMonth = dtmNow.month
        if strYear:
            intYear = int(strYear)
        else:
            intYear = dtmNow.year
        (strMessages, intDone, intAdverts, intToDo) = GetMessagesForMonth(objHere, intYear, intMonth)

    (strTopicsBlock1, strTopicsBlock2) = CreateTopicsBlocks(objHere, intYear, intMonth)
    strMonthBoxes = MonthBoxes()
#    strResult = strStyles + strScripts + """<form method="post" action="http://ecllocal.com:8080/Meta/ThreadingScreen">%s</form>""" % strMessages
    return """
%s
%s
<body>
    <form action = "#">
        <div class="MessageArea" id="MessageArea">
            %s
        </div>
        <div class="TopicsArea" id = "top">
            %s
        </div>
        <div class="TopicsArea" id = "top">
            %s
        </div>
        <div class="NavigationArea">
            <p>%s done, %s to do, %s adverts excluded</p>
            %s
        </div>
    </form>
</body>
""" % (strStyles, strScripts, strMessages, strTopicsBlock1, strTopicsBlock2, intDone, intToDo, intAdverts, strMonthBoxes)

def ProcessNewThread(objHere):
    objRequest = objHere.REQUEST
    strTopicId = objRequest["HTTP_TOPICID"]
    strSubject = objRequest["HTTP_SUBJECT"]
    print "ProcessNewThread, assigned to %s" % strTopicId
    dodThread = GetDOD(objHere, "E3Thread")
    objNewThread = dodThread.NewObject()
    objNewThread.TopicId = strTopicId
    objNewThread.Subject = strSubject
    Catalogue(objNewThread)
    return objNewThread.id

def ProcessSetThreadId(objHere):
    objRequest = objHere.REQUEST
    strMessageId = objRequest["HTTP_MESSAGEID"]
    strThreadId = objRequest["HTTP_THREADID"]
    print "ProcessSetThreadId for %s to %s" % (strMessageId, strThreadId)
    objMessage = SearchOne(objHere, "E3Messages", 'id', strMessageId)
    if not objMessage.hasProperty('ThreadId'):
        objMessage.manage_addProperty('ThreadId', '', 'string')
    objMessage.ThreadId = strThreadId
    objDataFolder = GetDataFolder(objHere, "E3Messages")
    objCatalogue = objDataFolder.Catalogue
    objCatalogue.catalog_object(objMessage)
    return ""

def ProcessNewTopic(objHere):
    print "ProcessNewTopic"
    objRequest = objHere.REQUEST
    strTopic = objRequest["HTTP_TOPIC"]
    strSubTopicOfTopicId = objRequest["HTTP_SUBTOPICOFTOPICID"]
    dodTopic = GetDOD(objHere, "E3Topic")
    if strSubTopicOfTopicId <> "Top":
        objParentTopic = SearchOne(objHere, "E3Topic", "id", strSubTopicOfTopicId)
        objNewTopic = dodTopic.NewObject(objParentTopic)
    else:
        objNewTopic = dodTopic.NewObject()
    objNewTopic.ShortTitle = strTopic
    objNewTopic.title = strTopic
    Catalogue(objNewTopic)
    return objNewTopic.id

def ClearThreadIds(objHere):
    objMessages = GetDataFolder(objHere, 'E3Messages')
    for objYear in objMessages.objectValues('Folder'):
        print objYear.id
        for objMonth in objYear.objectValues('Folder'):
            print objMonth.id
            for objMessage in objMonth.objectValues('Folder'):
                if not objMessage.hasProperty('OldThreadId'):
                    objMessage.manage_addProperty('OldThreadId', '', 'string')
                objMessage.OldThreadId = objMessage.ThreadId
                objMessage.ThreadId = ""

def AddSubjectProperties(objHere):
    objThreads = GetDataFolder(objHere, 'E3Thread')
    for objBatch in objThreads.objectValues('Folder'):
        for objThread in objBatch.objectValues('E3Thread'):
            if not objThread.hasProperty('Summary'):
                objThread.manage_addProperty('Summary', '', 'text')
            if not objThread.hasProperty('myFirstMessageDate'):
                objThread.manage_addProperty('myFirstMessageDate', cnEmptyZopeDate, 'date')
            if not objThread.hasProperty('myLastMessageDate'):
                objThread.manage_addProperty('myLastMessageDate', cnEmptyZopeDate, 'date')
            if not objThread.hasProperty('Publish'):
                objThread.manage_addProperty('Publish', False, 'boolean')

def FormatOneThread(objThread, intMessageCount):
    if intMessageCount == 0:
        return ""
    strSummary = objThread.Summary
#    if not strSummary:
#        strSummary = "Summary goes here in a little while, please"
    if not objThread.Publish:
        strUnpublished = "Unpublished:"
    else:
        strUnpublished = ""
#    strDate = objThread.GetLastMessageDate().strftime(cnShortDateFormat)
    return """
    <a href="/Forum/ShowThread?ThreadId=%s">
        %s
        <div class="ThreadSummaryBlock">
            <div class="ThreadSubject">%s</div>&nbsp;&nbsp;
            <div class="ThreadSummary">%s</div>
            <div class="ThreadStatistics">(%s&nbsp;msgs)</div>&nbsp;<div class="ThreadLink">More&nbsp;...</div>
        </div>
    </a>
""" % (objThread.id, strUnpublished, objThread.Subject, strSummary, intMessageCount)

def GetMessageCount(objHere, strThreadId):
    return len(SearchMany(objHere, "E3Messages", "ThreadId", strThreadId))

def GetThreadList(lstDates, dictThreads, blnManager, intLimitThreads, objHere, intMinMessages):
    strResult = ""
    intDone = 0
    for dtmDate in lstDates:
        for objThread in dictThreads[dtmDate]:
            if blnManager or objThread.Publish:
                intMessageCount = GetMessageCount(objHere, objThread.id)
                if (intDone < intLimitThreads and intMessageCount >= intMinMessages) or (not intLimitThreads and intMessageCount > 0) or (not intLimitThreads and blnManager):
                    strResult += FormatOneThread(objThread, intMessageCount)
                    intDone += 1
    return (intDone, strResult)

def GetThreadSummaries(objHere, lstTopicIds, intLimitThreads, intMinMessages, blnHomePage = False):
    if blnHomePage:
        blnManager = False
    else:
        blnManager = ManagerLoggedIn(objHere)

    dictThreads = {}

    for strTopicId in lstTopicIds:
        lstThreads = SearchMany(objHere, "E3Thread", "TopicId", strTopicId)
        for objThread in lstThreads:
            if not objThread.hasProperty("Deleted") or not objThread.Deleted:
                dtmDate = objThread.GetLastMessageDate()
                if not dictThreads.has_key(dtmDate):
                    dictThreads[dtmDate] = []
                dictThreads[dtmDate].append(objThread)

    lstDates = dictThreads.keys()
    lstDates.sort()
    lstDates.reverse()
    (intDone, strResult) = GetThreadList(lstDates, dictThreads, blnManager, intLimitThreads, objHere, intMinMessages)
    if not blnManager:
        while intDone < intLimitThreads and intMinMessages > 1:
            intMinMessages -= 1
            (intDone, strResult) = GetThreadList(lstDates, dictThreads, blnManager, intLimitThreads, objHere, intMinMessages)
    return strResult

def GetSubTopicIds(objTopic):
    lstResult = (objTopic.id, )
    for objSubTopic in objTopic.objectValues("E3Topic"):
        lstResult = lstResult + GetSubTopicIds(objSubTopic)
    return lstResult

def SubTopicCounts(objTopic):
    intThreads = 0
    intMessages = 0
    for objSubTopic in objTopic.objectValues('E3Topic'):
        (intThreadAdd, intMessageAdd) = SubTopicCounts(objSubTopic)
        intThreads += intThreadAdd + objSubTopic.ThreadCount
        intMessages += intMessageAdd + objSubTopic.MessageCount
    return (intThreads, intMessages)

def GetOneTopicSummary(objHere, strTopicId, blnWithChildren, intLimit, blnMainTopic = False, blnHomePage = False):
    objTopic = SearchOne(objHere, "E3Topic", "id", strTopicId)
    if not objTopic:
        return ""
    if blnWithChildren and not blnMainTopic:
        lstTopicIds = GetSubTopicIds(objTopic)
    else:
        lstTopicIds = (objTopic.id, )

    strThreads = GetThreadSummaries(objHere, lstTopicIds, intLimit, 5, blnHomePage)
    strSubTopics = ""
    intThreadCount = objTopic.ThreadCount
    intMessageCount = objTopic.MessageCount
    if blnMainTopic:
        strFullList = "&FullList"
    else:
        strFullList = ""
        for objSubTopic in objTopic.objectValues('E3Topic'):
            if blnWithChildren:
                (intThreadAdd, intMessageAdd) = SubTopicCounts(objSubTopic)
                intThreadCount += objSubTopic.ThreadCount + intThreadAdd
                intMessageCount += objSubTopic.MessageCount + intMessageAdd
            if strSubTopics:
                strSubTopics += " | "
            strSubTopics += """<a href = "/Forum/ShowTopic?TopicId=%s">%s</a> """ % (objSubTopic.id, objSubTopic.ShortTitle)
        if strSubTopics:
            strSubTopics = """<p class="SubTopics">%s</p>""" % strSubTopics
#    for objSubTopic in objTopic.objectValues('E3Topic'):
#        strThreads += GetThreadSummaries(objHere, (objSubTopic.id, ), False)
    if intThreadCount == 1:
        strThreadsPlural = ""
    else:
        strThreadsPlural = "s"
    return """
<div class="OneTopicBlock">
    <div class="TopicHeader">
        <a href="/Forum/ShowTopic?TopicId=%s%s" class="TopicTitle">%s</a>
        <div class="MessageCount">%s&nbsp;messages&nbsp;in&nbsp;%s&nbsp;thread%s</div>
        %s
    </div>
    %s
</div>""" % (objTopic.id, strFullList, objTopic.title, intMessageCount, intThreadCount, strThreadsPlural, strSubTopics, strThreads)

def GetDiscussions(objHere, lstTopicIds, strMainTopicId = "", blnHomePage = False):
    strResult = ""
    for strTopicId in lstTopicIds:
        strResult += GetOneTopicSummary(objHere, strTopicId, True, 5, strTopicId == strMainTopicId, blnHomePage)
    return strResult

def GetLongThreads(dictThreads, intMinMessages, intThreadsRequired, lstDates):
    lstResult = []
    for dtmDate in lstDates:
        for objThread in dictThreads[dtmDate]:
            intMessageCount = GetMessageCount(objThread, objThread.id)
            if intMessageCount > intMinMessages:
                lstResult.append(objThread)
                if len(lstResult) >= intThreadsRequired:
                    return lstResult
    return lstResult

def GetRecentThreads(objHere, intMinMessages, intThreadsRequired):
    dictThreads = {}
    objThreads = objHere.unrestrictedTraverse("/Data/E3/E3Threads")
    for objBatch in objThreads.objectValues("Folder"):
        for objThread in objBatch.objectValues("E3Thread"):
            if (not objThread.hasProperty("Deleted") or not objThread.Deleted) and objThread.Publish:
                dtmDate = objThread.GetLastMessageDate()
                if not dictThreads.has_key(dtmDate):
                    dictThreads[dtmDate] = []
                dictThreads[dtmDate].append(objThread)

    lstDates = dictThreads.keys()
    lstDates.sort()
    lstDates.reverse()

    return GetLongThreads(dictThreads, intMinMessages, intThreadsRequired, lstDates)

def ForumSummary(objHere):
    lstTopics = cnTopTopics
    strDiscussions = GetDiscussions(objHere, lstTopics, "", True)
    strResult = """
<fieldset>
    <legend>Recent list messages by discussion</legend>
    %s
</fieldset>
""" % strDiscussions
    return strResult

def FormatOneDiscussionForHomePage(objDiscussion):
    intMessageCount = GetMessageCount(objDiscussion, objDiscussion.id)
    strResult = """
    <a href="/Forum/ShowThread?ThreadId=%s" class="HomePageBlock">
        <div class="HomePageTitle">%s</div>
        <div class="HomePageSubtitle">(%s&nbsp;msgs)</div>
        <div class="HomePageText">%s</div>
    </a>""" % (objDiscussion.id, objDiscussion.Subject, intMessageCount, objDiscussion.Summary)
    return strResult

def ShowRecentDiscussions(objHere):
    strDiscussions = ""
    lstRecentDiscussions = GetRecentThreads(objHere, 5, 3)
    for objDiscussion in lstRecentDiscussions:
        strDiscussions += FormatOneDiscussionForHomePage(objDiscussion)
    strResult = """
<fieldset class="HomePage">
    <legend>Discussions</legend>
    %s
    <a href="/Archive" class="HomePageBlock">
       <div class="HomePageSubtitle">Show all discussions</div>
    </a>
</fieldset>""" % strDiscussions
    return strResult

def BestOfDiscussionsArea(objHere):
#    if ManagerLoggedIn(objHere):
#        lstTopics = ('E3Topic00330', 'E3Topic00324', 'E3Topic00333', 'E3Topic00320', 'E3Topic00329', 'E3Topic00340', 'E3Topic00338')
#    else:
    lstTopics = cnTopTopics
    strDiscussions = GetDiscussions(objHere, lstTopics, "", True)
    intMessageCount = CountPastMessages(objHere)

    strResult = """
    <p>A selection from %s messages sent by 2000+ members since 1999. More in the <a href="/Archive">list archive</a></p>
    %s""" % (intMessageCount, strDiscussions)
#    print strResult
    return strResult

def GetPageTitleForTopic(objHere):
    strTopicId = GetParameter(objHere.REQUEST, "TopicId")
    if not strTopicId:
        return ""

    objTopic = SearchOne(objHere, "E3Topic", "id", strTopicId)
    if not objTopic:
        return ""

    if objTopic.objectValues("E3Topic"):
        return objTopic.title
    else:
        return objTopic.unrestrictedTraverse("..").title

def GetPageTitleForThread(objHere):
    strThreadId = GetParameter(objHere.REQUEST, "ThreadId")
    if not strThreadId:
        return "No id"

    objThread = SearchOne(objHere, "E3Thread", "id", strThreadId)
    if not objThread:
        return "not found"

    return objThread.Subject

def ShowOneTopicPlusChildren(objTopic):
    strThreads = GetThreadSummaries(objTopic, (objTopic.id, ), True, 0, 3)
    strResult = """
<h2>%s</h2>
    %s""" % (objTopic.title, strThreads)

    for objSubTopic in objTopic.objectValues("E3Topic"):
        strResult += ShowOneTopicPlusChildren(objSubTopic)

    return strResult

def ShowTopic(objHere):
    strTopicId = GetParameter(objHere.REQUEST, "TopicId")
    if not strTopicId:
        return "No topic specified"
    objTopic = SearchOne(objHere, "E3Topic", "id", strTopicId)
    if not objTopic:
        return "This topic cannot be found"
#     return ShowOneTopicPlusChildren(objTopic)

    if objHere.REQUEST.has_key("FullList"):
        if not objTopic.hasProperty("FullTopicScreen") or not objTopic.FullTopicScreen:
            strResult = GetOneTopicSummary(objHere, strTopicId, False, 0)
            if objTopic.hasProperty("FullTopicScreen"):
                objTopic.FullTopicScreen = strResult
            else:
                objTopic.manage_addProperty("FullTopicScreen", strResult, "text")

        return objTopic.FullTopicScreen

    if not objTopic.hasProperty("TopicScreen") or not objTopic.TopicScreen:
        strResult = ""

        lstTopics = []
        for objSubTopic in objTopic.objectValues("E3Topic"):
            if objSubTopic.MessageCount > 0:
                lstTopics.append(objSubTopic.id)

        if lstTopics:
            lstTopics = [objTopic.id, ] + lstTopics
            strResult = GetDiscussions(objHere, lstTopics, objTopic.id)

        if not strResult:
            strResult = GetOneTopicSummary(objHere, strTopicId, False, 0)

        if objTopic.hasProperty("TopicScreen"):
            objTopic.TopicScreen = strResult
        else:
            objTopic.manage_addProperty("TopicScreen", strResult, "text")

    return objTopic.TopicScreen


def OrderTopics(objTopic):
    dictResult = {}
    for objSubTopic in objTopic.objectValues('E3Topic'):
        intOrder = objSubTopic.Order
        if not intOrder in dictResult.keys():
            dictResult[intOrder] = []
        dictResult[intOrder].append(objSubTopic)
    lstResult = dictResult.keys()
    lstResult.sort()
    return (lstResult, dictResult)

def FormatOneTopicsLeaf(objTopic, intLevel):
    if objTopic.ThreadCount > 0 or objTopic.objectValues("E3Topic"):
        if objTopic.id in cnTopTopics:
            strClass = "TopTopicsLeaf"
        else:
            strClass = "TopicsLeaf"
        return """<a href="/Forum/ShowTopic?TopicId=%s" class="%s">%s </a>""" % (objTopic.id, strClass, objTopic.ShortTitle)
    return ""

def TopicsBranch(objTopic, intLevel):
    (lstOrder, dictTopics) = OrderTopics(objTopic)
    strResult = ""
    for intOrder in lstOrder:
        for objSubTopic in dictTopics[intOrder]:
            if intLevel > 0 or objSubTopic.id in cnTopTopics:
                strResult += FormatOneTopicsLeaf(objSubTopic, intLevel) + TopicsBranch(objSubTopic, intLevel + 1)
    return strResult

def TopicsTree(objHere):
    objTopics = GetDataFolder(objHere, "E3Topic")
    return """
<style>
    #RightBox .TopicsLeaf {margin:0; padding:0; colour: green;}
</style>""" + TopicsBranch(objTopics, 0)

def MessageSummary(objMessage, blnManager):
    strTemplate = """
    <div class="SummaryBlock">
        <div class="SummaryBlockIndent">%(ClearLink)s
            <p>
                <a class="SummarySubject" href="/Archive/ViewThread?ThreadId=%(MessageId)s">%(Subject)s</a><br>
                Posted %(MessageDate)s by %(Sender)s
            </p>
            <p>%(MessageText)s</p>
            <a href="/Archive/ViewThread?ThreadId=%(MessageId)s" class="SummaryLink">
                <p class="SummaryShortened">%(Shortened)s Full Message</p>
            </a>
        </div>
    </div>
"""
    strDate = objMessage.mailDate.strftime("%d %b %Y, %H:%M")
    strText = objMessage.mailBody.strip().decode('ascii', 'ignore')
    strSubject = ClearSubjectHeader(objMessage.mailSubject).strip()
    strSender = GetSenderIdentification(objMessage, True)
    strName = ExtractName(objMessage.mailFrom)
    intMessageNumber = 1

    (blnShortened, strMessageText) = PrepareMessageText(strText)
    if blnShortened:
        strShortened = "(cut off after 500 words) ..."
    else:
        strShortened = ""

    if blnManager:
        strClearLink = """<p>
    <a href="http://ecllocal.com:8080/Meta/ClearThreadForMessage?MessageId=%s">Clear topic for thread</a>
    | <a href="http://ecllocal.com:8080/Meta/TagToMoveMessage?MessageId=%s">Move message</a>
</p>""" % (objMessage.id, objMessage.id)
    else:
        strClearLink = ""

    strTemplate = unicode(strTemplate, 'utf-8', 'replace')
    strResult = strTemplate % {'ClearLink': strClearLink,
            'MessageId': objMessage.id,
            'Subject': strSubject,
            'MessageDate': strDate,
            'MessageNumber': intMessageNumber,
            'Sender': strSender,
            'MessageText': strMessageText,
            'Shortened': strShortened}
#    strResult = strTemplate % {'ClearLink': strClearLink,
#            'MessageId': objMessage.id,
#            'Subject': strSubject.decode('ascii', 'ignore'),
#            'MessageDate': strDate,
#            'MessageNumber': intMessageNumber,
#            'Sender': strSender.decode('ascii', 'ignore'),
#            'MessageText': strMessageText.decode('ascii', 'ignore'),
#            'Shortened': strShortened}
#    try:
#        strResult = unicode(strResult, 'ascii', 'ignore')
#    except:
#        pass
    return strResult

def LoginOrJoinForm(objHere):
    return "You must be logged in"

def GetTopicOptions(objFolder, strSelectedId, intLevel):
    strResult = ""
    for objTopic in objFolder.objectValues("E3Topic"):
        if objTopic.title <> "Dummy":
            if objTopic.id == strSelectedId:
                strSelected = " selected "
            else:
                strSelected = ""
            strResult += """<option value="%s" %s>%s</option>\n""" % (objTopic.id, strSelected, ("." * (3 * intLevel)) + objTopic.title)
            strResult += GetTopicOptions(objTopic, strSelectedId, intLevel + 1)
    return strResult

def GetLoginBlock(intMessagesFound, intMessagesShown):
    strCount = "This discussion has %s message%s, of which %s message%s are public" % \
        (intMessagesFound, IsPlural(intMessagesFound), intMessagesShown, IsPlural(intMessagesShown))
    strResult = """
    <fieldset>
        <legend>Only public messages shown</legend>
        <p>%s</p>
        <p><b>To view all messages, login or join now</b>, using the form on the left-hand side of this webpage</p>
        <p>Your first three months are free, no need to enter any payment details now</p>
    </fieldset>""" % strCount
    return strResult

def ShowThread(objHere):

    blnFullMember = IsFullMember(objHere)

    strThreadId = GetParameter(objHere.REQUEST, "ThreadId")
    if not strThreadId:
        return "No discussion thread specified"
    objThread = SearchOne(objHere, "E3Thread", "id", strThreadId)
    if not objThread:
        return "This discussion thread cannot be found"


    strThread = objThread.Subject
    objTopic = SearchOne(objHere, "E3Topic", "id", objThread.TopicId)

    blnMaintenance = False
    if ManagerLoggedIn(objHere):
        strMaintenance = GetParameter(objHere.REQUEST, "Maintenance")
        if strMaintenance == "Yes":
            blnMaintenance = True

    #if objThread.hasProperty("ThreadScreen") and objThread.ThreadScreen and not blnMaintenance:
    #    return objThread.ThreadScreen

    strTopic = objTopic.title
    strForm = ""
    strSummary = ""
#    blnManager = False
    if blnMaintenance:
        if objThread.Publish:
            strPublishCheckBox = " checked "
        else:
            strPublishCheckBox = ""
        strFormURL = ""
        objTopics = GetDataFolder(objHere, "E3Topic")
        strOptions = GetTopicOptions(objTopics, objThread.TopicId, 0)
        strForm = """<form><fieldset>
    <p>Subject <input type="text" value="%s" name="ThreadSubject" size="70"></p>
    <p>Summary <textarea name="ThreadSummary" cols="40" style="font-size:12px">%s</textarea></p>
    <p>Publish <input type="checkbox" name="ThreadPublish" %s></p>
    <p>Topic <select name="TopicId">%s</select></p>
    <input type="hidden" name="Action" value="UpdateThread">
    <input type="hidden" name="ThreadId" value="%s">
    <p><input type="submit" value="Update Thread"></p>
</fieldset></form>""" % (ToUnicode(objThread.Subject), ToUnicode(objThread.Summary), strPublishCheckBox, strOptions, objThread.id)
    else:
        if objThread.Summary:
            strSummary = """
<fieldset>
    <legend>Summary</legend>
    <p>%s</p>
</fieldset>
""" % ToUnicode(InsertBrs(objThread.Summary))

    lstMessages = SearchMany(objHere, "E3Messages", "ThreadId", strThreadId)
    dictMessages = {}
    for objMessages in lstMessages:
        dictMessages[objMessages.mailDate] = objMessages

    lstDates = dictMessages.keys()
    lstDates.sort()

    intMessagesFound = len(lstDates)
    intMessagesShown = 0

    strMessages = ""
    for dtmDate in lstDates:
        objMessage = dictMessages[dtmDate]
        if blnFullMember or not objMessage.Private:
            intMessagesShown += 1
            strMessages += ToUnicode(MessageSummary(objMessage, blnMaintenance))

    if intMessagesShown < intMessagesFound:
        strLoginOrJoin = GetLoginBlock(intMessagesFound, intMessagesShown)
    else:
        strLoginOrJoin = ""

    strResult = """%s
<h2><a href="/Forum/ShowTopic?TopicId=%s">%s</a></h2>
    %s
    %s
    %s""" % (strForm, objThread.TopicId, strTopic, strSummary, strMessages, strLoginOrJoin)

    if not blnMaintenance and not objThread.hasProperty("ThreadScreen"):
        objThread.manage_addProperty("ThreadScreen", strResult, "text")
    return strResult

def ThreadMaintenance(objHere):
#    if not ManagerLoggedIn(objHere):
#        return "You need to be a manager to do this"
    strResult = "<ol>\n"
    for objBatch in objHere.unrestrictedTraverse("/Data/E3/E3Threads").objectValues("Folder"):
        for objThread in objBatch.objectValues("E3Thread"):
            if not objThread.Publish:
                strResult += """<li><a href="/Forum/ShowThread?ThreadId=%s&Maintenance=Yes">%s: %s</a></li>\n""" % (objThread.id, objThread.id, objThread.Subject)
    strResult += "</ol>\n"
    return strResult

def SetThreadDates(objHere):
    objThreads = GetDataFolder(objHere, 'E3Thread')
    for objBatch in objThreads.objectValues('Folder'):
        for objThread in objBatch.objectValues('E3Thread'):
            objThread.SetMessageDates()

def ClearThreadForMessage(objHere):
    strMessageId = GetParameter(objHere.REQUEST, "MessageId")
    if not strMessageId:
        return "<p>No message id specified</p>"

    objMessage = SearchOne(objHere, "E3Messages", "id", strMessageId)
    if not objMessage:
        return "<p>Message not found: %s</p>" % strMessageId

    objMessage.ThreadId = ""

    objDataFolder = GetDataFolder(objHere, "E3Messages")
    objCatalogue = objDataFolder.Catalogue
    objCatalogue.catalog_object(objMessage)
    return "<p>Thread cleared for this message</p>"

def XMLWriteObjectStart(fileExport, strObjectType):
    fileExport.write("""<object type="%s">\n""" % strObjectType)

def XMLWriteObjectEnd(fileExport):
    fileExport.write("</object>\n")

def XMLWriteString(fileExport, strName, strString):
    fileExport.write("""\t<string name="%s">%s</string>\n""" % (strName, strString))

def XMLWriteBoolean(fileExport, strName, blnBoolean):
    fileExport.write("""\t<boolean name="%s">%s</boolean>\n""" % (strName, blnBoolean))

def XMLWriteInteger(fileExport, strName, intInteger):
    fileExport.write("""\t<integer name="%s">%s</integer>\n""" % (strName, intInteger))

def XMLWriteStart(fileExport, strContents):
    fileExport.write("""<data export contents = "%s">\n""" % strContents)

def XMLWriteEnd(fileExport):
    fileExport.write("""</data export>\n\n""")

def ExportOneThread(objThread, fileExport):
    XMLWriteObjectStart(fileExport, "OneThread")
    XMLWriteString(fileExport, "id", objThread.id)
    XMLWriteString(fileExport, "TopicId", objThread.TopicId)
    XMLWriteString(fileExport, "Subject", objThread.Subject)
    XMLWriteBoolean(fileExport, "Publish", objThread.Publish)
    XMLWriteString(fileExport, "Summary", objThread.Summary)
    XMLWriteObjectEnd(fileExport)

def ExportOneMessage(objMessage, fileExport):
    XMLWriteObjectStart(fileExport, "OneMessage")
    XMLWriteString(fileExport, "id", objMessage.id)
    XMLWriteString(fileExport, "ThreadId", objMessage.ThreadId)
    XMLWriteObjectEnd(fileExport)

def ExportOneTopic(objTopic, fileExport, objParentTopic):
    XMLWriteObjectStart(fileExport, "OneTopic")
    XMLWriteString(fileExport, "id", objTopic.id)
    XMLWriteString(fileExport, "title", objTopic.title)
    XMLWriteInteger(fileExport, "Order", objTopic.Order)
    XMLWriteString(fileExport, "ShortTitle", objTopic.ShortTitle)
    if objParentTopic:
        XMLWriteString(fileExport, "Parent", objParentTopic.id)
    XMLWriteObjectEnd(fileExport)
    for objSubTopic in objTopic.objectValues("E3Topic"):
        ExportOneTopic(objSubTopic, fileExport, objTopic)

def ExportThreads(objHere, fileExport):
    XMLWriteStart(fileExport, "Threads")
    objDataFolder = GetDataFolder(objHere, "E3Thread")
    for objBatch in objDataFolder.objectValues("Folder"):
        for objThread in objBatch.objectValues("E3Thread"):
            ExportOneThread(objThread, fileExport)
    XMLWriteEnd(fileExport)

def ExportMessages(objHere, fileExport):
    XMLWriteStart(fileExport, "Messages")
    objDataFolder = GetDataFolder(objHere, "E3Thread")
    for objBatch in objDataFolder.objectValues("Folder"):
        for objThread in objBatch.objectValues("E3Thread"):
            lstMessages = SearchMany(objHere, "E3Messages", "ThreadId", objThread.id)
            for objMessage in lstMessages:
                ExportOneMessage(objMessage, fileExport)
    XMLWriteEnd(fileExport)

def ExportTopics(objHere, fileExport):
    XMLWriteStart(fileExport, "Topics")
    objDataFolder = GetDataFolder(objHere, "E3Topic")
    for objTopic in objDataFolder.objectValues("E3Topic"):
        ExportOneTopic(objTopic, fileExport, None)
    XMLWriteEnd(fileExport)

def ExportForums(objHere):
    fileExport = open("ForumsData.txt", "w")
    ExportThreads(objHere, fileExport)
    ExportMessages(objHere, fileExport)
    ExportTopics(objHere, fileExport)
    fileExport.close()

def ExtractValue(strObject, strPropertyName):
    strStart = """name="%s">""" % strPropertyName
    if not strStart in strObject:
        return ""
    intStart = strObject.find(strStart) + len(strStart)
    strProperty = strObject[intStart:]
    intEnd = strProperty.find("</")
    strProperty = strProperty[:intEnd]
    return strProperty

def ExtractOneObject(strData, strObjectType, dictProperties):
    strStart = """<object type="%s">""" % strObjectType
    intStart = strData.find(strStart) + len(strStart)
    strData = strData[intStart:]
    strEnd = """</object>"""
    intEnd = strData.find(strEnd)
    strObject = strData[:intEnd]
    strData = strData[intEnd + len(strEnd):]
    if not strStart in strData:
        strData = ""
    dictResult = {}
    for strProperty in dictProperties.keys():
        strPropertyType = dictProperties[strProperty]
        strValue = ExtractValue(strObject, strProperty)
#        print strProperty, strPropertyType, strValue
        if strPropertyType == "string":
            dictResult[strProperty] = strValue
        elif strPropertyType == "integer":
            dictResult[strProperty] = int(strValue)
        elif strPropertyType == "boolean":
            if strProperty:
                dictResult[strProperty] = True
            else:
                dictResult[strProperty] = False
    return (strData, dictResult)

def ImportThreads(objHere, strData):
    dodThread = GetDOD(objHere, "E3Thread")
    objCatalogue = GetDataFolder(objHere, "E3Thread").Catalogue
    strThreads = ExtractSection(strData, "Threads")
    dictThreads = {}
    while strThreads:
        (strThreads, dictProperties) = ExtractOneObject(strThreads,
 "OneThread",
    {'id': 'string', 'TopicId': 'string', 'Subject': 'string', 'Publish': 'boolean', 'Summary': 'string'})
        strId = dictProperties['id']
        objThread = SearchOne(objHere, "E3Thread", "id", strId)
        if objThread:
            print "Already in database: %s" % strId
        else:
            dictThreads[strId] = dictProperties

    lstIds = dictThreads.keys()
    lstIds.sort()

    for strId in lstIds:
        print "Creating new thread: %s" % strId

        dictProperties = dictThreads[strId]
        objThread = NewObjectForId(dodThread, strId)
        if objThread:
            objThread.TopicId = dictProperties['TopicId']
            objThread.Subject = dictProperties['Subject']
            objThread.Publish = dictProperties['Publish']
            objThread.Summary = dictProperties['Summary']
            objCatalogue.catalog_object(objThread)

def ImportMessages(objHere, strData):
    objCatalogue = GetDataFolder(objHere, "E3Messages").Catalogue
    strMessageInfo = ExtractSection(strData, "Messages")
    while strMessageInfo:
        (strMessageInfo, dictProperties) = ExtractOneObject(strMessageInfo, "OneMessage",
    {"id": "string", "ThreadId": "string"})
        strId = dictProperties['id']
        strThreadId = dictProperties['ThreadId']
        objMessage = SearchOne(objHere, "E3Messages", "id", strId)
        if not objMessage:
            print "Not found, message %s" % strId
        else:
            if objMessage.ThreadId == strThreadId:
                print "Already set, message %s, ThreadId %s" % (strId, strThreadId)
            else:
                objMessage.ThreadId = strThreadId
                objCatalogue.catalog_object(objMessage)
                print "Setting ThreadId to %s for message %s" % (strThreadId, strId)

def ExtractSection(strData, strSectionName):
    strStart = """<data export contents = "%s">""" % strSectionName
    intStart = strData.find(strStart)
    if intStart < 0:
        print "Section not found: %s" % strSectionName
        return ""
    strResult = strData[intStart:]
    strEnd = "</data export>"
    intEnd = strResult.find(strEnd)
    strResult = strResult[:intEnd]
    return strResult

def NewObjectForId(dodDefinition, strId, objParent = None):
    objResult = None
    while not objResult or objResult.id < strId:
        objResult = dodDefinition.NewObject(objParent)
        if objResult.id > strId:
            print "Id already set to %s whilst trying to create object %s" % (objResult.id, strId)
            return None
        elif objResult.id < strId:
            objResult.title = "Dummy"
    return objResult

def ImportTopics(objHere, strData):
    dodTopic = GetDOD(objHere, "E3Topic")
    strTopics = ExtractSection(strData, "Topics")
    objCatalogue = GetDataFolder(objHere, "E3Topic").Catalogue
    dictTopics = {}
    while strTopics:
        (strTopics, dictProperties) = ExtractOneObject(strTopics,
    "OneTopic",
    {"id": "string", "title": "string", "Order": "integer", "ShortTitle": "string", "Parent": "string"})
        strId = dictProperties['id']
        objTopic = SearchOne(objHere, "E3Topic", "id", strId)
        if objTopic:
            print "Already in database: %s" % strId
        else:
            dictTopics[strId] = dictProperties

    lstIds = dictTopics.keys()
    lstIds.sort()

    for strId in lstIds:
        dictProperties = dictTopics[strId]
        strParentId = dictProperties['Parent']
        if strParentId:
            objParentTopic = SearchOne(objHere, "E3Topic", "id", strParentId)
            if not objParentTopic:
                print "Parent not found: %s" % strParentId
            objTopic = NewObjectForId(dodTopic, strId, objParentTopic)
        else:
            objTopic = NewObjectForId(dodTopic, strId)
        if objTopic:
            print "Creating new topic: %s" % strId
            objTopic.title = dictProperties['title']
            objTopic.Order = dictProperties['Order']
            objTopic.ShortTitle = dictProperties['ShortTitle']
            objCatalogue.catalog_object(objTopic)

def ImportForums(objHere):
    fileImport = open("ForumsData.txt")
    strData = fileImport.read()
    fileImport.close()
    ImportThreads(objHere, strData)
    ImportMessages(objHere, strData)
    ImportTopics(objHere, strData)
    SetThreadDates(objHere)

def TagToMoveMessage(objHere):
    strMessageId = GetParameter(objHere.REQUEST, "MessageId")
    if not strMessageId:
        return "<p>No message id specified</p>"

    objMessage = SearchOne(objHere, "E3Messages", "id", strMessageId)
    if not objMessage:
        return "<p>Message not found: %s</p>" % strMessageId

    objData = objHere.unrestrictedTraverse('/Data/E3')
    objData.ToMove = objData.ToMove + (strMessageId, )

    return "<p>Message marked to be moved</p>"

def GetOneTopicStatistics(objTopics):
    for objTopic in objTopics.objectValues("E3Topic"):
        GetOneTopicStatistics(objTopic)
        lstThreads = SearchMany(objTopics, "E3Thread", "TopicId", objTopic.id)
        intThreads = len(lstThreads)
        intMessages = 0
        for objThread in lstThreads:
            intMessages += len(SearchMany(objTopics, "E3Messages", "ThreadId", objThread.id))
        if not objTopic.hasProperty("ThreadCount"):
            objTopic.manage_addProperty("ThreadCount", 0, "int")

        if not objTopic.hasProperty("MessageCount"):
            objTopic.manage_addProperty('MessageCount', 0, 'int')

        objTopic.ThreadCount = intThreads
        objTopic.MessageCount = intMessages

def GetTopicStatistics(objHere):
    objTopics = GetDataFolder(objHere, "E3Topic")
    GetOneTopicStatistics(objTopics)

def RemoveEmptyThreads(objHere):
    objThreads = GetDataFolder(objHere, "E3Thread")
    for objBatch in objThreads.objectValues("Folder"):
        for objThread in objBatch.objectValues("E3Thread"):
            if not len(SearchMany(objHere, "E3Messages", "ThreadId", objThread.id)):
                if not objThread.hasProperty("Deleted"):
                    objThread.manage_addProperty("Deleted", False, "boolean")
                objThread.Deleted = True
                print "Removing thread %s" % objThread.id

def RefreshThreadCaches(objHere):
    objThreads = GetDataFolder(objHere, "E3Thread")
    for objBatch in objThreads.objectValues("Folder"):
        for objThread in objBatch.objectValues("E3Thread"):
            if objThread.hasProperty("ThreadScreen"):
                objThread.ThreadScreen = ""

def RefreshTopicCaches(objTopic):
    if objTopic.hasProperty("FullTopicScreen"):
       objTopic.FullTopicScreen = ""

    if objTopic.hasProperty("TopicScreen"):
        objTopic.TopicScreen = ""

    for objSubTopic in objTopic.objectValues("E3Topic"):
        RefreshTopicCaches(objSubTopic)

def FinishForumProcess(objHere):
    print "Removing empty threads"
    RemoveEmptyThreads(objHere)

    print "Setting thread dates"
    SetThreadDates(objHere)

    print "Getting topic statistics"
    GetTopicStatistics(objHere)

    print "Refreshing thread caches"
    RefreshThreadCaches(objHere)

    print "Refreshing topic caches"
    objTopics = GetDataFolder(objHere, "E3Topic")
    RefreshTopicCaches(objTopics)

    print "Updating cache"
    UpdateCacheItem(objHere, "RHBlockTopicsTree")

def UpdateForumCache(objHere):
    print "Updating cache"
    UpdateCacheItem(objHere, "RHBlockTopicsTree")

    print "Updating home page"
    UpdateCacheItem(objHere, "HomePageContents")
