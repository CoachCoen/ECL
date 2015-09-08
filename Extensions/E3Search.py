# encoding: utf-8

# Error handling:
# "or", "and" without left or right hand operator
# missing brackets
# Incorrect date

import datetime
import types

from libDatabase import SearchOne
from libDatabase import SearchMany
from libDatabase import SearchManyBrains
from libBuildHTML import BuildDropdownList
from libBuildHTML import SimpleDropdown
from libBuildHTML import ShowChecked
from libBuildHTML import ShowSelected
from libBuildHTML import IsPlural
from libBuildHTML import BuildPagingList
from libGeneral import GetParameter
from libDate import MonthToNumber
from libDate import ShortMonthName
from libDatabase import GetDataFolder
from E3Messages import FormatOneThread
from libDatabase import SearchDateRange
from E3Messages import MessageCountForMonth
from libConstants import cnShortDateFormat
from libConstants import cnSearchResultsLimit
from E3Members import IsFullMember
from E3Members import GetCurrentMember
from libString import ToUnicode
from libBuildHTML import PutInFieldset

def GetOneDateArea(lstYearRange, dtmShowDate, strPrefix):
    lstMonthList = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    strResult = SimpleDropdown(strPrefix + "Date", range(1, 32), dtmShowDate.day, 'onChange  = "SelectDateRange()"') + " " + \
            SimpleDropdown(strPrefix + "Month", lstMonthList, dtmShowDate.strftime('%b'), 'onChange  = "SelectDateRange()"') + " " + \
            SimpleDropdown(strPrefix + "Year", range(lstYearRange[0], lstYearRange[1] + 1), dtmShowDate.year, 'onChange  = "SelectDateRange()"')
    return strResult

def GetDateAreas(dtmFromDate = None, dtmToDate = None):
    # 2 x 3 dropdown boxes, for date/month/year, from and to
    # Default: From 1 Jan 1997 till today
    if not dtmFromDate:
        dtmFromDate = datetime.datetime(year = 1999, month = 1, day = 1)

    if not dtmToDate:
        dtmToDate = datetime.datetime.today()

    strFromArea = GetOneDateArea((1999, dtmToDate.year), dtmFromDate, 'From')
    strToArea = GetOneDateArea((1999, dtmToDate.year), dtmToDate, 'To')
    return (strFromArea, strToArea)

def DefaultSearchFormValue(strField):
    if strField == 'Period':
        return 'Anytime'
    if strField == 'AdvertsOption':
        return 'Either'
    if strField == 'AttachmentOption':
        return 'Either'
    if strField == 'AttachmentType':
        return 'Any'
    if strField == 'FromDate':
        return '1'
    if strField == 'FromMonth':
        return 'Jan'
    if strField == 'FromYear':
        return '1997'
    if strField == 'ToDate':
        return str(datetime.datetime.today().day)
    if strField == 'ToMonth':
        return ShortMonthName(datetime.datetime.today().month)
    if strField == 'ToYear':
        return str(datetime.datetime.today().year)
    if strField == 'Offset':
        return '0'
    return ''

def NavigationForm(dictForm):
    strFieldList = ""
    for strField in ('SearchBody', 'SearchSubject', 'SearchBoth', 'Sender', 'Period', \
        'FromDate', 'FromMonth', 'FromYear', 'ToDate', 'ToMonth', 'ToYear', \
        'AdvertsOption', 'AttachmentOption', 'AttachmentType', 'Offset', 'WrittenBy'):
        if dictForm.has_key(strField):
            strValue = dictForm[strField]
        else:
            strValue = DefaultSearchFormValue(strField)
        strFieldList = strFieldList + """<input type="hidden" name="%s" value="%s">
""" % (strField, strValue)

    return """
    <form name="PagingForm" action="/Archive/ViewSearchResults" method="post">
        %s
    </form>""" % strFieldList

def BlankSearchForm():
    strResult = SearchFormTemplate()

    dictForm = {}
    for strField in ('SearchBody', 'SearchSubject', 'SearchBoth', 'Sender', 'Period', 'FromDate', 'ToDate', 'AdvertsOption', 'AttachmentType', 'AttachmentOption',     'TextOptionMessage', 'TextOptionSubject', 'Period7Days', 'Period30Days', 'Period90Days', 'PeriodRange', 'ExcludeAdverts', 'AdvertsOnly', 'AttachmentMustHave', 'AttachmentExclude', 'AttachmentDoc', 'AttachmentXls', 'AttachmentTxt', 'ErrorMessage', 'MemberMessagesOnly', 'SearchForWrittenBy'):
        dictForm[strField] = ''
    for strField in ('PeriodAnytime', 'AdvertsOptionEither', 'AttachmentEither', 'WrittenByAnyone'):
        dictForm[strField] = ' checked '
    (dictForm['FromDateArea'], dictForm['ToDateArea']) = GetDateAreas()
    dictForm['AttachmentAny'] = ' selected '
    return strResult % dictForm

def SearchFormTemplate():
    return """
<script type="text/javascript" language="Javascript">
function SelectDateRange() {
    document.searchform.Period[4].checked = true
}

function SelectSearchForWrittenBy() {
    document.searchform.WrittenBy[1].checked = true
}
</script>
                %(ErrorMessage)s
                <form action="/Archive/ViewSearchResults" method="post" name="searchform">
                    <fieldset>
	                    <legend>What was the message about </legend>
            	        <p>Message body or subject header<br />
                            <input type="text" name="SearchBoth" value="%(SearchBoth)s" class="txt"/></p>

            	        <p>Message body only<br />
                            <input type="text" name="SearchBody" value="%(SearchBody)s" class="txt"/></p>

            	        <p>Message subject header only<br />
                            <input type="text" name="SearchSubject" value="%(SearchSubject)s" class="txt"/></p>
                        <p>You can group words into phrase using double quotes and use "and", "or", "not" and round brackets. For more information see <a href="/Help/ShowOne?Id=ArchiveSearch">the archive search help page</a></p>

                    </fieldset>
					<fieldset>
						<legend>Who wrote the message</legend>
                        <p><input type="radio" name="WrittenBy" %(MemberMessagesOnly)s value="MemberMessagesOnly"/> Only my own messages</p>
						<p><input type="radio" name="WrittenBy" %(SearchForWrittenBy)s value="SearchForWrittenBy"/> Message written by: <input type="text" name="Sender" value="%(Sender)s" class="txt" onFocus = "SelectSearchForWrittenBy()"/></p>
                        <p><input type="radio" name="WrittenBy" %(WrittenByAnyone)s value="WrittenByAnyone"/> Message written by anyone</p>
					</fieldset>
					<fieldset>
						<legend>When was the message sent</legend>
						<p><input name="Period" type="radio" value="Anytime" %(PeriodAnytime)s/> Anytime
							<img src="images/Separator.gif" width="1" height="25" align="absmiddle" />
							<input name="Period" type="radio" value="7Days" %(Period7Days)s/> Last 7 days
							<img src="images/Separator.gif" width="1" height="25" align="absmiddle" />
							<input name="Period" type="radio" value="30Days" %(Period30Days)s/> Last 30 days
							<img src="images/Separator.gif" width="1" height="25" align="absmiddle" />
							<input name="Period" type="radio" value="90Days" %(Period90Days)s/>	Last 90 days<br />
							<input name="Period" type="radio" value="Range" %(PeriodRange)s/>	Between %(FromDateArea)s
							and %(ToDateArea)s
						</p>
					</fieldset>
					<fieldset>
						<legend>Adverts</legend>
						<p>
                	        <input name="AdvertsOption" type="radio" value="ExcludeAdverts" %(ExcludeAdverts)s"/> Exclude adverts
							<img src="images/Separator.gif" width="1" height="25" align="absmiddle" />
							<input name="AdvertsOption" type="radio" value="AdvertsOnly" %(AdvertsOnly)s/> Adverts only
							<img src="images/Separator.gif" width="1" height="25" align="absmiddle" />
							<input name="AdvertsOption" type="radio" value="Either" %(AdvertsOptionEither)s />	Either
						</p>
						<p>(Based on the text &quot;Adv&quot; in the email subject header)</p>
                    </fieldset>
                    <fieldset>
                        <legend>Attachments</legend>
						<p>
                	        <input name="AttachmentOption" type="radio" value="MustHave" %(AttachmentMustHave)s/> Must have attachment(s)
                	        <select name="AttachmentType">
                                <option value="Any" %(AttachmentAny)s>any attachment</option>
                                <option value=".doc" %(AttachmentDoc)s>.doc document</option>
                                <option value=".xls" %(AttachmentXls)s>.xls spreadsheet</option>
                                <option value=".txt" %(AttachmentTxt)s>.txt text file</option>
                            </select>
						</p>
						<p>
						    <input name="AttachmentOption" type="radio" value="Exclude" %(AttachmentExclude)s/>
						    Exclude messages with attachment(s)
							<img src="images/Separator.gif" width="1" height="25" align="absmiddle" />
							<input name="AttachmentOption" type="radio" value="Either" %(AttachmentEither)s/>
							Either						</p>
					</fieldset>
					<fieldset>
						<legend>GO</legend>
						<p>
							<input type="submit" value="Search" class="btn"/>
						</p>
					</fieldset>
                </form>
"""
def GetMultipleParameters(objRequest, lstParameters):
    dictResult = {}
    for strParameter in lstParameters:
        dictResult[strParameter] = GetParameter(objRequest, strParameter)
    return dictResult

def GetSenderList(objHere, strSender):
    lstResult = []

    lstResult = SearchMany(objHere, 'E3EmailAddress', 'EmailAddress', strSender)
    for intI in range(0, len(lstResult)):
        lstResult[intI] = lstResult[intI].unrestrictedTraverse('..')

    for objMember in SearchMany(objHere, 'E3Member', 'Name', strSender):
        if not objMember in lstResult:
            lstResult.append(objMember)

    return lstResult

def RepeatForm(dictForm, strErrorMessage = ""):

    if strErrorMessage:
        strErrorMessage = """<p class="ErrorMessage">%s</p>""" % strErrorMessage

    dictForm['PeriodAnytime'] = ShowChecked(dictForm['Period'] == 'Anytime' or not dictForm['Period'])
    dictForm['Period7Days'] = ShowChecked(dictForm['Period'] == '7Days')
    dictForm['Period30Days'] = ShowChecked(dictForm['Period'] == '30Days')
    dictForm['Period90Days'] = ShowChecked(dictForm['Period'] == '90Days')
    dictForm['PeriodRange'] = ShowChecked(dictForm['Period'] == 'Range')

    dictForm['ExcludeAdverts'] = ShowChecked(dictForm['AdvertsOption'] == 'ExcludeAdverts')
    dictForm['AdvertsOnly'] = ShowChecked(dictForm['AdvertsOption'] == 'AdvertsOnly')
    dictForm['AdvertsOptionEither'] = ShowChecked(dictForm['AdvertsOption'] == 'Either' or not dictForm['AdvertsOption'])

    dictForm['AttachmentMustHave'] = ShowChecked(dictForm['AttachmentOption'] == 'MustHave')
    dictForm['AttachmentExclude'] = ShowChecked(dictForm['AttachmentOption'] == 'Exclude')
    dictForm['AttachmentEither'] = ShowChecked(dictForm['AttachmentOption'] == 'Either' or not dictForm['AttachmentOption'])

    dictForm['MemberMessagesOnly'] = ShowChecked(dictForm['WrittenBy'] == "MemberMessagesOnly")
    dictForm['SearchForWrittenBy'] = ShowChecked(dictForm['WrittenBy'] == "SearchForWrittenBy")
    dictForm['WrittenByAnyone'] = ShowChecked(dictForm['WrittenBy'] == "WrittenByAnyone")

    dictForm['AttachmentAny'] = ShowSelected(dictForm['AttachmentType'] == 'Any' or not dictForm['AttachmentType'])
    dictForm['AttachmentDoc'] = ShowSelected(dictForm['AttachmentType'] == '.doc')
    dictForm['AttachmentXls'] = ShowSelected(dictForm['AttachmentType'] == '.xls')
    dictForm['AttachmentTxt'] = ShowSelected(dictForm['AttachmentType'] == '.txt')

    dictForm['ErrorMessage'] = strErrorMessage

    dtmFromDate = ValidDate(int(dictForm['FromYear']), MonthToNumber(dictForm['FromMonth']), int(dictForm['FromDate']))
    dtmToDate = ValidDate(int(dictForm['ToYear']), MonthToNumber(dictForm['ToMonth']), int(dictForm['ToDate']))

    (dictForm['FromDateArea'], dictForm['ToDateArea']) = GetDateAreas(dtmFromDate, dtmToDate)

    for strField in ('SearchBoth', 'SearchSubject', 'SearchBody', 'Sender'):
        dictForm[strField] = dictForm[strField].replace('"', '&quot;')

    strResult = SearchFormTemplate() % dictForm

    return strResult

def HasAttachment(objMessage, strAttachmentType = ''):
    for objAttachment in objMessage.objectValues('File'):
        if not '.html' in str(objAttachment.id):
            if strAttachmentType:
                if strAttachmentType in objAttachment.title.lower():
                    return True
            else:
                return True
    return False

def FilterMessage(objMessage, blnNeedsAnyAttachment, blnNeedsSpecificAttachment, strAttachmentType, \
                blnExcludeAttachments, blnNeedsAdvert, blnNoAdverts):
    if blnNeedsAnyAttachment:
        if not HasAttachment(objMessage):
            return False

    if blnNeedsSpecificAttachment:
        if not HasAttachment(objMessage, strAttachmentType):
            return False

    if blnExcludeAttachments:
        if HasAttachment(objMessage):
            return False

    if blnNeedsAdvert:
        if not ('adv' in objMessage.mailSubject.lower()):
            return False

    if blnNoAdverts:
        if 'adv' in objMessage.mailSubject.lower():
            return False

    return True

def FilterList(lstMessages, dictForm):
    blnExcludeAttachments = False
    blnNeedsAnyAttachment = False
    blnNeedsSpecificAttachment = False
    blnNeedsAdvert = False
    blnNoAdverts = False

    strAttachmentType = dictForm['AttachmentType']

    if dictForm['AttachmentOption'] == 'MustHave':
        if dictForm['AttachmentType'] == 'Any':
            blnNeedsAnyAttachment = True
        else:
            blnNeedsSpecificAttachment = True

    elif dictForm['AttachmentOption'] == 'Exclude':
        blnExcludeAttachments = True

    if dictForm['AdvertsOption'] == 'AdvertsOnly':
        blnNeedsAdvert = True

    elif dictForm['AdvertsOption'] == 'ExcludeAdverts':
        blnNoAdverts = True

    lstResult = []
    for objBrain in lstMessages:
        blnFound = True
        try:
            objMessage = objBrain.getObject()
        except:
            blnFound = False
        if blnFound:
            if FilterMessage(objMessage, blnNeedsAnyAttachment, blnNeedsSpecificAttachment, strAttachmentType, \
                    blnExcludeAttachments, blnNeedsAdvert, blnNoAdverts):
                lstResult.append((objMessage.id, objMessage.mailDate))

    return lstResult

def MergeLists(lstOne, lstTwo):
    # Format: ((id, Date), (id, Date), ,,)
    lstResult = []

    if len(lstOne) > 0 and len(lstTwo) > 0:

        lstItem1 = lstOne.pop(0)
        lstItem2 = lstTwo.pop(0)


        while lstOne and lstTwo:
            if lstItem1[1] > lstItem2[1]:
                lstResult.append(lstItem1[0])
                lstItem1 = lstOne.pop(0)
            else:
                lstResult.append(lstItem2[0])
                lstItem2 = lstTwo.pop(0)

        if lstItem1[1] > lstItem2[1]:
            lstResult.append(lstItem1[0])
            lstResult.append(lstItem2[0])
        else:
            lstResult.append(lstItem2[0])
            lstResult.append(lstItem1[0])

    for lstItem in lstOne:
        lstResult.append(lstItem[0])

    for lstItem in lstTwo:
        lstResult.append(lstItem[0])

    return lstResult

def ValidDate(intYear, intMonth, intDate):
    blnDone = False
    while not blnDone:
        try:
            dtmResult = datetime.datetime(year = intYear, month = intMonth, day = intDate)
            blnDone = True
        except:
            intDate -= 1
            if intDate < 28:
                blnDone = True
    return dtmResult

def GetDateRange(dictForm, dtmFirstDate, dtmLastDate):
    dtmFromDate = dtmFirstDate
    dtmToDate = dtmLastDate

    if dictForm['Period'] == '7Days':
        deltaPeriod = datetime.timedelta(days = 7)
        dtmFromDate = dtmToDate - deltaPeriod
    elif dictForm['Period'] == '30Days':
        deltaPeriod = datetime.timedelta(days = 30)
        dtmFromDate = dtmToDate - deltaPeriod
    elif dictForm['Period'] == '90Days':
        deltaPeriod = datetime.timedelta(days = 90)
        dtmFromDate = dtmToDate - deltaPeriod
    elif dictForm['Period'] == 'Range':
        dtmFromDate = ValidDate(int(dictForm['FromYear']), MonthToNumber(dictForm['FromMonth']), int(dictForm['FromDate']))
        dtmToDate = ValidDate(int(dictForm['ToYear']), MonthToNumber(dictForm['ToMonth']), int(dictForm['ToDate']))
    return (dtmFromDate, dtmToDate)

def GotoScript():
    return """
<SCRIPT language="JavaScript">
function GotoPage(intOffset)
{
    document.PagingForm.Offset.value = intOffset
    document.PagingForm.submit();
}
</SCRIPT>
"""

def GetMessageForId(objCatalogue, strId):
    lstMessagesForId = objCatalogue.searchResults({'id': strId})
    if len(lstMessagesForId) == 0:
        return None
    lstValidMessages = []
    for objBrain in lstMessagesForId:
        try:
            lstValidMessages.append(objBrain.getObject())
        except:
            pass
    if len(lstValidMessages) <> 1:
        return None
    return lstValidMessages[0]

def CombineWords(lstTokens):
    # Apart from 'not', 'and', 'or', any other string of words can be combined into a single token (separate by spaces)
    lstResult = []
    lstToStore = []
    for strToken in lstTokens:
        if strToken.lower() in ['"', "'", "(", ")", "and", "or", "not"]:
            if lstToStore:
                lstResult.append(" ".join(lstToStore))
                lstToStore = []
            lstResult.append(strToken)
        else:
            lstToStore.append(strToken)
    if lstToStore:
        lstResult.append(" ".join(lstToStore))
    return lstResult

def Tokenise(strString):
    lstResult = []
    strWord = ""
    blnDoubleQuote = False
    blnSingleQuote = False
    for strChar in strString:
        blnSaveWord = False
        blnSaveChar = False
        if blnSingleQuote:
            if strChar == "'":
                blnSaveWord = True
                blnSingleQuote = False
            else:
                strWord += strChar
        elif blnDoubleQuote:
            if strChar == '"':
                blnSaveWord = True
                blnDoubleQuote = False
            else:
                strWord += strChar
        elif strChar == ' ':
            blnSaveWord = True
        elif strChar in ['(', ')']:
            blnSaveChar = True
        elif strChar == '"':
            blnSaveWord = True
            blnDoubleQuote = True
        elif strChar == "'":
            blnSaveWord = True
            blnSingleQuote = True
        else:
            strWord += strChar

        if blnSaveChar or blnSaveWord:
            if strWord:
                lstResult.append(strWord)
                strWord = ""

        if blnSaveChar:
            lstResult.append(strChar)

    if strWord:
        lstResult.append(strWord)

    if blnDoubleQuote:
        return (None, "Missing closing double quote")

    if blnSingleQuote:
        return (None, "Missing closing single quote")

    lstResult = CombineWords(lstResult)

    return (lstResult, None)

def FindBracketPairs(lstTokens):
    lstStack = []
    lstPairs = []
    for intI in range(0, len(lstTokens)):
        if lstTokens[intI] == '(':
            lstStack.append(intI)
        if lstTokens[intI] == ')':
            if lstStack:
                intOpening = lstStack.pop()
                lstPairs.append((intOpening, intI))
            else:
                return (None, "Missing opening bracket")
    if len(lstStack) > 0:
        return (None, "Missing closing bracket")
    return (lstPairs, "")

def GroupBrackets(lstTokens, intOpening, intClosing):
    lstResult = lstTokens
    lstGroup = lstTokens[intOpening + 1:intClosing]
    lstTokens[intOpening] = lstGroup
    for intI in range(intClosing, intOpening, -1):
        del(lstTokens[intI])

    return lstTokens

def RemoveNone(lstList):
    lstResult = []
    for varItem in lstList:
        if varItem:
            if type(varItem) == types.ListType:
                varItem = RemoveNone(varItem)
            lstResult.append(varItem)
    return lstResult

def ParseBrackets(lstTokens):
    (lstBracketPairs, strErrorMessage) = FindBracketPairs(lstTokens)
    if strErrorMessage:
        return (None, strErrorMessage)
    lstBracketPairs.reverse()
    for (intOpening, intClosing) in lstBracketPairs:
        lstTokens = GroupBrackets(lstTokens, intOpening, intClosing)
    return (lstTokens, "")

def ParseOneNot(lstTokens):
    intLocation = lstTokens.index('not')
    if intLocation == len(lstTokens) - 1:
        return (None, "'not' cannot be the only or the last word")
    lstTokens[intLocation] = ['not', lstTokens[intLocation + 1]]
    del(lstTokens[intLocation + 1])
    return (lstTokens, "")

def ParseNot(lstTokens):
    # Replace .... not A .... with ... (not A) ....

    for intI in range(0, len(lstTokens)):
        varItem = lstTokens[intI]
        if type(varItem) == types.ListType:
            (lstTokens[intI], strErrorMessage) = ParseNot(varItem)
            if not lstTokens[intI]:
                return (None, strErrorMessage)

    while HasOperator(lstTokens, 'not'):
        (lstTokens, strErrorMessage) = ParseOneNot(lstTokens)
        if not lstTokens:
            return (None, strErrorMessage)

    return (lstTokens, "")

def HasOperator(lstTokens, strOperator):
    try:
        intDummy = lstTokens.index(strOperator)
    except:
        return False
    return True

def ParseOneAndOr(lstTokens, strOperator):
    intStart = lstTokens.index(strOperator)
    if intStart == 0:
        return (None, "'%s' cannot be the first word of (a part of) the query" % strOperator)

    intEnd = intStart + 2
    while intEnd < len(lstTokens) and lstTokens[intEnd] == strOperator:
        intEnd += 2
    intEnd -= 2
    if intEnd == len(lstTokens) - 1:
        return (None, "'%s' cannot be the last word of (a part of) the query" % strOperator)

    lstNew = [strOperator]
    for intI in range(intStart - 1, intEnd + 3, 2):
        lstNew.append(lstTokens[intI])
    lstTokens[intStart - 1] = lstNew
    for intI in range(intEnd + 1, intStart - 1, -1):
        del(lstTokens[intI])
    return (lstTokens, "")

def ParseAndOr(lstTokens, strOperator):
    # replace: a and b and c
    # with: (and a b c)
    # We should now have a and/or b and/or c and/or d and/or e, etc
    # where a, b, c etc can be another list
    for intI in range(0, len(lstTokens)):
        varItem = lstTokens[intI]
        if type(varItem) == types.ListType:
            (lstTokens[intI], strErrorMessage) = ParseAndOr(varItem, strOperator)
            if not lstTokens[intI]:
                return (None, strErrorMessage)

    while HasOperator(lstTokens, strOperator):
        (lstTokens, strErrorMessage) = ParseOneAndOr(lstTokens, strOperator)
        if not lstTokens:
            return (None, strErrorMessage)

    return (lstTokens, "")

def InsertMissingAnd(lstTokens):
    # Assume "a b c" means "a or b or c"
    lstResult = []
    blnUnprocessed = False
    for varItem in lstTokens:
        if varItem in ['and', 'or', 'not']:
            blnUnprocessed = False
        else:
            if blnUnprocessed:
                lstResult.append('and')
            blnUnprocessed = True
        lstResult.append(varItem)
    return lstResult

# Possible errors:
# and/or followed directly by and/or
# and/or at end or start of (sub)sentence
# not at end of (sub)sentence
# not followed directly by and/or
# bracket missing
# single/double quote missing
# not at the highest level (e.g. "not headset") - this would give too many results
# generalisation of above: "not" which isn't covered by an "and" (e.g. "phone or not headset")

def FoundDateOrder(objMessage1, objMessage2):
    return cmp(objMessage2.mailDate, objMessage1.mailDate)

def FoundBrainsDateOrder(objBrain1, objBrain2):
#    print "Comparing %s with %s" % (objBrain1.mailDate, objBrain2.mailDate)
    return cmp(objBrain2.mailDate, objBrain1.mailDate)

class SearchNode:
    def __init__(self, varTokens = None, strField = ""):
        self.Children = []
        self.SearchFor = ''
        self.Field = ""
        self.FromDate = None
        self.ToDate = None
        self.Found = None
        self.BrainsFound = None
        self.NumberFound = -1
        self.FinalSearchDone = False
        self.ObjectsLoaded = False
        if varTokens:
            if type(varTokens) == types.StringType:
                self.Field = strField
                self.Operator = 'contains'
                self.SearchFor = self.RemoveQuotes(varTokens)
            else:
                if len(varTokens) == 1:
                    self.Field = strField
                    self.Operator = 'contains'
                    self.SearchFor = self.RemoveQuotes(varTokens[0])
                else:
                    self.Operator = varTokens[0]
                    for varItem in varTokens[1:]:
                        self.Children.append(SearchNode(varItem, strField))

    def Sort(self):
        # Put most recent message first
        if self.Found:
            self.Found.sort(FoundDateOrder)
        elif self.BrainsFound:
            self.BrainsFound.sort(FoundBrainsDateOrder)

    def FoundCount(self):
        if self.Found:
            return len(self.Found)
        if self.BrainsFound:
            return len(self.BrainsFound)
        if self.NumberFound >= 0:
            return self.NumberFound
        return 0

    def RemoveQuotes(self, strString):
        if strString[0] in ['"', "'"]:
            strString = strString[1:-1]
        return strString

    def Print(self, intLevel):
        print "   " * intLevel, self.Field, self.Operator, self.SearchFor,
        if self.FromDate:
            print self.FromDate,
        if self.ToDate:
            print self.ToDate,
        print
        print "Found: %s" % self.FoundCount()
#        if self.Found:
#            print "Found: %s" % len(self.Found)
#        else:
#            print "Found: %s" % self.Found
        for varItem in self.Children:
            varItem.Print(intLevel + 1)

    def FilterNot(self, objMessage):
        return not self.Children[0].Filter(objMessage)

    def FilterOr(self, objMessage):
        for objChild in self.Children:
            if objChild.Filter(objMessage):
                return True
        return False

    def FilterAnd(self, objMessage):
        for objChild in self.Children:
            if not objChild.Filter(objMessage):
                return False
        return True

    def FilterContains(self, objMessage):
        if not objMessage:
            return False
        if self.Field == "mailSubject":
            strField = objMessage.mailSubject
        elif self.Field == "mailFrom":
            strField = objMessage.mailFrom
        elif self.Field == "UserId":
            strField = objMessage.UserId
        else:
            strField = objMessage.getProperty(self.Field)
        strField = strField.lower()
        if self.SearchFor.lower() in strField:
            return True
        return False

    def FilterDateFrom(self, objMessage):
        if datetime.datetime.fromtimestamp(objMessage.mailDate) >= self.FromDate:
            return True
        return False

    def FilterDateTo(self, objMessage):
        if datetime.datetime.fromtimestamp(objMessage.mailDate) <= self.ToDate:
            return True
        return False

    def FilterDateRange(self, objMessage):
        if datetime.datetime.fromtimestamp(objMessage.mailDate) < self.FromDate:
            return False
        if datetime.datetime.fromtimestamp(objMessage.mailDate) > self.ToDate:
            return False
        return True

    def FilterAttachment(self, objMessage):
        if self.Operator == 'attachment':
            if self.SearchFor == 'Any':
                return HasAttachment(objMessage)
            else:
                return HasAttachment(objMessage, self.SearchFor)
        else:
            return not HasAttachment(objMessage)

    def Filter(self, objMessage):
        if self.Operator == 'not':
            return self.FilterNot(objMessage)
        elif self.Operator == 'and':
            return self.FilterAnd(objMessage)
        elif self.Operator == 'or':
            return self.FilterOr(objMessage)
        elif self.Operator == 'contains':
            return self.FilterContains(objMessage)
        elif self.Operator == 'datefrom':
            return self.FilterDateFrom(objMessage)
        elif self.Operator == 'dateto':
            return self.FilterDateTo(objMessage)
        elif self.Operator == 'daterange':
            return self.FilterDateRange(objMessage)
        elif self.Operator == 'attachment':
            return self.FilterAttachment(objMessage)
        elif self.Operator == 'noattachment':
            return self.FilterAttachment(objMessage)

    def SearchNot(self, strField):
        self.NumberFound = 100000
        # Not is only used to filter, so use at end

    def AddToList(self, lstMain, lstToAdd, blnBrains = False):
        lstResult = lstMain
        if blnBrains:
            lstPaths = []
            for objBrain in lstMain:
                lstPaths.append(objBrain.getPath())
            for objBrain in lstToAdd:
                strPath = objBrain.getPath()
                if not strPath in lstPaths:
                    lstResult.append(objBrain)
                    lstPaths.append(strPath)

        else:
            for objObject in lstToAdd:
                if not objObject in lstResult:
                    lstResult.append(objObject)

        return lstResult

    def MergeMessageLists(self, lstOne, lstTwo, blnBrains = False):
#        TimeTrace("Merge start, %s + %s" % (len(lstOne), len(lstTwo)))
        if (not lstOne) or len(lstOne) == 0:
            lstResult = lstTwo

        elif (not lstTwo) or len(lstTwo) == 0:
            lstResult = lstOne

        elif len(lstOne) > len(lstTwo):
            lstResult = self.AddToList(lstOne, lstTwo, blnBrains)

        else:
            lstResult = self.AddToList(lstTwo, lstOne, blnBrains)

#        TimeTrace("Merge end, %s + %s" % (len(lstOne), len(lstTwo)))
        return lstResult

    def SearchOr(self, objHere):
        lstResult = []
        blnObjectsLoaded = False
        # Search all objects
        # Find out if any had to load the objects,
        #   if so, they all need to load the objects
        for objChild in self.Children:
            if objChild:
                objChild.Search(objHere, True)
                if objChild.ObjectsLoaded:
                    blnObjectsLoaded = True

        for objChild in self.Children:
            if objChild:
                if blnObjectsLoaded:
                    if not objChild.ObjectsLoaded:
                        objChild.LoadObjects()
                    lstResult = self.MergeMessageLists(lstResult, objChild.Found)
                else:
                    lstResult = self.MergeMessageLists(lstResult, objChild.BrainsFound, True)

        if blnObjectsLoaded:
            self.Found = lstResult
            self.ObjectsLoaded = True
        else:
            self.BrainsFound = lstResult

    def LoadObjects(self):
        if not ObjectsLoaded:
            lstObjects = []
            for objBrain in self.BrainsFound:
                lstObjects.append(objBrain.getObject())
            self.Found = lstObjects
            self.ObjectsLoaded = True

    def SearchOneAnd(self, objBrain, objMessage, lstChildrenWhichFilterOnBrains, lstChildrenWhichFilterOnMessage):
        for objChild in lstChildrenWhichFilterOnBrains:
            if not objChild.Filter(objBrain):
                return False
        if lstChildrenWhichFilterOnMessage:
            if not objMessage:
                objMessage = objBrain.getObject()
#                print ".",
            for objChild in lstChildrenWhichFilterOnMessage:
                if not objChild.Filter(objMessage):
                    return False
        return True

    def FilterNeedsMessage(self):
        if self.Operator in ['not', 'and', 'or']:
            for objChild in self.Children:
                if objChild.FilterNeedsMessage():
                    return True
            return False
        elif self.Operator == 'contains':
            # mailSubject, mailFrom - stored in meta data
            if self.Field in ['mailSubject', 'mailFrom', 'UserId']:
                return False
            return True
        elif self.Operator in ['datefrom', 'dateto', 'daterange']:
            return False
        elif self.Operator == 'attachment':
            return True
        elif self.Operator == 'noattachment':
            return True
        return True

    def SplitFilters(self, objStart):
        lstOnBrains = []
        lstOnMessage = []

        for objChild in self.Children:
            if objChild <> objStart:
                # We need the whole message when:
                    # Any of the sub filters needs the whole message
                    #
                if objChild.FilterNeedsMessage():
                    lstOnMessage.append(objChild)
                else:
                    lstOnBrains.append(objChild)
        return (lstOnBrains, lstOnMessage)

    def SearchAnd(self, objHere):
        # Make sure that all children are done
        # then choose child with least messages found
        # filter these messages against the other children
#        TimeTrace("SearchAnd start")
        objStart = self.Children[0]
        for objChild in self.Children:
            objChild.Search(objHere)
            if objChild.FoundCount():
                if not objStart:
                    objStart = objChild
                else:
                    if objChild.FoundCount() < objStart.FoundCount():
                        objStart = objChild

        # Sort out Found/BrainsFound
        # If objStart.RecordsLoaded - all fine, just start filtering
        # We start off either with an objMessage or an objBrain
        # If we don't have an objMessage yet, work with the objBrain for as long as possible
        # So do any filters which don't require an objMessage first
        # If there are then still any filters left which do require an objMessage, now load the objMessage, then go through those

#        TimeTrace("SearchAnd A")
#        print "objStart: "
#        objStart.Print(3)
        objStart.Search(objHere, True)
        lstResult = []

#        TimeTrace("SearchAnd B")

        (lstChildrenWhichFilterOnBrains, lstChildrenWhichFilterOnMessage) = self.SplitFilters(objStart)

#        TimeTrace("SearchAnd C")

        if objStart.BrainsFound:
            for objBrain in objStart.BrainsFound:
                if self.SearchOneAnd(objBrain, None, lstChildrenWhichFilterOnBrains, lstChildrenWhichFilterOnMessage):
                    lstResult.append(objBrain)
            self.BrainsFound = lstResult

        elif objStart.Found:
            for objMessage in objStart.Found:
                if self.SearchOneAnd(None, objMessage, lstChildrenWhichFilterOnBrains, lstChildrenWhichFilterOnMessage):
                    lstResult.append(objMessage)
            self.Found = lstResult
#        TimeTrace("SearchAnd finish")

    def SearchContains(self, objHere):
        strSearchFor = self.SearchFor.strip()
#        TimeTrace("Search contains %s in %s" % (strSearchFor, self.Field))

        if len(strSearchFor.split()) > 1:
            strSearchFor = '"%s"' % strSearchFor
        self.BrainsFound = SearchManyBrains(objHere, 'E3Messages', self.Field, '%s' % strSearchFor)
#        TimeTrace("Done")

    def SearchFrom(self, objHere, blnFinalSearch):
        if blnFinalSearch:
            self.Found = SearchMessageDateRange(objHere, self.FromDate, None)
        else:
            self.NumberFound = CountDateRange(objHere, self.FromDate, None)

    def SearchTo(self, objHere, blnFinalSearch):
        if blnFinalSearch:
            self.Found = SearchMessageDateRange(objHere, None, self.ToDate)
        else:
            self.NumberFound = CountDateRange(objHere, None, self.ToDate)

    def SearchDateRange(self, objHere, blnFinalSearch):
        if blnFinalSearch:
            self.Found = SearchMessageDateRange(objHere, self.FromDate, self.ToDate)
        else:
            self.NumberFound = CountDateRange(objHere, self.FromDate, self.ToDate)

    def Search(self, objHere, blnFinalSearch = False):
#      TimeTrace(".Search: %s, %s" % (self.Operator, self.Field))
        if self.FinalSearchDone:
            return
        if self.Operator == 'not':
            self.SearchNot(objHere)
            self.FinalSearchDone = True
        elif self.Operator == 'and':
            self.SearchAnd(objHere)
            self.FinalSearchDone = True
        elif self.Operator == 'or':
            self.SearchOr(objHere)
            self.FinalSearchDone = True
        elif self.Operator == 'contains':
            self.SearchContains(objHere)
            self.FinalSearchDone = True
        elif self.Operator == 'datefrom':
            self.SearchFrom(objHere, blnFinalSearch)
            self.FinalSearchDone = blnFinalSearch
        elif self.Operator == 'dateto':
            self.SearchTo(objHere, blnFinalSearch)
            self.FinalSearchDone = blnFinalSearch
        elif self.Operator == 'daterange':
            self.SearchDateRange(objHere, blnFinalSearch)
            self.FinalSearchDone = blnFinalSearch
        elif self.Operator == 'attachment':
            self.NumberFound = 100000
        elif self.Operator == 'noattachment':
            self.NumberFound = 100000
#        TimeTrace(".Search done (%s, %s)" % (self.Operator, self.Field))

    def FilterOutPrivateObjects(self, lstObjects):
        lstResult = []
        for objObject in lstObjects:
            if not objObject.Private:
                lstResult.append(objObject)
        return lstResult

    def FilterOutPrivateMessages(self):
        if self.Found:
            self.PublicFound = self.FilterOutPrivateObjects(self.Found)
        else:
            self.PublicBrainsFound = self.FilterOutPrivateObjects(self.BrainsFound)

    def ListResults(self, objRequest, blnFullMember):
        if blnFullMember:
            if self.ObjectsLoaded:
                lstFound = self.Found
            else:
                lstFound = self.BrainsFound
        else:
            if self.ObjectsLoaded:
                lstFound = self.PublicFound
            else:
                lstFound = self.PublicBrainsFound

        if lstFound:
            intThreads = len(lstFound)
        else:
            intThreads = 0

        if not intThreads:
            return ("", "", "", 0)

        strOffset = GetParameter(objRequest, 'Offset')
        if strOffset:
            intOffset = int(strOffset)
        else:
            intOffset = 0

        blnEvenRow = False

        strNavigation = ""
        strNavigationHandling = ""
        intMaxMessages = 20
        intFirstThread = intOffset + 1
        intLastThread = intFirstThread + intMaxMessages - 1
        if intLastThread > intThreads:
            intLastThread = intThreads

        if intThreads > intMaxMessages:
            strNavigationHandling = GotoScript() + NavigationForm(objRequest)

        if intThreads > intMaxMessages:
            strLink = "javascript: GotoPage(%s)"
            strNavigation = BuildPagingList(intMaxMessages, intThreads, intFirstThread, intLastThread, strLink, intOffset)

        strList = ""
        for intI in range(intFirstThread - 1, intLastThread):
            if self.ObjectsLoaded:
                objObject = lstFound[intI]
            else:
                objObject = lstFound[intI].getObject()
            strList += FormatOneThread(objObject, blnEvenRow, blnFullMember)

        return (strList, strNavigationHandling, strNavigation, intThreads)

def ClearDateRange(dtmFromDate, dtmToDate):
    if not dtmFromDate:
        dtmFromDate = datetime.datetime(year = 1997, month = 1, day = 1)

    if not dtmToDate:
        dtmToDate = datetime.datetime.today()
    return (dtmFromDate, dtmToDate)

def InRange(dtmDate, dtmFrom, dtmTo):
    if dtmDate < dtmFrom:
        return False
    if dtmDate > dtmTo:
        return False
    return True

def SearchMessageDateRange(objHere, dtmFromDate, dtmToDate):
    (dtmFromDate, dtmToDate) = ClearDateRange(dtmFromDate, dtmToDate)

    lstFound = []

    objMessages = GetDataFolder(objHere, 'E3Messages')

    for intYear in range(dtmFromDate.year, dtmToDate.year + 1):
        if intYear == dtmFromDate.year:
            intStartMonth = dtmFromDate.month
        else:
            intStartMonth = 1
        if intYear == dtmToDate.year:
            intEndMonth = dtmToDate.month
        else:
            intEndMonth = 12

        for intMonth in range(intStartMonth, intEndMonth + 1):
            blnEdgeMonth = False
            if intYear == dtmFromDate.year and intMonth == dtmFromDate.month:
                blnEdgeMonth = True
            if intYear == dtmToDate.year and intMonth == dtmToDate.month:
                blnEdgeMonth = True
            try:
                objMonth = objMessages.unrestrictedTraverse('%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
            except:
                objMonth = None
            if objMonth:
                for objThread in objMonth.objectValues():
                    if not blnEdgeMonth or InRange(datetime.datetime.fromtimestamp(objThread.mailDate), dtmFromDate, dtmToDate):
                        lstFound.append(objThread)
                    for objMessage in objThread.objectValues('Folder'):
                        if not blnEdgeMonth or InRange(datetime.datetime.fromtimestamp(objMessage.mailDate), dtmFromDate, dtmToDate):
                            lstFound.append(objMessage)
    return lstFound

def GetMessagesForMonth(objHere, intYear, intMonth):
    objMessages = GetDataFolder(objHere, 'E3Messages')
    try:
        objMonth = objMessages.unrestrictedTraverse('Messages/%s/%s-%s' % (intYear, intYear, str(intMonth).zfill(2)))
        return objMonth
    except:
        return None

def CountToEndOfMonth(objHere, dtmFromDate):
    objMonth = GetMessagesForMonth(objHere, dtmFromDate.year, dtmFromDate.month)
    intResult = 0
    if not objMonth:
        return 0
    for objMessage in objMonth.objectValues('Folder'):
        if FromZopeDate(objMessage.mailDate) >= dtmFromDate:
            intResult += 1
    return intResult

def CountFromStartOfMonth(objHere, dtmToDate):
    objMonth = GetMessagesForMonth(objHere, dtmToDate.year, dtmToDate.month)
    if not objMonth:
        return 0
    for objMessage in objMonth.objectValues('Folder'):
        if FromZopeDate(objMessage.mailDate) <= dtmToDate:
            intResult += 1
    return intResult

def CountWithinMonth(objHere, dtmFromDate, dtmToDate):
    objMonth = GetMessagesForMonth(objHere, dtmFromDate.year, dtmFromDate.month)
    if not objMonth:
        return 0
    for objMessage in objMonth.objectValues('Folder'):
        if FromZopeDate(objMessage.mailDate) >= dtmFromDate and FromZopeDate(objMessage.mailDate) <= dtmToDate:
            intResult += 1
    return intResult

def CountDateRange(objHere, dtmFromDate, dtmToDate):
    (dtmFromDate, dtmToDate) = ClearDateRange(dtmFromDate, dtmToDate)

    lstCountList = GetDataFolder(objHere, 'E3Messages').MessageCount

    intResult = 0


    for intYear in range(dtmFromDate.year, dtmToDate.year + 1):
        lstYearCounts = None
        for strLine in lstCountList:
            lstCounts = strLine.split()
            if int(lstCounts[0]) == intYear:
                lstYearCounts = strLine.split()

        if intYear == dtmFromDate.year:
            intStartMonth = dtmFromDate.month + 1
        else:
            intStartMonth = 1
        if intYear == dtmToDate.year:
            intEndMonth = dtmToDate.month - 1
        else:
            intEndMonth = 12


        for intMonth in range(intStartMonth, intEndMonth + 1):
            if lstYearCounts:
                intResult += int(lstYearCounts[intMonth])

        # Whole months done, now add the final days, at start and at end
    if (dtmFromDate.year, dtmFromDate.month) <> (dtmToDate.year, dtmToDate.month):
        intResult += CountToEndOfMonth(objHere, dtmFromDate)
        intResult += CountFromStartOfMonth(objHere, dtmToDate)
    else:
        intResult += CountWithinMonth(objHere, dtmFromDate, dtmToDate)
    return intResult

def RemoveObsoleteNesting(lstTokens):
    for intI in range(0, len(lstTokens)):
        if type(lstTokens[intI]) == types.ListType:
            lstTokens[intI] = RemoveObsoleteNesting(lstTokens[intI])
    if len(lstTokens) == 1 and type(lstTokens[0]) == types.ListType:
        lstTokens = lstTokens[0]
    return lstTokens
    # Replaces [['a']] with ['a']

def OperatorInQuotes(lstTokens):
    for strToken in lstTokens:
        if strToken[0] in ['"', "'"]:
            strToken = strToken.replace('"', '')
            strToken = strToken.replace("'", '')
            lstSubTokens = strToken.split()
            for strOperator in ('and', 'or', 'not'):
                if strOperator in lstSubTokens:
                    return strOperator
    return ""

def ParseTokens(lstTokens):
#    strOperator = OperatorInQuotes(lstTokens)
#    if strOperator:
#        return (None, "'%s' cannot be used between double or single quotes")

    (lstTokens, strErrorMessage) = ParseBrackets(lstTokens)
    if not lstTokens:
        return (None, strErrorMessage)

    (lstTokens, strErrorMessage) = ParseNot(lstTokens)
    if not lstTokens:
        return (None, strErrorMessage)

    lstTokens = InsertMissingAnd(lstTokens)

    (lstTokens, strErrorMessage) = ParseAndOr(lstTokens, 'and')
    if not lstTokens:
        return (None, strErrorMessage)

    (lstTokens, strErrorMessage) = ParseAndOr(lstTokens, 'or')
    if not lstTokens:
        return (None, strErrorMessage)

    lstTokens = RemoveObsoleteNesting(lstTokens)

    if lstTokens[0] == 'not':
        return (None, "'not' cannot be the main condition")

    return (lstTokens, "")

##SearchMany(objHere, "E3Message", "mailFrom", strWho)

def MemberSearch(objHere, strWho):
    lstMembers = SearchMany(objHere, "E3Member", "Name", strWho)
    lstEmailAddresses = SearchMany(objHere, "E3EmailAddress", "EmailAddress", strWho)
    for objEmailAddress in lstEmailAddresses:
#        print objEmailAddress.EmailAddress
        objMember = objEmailAddress.unrestrictedTraverse('..')
        if not objMember in lstMembers:
            lstMembers.append(objMember)
    if lstMembers:
        if len(lstMembers) == 1:
            return SearchNode((lstMembers[0].id, ), 'UserId')
        else:
            lstOrList = ['or']
            for objMember in lstMembers:
#                lstOrList.append(SearchNode((objMember.id, ), 'MemberId'))
                lstOrList.append(objMember.id)

            return SearchNode(lstOrList, 'UserId')
    else:
        return None

def ToPythonDate(dtmDate):
    dtmResult = Date(dtmDate.date(), dtmDate.month(), dtmDate.year())
    return dtmResult

def RangeSearch(dtmFromDate, dtmToDate):
    objResult = SearchNode()
    if not dtmFromDate:
        objResult.Operator = "dateto"
    elif not dtmToDate:
        objResult.Operator = "datefrom"
    else:
        objResult.Operator = "daterange"

#    objResult.FromDate = ToPythonDate(dtmFromDate)
#    objResult.ToDate = ToPythonDate(dtmToDate)
    objResult.FromDate = dtmFromDate
    objResult.ToDate = dtmToDate
    return objResult

def AttachmentSearch(blnMustHave, strAttachmentType):
    objResult = SearchNode()
    if blnMustHave:
        objResult.Operator = "attachment"
    else:
        objResult.Operator = "noattachment"
    objResult.SearchFor = strAttachmentType
    return objResult

def AddNot(objCriteria):
    objResult = SearchNode()
    objResult.Operator = "not"
    objResult.Children.append(objCriteria)
    return objResult

def AdvertSearch(blnMustHave):
    objResult = SearchNode()
    objResult.Operator = "contains"
    objResult.Field = "mailSubject"
    objResult.SearchFor = "adv"
    if not blnMustHave:
        objResult = AddNot(objResult)
    return objResult

def CombineSearchTrees(lstSearchTrees, strOperator):
    if len(lstSearchTrees) > 1:
        objResult = SearchNode()
        objResult.Operator = strOperator
        objResult.Children = lstSearchTrees
        return objResult
    elif len(lstSearchTrees) == 1:
        return lstSearchTrees[0]
    else:
        return None

def SearchFormComplete(dictForm):
    for strName in ('SearchBoth', 'SearchSubject', 'SearchBody', 'Sender'):
        if dictForm[strName]:
            return True
    if dictForm['WrittenBy'] == 'MemberMessagesOnly':
        return True
    if dictForm['Period'] <> 'Anytime':
        return True
    return False

def BuildSearchTree(objHere, objRequest, strSearchBoth):
    strOffset = ""
    if objRequest:
        strOffset = GetParameter(objRequest, "Offset")

    if strOffset:
        intOffset = int(strOffset)
    else:
        intOffset = 0

    dictForm = {}
    for strName in ('SearchBoth', 'SearchSubject', 'SearchBody', 'Sender', 'Period', 'FromDate', 'ToDate', 'FromMonth', 'ToMonth', 'FromYear', 'ToYear', 'AdvertsOption', 'AttachmentType', 'AttachmentOption', 'MemberList', 'WrittenBy'):
        if strSearchBoth:
            dictForm[strName] = DefaultSearchFormValue(strName)
        else:
            dictForm[strName] = GetParameter(objRequest, strName)
            if not dictForm[strName]:
                dictForm[strName] = DefaultSearchFormValue(strName)

    if strSearchBoth:
        dictForm['SearchBoth'] = strSearchBoth

    dictForm['Offset'] = str(intOffset)

    # Must have at least body/subject/both/who/when
    if not SearchFormComplete(dictForm):
        return (None, dictForm, "You must search for at least mail body, mail subject, who wrote it or when it was sent")
    lstSearchTrees = []

    if dictForm['Sender'] and dictForm['WrittenBy'] == 'SearchForWrittenBy':
        strSender = dictForm['Sender']
        objSender = MemberSearch(objHere, strSender)

#        lstSearchTrees.append(CombineSearchTrees([SearchNode(lstTokens, 'mailSubject'), \
#                                                 SearchNode(lstTokens, 'mailBody')], 'or'))

#        if not objSender:
#            return (None, dictForm, "No one found for '%s'" % dictForm['Sender'])
#        else:
#            return SearchNode(lstOrList, 'UserId')
        lstSearchTrees.append(CombineSearchTrees([objSender, SearchNode((strSender, ), 'mailFrom')], 'or'))

    if dictForm['WrittenBy'] == 'MemberMessagesOnly':
        objMember = GetCurrentMember(objHere)
        if objMember:
            lstSearchTrees.append(SearchNode(objMember.id, 'UserId'))

    for strField in ['SearchSubject', 'SearchBody']:
        if dictForm[strField]:
            strFieldName = {'SearchSubject': 'mailSubject', 'SearchBody': 'mailBody'}[strField]
            (lstRawTokens, strErrorMessage) = Tokenise(dictForm[strField].lower())
            if not lstRawTokens:
                return (None, dictForm, strErrorMessage)
            (lstTokens, strErrorMessage) = ParseTokens(lstRawTokens)
            if not lstTokens:
                return (None, dictForm, strErrorMessage)
            lstSearchTrees.append(SearchNode(lstTokens, strFieldName))

    if dictForm['SearchBoth']:

        (lstRawTokens, strErrorMessage) = Tokenise(dictForm['SearchBoth'].lower())
        if not lstRawTokens:
            return (None, dictForm, strErrorMessage)

        (lstTokens, strErrorMessage) = ParseTokens(lstRawTokens)
        if not lstTokens:
            return (None, dictForm, strErrorMessage)

        lstSearchTrees.append(CombineSearchTrees([SearchNode(lstTokens, 'mailSubject'), \
                                                 SearchNode(lstTokens, 'mailBody')], 'or'))

    dtmFirstDate = datetime.datetime(year = 1997, month = 1, day = 1)
    dtmLastDate = datetime.datetime.today()

    (dtmFromDate, dtmToDate) = GetDateRange(dictForm, dtmFirstDate, dtmLastDate)

    if dtmFromDate > dtmFirstDate:
        if dtmToDate < dtmLastDate:
            lstSearchTrees.append(RangeSearch(dtmFromDate, dtmToDate))
        else:
            lstSearchTrees.append(RangeSearch(dtmFromDate, None))
    else:
        if dtmToDate < dtmLastDate:
            lstSearchTrees.append(RangeSearch(dtmFromDate, dtmToDate))

    strAttachmentType = dictForm['AttachmentType']

    if dictForm['AttachmentOption'] == 'MustHave':
        if dictForm['AttachmentType'] == 'Any':
            lstSearchTrees.append(AttachmentSearch(True, ""))
            blnNeedsAnyAttachment = True
        else:
            lstSearchTrees.append(AttachmentSearch(True, strAttachmentType))

    elif dictForm['AttachmentOption'] == 'Exclude':
        lstSearchTrees.append(AttachmentSearch(False, ""))

    if dictForm['AdvertsOption'] == 'AdvertsOnly':
        lstSearchTrees.append(AdvertSearch(True))

    elif dictForm['AdvertsOption'] == 'ExcludeAdverts':
        lstSearchTrees.append(AdvertSearch(False))

    return (CombineSearchTrees(lstSearchTrees, 'and'), dictForm, None)

def FormatSearchResults(strList, strNavigationHandling, strNavigation, intThreads, strCriteria, blnFullMember):
    strTemplate = """
    <fieldset>
        <legend>Search results</legend>
        <p>%(Criteria)s</p>
        %(Found)s
        %(PublicMessage)s
    </fieldset>
    <form action="/Archive/ViewSearchResults" method="Post">
        <fieldset>
            <legend>Search again</legend>
                <p><input type="text" name="SearchBoth" class="txt"/>
                   <input name="Input" type="submit" value="Search" class="btn"/></p>
				%(AdvancedSearch)s
        </fieldset>
	</form>
    %(List)s"""
    if blnFullMember:
        strPublicMessage = ""
    else:
        strPublicMessage = """<p>To view all messages <a href="/Membership">join now</a> or log in. Membership is free for the first three months</p>"""
    if intThreads > 0:
        if blnFullMember:
            strFound = "<h2>%s message%s found</h2>" % (intThreads, IsPlural(intThreads))
        else:
            strFound = "<h2>%s public message%s found</h2>" % (intThreads, IsPlural(intThreads))
#        strFound += """<p>(The number of results may be limited to save processing time. A more detailed search may bring up messages which are not currently listed)</p>"""

        strNavigation = "<p>%s</p>" % strNavigation
        strList = "<p>&nbsp;</p>" + strNavigationHandling + strNavigation + strList + strNavigation
    else:
        if blnFullMember:
            strFound = "<h2>No messages found</h2>"
        else:
            strFound = "<h2>No public messages found</h2>"
        strList = ""
    if blnFullMember:
        strAdvancedSearch = """<p>Or go to the <a href="/Archive/AdvancedSearch">advanced search form</a></p>"""
    else:
        strAdvancedSearch = ""
    return strTemplate % {'Criteria': strCriteria,
                            'Found': strFound,
                            'PublicMessage': strPublicMessage,
                            'List': strList,
                            'AdvancedSearch': strAdvancedSearch}

def DescribeCriteria(dictForm):
    lstResult = []
    if dictForm['SearchBody']:
        lstResult.append('Message body contains "%s"' % dictForm['SearchBody'])

    if dictForm['SearchSubject']:
        lstResult.append('Message subject contains "%s"' % dictForm['SearchSubject'])

    if dictForm['SearchBoth']:
        lstResult.append('Message body or subject contains "%s"' % dictForm['SearchBoth'])

    if dictForm['WrittenBy'] == 'SearchForWrittenBy' and dictForm['Sender']:
        lstResult.append('Sender contains "%s"' % dictForm['Sender'])

    if dictForm['WrittenBy'] == 'MemberMessagesOnly':
        lstResult.append('Only my own messages')

    if dictForm['Period'] == '7Days':
        lstResult.append('Message sent in last 7 days')

    if dictForm['Period'] == '30Days':
        lstResult.append('Message sent in last 30 days')

    if dictForm['Period'] == '90Days':
        lstResult.append('Message sent in last 90 days')

    if dictForm['Period'] == 'Range':
        lstResult.append('Message sent between %s %s %s and %s %s %s' % (dictForm['FromDate'], dictForm['FromMonth'], dictForm['FromYear'], dictForm['ToDate'], dictForm['ToMonth'], dictForm['ToYear']))

    if dictForm['AttachmentOption'] == 'MustHave':
        if dictForm['AttachmentType'] == 'Any':
            lstResult.append('Must have an attachment')
        else:
            lstResult.append('Must have an attachment of type %s' % dictForm['AttachmentType'])

    elif dictForm['AttachmentOption'] == 'Exclude':
        lstResult.append('Exclude messages with an attachment')

    if dictForm['AdvertsOption'] == 'ExcludeAdverts':
        lstResult.append('Exclude adverts')

    if dictForm['AdvertsOption'] == 'AdvertsOnly':
        lstResult.append('Adverts only')

    if len(lstResult) == 0:
        return "All messages"

    elif len(lstResult) == 1:
        return "Searching for: %s" % lstResult[0]

    else:
        strResult = """Searching for:
        <ul>"""
        for strCriteria in lstResult:
            strResult = strResult + "<li>%s</li>\n" % strCriteria
        strResult = strResult + "</ul>"
        return strResult

def TimeTrace(strText):
    dtmNow = datetime.datetime.today()
    print dtmNow, strText

def SearchResults(objHere, objRequest, strSearchText = ""):
#    print ""
#    print "-" * 30
#    print "New search started"
#    print "-" * 30
#    TimeTrace("Start of Search Results")
    (objSearchTree, dictForm, strErrorMessage) = BuildSearchTree(objHere, objRequest, strSearchText)
#    TimeTrace("BuildSearchTree done")

    if objSearchTree:
#        objSearchTree.Print(0)
        objSearchTree.Search(objHere, True)
#        TimeTrace("objSearchTree.Search done")
        objSearchTree.Sort()
#        TimeTrace("objSearchTree.Sort done")

#        objSearchTree.Print(0)
        blnFullMember = IsFullMember(objHere)
        if not blnFullMember:
            objSearchTree.FilterOutPrivateMessages()
        (strList, strNavigationHandling, strNavigation, intThreads) = objSearchTree.ListResults(dictForm, blnFullMember)
        strCriteria = DescribeCriteria(dictForm)
        strResult = FormatSearchResults(strList, strNavigationHandling, strNavigation, intThreads, strCriteria, blnFullMember)
        strResult = ToUnicode(strResult)
#        try:
#            strResult = unicode(strResult, 'ascii', 'replace')
#        except:
#            pass
    else:
        strResult = RepeatForm(dictForm, strErrorMessage)
        objSearchTree = None
    return strResult

