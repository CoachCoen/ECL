# encoding: utf-8

import datetime
import math

from libDate import GetLastDate
from libDate import ShortMonthName
from libDate import MonthName

"""Functions for creating HTML chunks and pages"""

def FullURL(objHere, lstToStrip = []):
    strResult = objHere.REQUEST.VIRTUAL_URL
    strQueryString = objHere.REQUEST.QUERY_STRING
    if strQueryString:
        # Strip out any actions in the query string, since they should only be done once
        # Then re-built the query string
        lstItems = strQueryString.split('&')
        lstResult = []
        for strItem in lstItems:
            lstParts = strItem.split('=')
            blnAppend = True
            for strToStrip in lstToStrip:
                if strToStrip.lower() == lstParts[0].lower():
                    blnAppend = False
            if 'action' == lstParts[0].lower():
                blnAppend = False
            if blnAppend:
                lstResult.append(strItem)
        strQueryString = "&".join(lstResult)
        strResult += "?" + strQueryString

    return strResult

def HTMLParagraphs(strString):
    strString = strString.strip()
    if ("<p>" in strString.lower()) or ("<br>" in strString.lower()):
        if strString[:3].lower() == "<p>":
            return strString
        else:
            return "<p>%s</p>" % strString
    else:
        lstLines = strString.split("\n")
        strResult = ""
        for strLine in lstLines:
            strLine = strLine.strip()
            if strLine:
                strResult += "<p>%s</p>\n" % strLine
    return strResult

def PutInFieldset(strTitle, strData):
    if not strData:
        return ""
    return """<fieldset>
    <legend>%s</legend>
%s
</fieldset>""" % (strTitle, strData)

def PutInARow(lstItems):
    strResult = "<tr>\n"
    for varItem in lstItems:
        strItem = "%s" % varItem
        if not strItem:
            strItem = "&nbsp;"
        strResult += """<td>%s</td>\n""" % strItem
    strResult += "</td>\n"
    return strResult

def GetPageList(strLink, intThreads, intMaxPages, intOffset):
    """Create a line of page numbers, with links to the other pages,
        note: strLink can be something like "Javascript: GotoPage(%s)"
        The code will fill in the page number"""
    strResult = ""
    lstResult = []
    intFirstPage = 0
    intLastPage = int(math.ceil((intThreads - 1)/intMaxPages))
    intCurrentPage = int(intOffset/intMaxPages)
    if intLastPage - intFirstPage > 10:
        intFirstPage = intCurrentPage - 5
        intLastPage = min(intLastPage, intCurrentPage + 5)
    if intLastPage - intFirstPage < 10:
        intFirstPage = max(0, intLastPage - 10)
    if intFirstPage < 0:
        intLastPage = intLastPage - intFirstPage
        intFirstPage = 0
    for intI in range(intFirstPage, intLastPage + 1):
        if intCurrentPage == intI:
            lstResult.append("[%s]" % (intI + 1))
        else:
            lstResult.append("""<a href="%s">%s</a>""" % (strLink % (intI * intMaxPages), intI + 1))
    return " ".join(lstResult)

def BuildPagingList(intMaxMessages, intThreads, intFirstThread, intLastThread, strLink, intOffset):
    """Create navigation line, something like:
        Showing threads 1 to 200 - Previous Page - 1 2 3 4 5 - Next Page"""
    strResult = """Showing messages %(FirstThread)s to %(LastThread)s - """ % {'FirstThread': intFirstThread,
                'LastThread': intLastThread}

    if intOffset > 0:
        intPreviousOffset = max(intOffset - intMaxMessages, 0)
        strResult = strResult +  """<a href="%s">Previous Page</a> - """ % (strLink % intPreviousOffset)

    strResult = strResult + GetPageList(strLink, intThreads, intMaxMessages, intOffset)

    if intOffset + intMaxMessages < intThreads:
        intNextOffset = intOffset + intMaxMessages
        strResult = strResult +  """ - <a href="%s">Next Page</a>""" % (strLink % intNextOffset)

    return strResult

def ShowSelected(blnIsSelected):
    if blnIsSelected:
        return " selected "
    return ""

def ShowChecked(blnIsChecked):
    if blnIsChecked:
        return " checked "
    return ""

def IsPlural(intCount):
    if intCount <> 1:
        return "s"
    return ""

def GetMonthDropdown(intMonth):
    """Creates dropdown box, listing the months, with intMonth selected
        Fieldname is 'Month'
        Returns the month number"""
    strResult = """<select name="Month">\n"""
    for intI in range(1, 13):
        strSelected = ""
        if intI == intMonth:
            strSelected = " selected "
        strMonth = MonthName(intI)
        strResult = strResult + """<option%s value="%s">%s</option>\n""" % (strSelected, intI, strMonth)
    strResult = strResult + "</select>\n"
    return strResult

def GetYearDropdown(intYear, intStartYear = 1997):
    """Creates dropdown box, listing years between intStartYear and current year,
        with intYear selected
        Fieldname is 'Year'
        intStartYear defaults to 1997"""
    dtmNow = datetime.datetime.today()
    strResult = """<select name="Year">\n"""
    for intI in range(dtmNow.year, 1997, -1):
        strSelected = ""
        if intI == intYear:
            strSelected = " selected "
        strResult = strResult + "<option%s>%s</option>\n" % (strSelected, intI)
    strResult = strResult + "</select>\n"
    return strResult

def GetDateDropdown(intYear, intMonth, intDate = 0):
    """Creates dropdown box, listings days between 1 and maximum
        day for intYear/intMonth, with intDate selected
        Fieldname is 'Date'"""
    strResult = """<select name="Date">
                    <option selected value="0">Whole month</option>\n"""

    intLastDate = GetLastDate(intYear, intMonth)
    for intI in range(1, intLastDate + 1):
        if intI == intDate:
            strSelected = 'selected'
        else:
            strSelected = ''
        strResult = strResult + """<option %s value="%s">%s %s %s</option>\n""" % (strSelected, intI, intI, ShortMonthName(intMonth), str(intYear)[2:])
    strResult = strResult + "</select>"
    return strResult

def SimpleDropdown(strName, lstOptions, varSelected, strAdditionalAttributes = ""):
    """Create dropdown box
        lstOptions is a list of values, which are shown and returned
        varSelected is the value that is currently selected
        strName is the fieldname"""
    strResult = """<select name="%s" %s>
        """ % (strName, strAdditionalAttributes)
    for varValue in lstOptions:
        strResult = strResult + """<option %s>%s</option>\n""" % (ShowSelected(varValue == varSelected), varValue)
    strResult = strResult + "</select>"
    return strResult

def BuildDropdownList(strName, strFirstOption, lstOptions):
    """Create dropdown box
        lstOptions is a list of (text, value)
        FirstOption is the one that will be selected, the first one in the list
        strName is the fieldname"""
    strResult = """<select name="%s">
        <option selected>%s</option>
        """ % (strName, strFirstOption)
    for (strText, strValue) in lstOptions:
        strResult = strResult + """<option value="%s">%s</option>\n""" % (strValue, strText)
    strResult = strResult + "</select>"
    return strResult

def ShowIf(blnCondition, strToShow):
    """If blnCondition return strToShow otherwise return blank"""
    if blnCondition:
        return strToShow
    return ""

def InsertParagraphs(strString):
    lstString = strString.split("\n")
    strResult = ""
    for strLine in lstString:
        strResult += "<p>%s</p>\n" % strLine
    return strResult

def InsertBrs(strBody):
    """Replace crlf with <br>"""
    strResult = strBody.replace('\n', '<br>\n')
    return strResult

def FormatLinksForHTML(strText):
    """Remove all double quotes"""
    strNewText = strText.replace('"', '')
#    lstText = string.split(strText, '"')
#    strNewText = string.join(lstText, '')
    return strNewText

def PointURLAtMCI(strAbsoluteURL):
    """Change relative url into absolute url"""
    strURL = strAbsoluteURL
    intPosition = strURL.find("/MCI/")
    strURL = "http://www.MentorCoaches.com/" + strURL[intPosition+5:]
    return strURL
