import random
import string

from libForms import CreateForm, FormProcessing, ReportErrors
from libForms import LoadDataFromObject, CheckRequiredFields
from libForms import SaveNewFromForm
from E3Members import GetCurrentMember
from libConstants import cnProfileFieldNames
from libConstants import cnCountryNames
from libConstants import cnProductFieldNames
from libConstants import cnServiceFieldNames
from libConstants import cnEventFieldNames
from libConstants import cnPnSCategories
from libConstants import cnEventCategories
from libConstants import cnMOGroups
from libConstants import cnEventMOGroups
from libConstants import cnRelationOptions
from libConstants import cnEventRelationOptions
from libConstants import cnDictRelationOptions
from libConstants import cnRoles
from libConstants import cnEventRoles
from libConstants import cnOrganisationTypes
from libForms import GetDataFromForm
from libDatabase import Catalogue
from libGeneral import GetParameter
from libDatabase import SearchOne
from libDatabase import SearchMany
from libDatabase import GetDOD
from libDatabase import GetDataFolder
from libForms import UpdateObjectFromData
from LocalPaths import cnLocalPathExtensions
from E3Members import IsFullMember
from E3TempData import SetMessage
from libBuildHTML import InsertBrs
from libEmail import SendEmail
from libBuildHTML import HTMLParagraphs
from libString import ListToText
from libDate import ShortMonthName
from libDate import MonthName
from libString import TruncateLine
from libConstants import cnFirstDate
from libGeneral import CombineLists
from libProcessHTML import HTMLToText

import datetime

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEMessage import MIMEMessage

from libForms import Fieldset
from libForms import Paragraph
from libForms import Tabset
from libForms import OneTab
from libForms import CheckboxControl
from libForms import TextControl
from libForms import HiddenControl
from libForms import SelectControl
from libForms import TextArea
from libForms import RichTextArea
from libForms import SubmitControl
from libForms import PureText
from libForms import MultiOptionBlock
from libForms import AddOneOption
from libForms import DateControl
import urllib

from libString import ToUnicode
from libString import PrepareMessageText
from StringValidator import StringValidator

import xml.sax.saxutils

from libBuildHTML import FullURL

cnConvertReason = {'Advert': 'own', 'Recommendation': 'recommend', 'Listing': 'interest'}

def GetOrganisationNameForId(objHere, strOrganisationId):
    if strOrganisationId:
        objOrganisation = SearchOne(objHere, "E3Organisation", "id", strOrganisationId)
        if objOrganisation:
            return objOrganisation.Name
    return ""

def GetEventSeriesDetails(objHere, strEventSeriesId):
    if strEventSeriesId:
        objEventSeries = SearchOne(objHere, "E3EventSeries", "id", strEventSeriesId)
        if objEventSeries:
            return (objEventSeries.Title, objEventSeries.Description)
    return ("", "")

def GetComingEvents(objHere, intMaxEvents):
    dtmToday = datetime.date.today()
    lstEvents = SearchMany(objHere, "E3Offering", "Type", "Event")
    dictResult = {}
    for objEvent in lstEvents:
        if objEvent.Status == "Published" and objEvent.Live():
            dtmStartDate = objEvent.GetStartDate()
            if dtmStartDate > dtmToday:
                if not dictResult.has_key(dtmStartDate):
                    dictResult[dtmStartDate] = []
                dictResult[dtmStartDate].append(objEvent)

    lstDates = dictResult.keys()
    lstDates.sort()
    lstResult = []
    for dtmDate in lstDates:
        for objEvent in dictResult[dtmDate]:
            lstResult.append(objEvent)
            if len(lstResult) >= intMaxEvents:
                return lstResult
    return lstResult

def ListOneEventForHomePage(objEvent):
    strDescription = objEvent.TruncatedDescription(80)

    if strDescription:
        strDescription = """<div class="HomePageText">%s</div>""" % strDescription

    strBy = objEvent.GetBy(True)
    if "Anonymous" in strBy:
        strBy = ""

    strResult = """
    <a href="/Offerings?Id=%s" class="HomePageBlock">
        <div class="HomePageTitle">%s</div>
        <div class="HomePageSubtitle">(%s%s)</div>
        %s
    </a>
    """ % (objEvent.id, objEvent.myTitle, objEvent.DateDescription, strBy, strDescription)
    return strResult

def ShowComingEvents(objHere):
    lstEvents = GetComingEvents(objHere, 3)
    strEvents = ""

    for objEvent in lstEvents:
        strEvents += ListOneEventForHomePage(objEvent)

    if strEvents:
        strResult = """
<fieldset class="HomePage">
    <legend>Events organised for and by Coaches</legend>
    %s
    <a href="/Events" class="HomePageBlock">
        <div class="HomePageSubtitle">Show all events</div>
    </a>
</fieldset>
""" % strEvents
    else:
        strResult = ""
    return strResult

def ChooseFeaturedOffering(objHere):
    lstUnfeaturedOfferings = []
    lstFeaturedOfferings = []

    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objOffering in objMember.Offerings.objectValues("E3Offering"):
                if objOffering.CanFeature():
                    if objOffering.GetLastFeatured() < cnFirstDate:
                        lstUnfeaturedOfferings.append(objOffering)
                    else:
                        lstFeaturedOfferings.append(objOffering)

    if lstUnfeaturedOfferings:
        objOffering = random.choice(lstUnfeaturedOfferings)
        return objOffering

    dictFeaturedOfferings = {}
    for objOffering in lstFeaturedOfferings:
        dictFeaturedOfferings[objOffering.GetLastFeatured] = objOffering

    lstDates = dictFeaturedOfferings.keys()
    lstDates.sort()
    objOffering = dictFeaturedOfferings[lstDates[0]]

    return objOffering

def RecordFeaturedOffering(objHere, strId):
    objData = objHere.unrestrictedTraverse("/Data/E3")
    objData.RecentFeaturedOfferings = objData.RecentFeaturedOfferings + (strId, )

def ShowFeaturedOffering(objHere):
    objOffering = ChooseFeaturedOffering(objHere)
    objOffering.SetLastFeatured(datetime.date.today())
    RecordFeaturedOffering(objHere, objOffering.id)

    strBy = objOffering.GetBy(True)
    if strBy:
        strBy = """<div class="HomePageSubtitle">%s</div>
        """ % strBy

    (blnDummy, strDescription) = PrepareMessageText(objOffering.Description, 200, False)

    strResult = """
<fieldset class="HomePage">
    <legend>Featured offering</legend>
    <a href="/Offerings?Id=%s" class="HomePageBlock">
        <div class="HomePageTitle">%s</div>
        %s
        <div class="HomePageText">%s</div>
    </a>

    <a href="/Offerings" class="HomePageBlock">
       <div class="HomePageSubtitle">Show all products and services</div>
    </a>
</fieldset>
""" % (objOffering.id, objOffering.myTitle, strBy, strDescription)

    try:
        strResult = unicode(strProfile, 'utf-8', 'replace')
    except:
        pass
    return strResult

def CheckHasEvents(objHere, intYear, intMonth):
    dictDayHasEvent = {}
    for intI in range (1, 32):
        dictDayHasEvent[intI] = False

    dictMonthHasEvent = {}
    for intI in range (1, 13):
        dictMonthHasEvent[intI] = False

    dictYearHasEvent = {}
    for intI in range(1990, 2100):
        dictYearHasEvent[intI] = False

    lstEvents = SearchMany(objHere, "E3Offering", "Type", "Event")
    for objEvent in lstEvents:
        if objEvent.Status == "Published" and objEvent.Live():
            dtmStartDate = objEvent.GetStartDate()
            if dtmStartDate.year == intYear:
                if dtmStartDate.month == intMonth:
                    dictDayHasEvent[dtmStartDate.day] = True
                dictMonthHasEvent[dtmStartDate.month] = True
            dictYearHasEvent[dtmStartDate.year] = True

    return (dictDayHasEvent, dictMonthHasEvent, dictYearHasEvent)

def CalendarLink(strFullURL, intYear, intMonth = None, intDate = None):
    strResult = strFullURL + "Year=%s" % intYear
    if intMonth:
        strResult += "&Month=%s" % intMonth
        if intDate:
            strResult += "&Date=%s" % intDate
    return strResult

def EventCalendar(objHere):
#    strFullURL = FullURL(objHere, ('month', 'year', 'day'))
#    if "?" in strFullURL:
#        strFullURL += "&"
#    else:
#        strFullURL += "?"
    strFullURL = "/Events?"
    dtmNow = datetime.date.today()
#    intMonth =
    strResult = "Calendar here please"
    strMonth = GetParameter(objHere, "Month")
    if strMonth:
        intMonth = int(strMonth)
    else:
        intMonth = dtmNow.month
    strYear = GetParameter(objHere, "Year")
    if strYear:
        intYear = int(strYear)
    else:
        intYear = dtmNow.year

    (dictDayHasEvent, dictMonthHasEvent, dictYearHasEvent) = CheckHasEvents(objHere, intYear, intMonth)

    intPrevYear = intYear
    intPrevMonth = intMonth - 1
    if not intPrevMonth:
        intPrevMonth = 12
        intPrevYear -= 1

    intNextYear = intYear
    intNextMonth = intMonth + 1
    if intNextMonth > 12:
        intNextMonth = 1
        intNextYear += 1

    strResult = """
<table class="Calendar">
    <tr>
        <td colspan="7" class="Title"><a href="%s">&lt;&lt;</a>&nbsp;&nbsp;%s %s&nbsp;&nbsp;<a href="%s">&gt;&gt;</a></td>
    </tr>
    <tr>
        <td>Mo</td>
        <td>Tu</td>
        <td>We</td>
        <td>Th</td>
        <td>Fr</td>
        <td>Sa</td>
        <td>Su</td>
    </tr>
    <tr>
""" % (CalendarLink(strFullURL, intPrevYear, intPrevMonth), MonthName(intMonth), intYear,
       CalendarLink(strFullURL, intNextYear, intNextMonth))
    dtmDate = datetime.date(intYear, intMonth, 1)
    intWeekDay = dtmDate.weekday()
    if intWeekDay:
        for intI in range(0, intWeekDay):
            strResult += "<td>&nbsp;</td>\n"
    while dtmDate.month == intMonth:
        if dictDayHasEvent[dtmDate.day]:
            strDay = str(dtmDate.day)
            if len(strDay) == 1:
                strDay = "&nbsp;&nbsp;" + strDay
            strResult += """<td class="HasEvent"><a href="%s">%s</a></td>\n""" % \
                (CalendarLink(strFullURL, intYear, intMonth, dtmDate.day), strDay)
        else:
            strResult += """<td class="NoEvent">%s</td>\n""" % dtmDate.day
        dtmDate += datetime.timedelta(days=1)
        if not dtmDate.weekday() and dtmDate.month == intMonth:
            strResult += "</tr>\n<tr>\n"
    if dtmDate.weekday():
        for intI in range(dtmDate.weekday(), 7):
            strResult += "<td>&nbsp;</td>\n"
    strResult += "</table>\n"

    strResult += """<table class="Calendar">\n"""
    intCellMonth = 1
    for intI in range(0, 2):
        strResult += "<tr>\n"
        for intJ in range(0, 6):
            if dictMonthHasEvent[intCellMonth]:
                strResult += """<td class="HasEvent"><a href="%s">%s</a></td>\n""" % \
                (CalendarLink(strFullURL, intYear, intCellMonth),ShortMonthName(intCellMonth).lower())
            else:
                strResult += """<td class="NoEvent">%s</td>\n""" % ShortMonthName(intCellMonth).lower()
            intCellMonth += 1
        strResult += "</tr>\n"
#    strResult += "</table>\n"

#    strResult += """<table class="Calendar">\n"""
    strResult += "<tr>\n"
    for intI in range(intYear - 1, intYear + 2):
        if dictYearHasEvent[intI]:
            strResult += """<td class="HasEvent" colspan="2"><a href="%s">%s</a></td>\n""" % \
                (CalendarLink(strFullURL, intI), intI)
        else:
            strResult += """<td class="NoEvent" colspan="2">%s</td>\n""" % intI
    strResult += "</tr>\n"
    strResult += "</table>\n"
    return strResult

def SortByTitle(objOffering1, objOffering2):
    return cmp(objOffering1.GetTitle(), objOffering2.GetTitle())

def FormatOfferingList(objHere, lstOfferings):
    lstOfferings.sort(SortByTitle)
    strResult = ""
    blnFullMember = IsFullMember(objHere)
    for objOffering in lstOfferings:
        strResult += FormatOneOffering(objOffering, blnFullMember)
    return strResult

def ListBooksByMembers(objHere):
    lstProducts = SearchMany(objHere, "E3Offering", "Type", "Service") + SearchMany(objHere, "E3Offering", "Type", "Product")
    lstBooks = []
    for objProduct in lstProducts:
        if "book" in objProduct.Category.lower() and objProduct.IsOwn() and objProduct.Live() and objProduct.Status == "Published":
            lstBooks.append(objProduct)
    if lstBooks:
        strResult = FormatOfferingList(objHere, lstBooks)
    else:
        strResult = "<p>No books found</p>"
    return strResult

def ListRolesForEvent(objOffering, blnFullMember):
    strResult = ""
    lstRoles = SearchMany(objOffering, "E3Role", "ItemId", objOffering.id)
    for objRole in lstRoles:
        objMember = SearchOne(objOffering, "E3Member", "id", objRole.MemberId)
        strResult += "<form>%s</form>" % objMember.ProfilePersonalDetails(blnFullMember, objRole.RoleType, True)
    return strResult

def CreateLocationDescription(objOffering):
    lstResult = []
    if objOffering.InternetBased:
        lstResult.append("Internet")

    if objOffering.TelephoneBased:
        lstResult.append("telephone")

    if objOffering.FaceToFace:
        strF2F = "face to face"
        if objOffering.Country <> "Enter the country":
            strCountry = objOffering.Country
        else:
            strCountry = ""
        if strCountry or objOffering.Location:
            strF2F += ": "
            if strCountry:
                strF2F += strCountry
                if objOffering.Location:
                    strF2F += ", "
            strF2F += objOffering.Location
        lstResult.append(strF2F)

    if not lstResult and (objOffering.Country <> "Enter the country" or objOffering.Location):
        strResult = ""
        if objOffering.Country <> "Enter the country":
            strResult = objOffering.Country
            if objOffering.Location:
                strResult += ", "
        strResult += objOffering.Location
    else:
        strResult = "By " + ", ".join(lstResult)

    return strResult

def EventSeriesForEvent(objOffering):
    # If this event is part of an event series, show all events for this series
    strEventSeriesId = objOffering.EventSeriesId
    if not strEventSeriesId:
        return ""

    objEventSeries = SearchOne(objOffering, "E3EventSeries", "id", strEventSeriesId)
    if not objEventSeries:
        return ""

    strResult = """
<fieldset>
    <legend>Part of %s</legend>
    <p>Series title: %s</p>
""" % (objEventSeries.Title, objEventSeries.Title)

    if objEventSeries.Description:
        strResult += "<p>%s</p>\n" % objEventSeries.Description

    lstEvents = SearchMany(objOffering, "E3Offering", "EventSeriesId", strEventSeriesId)
    lstResult = []
    for objEvent in lstEvents:
        if objEvent.Status == "Published":
            lstResult.append(objEvent)

    if len(lstResult) > 1:
        lstResult.sort(SortByDate)
        strResult += "<p>All events in this series:</p>"
        strResult += "<ul>\n"
        for objEvent in lstResult:
            strResult += """<li>%s <a href="/Events?EventId=%s">%s</a> (%s)</li>\n""" % (objEvent.DateDescription, objEvent.id, objEvent.myTitle, objEvent.Category)
        strResult += "</ul>\n"
    else:
        strResult += "<p>No other events listed (yet) in this series</p>\n"

    strResult += "</fieldset>\n"
    return strResult

def ShowOneEvent(objOffering, strSendersName = "", strSendersEmailAddress = "", strSendersComments = ""):
    strResult = u""
    objMember = objOffering.unrestrictedTraverse('../../')
    blnFullMember = IsFullMember(objMember)

    blnAdvert = ("own" in objOffering.Relation)

    strWhere = objOffering.Location

    if objOffering.Description:
        strDescription = objOffering.Description
        if not "<" in strDescription and not ">" in strDescription:
            strDescription = InsertBrs(strDescription)
        strDescription = "<p>%s</p>" % ToUnicode(strDescription)
    else:
        strDescription = ""

    strDetails = """
<fieldset>
    <legend>%s</legend>
    <p>%s</p>
    <p>%s</p>
    <p>Submitted by <a href="/Members/ViewProfile?MemberId=%s">%s</a></p>
    %s
</fieldset>
""" % (objOffering.myTitle, objOffering.DateDescription, strWhere, objMember.id, objOffering.GetMemberName(blnFullMember), strDescription)

    strResult += strDetails

    if objOffering.OfferForMembers and blnFullMember:
        strResult += ToFieldset("Special offer for Euro Coach List members", objOffering.OfferForMembers)

    strResult += GetTargetAudienceBlock(objOffering)
    strResult += GetCoversBlock(objOffering)

    if objOffering.WebsiteAddress:
        strLink = """<p>Go to <a href="%s" target="_blank">%s</a></p>""" % (objOffering.WebsiteAddress, objOffering.WebsiteAddress)
        strResult += ToFieldset("More information", strLink)

    strResult += ToUnicode(EventSeriesForEvent(objOffering))

    if objOffering.OrganisationId <> "Own":
        objOrganisation = SearchOne(objOffering, "E3Organisation", "id", objOffering.OrganisationId)
        if objOrganisation:
            strResult += ToUnicode(objOrganisation.DetailsBlock("Organised by/for"))

    strResult += ListRolesForEvent(objOffering, blnFullMember)
#    if blnAdvert:
#        strResult += """<form action="#">%s</form>""" % \
#            (objMember.ProfilePersonalDetails(blnFullMember, "Provided by", True) + \
#            objMember.ProfileContactDetails(blnFullMember))

    strResult = ToUnicode(strResult)
#    if blnAdvert:
#        strNamePlusLink = """<a href="/Members/ViewProfile?MemberId=%s">%s</a>""" % (objMember.id, objOffering.GetMemberName(blnFullMember))
#        strResult += ContactFormForOffering(objOffering, strNamePlusLink, strSendersName, strSendersEmailAddress, strSendersComments)

    # if event series, list full series here

    return strResult

def ShowEvents(objHere):
    strEventId = GetParameter(objHere, "EventId")
    if strEventId:
        objEvent = SearchOne(objHere, "E3Offering", "id", strEventId)
        if objEvent and objEvent.Type == "Event" and objEvent.Status == "Published" and objEvent.Live():
            return ShowOneEvent(objEvent)

    blnFullMember = IsFullMember(objHere)

    dtmNow = datetime.date.today()
    intDate = 0
    strDate = ""

    strYear = GetParameter(objHere, "Year")
    if strYear:
        intYear = int(strYear)

        strMonth = GetParameter(objHere, "Month")
        if strMonth:
            intMonth = int(strMonth)
            strDate = GetParameter(objHere, "Date")
            if strDate:
                intDate = int(strDate)
        else:
            intMonth = dtmNow.month
    else:
        intYear = dtmNow.year
        intMonth = dtmNow.month

    if intDate:
        dtmDate = datetime.date(intYear, intMonth, intDate)
    else:
        dtmFrom = datetime.date(intYear, intMonth, 1)
        intNextMonth = intMonth + 1
        if intNextMonth > 12:
            intNextYear = intYear + 1
            intNextMonth = 1
        else:
            intNextYear = intYear
        dtmBefore = datetime.date(intNextYear, intNextMonth, 1)

    lstResult = []
    lstEvents = SearchMany(objHere, "E3Offering", "Type", "Event")
    for objEvent in lstEvents:
#        print objEvent.GetStartDate(), objEvent.Status
        if objEvent.Status == "Published" and objEvent.Live():
            dtmStartDate = objEvent.GetStartDate()
            if (intDate and dtmStartDate == dtmDate) or (not intDate and dtmStartDate >= dtmFrom and dtmStartDate < dtmBefore):
                lstResult.append(objEvent)

    strTitle = "Events listing for %s %s %s" % (strDate, MonthName(intMonth), intYear)
    strResult = "<h2>%s</h2>\n" % strTitle

    if not lstResult:
        return strResult + "<p>No events found. Please check again later</p>"

    if len(lstResult) == 1:
        return ShowOneEvent(lstResult[0])


    lstResult.sort(SortByDate)

    for objEvent in lstResult:
        strResult += objEvent.SummaryBlock(blnFullMember)

    return strResult

def SortBy(objItem1, objItem2, lstProperties):
    for strProperty in lstProperties:
        intCompare = cmp(objItem1.getProperty(strProperty), \
            objItem2.getProperty(strProperty))
        if intCompare:
            return intCompare
    return intCompare

def SortByRoleAndName(objItem1, objItem2):
    if objItem1[0] <> objItem2[0]:
        return cmp(objItem[0], objItem2[0])
    return cmp(objItem1[2], objItem2[2])

def GetPeopleForItem(objHere, strItemId, blnFullMember):
    lstPeople = []
    for objRole in SearchMany(objHere, "E3Role", "ItemId", strItemId):
        objMember = SearchOne(objHere, "E3Member", "id", objRole.MemberId)
        lstPeople.append((objRole.RoleType, objMember.id, objMember.VisibleName(blnFullMember)))
    lstPeople.sort(SortByRoleAndName)
    strResult = ""
    for (strRole, strId, strName) in lstPeople:
        strResult += """<li>%s: <a href="/Members/ViewProfile?MemberId=%s">%s</a></li>\n""" % (strRole, strId, strName)
    return strResult

def SortByDate(objEvent1, objEvent2):
    return cmp(objEvent1.StartDate, objEvent2.StartDate)

def GetEventsForOrganisation(objOrganisation, blnFutureEvents):
    dtmNow = datetime.date.today()
    lstResult = []
    lstEvents = SearchMany(objOrganisation, "E3Offering", "Type", "Event")
    for objEvent in lstEvents:
        if objEvent.OrganisationId == objOrganisation.id:
            if (blnFutureEvents and objEvent.GetStartDate() >= dtmNow) or \
                (not blnFutureEvents and objEvent.GetStartDate() < dtmNow):
                lstResult.append(objEvent)

    lstResult.sort(SortByDate)

    strResult = ""
    for objEvent in lstResult:
        if objEvent.Status == "Published":
            strResult += """<li>%s <a href="/Events?EventId=%s">%s</a></li>\n""" % (objEvent.DateDescription, objEvent.id, objEvent.myTitle)
    return strResult

def ShowOneOrganisationInFull(objOrganisation):
    blnFullMember = IsFullMember(objOrganisation)
#    strCreatedById = objOrganisation.CreatedBy
#    objMember = SearchOne(objOrganisation, "E3Member", "id", strCreatedById)
#    strCreatedName = objMember.VisibleName(blnFullMember)

    strResult = """
<fieldset>
    <legend>%s</legend>
    <p>%s</p>
    <p>%s</p>
</fieldset>
""" % (objOrganisation.Name, objOrganisation.OrganisationType, objOrganisation.Description)

    strResult = ToUnicode(strResult)

    strPeople = GetPeopleForItem(objOrganisation, objOrganisation.id, blnFullMember)
    if strPeople:
        strResult +=  """
<fieldset>
    <legend>People</legend>
    <ul>
    %s
    </ul>
</fieldset>""" % strPeople

    strEvents = GetEventsForOrganisation(objOrganisation, True)
    if strEvents:
        strResult +=  """
<fieldset>
    <legend>Coming events</legend>
    <ul>
    %s
    </ul>
</fieldset>""" % strEvents

    strEvents = GetEventsForOrganisation(objOrganisation, False)
    if strEvents:
        strResult +=  """
<fieldset>
    <legend>Past events</legend>
    <ul>
    %s
    </ul>
</fieldset>""" % strEvents

    return strResult

def SortByTypeAndName(objOrg1, objOrg2):
    if objOrg1.OrganisationType == objOrg2.OrganisationType:
        return cmp(ToUnicode(objOrg1.Name), ToUnicode(objOrg2.Name))
    return cmp(objOrg1.OrganisationType, objOrg2.OrganisationType)

def ShowOneOrganisation(objOrganisation):
    # Name, description
    strResult = """<p><a href=".?OrganisationId=%s">%s</a></p>\n""" % (objOrganisation.id, objOrganisation.Name)
    return strResult

def ShowOrganisations(objHere, blnNetworks = True, blnNonNetworks = True):
    strOrganisationId = GetParameter(objHere, "OrganisationId")
    if strOrganisationId:
        objOrganisation = SearchOne(objHere, "E3Organisation", "id", strOrganisationId)
#        print "OrganisationId: ", strOrganisationId
        if objOrganisation:
            return ShowOneOrganisationInFull(objOrganisation)

    lstOrganisations = []
    for objBatch in GetDataFolder(objHere, "E3Organisation").objectValues("Folder"):
        for objOrganisation in objBatch.objectValues("E3Organisation"):
            if (blnNetworks and blnNonNetworks) or \
                (blnNetworks and "network" in objOrganisation.OrganisationType.lower()) or \
                (blnNonNetworks and not "network" in objOrganisation.OrganisationType.lower()):
                lstOrganisations.append(objOrganisation)

    lstOrganisations.sort(SortByTypeAndName)
    strResult = ""
    strOrganisationType = ""
    for objOrganisation in lstOrganisations:
        if objOrganisation.OrganisationType <> strOrganisationType:
            strResult += "<h2>%s</h2>\n" % objOrganisation.OrganisationType
            strOrganisationType = objOrganisation.OrganisationType
        strResult += ToUnicode(ShowOneOrganisation(objOrganisation))

    if not strResult:
        strResult = "<p>No organisations found. Please check again later</p>"

    if not blnNetworks:
        strResult += """<p>See also the <a href="/Networks">list of networking organisations</a></p>"""

    return strResult

def EventSeriesForm(strAction, strButton, lstOrganisations):
    return (Fieldset("Offerings - %s an event series" % strAction, None,
                Paragraph(
                    TextControl("Title", "Title"), HiddenControl('EventSeriesId')),
                Paragraph(
                    SelectControl("Organised by", 'OrganisationId', lstOrganisations, "To add an organisation use the Organisations tab", True)),
                Paragraph(
                    TextArea('Description', 'Description')),
                Paragraph(
                    SubmitControl(strButton))), )

def NewEventSeriesForm(objMember):
    lstOrganisations = GetOrganisations(objMember)
    lstOrganisations = [('Own event series', 'Own'), ] + lstOrganisations

    lstForm = EventSeriesForm("Add", 'Add an event series', lstOrganisations)
    strResult = CreateForm(objMember, lstForm, {}, dictHiddenFields = {"CreatedBy": objMember.id})
    return strResult

def ValidateEventSeries(dictData, objEventSeries):
    return CheckRequiredFields(dictData, ('Title', ))

def EditEventSeriesForm(objEventSeries, blnUpdate, lstOrganisations):

    lstFields = ("Title", "OrganisationId", "Description")
    lstLoadFields = lstFields + ('EventSeriesId', )
    lstFormFields = lstFields + ('EventSeriesId', )

    lstForm = EventSeriesForm("Update", 'Update event series', lstOrganisations)
    dictData = {}
    dictData['EventSeriesId'] = objEventSeries.id
    strResult = FormProcessing(objEventSeries, lstLoadFields, lstForm, blnUpdate, ValidateEventSeries, lstFields, lstFormFields, dictData)
    return strResult

def GetEventSeriesList(objMember):
    strResult = ""
    lstEventSeries = GetExistingEventSeries(objMember, objMember.id)
    for (strTitle, strId) in lstEventSeries:
        strResult += """<li><a href=".?EventSeriesId=%s">%s</a></li>\n""" % (strId, strTitle)
    return strResult

def GetEventSeriesTab(objMember):
    strResult = ""
    blnDefaultTab = False

    strSubmitButton = GetParameter(objMember, "SubmitButton")
    blnUpdateEventSeries = (strSubmitButton == "Update event series")
    blnAddEventSeries = (strSubmitButton == "Add an event series")
    blnDefaultTab = (blnUpdateEventSeries or blnAddEventSeries)

    lstOrganisations = GetOrganisations(objMember)
    lstOrganisations = [('Own event series', 'Own'), ] + lstOrganisations

    # If EventSeriesId, then start with form to edit it
    strEventSeriesId = GetParameter(objMember, "EventSeriesId")
    if strEventSeriesId:
        objEventSeries = SearchOne(objMember, "E3EventSeries", "id", strEventSeriesId)
        if objEventSeries:
            strResult += EditEventSeriesForm(objEventSeries,  blnUpdateEventSeries, lstOrganisations)
            blnDefaultTab = True

    if blnAddEventSeries or (blnUpdateEventSeries and not strEventSeriesId):
        lstFields = ("Title", "OrganisationId", "Description", "CreatedBy")
        lstForm = EventSeriesForm("Update", 'Update event series', lstOrganisations)
        (objEventSeries, strForm) = SaveNewFromForm(objMember, "E3EventSeries", lstFields, lstForm, ValidateEventSeries, strIdField = "EventSeriesId")
        strResult += strForm

    strResult += NewEventSeriesForm(objMember)

    strEventSeriesList = GetEventSeriesList(objMember)
    if strEventSeriesList:
        strResult += """
<fieldset>
    <legend>Offerings - Your event series</legend>
    <ul>
        %s
    </ul>
</fieldset>""" % ToUnicode(strEventSeriesList)
    return (strResult, blnDefaultTab)

def SortByTitle(objOne, objTwo):
    return cmp(objOne.Title, objTwo.Title)

def ListOneEvent(objEvent):
    strResult = """
<p id="MessageBox1"><a href="/MyECL/Events/Edit?id=%s">%s, %s (%s)</a></p>""" % (objEvent.id, objEvent.myTitle, objEvent.DateDescription, objEvent.Category)
    return strResult

def GetEventsList(objMember):
    lstResult = []
    for objOffering in objMember.Offerings.objectValues("E3Offering"):
        if objOffering.Type == "Event":
            lstResult.append(objOffering)

    lstResult.sort(SortByTitle)

    strResult = ""
    for objOffering in lstResult:
        strResult += ListOneEvent(objOffering)

#    if not strResult:
#        strResult = "<p>No events listed</p>"
    return strResult

def GetEventsTab(objMember):
    strEventsList = GetEventsList(objMember)
    strResult = """
<fieldset>
    <legend>Add a new event</legend>
    <p><a href="/MyECL/Events/Edit">Go to the new events page</a></p>
</fieldset>"""
    if strEventsList:
        strResult += """
<fieldset>
    <legend>Events</legend>
    %s
</fieldset>""" % strEventsList
    return strResult

def SortByName(objOne, objTwo):
    return cmp(ToUnicode(objOne.Name), ToUnicode(objTwo.Name))

def ListOneOrganisation(objOrganisation):
    strResult = """
<p><a href="/MyECL?OrgId=%s">%s (%s)</a></p>""" % (objOrganisation.id, objOrganisation.Name, objOrganisation.OrganisationType)
    return strResult

def GetOrganisationsList(objMember, strIncludeType = None, strExcludeType = None):
    lstOrganisations = SearchMany(objMember, "E3Organisation", "CreatedBy", objMember.id)
    lstResult = []
    for objOrganisation in lstOrganisations:
        if ((not strIncludeType or (strIncludeType in objOrganisation.OrganisationType)) and
            (not strExcludeType or (not (strExcludeType in objOrganisation.OrganisationType)))):
            lstResult.append(objOrganisation)

    lstResult.sort(SortByName)

    strResult = ""
    for objOrganisation in lstResult:
        strResult += ToUnicode(ListOneOrganisation(objOrganisation))

#    if not strResult:
#        strResult = "<p>No organisations found</p>"

    return strResult

def ListOrganisations(objMember):
#    strChapters = GetOrganisationsList(objMember, "coaches network")
#    strOther = GetOrganisationsList(objMember, None, "coaches network")
    strOrganisations = GetOrganisationsList(objMember)
    if not strOrganisations:
        return ""

    strResult = """
<fieldset>
    <legend>Your registered organisations</legend>
%s
</fieldset>""" % strOrganisations
    return strResult

def GetOrganisationsOverview():
    strResult = """
<fieldset>
    <legend>Organisations - Overview</legend>
    <p>Organisations include:</p>
    <ul>
        <li>Coaching chapters, groups, circles and other coaching networks</li>
        <li>Other networks</li>
        <li>Coach training and other training organisations</li>
        <li>Coaching organisations</li>
        <li>Other organisations</li>
    </ul>
</fieldset>"""
    return strResult

def ValidateOrganisation(dictData, objOrganisation):
    return CheckRequiredFields(dictData, ('Name', ))

def UpdateOrganisationRole(objOrganisation, objMember, strRole):
#    print "Update organisation role to %s for %s" % (strRole, objOrganisation.id)
    lstRoles = SearchMany(objOrganisation, "E3Role", "MemberId", objMember.id)
    for objRole in lstRoles:
#        print objRole.ItemId, objRole.RoleType
        if objRole.ItemId == objOrganisation.id:
            objRole.RoleType = strRole

def AddOrganisationRole(objOrganisation, objMember, strRole):
    dodRole = GetDOD(objOrganisation, "E3Role")
    objRole = dodRole.NewObject()
    objRole.MemberId = objMember.id
    objRole.ItemId = objOrganisation.id
    objRole.RoleType = strRole
    Catalogue(objRole)

def GetOrganisationRole(objOrganisation, objMember):
    lstRoles = SearchMany(objOrganisation, "E3Role", "MemberId", objMember.id)
    for objRole in lstRoles:
        if objRole.ItemId == objOrganisation.id:
            return objRole.RoleType
    return ""

def OrganisationForm(strTitle, strButton):
    lstResult = (Fieldset(strTitle, None,
            Paragraph(
                TextControl("Name", "Name"), HiddenControl('OrgId')),
            Paragraph(
                SelectControl("Type", "OrganisationType", cnOrganisationTypes)),
            Paragraph(
                TextArea("Description", "Description")),
            Paragraph(
                SelectControl('Your role', 'Role', cnRoles)),
            Paragraph(
                SubmitControl(strButton))),)
    return lstResult

def EditOrganisationForm(objOrganisation, objMember, blnUpdate):
    lstLoadFields = ('Name', 'OrganisationType', 'Description')
    lstSaveFields = lstLoadFields
    lstFormFields = lstLoadFields + ('Role', 'OrgId')

    lstForm = OrganisationForm("Edit Organisation", "Update organisation details")

    dictData = {}
    dictData['OrgId'] = objOrganisation.id
    dictData['Role'] = GetOrganisationRole(objOrganisation, objMember)

    strResult = FormProcessing(objOrganisation, lstLoadFields, lstForm, blnUpdate, ValidateOrganisation, lstSaveFields, lstFormFields, dictData)
    if blnUpdate:
        UpdateOrganisationRole(objOrganisation, objMember, GetParameter(objOrganisation, "Role"))
    return strResult

def GetOrganisationsTab(objMember):
    strResult= u""
    strSubmitButton = GetParameter(objMember, "SubmitButton")
    blnUpdateOrganisation = (strSubmitButton == "Update organisation details")
    blnAddOrganisation = (strSubmitButton == "Add organisation")
    blnResult = blnUpdateOrganisation or blnAddOrganisation

    strOrganisationId = GetParameter(objMember, "OrgId")
    strResult += GetOrganisationsOverview()

    objOrganisation = None
    if strOrganisationId:
        objOrganisation = SearchOne(objMember, "E3Organisation", "id", strOrganisationId)
        blnResult = True

    if objOrganisation:
        strResult += ToUnicode(EditOrganisationForm(objOrganisation, objMember, blnUpdateOrganisation))

    if blnAddOrganisation or (blnUpdateOrganisation and not strOrganisationId):
        lstFields = ('Name', 'OrganisationType', 'Description')
        lstForm = OrganisationForm("Edit Organisation", "Update organisation details")
        (objOrganisation, strForm) = SaveNewFromForm(objMember, "E3Organisation", lstFields, lstForm, ValidateOrganisation, strIdField = "OrgId")
        if objOrganisation:
            AddOrganisationRole(objOrganisation, objMember, GetParameter(objOrganisation, "Role"))
            objOrganisation.CreatedBy = objMember.id
            Catalogue(objOrganisation)
        strResult += strForm

    # Empty form to add an organisation
    lstForm = OrganisationForm("Add an organisation", 'Add organisation')
    strResult += CreateForm(objMember, lstForm, {})

    # List organisations so far
    strResult += ToUnicode(ListOrganisations(objMember))

    return (strResult, blnResult)

def BookAlreadyImported(objHere, strWebsiteAddress):
    objMembers = GetDataFolder(objHere, "E3Member")
    for objBatch in objMembers.objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            for objOffering in objMember.Offerings.objectValues("E3Offering"):
                if objOffering.WebsiteAddress == strWebsiteAddress:
                    return True
    return False

def DescriptionLine(strTitle, strValue):
    if strValue:
        return "<p><label><b>%s:</b></label> %s</p>\n" % (strTitle, strValue)
    return ""

def MyJoin(strString, lstItems):
    lstResult = []
    for varItem in lstItems:
        if varItem:
            lstResult.append(str(varItem).strip())
    return strString.join(lstResult)

def BriefBookDescription(objBook):
    lstResult = objBook.Authors + ("%s pages" % objBook.Pages, objBook.Format, objBook.Publisher, objBook.Year)
    return MyJoin(", ", lstResult)

def BookDescription(objBook, strFullTitle):
    strResult = ""

    strImage = objBook.FullImageLink()

    if strImage:
        strImage = """<img src="%s" width="240" height="240" align="left" border="0">""" % strImage

    strResult += strImage

    strResult += "<p><b>%s</b></p>\n" % strFullTitle

    if objBook.Review:
        objReview = SearchOne(objBook, "MCIBookReview", "id", objBook.Review)
        if objReview:
            strResult += """<p>&quot;%s&quot; <a href="http://www.mentorcoaches.com/Books/ShowBook?Id=%s">Full&nbsp;Review&nbsp;&gt;&gt;</a></p>
""" % (objReview.ReviewSummary, objBook.id)

    strAuthors = ", ".join(objBook.Authors)
    if "," in strAuthors:
        strAuthorPlural = "s"
    else:
        strAuthorPlural = ""
    strResult += DescriptionLine("Author" + strAuthorPlural, strAuthors)

    strIssue = MyJoin(", ", ("%s pages" % objBook.Pages, objBook.Format))
    strResult += DescriptionLine("Format", strIssue)

    strPublished = MyJoin(", ", (objBook.Publisher, str(objBook.Year)))
    strResult += DescriptionLine("Published", strPublished)

    strResult += DescriptionLine("ISBN", objBook.ISBN)

    strResult += "<p>%s</p>\n" % objBook.ShoppingLinks(True)

    strResult += """<p style="margin-top: 10px;">Book information provided by <a href="http://www.MentorCoaches.com" target="_blank">Mentor Coaches International</a></p>\n"""
    return strResult

def FindFieldNameForMultiOption(objHere, strCategory):
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3MultiOption').objectValues('Folder'):
        for objOption in objBatch.objectValues('E3MultiOption'):
            if objOption.Option == strCategory:
                return objOption.FieldName
    return ""

def ExtractReaderCategories(objHere, lstReaderCategories):
    lstTargetAudienceCoaches = []
    lstTargetAudienceGeneral = []
    for strReaderCategory in lstReaderCategories:
        objReaderCategory = SearchOne(objHere, "MCIReaderCategory", "id", strReaderCategory)
        if objReaderCategory:
            strCategory = objReaderCategory.CategoryName
            strFieldName = FindFieldNameForMultiOption(objHere, strCategory)
            if strFieldName == "TargetAudienceCoaches":
                lstTargetAudienceCoaches.append(strCategory)
            elif strFieldName == "TargetAudienceGeneral":
                lstTargetAudienceGeneral.append(strCategory)
            else:
                print "No multi option for reader category: %" % strCategory
        else:
            print "Reader category not found: %s in group %s" % (strReaderCategory, strFieldName)
    return (lstTargetAudienceCoaches, lstTargetAudienceGeneral)

def ExtractBookCategories(objHere, lstCategories):
    lstTopicsBusinessAndCareer = []
    lstTopicsPersonalSuccess = []
    lstBooksForCoaches = []
    for strCategory in lstCategories:
        if strCategory == "MCIBookCategory00001":
            lstBooksForCoaches.append("Coaching")
        elif strCategory == "MCIBookCategory00030":
            lstTopicsBusinessAndCareer.append("General")
        elif strCategory == "MCIBookCategory00031":
            lstTopicsPersonalSuccess.append("General")
        else:
            objCategory = SearchOne(objHere, "MCIBookCategory", "id", strCategory)
            if objCategory:
                strCategory = objCategory.CategoryName
                strFieldName = FindFieldNameForMultiOption(objHere, strCategory)
                if strFieldName == "TopicsBusinessAndCareer":
                    lstTopicsBusinessAndCareer.append(strCategory)
                elif strFieldName == "TopicsPersonalSuccess":
                    lstTopicsPersonalSuccess.append(strCategory)
                elif strFieldName == "BooksForCoaches":
                    lstBooksForCoaches.append(strCategory)
                else:
                    print "No multi option for category: %s in group %s" % (strCategory, strFieldName)
            else:
                print "Category not found: %s" % strReaderCategory

    return (lstTopicsBusinessAndCareer, lstTopicsPersonalSuccess, lstBooksForCoaches)

def ImportOneBook(objBook, dodOffering, objTarget):
    # Check if it already exists, by going through the links
    strWebsiteAddress = "http://www.mentorcoaches.com/Books/ShowBook?Id=%s" % objBook.id
    if BookAlreadyImported(objBook, strWebsiteAddress):
        print "Already imported: %s" % objBook.id
        return

    objOffering = dodOffering.NewObject(objTarget)

    # Fixed stuff:
    objOffering.Category = "Books, e-books, other publications"
    objOffering.OfferForMembers = ""
    objOffering.Relation = cnDictRelationOptions['List']
    objOffering.Status = "Published"
    objOffering.DeliveryMechanismProduct = ""
    objOffering.DeliveryMechanismService = ""
    objOffering.GroupSize = ""

    # Variable stuff, general:
    strFullTitle = MyJoin(" - ", (objBook.Title, objBook.SubTitle))
    objOffering.myTitle = strFullTitle

    strDescription = BookDescription(objBook, strFullTitle)

#    objOffering.WebsiteAddress = "http://www.mentorcoaches.com/Books/ShowBook?Id=%s" % objBook.id

    # To do:
    objOffering.Description = strDescription
    objOffering.BriefDescription = BriefBookDescription(objBook)
    (objOffering.TargetAudienceCoaches, objOffering.TargetAudienceGeneral) = ExtractReaderCategories(objBook, objBook.ReaderCategories)
    (objOffering.TopicsBusinessAndCareer, objOffering.TopicsPersonalSuccess, objOffering.BooksForCoaches) = ExtractBookCategories(objBook, objBook.Categories)
    Catalogue(objOffering)

def ImportMCIBooks(objHere):
    dodOffering = GetDOD(objHere, "E3Offering")
    objTarget = objHere.unrestrictedTraverse("/Data/E3/E3Members/Batch006/E3Member006060/Offerings")
    objBooks = objHere.unrestrictedTraverse("/Data/MCI/MCIBooks")
    intDone = 0
    for objBatch in objBooks.objectValues("Folder"):
        for objBook in objBatch.objectValues("MCIBook"):
            if intDone < 30:
                ImportOneBook(objBook, dodOffering, objTarget)
#                intDone += 1

def ListPnSCategories(objHere):
    strResult = ""
    for strCategory in cnPnSCategories:
        strResult += """
    <a href="/Offerings?Category=%(URLCategory)s">
        %(Category)s
    </a>
&nbsp; \n """ % {'Category': strCategory,
                'URLCategory': urllib.quote(strCategory)}
    return "<p>%s</p>" % strResult

def UpdateMultiOptionOfferingsCount(objHere):
    dictCounts = {}
    objMembers = GetDataFolder(objHere, "E3Member")
    for objBatch in objMembers.objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.Live():
                for objOffering in objMember.Offerings.objectValues("E3Offering"):
                    if objOffering.Deleted == "No":
                        for (strTab, strDescription, strGroup) in cnMOGroups:
                            lstOptions = objOffering.getProperty(strGroup)
                            if lstOptions:
                                for strOption in lstOptions:
                                    if not dictCounts.has_key((strGroup, strOption)):
                                        dictCounts[(strGroup, strOption)] = 0
                                    dictCounts[(strGroup, strOption)] += 1

#    print dictCounts
    objMultiOptions = GetDataFolder(objHere, "E3MultiOption")
    for objBatch in objMultiOptions.objectValues("Folder"):
        for objOption in objBatch.objectValues("E3MultiOption"):
            strOption = objOption.Option
            strGroup = objOption.FieldName
            if dictCounts.has_key((strGroup, strOption)):
                intCount = dictCounts[(strGroup, strOption)]
            else:
                intCount = 0
            if not objOption.hasProperty("OfferingsCount"):
                objOption.manage_addProperty('OfferingsCount', intCount, 'int')
            else:
                objOption.OfferingsCount = intCount

def UpdateCategoryOfferingsCount(objHere):
    dictCounts = {}
    objMembers = GetDataFolder(objHere, "E3Member")
    for objBatch in objMembers.objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.Live():
                for objOffering in objMember.Offerings.objectValues("E3Offering"):
                    if objOffering.Deleted == "No" and objOffering.Status=="Published":
                        strCategory = objOffering.Category
                        if not dictCounts.has_key(strCategory):
                            dictCounts[strCategory] = 0
                        dictCounts[strCategory] += 1

#    print dictCounts
    objCategories = GetDataFolder(objHere, "E3OfferingCategory")
    for objCategory in objCategories.objectValues('E3OfferingCategory'):
        if objCategory.Category in dictCounts.keys():
            objCategory.CategoryCount = dictCounts[objCategory.Category]
        else:
            objCategory.CategoryCount = 0

def UpdateCounts(objHere):
    UpdateCategoryOfferingsCount(objHere)
    UpdateMultiOptionOfferingsCount(objHere)

def LoadMultiOptionsWithId(objHere):
    dictResult = {}
    objOptions = GetDataFolder(objHere, "E3MultiOption")
    for objBatch in objOptions.objectValues("Folder"):
        for objOption in objBatch.objectValues("E3MultiOption"):
            strFieldName = objOption.FieldName
            if not dictResult.has_key(strFieldName):
                dictResult[strFieldName] = []
            strOption = objOption.Option
            dictResult[strFieldName].append((objOption.id, objOption.Option, objOption.OfferingsCount))
    return dictResult

def CreateInitialCategories(objHere):
    dodOfferingCategory = GetDOD(objHere, "E3OfferingCategory")
    for strCategory in cnPnSCategories:
        objCategory = dodOfferingCategory.NewObject()
        objCategory.Category = strCategory
        Catalogue(objCategory)

def SortSecondEntry(lst1, lst2):
    return cmp(lst1[1], lst2[1])

def MultiOptionsHasRecords(lstOptions):
    for (strId, strOption, intOfferingsCount) in lstOptions:
        if intOfferingsCount:
            return True
    return False

def BuildMultiOptionsSearch(objHere):
    strResult = ""
    dictMultiOptions = LoadMultiOptionsWithId(objHere)
    for (strTab, strDescription, strGroup) in cnMOGroups:
        lstOptions = dictMultiOptions[strGroup]
        if MultiOptionsHasRecords(lstOptions):
            lstOptions.sort(SortSecondEntry)
            strOptions = ""
            for (strId, strOption, intOfferingsCount) in lstOptions:
                if intOfferingsCount:
                    strOptions += """<div class="LocationOption"><input type="checkbox" value="%(Text)s" name="MO-%(FieldName)s-%(Id)s" id="%(Id)s"> <a href="/Offerings?OptionId=%(Id)s">%(Text)s (%(Count)s)</a></div>&nbsp; \n """ % {'FieldName': strGroup,
        'Id': strId,
        'Text': strOption,
        'Count': intOfferingsCount}

            strResult += """
<div class="tabbertab" title="%(Tab)s">
    <h2>%(Tab)s</h2>
    <p><b>%(Description)s</b></p>
    <p>%(Options)s</p>
</div>""" % {'Tab': strTab,
            'Description': strDescription,
            'Options': strOptions}
    return strResult

def CategoryOptions(objHere):
    objCategories = GetDataFolder(objHere, "E3OfferingCategory")
    strResult = ""
    for objCategory in objCategories.objectValues("E3OfferingCategory"):
        if objCategory.CategoryCount:
            strResult += """<div class="LocationOption">
    <input type="checkbox" value="%(Category)s" name="Category-%(Id)s" id="%(Id)s">
    <a href="/Offerings?Category=%(URLCategory)s">
        %(Category)s (%(Count)s)
    </a>
</div>
&nbsp; \n """ % {'Category': objCategory.Category,
                'Count': objCategory.CategoryCount,
                'Id': objCategory.id,
                'URLCategory': urllib.quote(objCategory.Category)}
    return strResult

def CategoryOptionsOld(lstCategories, strCategoryName):
    strResult = ""
    intI = 0
    for strCategory in lstCategories:
        intI += 1
        strResult += """<div class="LocationOption">
    <input type="checkbox" value="%(Category)s" name="%(CategoryName)s-%(I)s" id="%(Category)s">
    <a href="/Offerings?%(CategoryName)s=%(URLCategory)s">
        %(Category)s
    </a>
</div>
&nbsp; \n """ % {'Category': strCategory,
                'CategoryName': strCategoryName,
                'I': str(intI).zfill(2),
                'URLCategory': urllib.quote(strCategory)}
    return strResult

def SearchScreen(objHere):
    strMultiOptions = BuildMultiOptionsSearch(objHere)
    strCategories = CategoryOptions(objHere)
    strReason = CategoryOptionsOld(('Advert', 'Recommendation', 'Listing'), "Reason")
    strURL = objHere.REQUEST.ACTUAL_URL
    strResult = """
<script type="text/javascript" src="/js/tabber.js"></script>
<fieldset>
    <legend>Text search</legend>
    <form method="post" action="%s">
        <p>
            Search for <input type = "text" class="txt" name="SearchFor">
            <input type="Submit" Value = "Search" class="btn" name="Submit">
        </p>
    </form>
</fieldset>
<fieldset>
    <legend>Detailed search</legend>
    <form method="post" action="%s">
        <div class="tabber" id="tab1">
            <div class="tabbertab" title="General">
                <h2>General</h2>
                <p><label>Title contains</label> <input name="TitleContains" class="txt" type="text"></p>
                <p><label>Description contains</label> <input name="DescriptionContains" class="txt" type="text"></p>
                <p><b>Category</b></p>
                <p>%s</p>
                <p><b>Reason for offering</b></p>
                <div class="LocationOption">
                    <input value="Advert" name="Reason-01" id="Advert" type="checkbox">
                    <a href="/Offerings?Reason=Advert">Advert</a>
                </div>
                <div class="LocationOption">
                    <input value="Recommendation" name="Reason-02" id="Recommendation" type="checkbox">
                    <a href="/Offerings?Reason=Recommendation">Recommendation</a>
                </div>
                <div class="LocationOption">
                    <input value="Listing" name="Reason-03" id="Listing" type="checkbox">
                <a href="/Offerings?Reason=Listing">Listing</a>
                </div>
            </div>
            %s
        </div>
        <p><input type="Submit" value = "Search" class="btn" name="Submit"></p>
    </form>
</fieldset>""" % (strURL, strURL, strCategories, strMultiOptions)
    return strResult

def GetCriteria(objHere):
    objRequest = objHere.REQUEST
    strSearchFor = GetParameter(objRequest, "SearchFor")
    dictCriteria = {'SearchFor': None, 'Contains': [], 'Option': {}, 'Category': [], 'Reason': []}
    if strSearchFor:
        dictCriteria['SearchFor']= strSearchFor
        return ('"%s"' % strSearchFor, dictCriteria)

    lstSearchFor = []

    strTitleContains = GetParameter(objRequest, "TitleContains")
    if strTitleContains:
        lstSearchFor.append('Title contains "%s"' % strTitleContains)
        dictCriteria['Contains'].append(('myTitle', strTitleContains))

    strDescriptionContains = GetParameter(objRequest, "DescriptionContains")
    if strDescriptionContains:
        lstSearchFor.append('Description contains "%s"' % strDescriptionContains)
        dictCriteria['Contains'].append(('Description', strDescriptionContains))

    for strName in objRequest.form.keys():
        strValue = objRequest.form[strName]
        if strName.startswith("Category"):
            (strStart, strCategoryId) = strName.split("-")
            lstSearchFor.append(strValue)
            dictCriteria["Category"].append(strValue)

        elif strName.startswith("Reason"):
            (strStart, strReasonId) = strName.split("-")
            lstSearchFor.append(strValue)
            if strReasonId == "Listing":
                lstSearchFor.append("...")
            dictCriteria["Reason"].append(strValue)

        elif strName.startswith("MO"):
            (strStart, strGroup, strOptionId) = strName.split("-")
            lstSearchFor.append(strValue)
            if not strGroup in dictCriteria["Option"].keys():
                dictCriteria["Option"][strGroup] = []
            dictCriteria["Option"][strGroup].append(strValue)

    strResult = ", ".join(lstSearchFor)
    return (strResult, dictCriteria)

def SearchInOffering(objOffering, strSearchFor):
    strSearchFor = strSearchFor.lower()
    for (strId, varProperty) in objOffering.propertyItems():
        if varProperty:
            strType = objOffering.getPropertyType(strId)
            if strType in ('string', 'ustring', 'text', 'utext'):
                strSearchIn = varProperty.lower()
            elif strType in ('lines', ):
                strSearchIn = " ".join(varProperty)
                strSearchIn = strSearchIn.lower()
            else:
                strSearchIn = ""
            if strSearchFor in strSearchIn:
                return True
    return False

def ScoreAgainstCriteria(objOffering, dictCriteria):
    if dictCriteria["SearchFor"]:
        if SearchInOffering(objOffering, dictCriteria["SearchFor"]):
            return 1
        else:
            return 0

    intResult = 0
    for strCategory in dictCriteria["Category"]:
        if strCategory == objOffering.Category:
            intResult += 5

    for strReason in dictCriteria["Reason"]:
        strReason = cnConvertReason[strReason]
        if objOffering.HasReason(strReason):
            intResult += 3

    for (strField, strValue) in dictCriteria["Contains"]:
        if strValue.lower() in objOffering.getProperty(strField).lower():
            intResult += 3

    for strGroup in dictCriteria["Option"]:
        for strOption in dictCriteria["Option"][strGroup]:
            lstProperty = objOffering.getProperty(strGroup)
            if lstProperty:
                for strHasOption in lstProperty:
                    if strOption in strHasOption:
                        intResult += 1

    return intResult

def SearchOfferingsForCriteria(objHere, dictCriteria):
    lstResult = []
    objMembers = GetDataFolder(objHere, "E3Member")
    for objBatch in objMembers.objectValues("Folder"):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.Live():
                for objOffering in objMember.Offerings.objectValues("E3Offering"):
                    if objOffering.Deleted == "No" and objOffering.Status == "Published":
                        intScore = ScoreAgainstCriteria(objOffering, dictCriteria)
                        if intScore:
                            lstResult.append((intScore, objOffering))
    return lstResult

def ReverseOrder(var1, var2):
    return cmp(var2, var1)

def SortByScoreAndTitle(var1, var2):
    if var1[0] == var2[0]:
        return cmp(var1[1].myTitle, var2[1].myTitle)
    return cmp(var2[0], var1[0])

def ReduceList(lstList, intOffset, intMaxEntries = 20):
    return lstList[intOffset:(intOffset + intMaxEntries)]

def Navigation(intOffset, intResultCount, strURL, intMaxEntries = 20):
#    Showing 1 - 20 of 621
#    << Prev - 1 2 3 4 5 6 7 8 9 10 - Next >>
    intFirst = intOffset + 1
    intLast = intOffset + intMaxEntries
    intMiddleEntry = int(intMaxEntries/2)
    if intLast > intResultCount:
        intLast = intResultCount
    strResult = "<p>Showing %s - %s of %s" % (intFirst, intLast, intResultCount)

    if intResultCount <= 20:
        return strResult + "</p>"
    else:
        strResult += "<br>\n"

    intCurrentPage = (intOffset / intMaxEntries) + 1
    intFirstPage = intCurrentPage - 5
    if intFirstPage < 1:
        intFirstPage = 1
    intLastPage = intFirstPage + intMiddleEntry
    (intMaxPage, intRemainder) = divmod(intResultCount, intMaxEntries)
    if intRemainder:
        intMaxPage += 1
    if intLastPage > intMaxPage:
        intFirstPage = intMaxPage - intMiddleEntry
        intLastPage = intMaxPage
    if intFirstPage < 1:
        intFirstPage = 1

    if intOffset:
        strPrev = """<a href = "%s&Offset=%s">&lt;&lt;&nbsp;Prev</a> - """ % (strURL, intOffset - intMaxEntries)
    else:
        strPrev = ""

    if intCurrentPage < intMaxPage:
        strNext = """ - <a href = "%s&Offset=%s">Next &gt;&gt;</a>""" % (strURL, intOffset + intMaxEntries)
    else:
        strNext = ""

    if intMaxPage > intMiddleEntry + 1:
        strFirst = """<a href = "%s&Offset=0">First</a> - """ % strURL
        strLast = """ - <a href = "%s&Offset=%s">Last</a>""" % (strURL, (intMaxPage - 1) * intMaxEntries)
    else:
        strFirst = ""
        strLast = ""

    strPages = ""
    for intI in range(intFirstPage, intLastPage + 1):
        if intI == intCurrentPage:
            strPages += " %s " % intI
        else:
            strPages += """ <a href="%s&Offset=%s">%s</a> """ % (strURL, (intI - 1)* intMaxEntries, intI)

    strResult += "%s</p>\n" % (strFirst + strPrev + strPages + strNext + strLast)

    return strResult

def GeneralOfferingsSearch(objHere, strSearchFor):
    dictCriteria = {'SearchFor': strSearchFor, 'Contains': [], 'Option': {}, 'Category': [], 'Reason': []}
    return GetSearchResults(objHere, 0, dictCriteria, strSearchFor, True)

def SaveOfferingsSearch(objHere, lstOfferings, strCriteria, intObjectLocation = -1):

    dodSearchQuery = GetDOD(objHere, "E3SearchQuery")
    objSearchQuery = dodSearchQuery.NewObject()
    objSearchQuery.TableName = "Offerings"
    objSearchQuery.CriteriaDescription = strCriteria

    lstResult = []
    if intObjectLocation > -1:
        for lstItem in lstOfferings:
            lstResult.append(lstItem[intObjectLocation].id)
    else:
        for objOffering in lstOfferings:
            lstResult.append(objOffering.id)

    objSearchQuery.ObjectIds = lstResult

    Catalogue(objSearchQuery)
    return objSearchQuery.id

def SearchResults(objHere, intOffset):
    (strCriteria, dictCriteria) = GetCriteria(objHere)
    if not strCriteria:
        return None
    return GetSearchResults(objHere, intOffset, dictCriteria, strCriteria)

def GetSearchResults(objHere, intOffset, dictCriteria, strCriteria, blnSimpleVersion = False):
    lstOfferings = SearchOfferingsForCriteria(objHere, dictCriteria)

    if not lstOfferings:
        if blnSimpleVersion:
            return ""
        else:
            return """
    <fieldset>
        <p><b>Searching for: %s</b></p>
        <p>No products or services found</p>
    </fieldset>
    """ % strCriteria

    blnFullMember = IsFullMember(objHere)

    strSearchQueryId = SaveOfferingsSearch(objHere, lstOfferings, strCriteria, 1)

    lstOfferings.sort(SortByScoreAndTitle)
    intResultCount = len(lstOfferings)

    ReduceList(lstOfferings, intOffset)

    strNavigation = Navigation(intOffset, intResultCount, "/Offerings?SearchQueryId=%s" % strSearchQueryId)

    if blnSimpleVersion:
        strResult = strNavigation
    else:
        strResult = """
    <fieldset>
        <p><b>Searching for: %s</b></p>
        %s
    </fieldset>
    """ % (strCriteria, strNavigation)

    for (intScore, objOffering) in lstOfferings:
        strResult += FormatOneOffering(objOffering, blnFullMember)

    strResult += strNavigation

    return strResult

def OfferingsForOption(objHere, strOptionId):
    objOption = SearchOne(objHere, "E3MultiOption", "id", strOptionId)
    strOption = objOption.Option
    strGroup = objOption.FieldName
    lstOfferings = SearchMany(objHere, "E3Offering", "Option", strOption)
    lstResult = []
    for objOffering in lstOfferings:
        if objOffering.Live() and objOffering.Status == "Published":
            varProperty = objOffering.getProperty(strGroup)
            if varProperty:
                if strOption in objOffering.getProperty(strGroup):
                    lstResult.append(objOffering)
    return lstResult

def SortByTitle(obj1, obj2):
    return cmp(obj1.myTitle, obj2.myTitle)

def FormatOneOffering(objOffering, blnFullMember, blnEditLinks = False, blnWithName = True):
    if blnEditLinks:
        strLink = "/MyECL/Offerings/Edit?id=%s" % objOffering.id
    else:
        strLink = "/Offerings?Id=%s" % objOffering.id

    strTitle = ToUnicode(objOffering.GetTitle())

    if objOffering.IsOwn():
        strSender = objOffering.GetMemberName(blnFullMember)
        if strSender:
            strSender = "by " + strSender
    else:
        strSender = ""

    strSender = ToUnicode(strSender)

    strDescription = ToUnicode(objOffering.TruncatedDescription(80))

    if strDescription:
        strDescription = "<p>%s</p>" % strDescription

    if blnFullMember and objOffering.OfferForMembers:
        strOffer = "<p><b>Special offer:</b> %s</p>" % ToUnicode(TruncateLine(objOffering.OfferForMembers, 80))
    else:
        strOffer = ""
    strResult = u"""<a href="%(Link)s"><div id="MessageBox1">
					<p><b>%(Title)s</b> %(Sender)s</p>
					%(Description)s
                    %(Offer)s
				</div></a>""" % {'Link': strLink,
                                'Title': strTitle,
                                'Sender': strSender,
                                'Description': strDescription,
                                'Offer': strOffer}
    return strResult

def FormatOneCategory(strCategory, lstOfferings, blnFullMember):
    lstOfferings.sort(SortByTitle)
    if strCategory:
        strGroupTitle = "<h2>%s</h2>" % strCategory
    else:
        strGroupTitle = ""
    strResult = ""
    for objOffering in lstOfferings:
        strResult += FormatOneOffering(objOffering)
    return """%s
%s""" % (strGroupTitle, strResult)

def SortOnTitle(objOffering1, objOffering2):
    return cmp(objOffering1.myTitle, objOffering2.myTitle)

def FormatList(lstOfferings, blnFullMember, intOffset, strURL, strTitle, intMaxEntries = 20, blnTopNavigation = True):
# Used to list search results and services for a given Option
    # Group by category, sort by title
    # Line 1: Title and list member
    # Line 2: First line of description
    # (list members only) Line 3: First line of special offer

    if not lstOfferings or len(lstOfferings) == 0:
        return """
<fieldset>
    <p><b>%s</b></p>
    <p>No products or services found</p>
</fieldset>""" % strTitle

    lstOfferings.sort(SortOnTitle)

    intResultCount = len(lstOfferings)

    lstOfferings = ReduceList(lstOfferings, intOffset, intMaxEntries)

    strNavigation = Navigation(intOffset, intResultCount, strURL, intMaxEntries)

    if blnTopNavigation:
        strTopNavigation = strNavigation
    else:
        strTopNavigation = ""

    if strTitle:
        strResult = """
<fieldset>
    <p><b>%s</b></p>
    %s
</fieldset>
""" % (strTitle, strTopNavigation)
    else:
        strResult = strTopNavigation

    for objOffering in lstOfferings:

        strResult += FormatOneOffering(objOffering, blnFullMember)

    strResult += strNavigation

    return strResult

def ShowSavedOfferingsSearch(objHere, strSearchQueryId, intOffset):
    objSearchQuery = SearchOne(objHere, "E3SearchQuery", "id", strSearchQueryId)
    if not objSearchQuery:
        return "<p>Query not found</p>"

    intResultCount = len(objSearchQuery.ObjectIds)
    lstOfferingIds = ReduceList(objSearchQuery.ObjectIds, intOffset)

    strNavigation = Navigation(intOffset, intResultCount, "/Offerings?SearchQueryId=%s" % strSearchQueryId)

    blnFullMember = IsFullMember(objHere)

    strResult = """
    <fieldset>
        <p><b>%s</b></p>
        %s
    </fieldset>
    """ % (objSearchQuery.CriteriaDescription, strNavigation)

    for strOfferingId in lstOfferingIds:
        objOffering = SearchOne(objHere, "E3Offering", "id", strOfferingId)
        if objOffering:
            strResult += FormatOneOffering(objOffering, blnFullMember)

    strResult += strNavigation

    return strResult

def ListForOption(objHere, strOptionId, intOffset):
    strResult = ""
    blnFullMember = IsFullMember(objHere)
    objMultiOption = SearchOne(objHere, "E3MultiOption", "id", strOptionId)
    if objMultiOption and objMultiOption.OfferingsCount:
        lstOfferings = OfferingsForOption(objHere, strOptionId)
        strURL = "/Offerings?OptionId=%s" % strOptionId
        strTitle = objMultiOption.Option
        strResult = FormatList(lstOfferings, blnFullMember, intOffset, strURL, strTitle)
    return strResult

def OfferingsForCategory(objHere, strCategory):
    lstOfferings = SearchMany(objHere, "E3Offering", "Category", strCategory)
    lstResult = []
    for objOffering in lstOfferings:
        if objOffering.Live() and objOffering.Category == strCategory and objOffering.Status == "Published":
            lstResult.append(objOffering)
    return lstResult

def ListForCategory(objHere, strCategory, intOffset):
    strResult = ""
    blnFullMember = IsFullMember(objHere)
    lstOfferings = OfferingsForCategory(objHere, strCategory)
    if lstOfferings:
        strURL = objHere.REQUEST.ACTUAL_URL + "?Category=%s" % urllib.quote(strCategory)
        strResult = FormatList(lstOfferings, blnFullMember, intOffset, strURL, strCategory)
    return strResult

def OfferingsForReason(objHere, strReason):
    lstOfferings = SearchMany(objHere, "E3Offering", "Relation", strReason)
    lstResult = []
    for objOffering in lstOfferings:
        if objOffering.Live() and objOffering.Status == "Published":
            lstResult.append(objOffering)
    return lstResult

def ListForReason(objHere, strReason, intOffset):
    strResult = ""
    if cnConvertReason.has_key(strReason):
        strRealReason = cnConvertReason[strReason]
    else:
        strRealReason = strReason
    lstOfferings = OfferingsForReason(objHere, strRealReason)
    if lstOfferings:
        blnFullMember = IsFullMember(objHere)
        strResult = FormatList(lstOfferings, blnFullMember, intOffset, "/Offerings?Reason=%s" % strReason, strReason)
    return strResult

def ToFieldset(strTitle, strContents):
    return """<fieldset>
    <legend>%s</legend>
<p>%s</p>
</fieldset>""" % (strTitle, strContents)

def NumberToWords(intNumber):
    return {1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five'}[intNumber]

def ContactFormForOffering(objOffering, strNamePlusLink, strSendersName, strSendersEmailAddress, strSendersComments):
    intConfNumber1 = random.randrange(1, 5)
    intConfNumber2 = random.randrange(1, 5)
    strConfNumber1 = NumberToWords(intConfNumber1)
    strConfNumber2 = NumberToWords(intConfNumber2)
    strResult = """<fieldset>
<legend>Contact Form</legend>
<p>To contact %(Name)s use this form</p>
<form action="/Offerings?Id=%(OfferingId)s" method="post">
    <p>
        <label>Your name</label>
        <input type="text" name="SendersName" class="txt" value="%(SendersName)s">
    </p>
    <p>
        <label>Your email address</label>
        <input type="text" name="SendersEmailAddress" class="txt" value="%(SendersEmailAddress)s">
    </p>
    <p>
        <label>Your comments or request</label>
        <textarea name="SendersComments" cols="40" rows="5">%(SendersComments)s</textarea>
    </p>
    <input type="hidden" name="ConfNo" value="%(ConfNo)s">
    <input type="hidden" name="Action" value="MemberContactForm">
    <p>The following is to protect this list member from automated spam messages.<br> Please complete the simple sum below</p>
    <p>%(ConfNo1)s plus %(ConfNo2)s equals <input type="text" name="Confirmation"  size="3">
    </p>
    <p>
        <input type="submit" value="Submit my comments" name="Submit">
    </p>
</form>
</fieldset>""" % {"Name": strNamePlusLink,
                    "OfferingId": objOffering.id,
                    "ConfNo1": strConfNumber1.capitalize(),
                    "ConfNo2": strConfNumber2,
                    "ConfNo": (intConfNumber1 + intConfNumber2),
                    "SendersName": strSendersName,
                    "SendersEmailAddress": strSendersEmailAddress,
                    "SendersComments": strSendersComments}
    return ToUnicode(strResult)

def CategoryPlusTitle(objOffering):
    strTitle = objOffering.myTitle
    if strTitle:
        strTitle = " - " + strTitle
    return objOffering.Category + strTitle

def EventTitle(objHere):
    strResult = "Events Diary"

    strId = GetParameter(objHere.REQUEST, "EventId")
    if strId:
        objOffering = SearchOne(objHere, "E3Offering", "id", strId)

    if objOffering and objOffering.Live():
        if objOffering.myTitle:
            strResult = "%s (%s)" % (objOffering.myTitle, objOffering.Category)
        else:
            strResult = objOffering.Category
        if objOffering.IsOwn():
            strName = objOffering.GetMemberName(IsFullMember(objHere))
            if strName:
                strResult += " by " + strName

    return strResult

def OfferingTitle(objHere):
    strResult = "Products and Services - Adverts, Recommendations and Listings"

    strId = GetParameter(objHere.REQUEST, "Id")
    if strId:
        objOffering = SearchOne(objHere, "E3Offering", "id", strId)

    if objOffering and objOffering.Live():
        if objOffering.myTitle:
            strResult = "%s (%s)" % (objOffering.myTitle, objOffering.Category)
        else:
            strResult = objOffering.Category
        if objOffering.IsOwn():
            strName = objOffering.GetMemberName(IsFullMember(objHere))
            if strName:
                strResult += " by " + strName

    return strResult

def GetTargetAudienceBlock(objOffering):
    lstTargetAudience = CombineLists(objOffering.TargetAudienceCoaches, objOffering.TargetAudienceGeneral)
    strTargetAudience = ListToText(lstTargetAudience)
    if strTargetAudience:
        return ToFieldset("Particularly suitable for", strTargetAudience)
    return ""

def GetCoversBlock(objOffering):
    lstTopics = CombineLists(objOffering.TopicsPersonalSuccess, objOffering.TopicsBusinessAndCareer)
    strTopics = ListToText(lstTopics)
    if strTopics:
        return ToFieldset("It covers", strTopics)
    return ""

def GetBooksBlock(objOffering):
    lstTopics = objOffering.BooksForCoaches
    strTopics = ListToText(lstTopics)
    if strTopics:
        return ToFieldset("Book topic(s)", strTopics)
    return ""

def GetDeliveryBlock(objOffering, strTitle):
    lstDelivery = CombineLists(objOffering.DeliveryMechanismService, objOffering.DeliveryMechanismProduct)
    strDelivery = ListToText(lstDelivery)
    if strDelivery:
        return ToFieldset(strTitle, strDelivery)
    return ""

def ShowOneOffering(objOffering, strSendersName = "", strSendersEmailAddress = "", strSendersComments = ""):
    if not objOffering.Live():
        return ""
    strResult = ""

    objMember = objOffering.unrestrictedTraverse('../../')
    blnFullMember = IsFullMember(objMember)

    strResult += "<h2>%s</h2>" % CategoryPlusTitle(objOffering)

    blnAdvert = ("own" in objOffering.Relation)

    strNamePlusLink = """<a href="/Members/ViewProfile?MemberId=%s">%s</a>""" % (objMember.id, objOffering.GetMemberName(blnFullMember))

    if blnAdvert:
        strResult += """<form action="#">%s</form>""" % \
            (objMember.ProfilePersonalDetails(blnFullMember, "Provided by", True) + \
            objMember.ProfileContactDetails(blnFullMember))
    else:
        strResult += """<p>Submitted by %s</p>""" % strNamePlusLink

    strResult += GetTargetAudienceBlock(objOffering)
    strResult += GetCoversBlock(objOffering)
    strResult += GetDeliveryBlock(objOffering, "It is usually delivered via")
    strResult += GetBooksBlock(objOffering)

    strGroupSize = ListToText(objOffering.GroupSize)
    if strGroupSize:
        strResult += ToFieldset("I usually work", strGroupSize)

    if objOffering.Description:
        strDescription = ToUnicode(objOffering.Description)
        if not "<" in strDescription and not ">" in strDescription:
            strDescription = InsertBrs(strDescription)

        if objOffering.myTitle:
            strDescription = """<h2>%s</h2>
<p>%s</p>""" % (objOffering.myTitle, strDescription)

        strResult += ToFieldset("Description", strDescription)

    if objOffering.OfferForMembers and blnFullMember:
        strResult += ToFieldset("Special offer for Euro Coach List members", objOffering.OfferForMembers)

    if objOffering.WebsiteAddress:
        strLink = """<p>Go to <a href="%s" target="_blank">%s</a></p>""" % (objOffering.WebsiteAddress, objOffering.WebsiteAddress)
        strResult += ToFieldset("More information", strLink)

    strResult = ToUnicode(strResult)
    if blnAdvert:
        strResult += ContactFormForOffering(objOffering, strNamePlusLink, strSendersName, strSendersEmailAddress, strSendersComments)

    return strResult

def InsertReturnLink(strHTML):
    if strHTML:
        return """<p><a href="/Offerings">&lt; &lt; Return to Products and Services</a></p>""" + strHTML
    return ""

def CheckCommentsForm(strSendersName, strSendersEmailAddress, strSendersComments, strConfNo, strConfirmation):
    if not strSendersName or not strSendersEmailAddress or not strSendersComments:
        return """The form must be fully filled in. Please complete the form and re-submit"""

    objValidator = StringValidator(strSendersEmailAddress)
    if not objValidator.isEmail():
        return """The email address you entered (%s) is not valid. Please correct the email address""" % strSendersEmailAddress
    if strConfNo.strip() <> strConfirmation.strip():
        return """The sum at the end of the form was incorrect or incomplete. Please correct this and re-submit"""
    return ""

def SendCommentsToMember(objOffering, strSendersName, strSendersEmailAddress, strSendersComments):
    strSubject = "Euro Coach List - Visitor's comments on your product or service"
    objMember = objOffering.unrestrictedTraverse('..')
    strTo = objMember.PreferredEmailAddress()
    strMessage = u"""Someone submitted the following comment(s) or question(s) on the Euro Coach List website, whilst looking at the details of one of your products or services

The form details are:
-----------------------------------------
Your product or service: %s
Full details at: http://www.EuroCoachList.com/Offerings?Id=%s

Sender's name: %s
Sender's email address: %s

Sender's comments:
%s
-----------------------------------------
All the best,

Coen""" % (ToUnicode(CategoryPlusTitle(objOffering)), objOffering.id, ToUnicode(strSendersName), ToUnicode(strSendersEmailAddress), ToUnicode(strSendersComments))

    strMessage = strMessage.encode("ascii", "replace")

    SendEmail(objOffering, strMessage, strSubject, strTo)

def MainScreen(objHere):
# If no parameter: show search screen
# If id specified: show single offering
# If search parameters specified: show search results
# If MultiOptionId: show list for MultiOption
# If CategoryId: show list for CategoryId
    strId = GetParameter(objHere.REQUEST, "Id")
    strSearchQueryId = GetParameter(objHere.REQUEST, "SearchQueryId")
    strCategory = GetParameter(objHere.REQUEST, "Category")
    strSubmit = GetParameter(objHere.REQUEST, "Submit")
    strOptionId = GetParameter(objHere.REQUEST, "OptionId")
    strReason = GetParameter(objHere.REQUEST, "Reason")
    strOffset = GetParameter(objHere.REQUEST, "Offset")
    if strOffset and strOffset.isdigit():
        intOffset = int(strOffset)
    else:
        intOffset = 0
    strResult = ""
    if strId:
        objOffering = SearchOne(objHere, "E3Offering", "id", strId)
        if objOffering:
            if strSubmit == "Submit my comments":
                strSendersName = GetParameter(objHere.REQUEST, "SendersName")
                strSendersEmailAddress = GetParameter(objHere.REQUEST, "SendersEmailAddress")
                strSendersComments = GetParameter(objHere.REQUEST, "SendersComments")
                strConfNo = GetParameter(objHere.REQUEST, "ConfNo")
                strConfirmation = GetParameter(objHere.REQUEST, "Confirmation")

                strError = CheckCommentsForm(strSendersName, strSendersEmailAddress, strSendersComments, strConfNo, strConfirmation)

                if strError:
                    strResult = """<p class="ErrorMessage">%s</p>""" % strError
                    strResult += ShowOneOffering(objOffering, strSendersName, strSendersEmailAddress, strSendersComments)
                else:
#                    send the email
                    SendCommentsToMember(objOffering, strSendersName, strSendersEmailAddress, strSendersComments)
                    strResult = """<p class="ErrorMessage">Your comments have been sent</p>"""
                    strResult += ShowOneOffering(objOffering)
            else:
                strResult = ShowOneOffering(objOffering)

            strResult = InsertReturnLink(strResult)
    elif strSearchQueryId:
        strResult = ShowSavedOfferingsSearch(objHere, strSearchQueryId, intOffset)
    elif strCategory:
        strCategory = urllib.unquote(strCategory)
        strResult = ListForCategory(objHere, strCategory, intOffset)
        strResult = InsertReturnLink(strResult)
    elif strReason:
        strResult = ListForReason(objHere, strReason, intOffset)
        strResult = InsertReturnLink(strResult)
    elif strSubmit == "Search":
        strResult = SearchResults(objHere, intOffset)
        strResult = InsertReturnLink(strResult)
    elif strOptionId:
        strResult = ListForOption(objHere, strOptionId, intOffset)
        strResult = InsertReturnLink(strResult)

    if not strResult:
        strResult = SearchScreen(objHere)

    return strResult

def LoadMultiOptions(objHere):
    dictResult = {}
    objOptions = GetDataFolder(objHere, "E3MultiOption")
    for objBatch in objOptions.objectValues("Folder"):
        for objOption in objBatch.objectValues("E3MultiOption"):
            strFieldName = objOption.FieldName
            if not dictResult.has_key(strFieldName):
                dictResult[strFieldName] = []
            dictResult[strFieldName].append(objOption.Option)
    return dictResult

def OneRandomWord():
    strResult = ""
    for intI in range(0, random.randrange(3, 10)):
        strResult += random.choice(string.ascii_lowercase)
    return strResult

def RandomWords(intMin, intMax):
    intWords = random.randrange(intMin, intMax)
    lstResult = []
    for intI in range(0, intWords):
        lstResult.append(OneRandomWord())
    return (" ".join(lstResult))

def MaybeWords(intMin, intMax):
    if random.random() > 0.5:
        return RandomWords(intMin, intMax)
    return ""

def RandomOptions(lstOptions):
    lstResult = []
    for strOption in lstOptions:
        if random.random() > 0.7:
            lstResult.append(strOption)
    return lstResult

def CreateOneRandomOffering(objHere, dictMultiOptions, dodOffering, objMember):
    # cnPnSCategories
    objOffering = dodOffering.NewObject(objMember.Offerings)
    objOffering.myTitle = RandomWords(3, 8)
    objOffering.Category = random.choice(cnPnSCategories)
    objOffering.Description = RandomWords(20, 50)
    objOffering.OfferForMembers = MaybeWords(10, 30)
    objOffering.Type = "Service"
    objOffering.Status = "Published"
    objOffering.Relation = random.choice(cnRelationOptions)
    objOffering.TargetAudienceCoaches = RandomOptions(dictMultiOptions["TargetAudienceCoaches"])
    objOffering.TargetAudienceGeneral = RandomOptions(dictMultiOptions["TargetAudienceGeneral"])
    objOffering.TopicsBusinessAndCareer = RandomOptions(dictMultiOptions["TopicsBusinessAndCareer"])
    objOffering.TopicsPersonalSuccess = RandomOptions(dictMultiOptions["TopicsPersonalSuccess"])
    objOffering.DeliveryMechanismService = RandomOptions(dictMultiOptions["DeliveryMechanismService"])
    objOffering.DeliveryMechanismProduct = RandomOptions(dictMultiOptions["DeliveryMechanismProduct"])
    objOffering.GroupSize = RandomOptions(dictMultiOptions["GroupSize"])
    Catalogue(objOffering)

def CreateRandomOfferings(objHere):
    dictMultiOptions = LoadMultiOptions(objHere)
    objMember = GetDataFolder(objHere, "E3Member").Batch006.E3Member006060
    dodOffering = GetDOD(objHere, "E3Offering")
    for intI in range(1, 100):
        CreateOneRandomOffering(objHere, dictMultiOptions, dodOffering, objMember)

def ReadInitialMultiOptions(objHere):
    fileOptions = open(cnLocalPathExtensions + "MultiOptionStartingLists.txt")
    lstLines = fileOptions.readlines()
    intStatus = 0 # Not yet started
    for strLine in lstLines:
        strLine = strLine.replace("\n", "")
        if '~' in strLine:
            if intStatus in [0, 2]:
                intStatus = 1 # Looking for the fieldname
            else:
                intStatus = 2 # Reading the options
        else:
            if intStatus == 1:
                strFieldName = strLine
            else:
                AddOneOption(objHere, strFieldName, strLine)
    print "Done"

def EventTitleOnPage(objEvent):
    if not objEvent:
        return "Add an event"

    if "own" in objEvent.Relation:
        strResult = "Own event: "
    elif "recommend" in objEvent.Relation:
        strResult = "Recommendation: "
    else:
        strResult = "For coaches: "

    if objEvent.myTitle:
        strResult += objEvent.myTitle + " (%s)" % objEvent.Category
    else:
        strResult += objEvent.Category

    strResult += ", " + objEvent.DateDescription
    return strResult

def OfferingTitleOnPage(objOffering):
    if not objOffering:
        return "Add a product or service"

    if "own" in objOffering.Relation:
        strResult = "Own product or service: "
    elif "recommend" in objOffering.Relation:
        strResult = "Recommendation: "
    else:
        strResult = "For coaches: "

    strResult += objOffering.Category
    return strResult

def ListOfferings(objHere, blnEvents = False):
    objMember = GetCurrentMember(objHere)
    strOfferings = ListMyOfferings(objMember, blnEvents)
    if blnEvents:
        strResult = """
    <p><a href="/MyECL/Events/Edit">Add a new event >></a></p>
    %s
    <p><a href="/MyECL/Events/Edit">Add a new event >></a></p>
""" % strOfferings
    else:
        strResult = """
    <p><a href="/MyECL/Offerings/Edit">Add a new product or service >></a></p>
    %s
    <p><a href="/MyECL/Offerings/Edit">Add a new product or service >></a></p>
""" % strOfferings

    return strResult

def ListMyOfferings(objMember, blnEvents):
    dictOfferings = {}
    strOwn = ""
    strRec = ""
    strList = ""
    for objOffering in objMember.Offerings.objectValues("E3Offering"):
        if (objOffering.Type == "Event") == blnEvents:
#            print objOffering.Type, blnEvents
            if objOffering.IsOwn():
                strOwn += ListOneOffering(objOffering, blnEvents)
            elif objOffering.IsRecommendation():
                strRec += ListOneOffering(objOffering, blnEvents)
            else:
                strList += ListOneOffering(objOffering, blnEvents)

    if not strOwn + strRec + strList:
        if blnEvents:
            strResult = "<p>No events listed yet</p>"
        else:
            strResult = "<p>No products or services listed yet</p>"
    else:
        strOwn = MakeOL(strOwn, "Own products and services")
        strRec = MakeOL(strRec, "Recommendations")
        strList = MakeOL(strList, "Other products and services")
        strResult = strOwn + strRec + strList
    return strResult

def MakeOL(strList, strTitle):
    if strList:
        return """<h2>%s</h2>
<ol>
    %s
</ol>""" % (strTitle, strList)
    else:
        return ""

def ListOneOffering(objOffering, blnEvents):
    strStatus = objOffering.Status
    if strStatus:
        strStatus = " (%s)" % strStatus.split()[0]
    else:
        strStatus = ""

    strTitle = objOffering.myTitle
    if strTitle:
        strTitle = ": %s" % strTitle

    if blnEvents:
        strLink = "Events"
    else:
        strLink = "Offerings"

    strResult = """<li><a href = "/MyECL/%s/Edit?id=%s">%s%s</a>%s</li>\n""" % (strLink, objOffering.id, objOffering.Category, strTitle, strStatus)
    return strResult

def OfferingForm(blnNewOffering, blnDeleted):
    lstForm = []
    lstTabs = []
    lstTabs.append(OneTab("General",
                Paragraph(
                    SelectControl('Category', 'Category', cnPnSCategories),),
                Paragraph(
                    TextControl('Title or name', 'myTitle'),
                    HiddenControl('id'),
                    HiddenControl('Status'),
                    HiddenControl('Type'),
                    HiddenControl('Deleted')),
                Paragraph(
                    RichTextArea('Description, pricing, how to order, etc', 'Description'),),
                Paragraph(
                    TextArea('Special offer for Euro Coach List Members (shown to list members only)', 'OfferForMembers'),),
                Paragraph(
                    TextControl('More information at', 'WebsiteAddress'),),
                Paragraph(
                    SelectControl('Your reason for listing this product or service', 'Relation',
                cnRelationOptions))))

    for (strTab, strDescription, strGroup) in cnMOGroups:
        lstTabs.append(OneTab(strTab, MultiOptionBlock('', strDescription, strGroup)))

    lstExtraLine = None

    if blnNewOffering:
        lstButtons = Paragraph(
            SubmitControl('Save'),)
    elif blnDeleted:
        lstButtons = Paragraph(
            SubmitControl('Restore'),)
    else:
        lstButtons = Paragraph(
            SubmitControl('Update'),
            SubmitControl('Delete'))
        lstExtraLine = Paragraph(PureText('(A deleted product or service will be invisible to website visitors, but can still be restored)'))

    if lstExtraLine:
        lstForm.append(Fieldset("Product or Service Details", None,
            Tabset(*lstTabs),
            lstButtons,
            lstExtraLine))
    else:
        lstForm.append(Fieldset("Product or Service Details", None,
            Tabset(*lstTabs),
            lstButtons))

    return lstForm

def EventForm(objMember, blnNewOffering, blnDeleted, strMemberId):
    lstForm = []
    lstTabs = []

#Location:
#If a face to face event: country (dropdown), general location (e.g. county, province, nearest major city, etc)
#If a phone-based event: country where bridge is based
#Or internet/web-based

    lstGeneralParagraphs = []

    lstOrganisations = GetOrganisations(objMember)
    lstOrganisations = [('Own event', 'Own'), ] + lstOrganisations

    lstEventSeries = GetExistingEventSeries(objMember, strMemberId)
    lstEventSeries = [('Stand alone event', 'Single'), ] + lstEventSeries


    lstTabs.append(OneTab("General",
                Fieldset("What", None,
                    Paragraph(
                        TextControl('Title or name', 'myTitle'),
                        HiddenControl('id'),
                        HiddenControl('Status'),
                        HiddenControl('Type'),
                        HiddenControl('Deleted')),

                    Paragraph(
                        SelectControl('Category', 'Category', cnEventCategories))),

                Fieldset("When", None,
                    Paragraph(
                        DateControl('(Start) Date', 'StartDate', True, '(date / month / year)')),
                    Paragraph(
                        PureText('Note: This event will no longer be shown after the start date')),
                    Paragraph(
                        TextControl('Date description', 'DateDescription')),
                    Paragraph(
                        PureText("For instance '5th April 08', 'Mon 5/4/08 10-12', 'Four Monday evenings during May 2009'")),
                    Paragraph(
                        PureText(""))),

                Fieldset("Where", None,
                    Paragraph(
                        TextControl("Location", "Location")),
                    Paragraph(
                        PureText("Either the actual location or 'telephone-based', 'Internet-based', etc")),
                    Paragraph(
                        PureText(""))),

                Fieldset("Finally", None,
                    Paragraph(
                        TextControl('More information at', 'WebsiteAddress')),
                    Paragraph(
                        SelectControl('Your reason for listing this event', 'Relation',
                    cnEventRelationOptions)))))

    lstTabs.append(OneTab("Description",
                   Paragraph(
                    RichTextArea('Description, target audience, pricing, etc', 'Description', None, 400, 500),)))

    lstTabs.append(OneTab("Optional",
                Paragraph(
                    SelectControl('Organised by/for', 'OrganisationId', lstOrganisations, "To add an organisation use the Organisations tab on your profile", True)),
                Paragraph(
                    SelectControl('Event Series', 'EventSeriesId', lstEventSeries, "", True)),
                Paragraph(
                    SelectControl('Your role', 'Role', cnEventRoles)),
                Paragraph(
                    TextArea('Special offer for Euro Coach List Members (shown to list members only)', 'OfferForMembers'),),))

    for (strTab, strDescription, strGroup) in cnEventMOGroups:
        lstTabs.append(OneTab(strTab, MultiOptionBlock('', strDescription, strGroup)))

    lstExtraLine = None

    if blnNewOffering:
        lstButtons = Paragraph(
            SubmitControl('Save'),)
    elif blnDeleted:
        lstButtons = Paragraph(
            SubmitControl('Restore'),)
    else:
        lstButtons = Paragraph(
            SubmitControl('Update'),
            SubmitControl('Delete'))
        lstExtraLine = Paragraph(PureText('(A deleted event will be invisible to website visitors, but can still be restored)'))

    if lstExtraLine:
        lstForm.append(Fieldset("Event Details", None,
            Tabset(*lstTabs),
            lstButtons,
            lstExtraLine))
    else:
        lstForm.append(Fieldset("Event Details", None,
            Tabset(*lstTabs),
            lstButtons))

    return lstForm

def AddOrEditOffering(objHere, strType, lstFieldNames, lstForm):
    if not strId:
        try:
            strId = objHere.REQUEST.form["id"]
        except:
            strId = None

    return CreateForm(objMember, lstForm, dictOffering, "", {'Action': "Save%s" % strType})

def CleanWebsiteAddress(strAddress):
    if strAddress:
        strAddress = strAddress.strip()
        if strAddress[:7] <> 'http://':
            if '//' in strAddress:
                strAddress = strAddress[(strAddress.find('//') + 2):]
            strAddress = "http://" + strAddress
        else:
            if len(strAddress) == 7:
                strAddress = ""
    return strAddress

def FindRoleForMemberAndEvent(objMember, strEventId):
    lstRoles = SearchMany(objMember, "E3Role", "MemberId", objMember.id)
    for objRole in lstRoles:
        if objRole.ItemId == strEventId:
            return objRole
    return None

def SaveEventRole(objMember, dictEvent, strEventId):
    # Change the role for the member who created this event
    objRole = FindRoleForMemberAndEvent(objMember, strEventId)
    if not objRole:
        dodRole = GetDOD(objMember, "E3Role")
        objRole = dodRole.NewObject()
        objRole.MemberId = objMember.id
        objRole.ItemId = strEventId
    objRole.RoleType = dictEvent["Role"]
    Catalogue(objRole)

def ValidateEvent(dictEvent, objevent):
    return CheckRequiredFields(dictEvent, ("myTitle", "DateDescription", "Description"))

def SaveEvent(objMember, dictEvent, blnWithVerify = True):

    dictEvent['WebsiteAddress'] = CleanWebsiteAddress(dictEvent['WebsiteAddress'])
    objEvent = None

    if blnWithVerify:
        dictErrors = ValidateEvent(dictEvent, objMember)
        dictErrorTranslation = {"DateDescription": "Date description (When Tab)", "Description": "Description (Details Tab)", "myTitle": "Title (General Tab)"}

        strMessage = ReportErrors(dictErrors, dictErrorTranslation)
    else:
        dictErrors = {}

    if not dictErrors:
        strId = dictEvent["id"]
        if not strId:
            dodEvent = GetDOD(objMember, 'E3Offering')
            objEvent = dodEvent.NewObject(objMember.Offerings)
        else:
            objEvent = SearchOne(objMember, "E3Offering", "id", strId)

        UpdateObjectFromData(objEvent, dictEvent, cnEventFieldNames)
        Catalogue(objEvent)
        SaveEventRole(objMember, dictEvent, objEvent.id)
        strMessage = "Event saved"

    return (objEvent, strMessage, dictErrors)

def SaveOffering(objMember, dictOffering):
    strId = dictOffering["id"]
    if not strId:
        dodOffering = GetDOD(objMember, 'E3Offering')
        objOffering = dodOffering.NewObject(objMember.Offerings)

        dictOffering["Type"] = "Service"
        dictOffering['Status'] = "Draft"
    else:
        objOffering = SearchOne(objMember, "E3Offering", "id", strId)

    dictOffering['WebsiteAddress'] = CleanWebsiteAddress(dictOffering['WebsiteAddress'])

    UpdateObjectFromData(objOffering, dictOffering, cnServiceFieldNames)
    Catalogue(objOffering)

    return objOffering

def CreateOfferingStatus(objOffering):
    if not objOffering:
        strMessage = """<p>Your listing is not yet saved</p>"""

    elif objOffering.IsDraft():
        strMessage = """<p>Your listing is in draft mode. No one else can see it yet</p>
<p>To publish it, and make it visible to all website visitors, use the button below</p>
<p><input type="Submit" name="SubmitButton" value="Publish" class="btn"></p>"""

    else:
        strMessage = """<p>Your listing is published and visible to all website visitors</p>
<p><input type="Submit" name="SubmitButton" value="Unpublish" class="btn"></p>
        """

#    strURL = objOffering.REQUEST.ACTUAL_URL
    return """<fieldset>
        <legend>Status</legend>
        %s
    </fieldset>
""" % strMessage

def CheckRequiredEventFields(objEvent):
    # Title/name must be entered
    # Date, must be in the future
    # Where, at least one option
    # If f2f, location must be entered
    # Must have a date description
    lstMessages = []
    if not objEvent.myTitle:
        lstMessages.append("The title/name is missing")

    if not objEvent.DateDescription:
        lstMessages.append("The date description is missing")
    dtmStartDate = objEvent.GetStartDate()
    dtmNow = datetime.date.today()
    if dtmStartDate < dtmNow:
        lstMessages.append("The start date is in the past")

#    if not objEvent.FaceToFace and not objEvent.InternetBased and not objEvent.TelephoneBased:
    if not objEvent.Location:
        lstMessages.append("You have not entered how or where the event is delivered (Internet, telephone or location)")

#    if objEvent.FaceToFace and objEvent.Country == "Enter the country":
#        lstMessages.append("The country is missing for this face to face event")

    if lstMessages:
        if len(lstMessages) == 1:
            strResult = "<p>The following error has been found: %s</p>" % lstMessages[0]
        else:
            strResult = "<p>The following errors have been found:</p>\n<ul>\n"
            for strMessage in lstMessages:
                strResult += "<li>%s</li>\n" % strMessage
            strResult += "</ul>\n"
    else:
        strResult = ""
    return strResult

def CreateEventStatus(objEvent, strMessage):
    if not objEvent:
        strStatus = """<p>Your listing is not yet saved</p>"""

    elif objEvent.IsDraft():
        strErrorMessage = CheckRequiredEventFields(objEvent)
        if strErrorMessage:
            strStatus = """<p>%s</p>
<p><b>And your listing is in draft mode. No one else can see it yet</b></p>
<p>Before you can publish it, and make it visible to all website visitors, enter all required fields and save the event</p>""" % strErrorMessage
        else:
            strStatus = """<p><b>Your listing is in draft mode. No one else can see it yet</b></p>
<p>To publish it, and make it visible to all website visitors, use the button below</p>
<p><input type="Submit" name="SubmitButton" value="Publish" class="btn"></p>"""
    else:
        if "sent" in strMessage:
            strExtraMessage = ""
        else:
            strExtraMessage = "<p><b>To advertise this listing, see the end of this page</b></p>"
        strStatus = """<p>Your listing is published and visible to all website visitors</p>
%s
<p><input type="Submit" name="SubmitButton" value="Unpublish" class="btn"></p>
        """ % strExtraMessage

    return """<fieldset>
        <legend>Status</legend>
        %s
        %s
    </fieldset>
""" % (strMessage, strStatus)

def ReplaceLtGt(strString):
    return strString.replace('<', '&lt;').replace('>', '&gt;')

def PostOffering(objOffering):
    strRules = """<p>To post an offering to the list, it must be:</p>
<ul>
    <li>Saved</li>
    <li>An advert, recommendation, or specifically for coaches</li>
    <li>Published (to the website)</li>
    <li>Other than a standard coaching service (such as life coaching)</li>
</ul>
<p>Recommendations and other listings can only be sent once</p>
<p>Adverts for products and services can be re-sent no more than once every six months. You can send up to two adverts for your own events (workshops, presentations, etc), with at least one week between the two adverts</p>
"""

    strMessage = ""

    if not objOffering:
        strMessage = strRules

    elif objOffering.IsDraft():
        strMessage = """<p>Your listing is in draft mode. You need to publish it first</p>
""" + strRules

    elif objOffering.HasBeenPosted():
        intDaysSincePosted = objOffering.DaysSincePosted()
        if intDaysSincePosted < 182:
            strMessage = """<p>Your listing was posted %s<p>
<p>Adverts can be re-sent no more than once every six months. Please wait another %s day(s)</p>""" % (objOffering.GetFirstAnnouncementDate().strftime("%d %b %Y"), 182 - intDaysSincePosted)

    if not strMessage and objOffering.IsGeneralListing():
        strMessage = """<p>General listings cannot be emailed to the Euro Coach List"""

    if not strMessage:
        strTo = "EuroCoach-List@ForCoaches.com"
        strFrom = objOffering.GetFromAddress()
        (strHTMLBody, strTextBody) = objOffering.AdvertDetails()
        strSubject = objOffering.AdvertSubjectHeader()
        strSubject = ToUnicode(strSubject.encode('utf-8', 'replace'))
        strHTMLBody = ToUnicode(strHTMLBody.encode('utf-8', 'replace'))
        strMessage = u"""<p>To: %s</p>
<p>From: %s</p>
<p>Subject: %s</p>
<p>Message: </p>
<fieldset style="background-color:#F6F6F6">
    %s
</fieldset>
<p>Adverts (of your own product or service) can be re-sent once every six months. Recommendations and listings can only be sent once</p>
<p><input type="checkbox" name="MessageCorrect"><b>This message is correct</b>. I understand that I will not be able to resend it, even if I later discover an error in it</p>
<p><input type="checkbox" name="NotACoachingService"><b>This is not a standard coaching service</b>. Standard coaching services, such as business coaching or life coaching, can be listed but not sent to the list members. This is to stop the members from being flooded with standard coaching services. Please be considerate when posting something to the list members</p>
<p><input type = "submit" name="SubmitButton" value = "Checked and correct - email to the Euro Coach List members
" class="btn"></p>
""" % (strTo, ReplaceLtGt(strFrom), strSubject, strHTMLBody)
    return """<fieldset>
    <legend>Post your offering to the Euro Coach List members</legend>
    %s
</fieldset>""" % strMessage

def CreateOfferingEmail(strFrom, strSubject, strHTML, strId):
    objMessage = MIMEMultipart()
#    objDigest['Subject'] = strSubject
#    objDigest['From'] = 'eurocoach-list@forcoaches.com'
#    objDigest['Reply-to'] = 'noreply-eurocoach-list@forcoaches.com'
#    objDigest['To'] = 'eurocoach-list@forcoaches.com'
    objMessage["To"] = "Euro Coach List <eurocoach-list@forcoaches.com>"
    objMessage["From"] = strFrom
    objMessage["Subject"] = strSubject
    objMessage["X-MailBoxer-Archive"] = "No"
    objMessage["X-Message-Id"] = strId
    objMessage.preamble = strSubject
    objHTML = MIMEText(strHTML, 'html')
    objMessage.attach(objHTML)

    return objMessage.as_string()

def PostEvent(objEvent):
    strRules = """<p>To post an event to the list, it must be:</p>
<ul>
    <li>Saved</li>
    <li>An advert, recommendation, or specifically for coaches</li>
    <li>Published (to the website)</li>
</ul>
<p>Recommendations and other listings can only be sent once</p>
<p>You can send up to two adverts for your own events (workshops, presentations, etc), with at least one week between the two adverts</p>
"""

    strMessage = ""
    blnPostedOnce = False

    if not objEvent:
        strMessage = strRules

    elif objEvent.IsDraft():
        strMessage = """<p>Your listing is in draft mode. You need to publish it first</p>
""" + strRules

    elif objEvent.HasBeenPostedTwice():
        strMessage = """<p>Your event was posted %s and %s. You can only send two adverts for your event to the Euro Coach List</p>""" % (objEvent.GetFirstAnnouncementDate().strftime("%d %b %Y"), objEvent.GetReminderDate().strftime("%d %b %Y"))

    elif objEvent.HasBeenPosted():
        blnPostedOnce = True
        intDaysSincePosted = objEvent.DaysSincePosted()
        if intDaysSincePosted < 7:
            intToWait = 7 - intDaysSincePosted
            if intToWait == 1:
                strToWait = "day"
            else:
                strToWait = "%s days" % intToWait
            strMessage = """<p>Your event was posted %s<p>
<p>You can send two adverts for your event, with at least one week between them. Please wait another %s</p>""" % (objEvent.GetFirstAnnouncementDate().strftime("%d %b %Y"), strToWait)

    if not strMessage and objEvent.IsGeneralListing():
        strMessage = """<p>General listings cannot be emailed to the Euro Coach List"""

    if not strMessage:
        strTo = "EuroCoach-List@ForCoaches.com"
#        (strFrom, strSubject, strMessageBody, strPlainMessage) = BuildOfferingMessage(objEvent)
        strFrom = objEvent.GetFromAddress()
        strSubject = objEvent.AdvertSubjectHeader()
        (strMessageBody, strPlainMessage) = objEvent.AdvertDetails()
        strSubject = ToUnicode(strSubject.encode('utf-8', 'replace'))
        strMessageBody = ToUnicode(strMessageBody.encode('utf-8', 'xmlcharrefreplace'))

        if blnPostedOnce:
            strRepostMessage = "<b>This is your second and last advert for this event.</b> "
            strRepostMessage2 = ""
        else:
            strRepostMessage = ""
            strRepostMessage2 = " (apart from the second advert, in one week)"
        strMessage = u"""<p>To: %s</p>
<p>From: %s</p>
<p>Subject: %s</p>
<p>Message: </p>
<fieldset>
    <p>%s</p>
</fieldset>
<p>%sYou can send two adverts for your event, with at least one week between them. So please make sure the details are correct before sending the advert</p>
<p><input type="checkbox" name="MessageCorrect"><b>This message is correct</b>. I understand that I will not be able to resend it%s, even if I later discover an error in it</p>
<p><input type = "submit" name="SubmitButton" value = "Checked and correct - email to the Euro Coach List members
" class="btn"></p>
""" % (strTo, ReplaceLtGt(strFrom), strSubject, strMessageBody, strRepostMessage, strRepostMessage2)
    return """<fieldset>
    <legend>Post your Event to the Euro Coach List members</legend>
    %s
</fieldset>""" % strMessage

def SendMessageThroughMailBoxer(objHere, strMessage):
    objRequest = objHere.REQUEST
    objRequest['Mail'] = strMessage
    objMailBoxer = objHere.unrestrictedTraverse('/Websites/ECLv3/MailBoxer')
    objMailBoxer.listMail(objRequest)

def DoSendOffering(objOffering):
#    (strFrom, strSubject, strMessage, strPlainMessage) = BuildOfferingMessage(objOffering)
    strFrom = objOffering.GetFromAddress()
    strSubject = objOffering.AdvertSubjectHeader()
    (strMessage, strPlainMessage) = objOffering.AdvertDetails()

#    strMessage = GetHTMLHeader() + """<p style="font-family:sans-serif; font-size:80%">(This product or service is listed on the Euro Coach List website. To advertise your own product or service, go to <a href="http://www.EuroCoachList.Com/MyECL">www.EuroCoachList.com/MyECL</a>)</p>""" + strMessage

#    strMessage += GetHTMLFooter("""Disclaimer: Details for this product or service may have changed since this message was sent. It is your responsibility to verify the information""")
#    strPlainMessage += """Disclaimer: Details for this product or service may have changed since this message was sent. It is your responsibility to verify the information"""

    strSubject = strSubject.encode('utf-8', 'replace')
    try:
        strMessage = strMessage.encode('ascii', 'xmlcharrefreplace')
    except:
        strMessage = ToUnicode(strMessage).encode('ascii', 'xmlcharrefreplace')
    strEmailSource = CreateOfferingEmail(strFrom, strSubject, strMessage, objOffering.id)

    # Send the message
    SendMessageThroughMailBoxer(objOffering, strEmailSource)

    if objOffering.Type == "Event" and objOffering.HasBeenPosted():
        objOffering.SetReminderDate(datetime.datetime.now())
    else:
        objOffering.SetFirstAnnouncementDate(datetime.datetime.now())

def SendOfferingToEuroCoachList(objOffering, blnEvent = False):
    # Must have right boxes ticked
    lstMessage = []
    if not blnEvent and not objOffering.REQUEST.form.has_key("NotACoachingService"):
        lstMessage.append("You need to tick the box for 'not a standard coaching service'")
    if not objOffering.REQUEST.form.has_key("MessageCorrect"):
        lstMessage.append("You must tick the box to say that the message is correct")

    if lstMessage:
        strMessage = """<p class="ErrorMessage"> Your product or service could not be posted, for the following reason(s):<br>""" + "<br>".join(lstMessage) + "</p>"
        return strMessage

    DoSendOffering(objOffering)

    if blnEvent:
        return """<p class="ErrorMessage">Event details sent to the list members</p>"""
    else:
        return """<p class="ErrorMessage">Product or service details sent to the list members</p>"""

def AddOrEditService(objHere):
    # How this might be called:
    # 1. Completely new entry - no id found
        # Bring up a new entry

    # 2. No action to take, just show and ready for editing: id found, no button pressed
        # Load the record, nothing else

    # 3. A specific button pressed (Save, Publish): take action on the button
        # Take the action, then continue as per 2.

    objMember = GetCurrentMember(objHere)
    lstFieldNames = cnServiceFieldNames
    strMessage = ""
    strId = GetParameter(objHere.REQUEST, "id")

    try:
        strSubmitButton = objMember.REQUEST.form['SubmitButton']
    except:
        strSubmitButton = ""

    if strSubmitButton:
        if strSubmitButton <> "Restore":
            dictOffering = GetDataFromForm(objHere, objMember.REQUEST.form, cnServiceFieldNames)

    if strSubmitButton == "Save":
        dictOffering['Deleted'] = 'No'
        objOffering = SaveOffering(objMember, dictOffering)
        strMessage = """<p class="InfoMessage">Changes saved</p>"""
        dictOffering["id"] = objOffering.id
    elif strSubmitButton == "Update":
        objOffering = SaveOffering(objMember, dictOffering)
        strMessage = """<p class="InfoMessage">Changes saved</p>"""
    elif strSubmitButton == "Delete":
        dictOffering['Deleted'] = 'Yes'
        objOffering = SaveOffering(objMember, dictOffering)
    elif strSubmitButton == 'Restore':
        objOffering = SearchOne(objHere, "E3Offering", "id", strId)
        objOffering.Deleted = 'No'
        dictOffering = LoadDataFromObject(objOffering, lstFieldNames)
    elif strSubmitButton == "Unpublish":
        dictOffering['Status'] = "Draft"
        objOffering = SaveOffering(objMember, dictOffering)
    elif strSubmitButton == "Publish":
        dictOffering['Status'] = "Published"
        objOffering = SaveOffering(objMember, dictOffering)
    elif strSubmitButton.startswith("Checked"):
        objOffering = SaveOffering(objMember, dictOffering)
        strMessage = SendOfferingToEuroCoachList(objOffering)

    else:
        if strId:
            objOffering = SearchOne(objHere, "E3Offering", "id", strId)
        else:
            objOffering = None
        if objOffering:
            dictOffering = LoadDataFromObject(objOffering, lstFieldNames)
        else:
            dictOffering = {}
            dictOffering['WebsiteAddress'] = 'http://'
            objOffering = None
            strStatus = 'New'

    blnDeleted = False
    if dictOffering.has_key('Deleted'):
        if dictOffering['Deleted'] == 'Yes':
            blnDeleted = True
        blnNewOffering = False
    else:
        blnNewOffering = True

    if blnDeleted:
        strStatus = ""
        strPostOffering = ""
        strDeleted = """<p class="ErrorMessage">This product or service has been deleted<br>
    Before you can change it you need to click on &quot;Restore&quot;</p>
"""
    else:
        strStatus = CreateOfferingStatus(objOffering)
        strPostOffering = PostOffering(objOffering)
        strDeleted = ""

    lstForm = OfferingForm(blnNewOffering, blnDeleted)

    strForm = CreateForm(objMember, lstForm, dictOffering, "", {'Action': "SaveOffering"}, False, not blnDeleted, strPreceedWith = strStatus)
    strTitle = OfferingTitleOnPage(objOffering)
    strTitle = """<div class="OneTopicBlock"><div class="TopicHeader">%s</div></div>""" % strTitle

    strIntro = """
<fieldset>
    <legend>Information</legend>
    <p>This form is for advertising your own offerings (products and services), for recommending offerings provided by others and for listing offerings which are purely aimed at coaches</p>
</fieldset>"""

    strResult = ToUnicode(strTitle) + ToUnicode(strMessage) + ToUnicode(strDeleted) + ToUnicode(strForm) + ToUnicode(strPostOffering) + "</form>"
    return strResult

def SortOnFirstField(lst1, lst2):
    return cmp(ToUnicode(lst1[0]), ToUnicode(lst2[0]))

def GetOrganisations(objMember):
    # Only organisations with a link to the current member, i.e.:
        # Where there is a role for this member ...
#    objOrganisations = GetDataFolder(objHere, "E3Organisation")
    lstResult = []
#    for objBatch in objOrganisations.objectValues("Folder"):
#        for objOrganisation in objBatch.objectValues("E3Organisation"):

    # Only show organisations CreatedBy this member
    lstOrganisations = SearchMany(objMember, "E3Organisation", "CreatedBy", objMember.id)
    for objOrganisation in lstOrganisations:
        lstResult.append((objOrganisation.Name, objOrganisation.id))
    lstResult.sort(SortOnFirstField)
    return lstResult

def GetEventOrganiser(objMember):
    lstForm = (Fieldset('Own event', None,
        Paragraph(
            PureText('This is my own event')),
        Paragraph(
            SubmitControl('Continue'))),)

    strResult = CreateForm(objMember, lstForm, {}, "", {'OrganisationId': 'Own'})

    lstExistingOrganisations = GetOrganisations(objMember)

    lstForm = (Fieldset('Organised by an organisation', None,
        Paragraph(
            SelectControl('Organised by/for', 'OrganisationId', lstExistingOrganisations, "", True)),
        Paragraph(
            SubmitControl('Continue')),
        Paragraph(
            PureText('If the organisation is not listed, use the form below'))),)

    strResult += CreateForm(objMember, lstForm, {})

    lstForm = (Fieldset('Create a new organisation', None,
        Paragraph(
            PureText('This is organised by')),
        Paragraph(
            TextControl('Name', 'Name')),
        Paragraph(
            SelectControl('Type', 'OrganisationType', cnOrganisationTypes)),
        Paragraph(
            TextArea('Description', 'Description')),
        Paragraph(
            SelectControl('Your role in this organisation', 'Role', cnRoles)),
        Paragraph(
            SubmitControl('Continue'))),)

    strResult += CreateForm(objMember, lstForm, {}, "", {'OrganisationId': 'New'})

    return strResult

def SaveEventOrganiser(objHere, objMember):

    strName = GetParameter(objHere.REQUEST, "Name")
    strOrganisationType = GetParameter(objHere.REQUEST, "OrganisationType")
    strDescription = GetParameter(objHere.REQUEST, "Description")
    strRole = GetParameter(objHere.REQUEST, "Role")

    dodOrganisation = GetDOD(objHere, "E3Organisation")
    objOrganisation = dodOrganisation.NewObject()
    objOrganisation.Name = strName
    objOrganisation.OrganisationType = strOrganisationType
    objOrganisation.Description = strDescription
    objOrganisation.CreatedBy = objMember.id
    objOrganisation.title = strOrganisationType + ": " + strName
    Catalogue(objOrganisation)

    dodRole = GetDOD(objHere, "E3Role")
    objRole = dodRole.NewObject()
    objRole.MemberId = objMember.id
    objRole.ItemId = objOrganisation.id
    objRole.RoleType = strRole

    return objOrganisation.id

def AddEventSeries(strTitle, strId, lstEventSeries):
    strTitle = ToUnicode(strTitle)
    if not (strTitle, strId) in lstEventSeries:
        lstEventSeries.append((strTitle, strId))
    return lstEventSeries

def GetExistingEventSeries(objHere, strMemberId):
    # Events where:
        # EventSeries.CreatedBy == strMemberId, or
        # EventSeries.OrganisationBodyId == Organisation.id and
            # Organisation.CreatedBy == strMemberId or
        # Role.ItemId == Organisation.id and
            # Role.MemberId == strMemberId
    # Note: no duplicates

    lstResult = []
    for objEventSeries in SearchMany(objHere, "E3EventSeries", "CreatedBy", strMemberId):
        lstResult = AddEventSeries(objEventSeries.Title, objEventSeries.id, lstResult)

    for objOrganisation in SearchMany(objHere, "E3Organisation", "CreatedBy", strMemberId):
        for objEventSeries in SearchMany(objHere, "E3EventSeries", "OrganisationId", objOrganisation.id):
            lstResult = AddEventSeries(objEventSeries.Title, objEventSeries.id, lstResult)

    for objRole in SearchMany(objHere, "E3Role", "MemberId", strMemberId):
        for objEventSeries in SearchMany(objHere, "E3EventSeries", "OrganisationId", objRole.ItemId):
            lstResult = AddEventSeries(objEventSeries.Title, objEventSeries.id, lstResult)

    lstResult.sort(SortOnFirstField)
    return lstResult

def GetEventSeries(objHere, strOrganisationId, strMemberId):

    lstForm = (Fieldset('Single event', None,
        Paragraph(
            PureText('This is a single event')),
        Paragraph(
            SubmitControl('Continue'))),)

    strResult = CreateForm(objHere, lstForm, {}, "", {'EventSeriesId': 'Single', 'OrganisationId': strOrganisationId})

    lstEventSeries = GetExistingEventSeries(objHere, strMemberId)

    if lstEventSeries:

        lstForm = (Fieldset('Event Series', None,
            Paragraph(
                SelectControl('Part of', 'EventSeriesId', lstEventSeries, "", True)),
            Paragraph(
                SubmitControl('Continue')),
            Paragraph(
                PureText('If the event series is not listed, use the form below'))),)

        strResult += CreateForm(objHere, lstForm, {}, "", {'OrganisationId': strOrganisationId})

    lstForm = (Fieldset('New event series', None,
        Paragraph(
            PureText('This is part of the following series of events')),
        Paragraph(
            TextControl('Series title', 'Title')),
        Paragraph(
            TextArea('Description', 'Description')),
        Paragraph(
            SubmitControl('Continue'))),)

    strResult += CreateForm(objHere, lstForm, {}, "", {'EventSeriesId': 'New', 'OrganisationId': strOrganisationId})

    return strResult

def SaveEventSeries(objHere, objMember, strOrganisationId):
    strTitle = GetParameter(objHere, "Title")
    strDescription = GetParameter(objHere, "Description")
    strOrganisationId = GetParameter(objHere, "OrganisationId")

    dodEventSeries = GetDOD(objHere, "E3EventSeries")
    objEventSeries = dodEventSeries.NewObject()
    objEventSeries.CreatedBy = objMember.id
    objEventSeries.OrganisationId = strOrganisationId
    objEventSeries.Title = strTitle
    objEventSeries.Description = strDescription
    objEventSeries.title = strTitle

    Catalogue(objEventSeries)

    return objEventSeries.id

def AddOrEditEvent(objHere):
    # How this might be called:
    # 1. Completely new entry - no id found
        # Bring up a new entry

    # 2. No action to take, just show and ready for editing: id found, no button pressed
        # Load the record, nothing else

    # 3. A specific button pressed (Save, Publish): take action on the button
        # Take the action, then continue as per 2.
#    print "OrganisationId: |%s|" % strOrganisationId

    objMember = GetCurrentMember(objHere)

    lstFieldNames = cnEventFieldNames
    strMessage = ""
    strId = GetParameter(objHere.REQUEST, "id")

    strSubmitButton = GetParameter(objHere, "SubmitButton")

    dictErrors = {}

    if strSubmitButton:
        if strSubmitButton <> "Restore":
            dictEvent = GetDataFromForm(objHere, objMember.REQUEST.form, cnEventFieldNames)

#    print dictEvent

    if strSubmitButton == "Save":
        dictEvent['Deleted'] = 'No'
        (objEvent, strMessage, dictErrors) = SaveEvent(objMember, dictEvent)
        if objEvent:
            dictEvent["id"] = objEvent.id
    elif strSubmitButton == "Update":
        (objEvent, strMessage, dictErrors) = SaveEvent(objMember, dictEvent)
        if objEvent:
            dictEvent["id"] = objEvent.id
    elif strSubmitButton == "Delete":
        dictEvent['Deleted'] = 'Yes'
        (objEvent, strDummy, dictDummy) = SaveEvent(objMember, dictEvent, False)
    elif strSubmitButton == 'Restore':
        objEvent = SearchOne(objHere, "E3Offering", "id", strId)
        objEvent.Deleted = 'No'
        dictEvent = LoadDataFromObject(objEvent, lstFieldNames)
    elif strSubmitButton == "Unpublish":
        dictEvent['Status'] = "Draft"
        (objEvent, strDummy, dictDummy) = SaveEvent(objMember, dictEvent, False)
    elif strSubmitButton == "Publish":
        dictEvent['Status'] = "Published"
        (objEvent, strDummy, dictDummy) = SaveEvent(objMember, dictEvent, False)
    elif strSubmitButton.startswith("Checked"):
        (objEvent, strDummy, dictDummy) = SaveEvent(objMember, dictEvent, False)
        strMessage = SendOfferingToEuroCoachList(objEvent, True)

    else:
        if strId:
            objEvent = SearchOne(objHere, "E3Offering", "id", strId)
        else:
            objEvent = None

        if objEvent:
            dictEvent = LoadDataFromObject(objEvent, lstFieldNames)
        else:
            dictEvent = {}
            dictEvent['WebsiteAddress'] = 'http://'
            strStatus = 'New'
            dictEvent['Type'] = 'Event'
            dictEvent['Status'] = "Draft"
            strOrganisingBodyId = GetParameter(objHere, "OrganisingBodyId")
            strOrganisationId = GetParameter(objHere.REQUEST, "OrganisationId")
            strEventSeriesId = GetParameter(objHere.REQUEST, "EventSeriesId")
            if strOrganisationId == "New":
                strOrganisationId = SaveEventOrganiser(objHere, objMember)

            if not strOrganisationId:
                return GetEventOrganiser(objMember)

            if strEventSeriesId == "New":
                strEventSeriesId = SaveEventSeries(objHere, objMember, strOrganisationId)
#                strMessage = "Event saved"

            if not strEventSeriesId:
                return GetEventSeries(objHere, strOrganisationId, objMember.id)

            dictEvent['OrganisationId'] = strOrganisationId
            dictEvent['EventSeriesId'] = strEventSeriesId
            dictEvent['StartDate'] = 'dd/mm/yyyy'

    blnDeleted = False
    if dictEvent.has_key('Deleted'):
        if dictEvent['Deleted'] == 'Yes':
            blnDeleted = True
        blnNewEvent = False
    else:
        blnNewEvent = True

    if strMessage and not "class" in strMessage:
        strMessage = """<p class="InfoMessage">%s</p>""" % strMessage

    if blnDeleted:
        strStatus = ""
        strPostEvent = ""
        strDeleted = """<p class="ErrorMessage">This event has been deleted<br>
    Before you can change it you need to click on &quot;Restore&quot;</p>
"""
    else:
        strStatus = CreateEventStatus(objEvent, strMessage)
        strPostEvent = PostEvent(objEvent)
        strDeleted = ""

    lstForm = EventForm(objMember, blnNewEvent, blnDeleted, objMember.id)

    strForm = CreateForm(objMember, lstForm, dictEvent, "", {'Action': "SaveEvent"}, False, not blnDeleted, dictErrors = dictErrors, strPreceedWith = strStatus)
    strTitle = EventTitleOnPage(objEvent)
    strTitle = """<div class="OneTopicBlock"><div class="TopicHeader">%s</div></div>""" % strTitle

    strIntro = """
<fieldset>
    <legend>Information</legend>
    <p>This form is for advertising your own events (workshops, training, etc), for recommending events provided by others and for listing events which are purely aimed at coaches</p>
</fieldset>"""


#    print strPostEvent

    strResult = ToUnicode(strTitle) + ToUnicode(strDeleted) + ToUnicode(strForm) + ToUnicode(strPostEvent) + "</form>"
    return strResult

def TestMailBoxerMessage(objHere):
    print "Sending message through MailBoxer"
    objRequest = objHere.REQUEST
    strMessage = """Message-ID: <46CD9A55.5030809@coachcoen.com>
Date: Thu, 23 Aug 2007 15:31:49 +0100
From: Coen de Groot <coen@coachcoen.com>
User-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070531 CentOS/1.0.9-2.el4.centos SeaMonkey/1.0.9
MIME-Version: 1.0
To: Euro Coach List <eurocoach-list@forcoaches.com>
Subject: Events for coaches: what might you search for?
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit

Hi everyone,

I am planning to add an online diary of events for coaches to the Euro
Coach List website

To make sure it will include what you need, please let me know what you
might search for on the website

So far I've identified the following:
* Local coaching group (circle, chapter) meetings
* Local networking events
* Events by date
* Coach training
* Training events by location
* A teleclass or webinar for a particular topic
* Training in a particular topic
* All events by a particular list member

(note: I won't guarantee that all of the above will be there right from
the start)

Thanks,

Coen"""
    objRequest['Mail'] = strMessage
    objMailBoxer = objHere.unrestrictedTraverse('/Websites/ECLv3/MailBoxer')
    objMailBoxer.listMail(objRequest)
    print "Done"
