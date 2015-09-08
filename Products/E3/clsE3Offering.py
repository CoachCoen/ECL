import OFS.Folder
import Globals
from Functions import *
import DateTime
import datetime

from libConstants import cnEmptyZopeDate
from libConstants import cnFirstZopeDate

from libString import ListToText
from libString import TruncateLine
from libString import ToUnicode
from libBuildHTML import InsertBrs
from libProcessHTML import HTMLToText

from libDatabase import SearchOne
from libGeneral import CombineLists

from E3Offerings import GetOrganisationNameForId
from E3Offerings import GetEventSeriesDetails

class E3Offering(OFS.Folder.Folder):

    "E3Offering class"
    meta_type = 'E3Offering'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('myCreatedDate', DateTime.DateTime(), 'date')
        self.manage_addProperty('myTitle', '', 'ustring')
        self.manage_addProperty('StartDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('DateDescription', '', 'ustring')
        self.manage_addProperty('Publish', False, 'boolean')
        self.manage_addProperty('Type', '', 'string')
        self.manage_addProperty('Category', '', 'string')
        self.manage_addProperty('Description', '', 'utext')
        self.manage_addProperty('BriefDescription', '', 'utext')
        self.manage_addProperty('OfferForMembers', '', 'utext')
        self.manage_addProperty('Relation', '', 'string')
        self.manage_addProperty('RelationDetails', '', 'string')
        self.manage_addProperty('FaceToFace', False, 'boolean')
        self.manage_addProperty('InternetBased', False, 'boolean')
        self.manage_addProperty('TelephoneBased', False, 'boolean')
        self.manage_addProperty('RelatedTo', '', 'string')
        self.manage_addProperty('RelationType', '', 'string')
        self.manage_addProperty('Country', '', 'string')
        self.manage_addProperty('Location', '', 'ustring')
        self.manage_addProperty('BridgeCountry', '', 'string')
        self.manage_addProperty('MultiCountryBridge', False, 'boolean')
        self.manage_addProperty('Topic', '', 'ustring')
        self.manage_addProperty('myFirstAnnouncementDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('FirstAnnouncementSent', False, 'boolean')
        self.manage_addProperty('myReminderDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('ReminderSent', False, 'boolean')
        self.manage_addProperty('myCorrectionDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('CorrectionSent', False, 'boolean')
        self.manage_addProperty('Status', '', 'string')
        self.manage_addProperty('TargetAudienceCoaches', [], 'ulines')
        self.manage_addProperty('TargetAudienceGeneral', [], 'ulines')
        self.manage_addProperty('TopicsBusinessAndCareer', [], 'ulines')
        self.manage_addProperty('TopicsPersonalSuccess', [], 'ulines')
        self.manage_addProperty('DeliveryMechanismService', [], 'ulines')
        self.manage_addProperty('DeliveryMechanismProduct', [], 'ulines')
        self.manage_addProperty('BooksForCoaches', [], 'ulines')
        self.manage_addProperty('GroupSize', [], 'ulines')
        self.manage_addProperty('WebsiteAddress', '', 'ustring')
        self.manage_addProperty('Deleted', 'No', 'string')
        self.manage_addProperty('OrganisationId', 'Own', 'string')
        self.manage_addProperty('EventSeriesId', 'Single', 'string')
        self.manage_addProperty("myLastFeatured", cnEmptyZopeDate, 'date')

    def GetCreatedDate(self):
        return FromZopeDateTime(self.myCreatedDate)

    def SetLastFeatured(self, dtmDate):
        self.myLastFeatured = ToZopeDateTime(self, dtmDate)

    def GetLastFeatured(self):
        return FromZopeDateTime(self.myLastFeatured)

    def CanFeature(self):
        # Member is live, offering is published
        return self.Live() and self.IsPublished() and self.IsOwn()

    def IsPublished(self):
        return self.Status == "Published"

    def IsEvent(self):
        return self.Type == "Event"

    def GetBy(self, blnFullMember):
        if self.IsOwn():
            strName = self.GetMemberName(blnFullMember)
            if strName:
                return """ by %s """ % strName
            return ""
        else:
            strOrganisationId = self.OrganisationId
            objOrganisation = SearchOne(self, "E3Organisation", "id", strOrganisationId)
            if objOrganisation:
                return """ by %s """ % objOrganisation.Name
        return ""

    def GetHTMLFooter(self):
        return  """
    <p style="border-top: 1px solid black;
        color: rgb(112, 112, 112);
        font-family: sans-serif;
        font-size: 80%;
        clear: both;
        padding-bottom: 5px;
        line-height: 120%;">This
    product or service is listed on the Euro Coach List website. To
    advertise your own product or service, go to <a
     href="http://www.EuroCoachList.Com/MyECL">www.EuroCoachList.com/MyECL</a>.
    Details for this product or service may have changed since this message
    was sent. It is your responsibility to verify the information</p>

    """

    def GetTextFooter(self):
        return  "This product or service is listed on the Euro Coach List website. To advertise your own product or service, go to http://www.EuroCoachList.Com/MyECL. Details for this product or service may have changed since this message was sent. It is your responsibility to verify the information"

    def GetEventTitle(self):
        return "%s (%s), %s" % (self.myTitle, self.Category, self.DateDescription)

# Extracting info from offering (event, product or service)
# 2 different sources: Event or product/service
# 3 different uses: HTML preview (very similar to HTML email format), HTML email, text email
# So total of 2 x 3 = 6 combinations

    def GetTitle(self):
        if self.myTitle:
            return self.myTitle
        else:
            return self.Category

    def ReplaceGeneral(self, lstList, strCategory):
        if not lstList:
            return lstList
        lstResult = []
        for strLine in lstList:
            if strLine == "General":
                strLine = strCategory + " (general)"
            lstResult.append(strLine)
        return lstResult

    def RawAdvertDetails(self):

        dictResult = {}

        blnEvent = (self.Type == "Event")

        strTitle = self.myTitle
        if not strTitle:
            strTitle = self.Category

        dictResult["Title"] = strTitle

        if blnEvent:
            dictResult["MainDetails"] = []
            dictResult["MainDetails"].append(self.LocationDescription())
            dictResult["MainDetails"].append(self.DateDescription)
            strOrganisation = GetOrganisationNameForId(self, self.OrganisationId)
            if strOrganisation:
                dictResult["MainDetails"].append("Organised by/for " + strOrganisation)

            (strEventSeries, strEventSeriesDescription) = GetEventSeriesDetails(self, self.EventSeriesId)

            if strEventSeries:
                dictResult["EventSeries"] = strEventSeries
                if strEventSeriesDescription:
                    dictResult["EventSeriesDescription"] = strEventSeriesDescription

        else:

            dictResult["MainDetails"] = []
            if self.Category[:5].lower() <> 'other':
                dictResult["MainDetails"].append("Category: %s" % self.Category)

        lstMultiOptions = []

        lstTargetAudience = CombineLists(self.TargetAudienceCoaches, self.TargetAudienceGeneral)
        strTargetAudience = ListToText(lstTargetAudience)
        if strTargetAudience:
            lstMultiOptions.append(("Particularly suitable for", strTargetAudience))

        lstTopics = CombineLists(self.ReplaceGeneral(self.TopicsPersonalSuccess, "Personal"), self.ReplaceGeneral(self.TopicsBusinessAndCareer, "Business and Career"))
        strTopics = ListToText(lstTopics)
        if strTopics:
            lstMultiOptions.append(("It covers", strTopics))

        if not blnEvent:
            lstBooksForCoaches = self.BooksForCoaches
            strBooksForCoaches = ListToText(lstBooksForCoaches)
            if strBooksForCoaches:
                lstMultiOptions.append(("Book topics", strBooksForCoaches))

            lstDelivery = CombineLists(self.DeliveryMechanismService, self.DeliveryMechanismProduct)
            strDelivery = ListToText(lstDelivery)
            if strDelivery:
                lstMultiOptions.append(("Usually delivered via", strDelivery))

            strGroupSize = ListToText(self.GroupSize)
            if strGroupSize:
                lstMultiOptions.append(("I usually work", strGroupSize))

        if lstMultiOptions:
            dictResult["MultiOptions"] = lstMultiOptions

        if self.WebsiteAddress:
            dictResult["WebsiteAddress"] = self.WebsiteAddress

        if self.OfferForMembers:
            dictResult["SpecialOffer"] = self.OfferForMembers

        if blnEvent:
            dictResult["ListedAt"] = "http://www.EuroCoachList.com/Events?EventId=%s" % self.id
        else:
            dictResult["ListedAt"] = "http://www.EuroCoachList.com/Offerings?id=%s" % self.id

        return dictResult

    def AdvertSubjectHeader(self):
        strTitle = self.myTitle

        blnEvent = (self.Type == "Event")

        if blnEvent:
            strDate = self.DateDescription
            strLocation = self.LocationDescription()
            strFullTitle = "%s, %s, %s" % (strTitle, strDate, strLocation)
        else:
            if strTitle:
                strFullTitle = strTitle
            else:
                strFullTitle = self.Category

        (strSubject, strIntro) = self.GetIntros()

        strSubject += strFullTitle
        return strSubject

    def ContainsHTMLCode(self, strString):
        strString = strString.lower()
        for strCode in ('<p', '<br', '<td', '<span'):
            if strCode in strString:
                return True
        return False

    def FormatHTMLAdvert(self, dictDetails, strDescription, blnWithFooter, blnForDigest = False):
        if dictDetails.has_key("SpecialOffer"):
            strSpecialOffer = "<p>%s</p>\n" % dictDetails["SpecialOffer"]
        else:
            strSpecialOffer = ""

        strDetailsBlock = """
<p><b>%s</b></p>
%s
<p></p>
""" % (dictDetails["Title"], strSpecialOffer)
        print "FormatHTMLAdvert, processing strDescription"

        if not self.ContainsHTMLCode(strDescription):
            print "InsertBrs"
            strDescription = InsertBrs(strDescription)
            
        print "ToUnicode"
        strDescription = ToUnicode(strDescription)

        lstMainDetails = dictDetails["MainDetails"]

        if dictDetails.has_key("EventSeries"):
            strEventSeries = dictDetails["EventSeries"]
            if dictDetails.has_key("EventSeriesDescription"):
                strEventSeries += "<br>" + InsertBrs(dictDetails["EventSeriesDescription"])
            lstMainDetails.append(strEventSeries)

        if lstMainDetails:
            strMainDetails = u""
            for strDetails in lstMainDetails:
#                print strDetails
                strMainDetails += ToUnicode("<li>%s</li>\n" % strDetails)
            strDetailsBlock += """
<ul>
%s
</ul>
""" % strMainDetails

        if dictDetails.has_key("WebsiteAddress"):
            strDetailsBlock += """<p>More information at <a href="%s">%s</a></p>\n""" % (dictDetails["WebsiteAddress"], dictDetails["WebsiteAddress"])

        if dictDetails.has_key("MultiOptions"):
#            print dictDetails["MultiOptions"]
            strOtherDetails = ""
            for (strName, strOptions) in dictDetails["MultiOptions"]:
#                print "Option: |%s|" % strOptions
                strOtherDetails += "<li>%s: %s</li>\n" % (strName, strOptions)

            strDetailsBlock += """
<ul>
%s
</ul>
""" % strOtherDetails

        strDetailsBlock += """<p><a href="%s">Listed at the Euro Coach List Website</a></p>\n""" % (dictDetails["ListedAt"])

        if blnWithFooter:
            strFooter = self.GetHTMLFooter()
        else:
            strFooter = ""

        if blnForDigest:
            intSize = 100
        else:
            intSize = 80

        strResult = """
    <body bgcolor="#ffffff" text="#000000">
<div style="border:
    1px solid black;
    margin: 10px;
    padding: 10px;
    float: right;
    width: 40%%;
    font-family: sans-serif;
    font-size: %s%%;
    line-height: 120%%;">
%s
</div>
%s
%s
</body>""" % (intSize, ToUnicode(strDetailsBlock), strDescription, strFooter)
        return strResult

    def FormatTextAdvert(self, dictDetails, strDescription, blnWithFooter):
        strLine = "-" * len(dictDetails["Title"]) + "\n"
        strResult = strLine + dictDetails["Title"] + "\n" + strLine

        if dictDetails.has_key("SpecialOffer"):
            strResult += "Special offer for Euro Coach List members: %s\n" % dictDetails["SpecialOffer"]
        strResult += "\n"

        lstMainDetails = dictDetails["MainDetails"]

        if lstMainDetails:
            for strDetails in lstMainDetails:
                strResult += ToUnicode(strDetails) + "\n"
            strResult += "\n"

        if dictDetails.has_key("EventSeries"):
            strResult += ToUnicode(dictDetails["EventSeries"])
            if dictDetails.has_key("EventSeriesDescription"):
                strResult += ToUnicode(dictDetails["EventSeriesDescription"]) + "\n"
            strResult += "\n"

        if dictDetails.has_key("WebsiteAddress"):
            strResult += "More information at %s\n\n" % dictDetails["WebsiteAddress"]

        if dictDetails.has_key("MultiOptions"):
            for (strName, strOptions) in dictDetails["MultiOptions"]:
                strResult += "%s: %s\n" % (strName, ToUnicode(strOptions))
            strResult += "\n"

        strResult += "Listed at the Euro Coach List Website at %s\n" % dictDetails["ListedAt"]

        strDescription = HTMLToText(strDescription, True)
        strDescription = ToUnicode(strDescription)

        strResult += strLine + strDescription + strLine

        if blnWithFooter:
            strResult += self.GetTextFooter()
        return strResult

    def AdvertDetails(self, blnWithFooter = True, blnForDigest = False):
        strHTMLBody = ""
        strTextBody = ""

        dictDetails = self.RawAdvertDetails()
        strHTMLBody = self.FormatHTMLAdvert(dictDetails, self.Description, blnWithFooter, blnForDigest)
        strTextBody = self.FormatTextAdvert(dictDetails, self.Description, blnWithFooter)
        return (strHTMLBody, strTextBody)

    def GetLinks(self):
        if self.Type == "Event":
            strEditLink = "/MyECL/Events/Edit?id=%s" % self.id
            strViewLink = "/Events?EventId=%s" % self.id
        else:
            strEditLink = "/MyECL/Offerings/Edit?id=%s" % self.id
            strViewLink = "/Offerings?Id=%s" % self.id
        return (strEditLink, strViewLink)

    def EventSummaryDetails(self, blnFullMember, blnEditLinks):
        strBy = self.GetBy(blnFullMember)

        if blnEditLinks:
            strLink = "/MyECL/Events/Edit?id=%s" % self.id
        else:
            strLink = "/Events?EventId=%s" % self.id
        strTitle = "%s: %s (%s)" % (self.DateDescription, ToUnicode(self.myTitle), self.Category)
        return (strLink, strTitle, strBy)

    def PnSSummaryDetails(self, blnFullMember, blnEditLinks):
        if blnEditLinks:
            strLink = "/MyECL/Offerings/Edit?id=%s" % self.id
        else:
            strLink = "/Offerings?Id=%s" % self.id

        if self.myTitle:
            strTitle = self.myTitle
        else:
            strTitle = self.Category

        if self.IsOwn():
            strBy = self.GetMemberName(blnFullMember)
            if strBy:
                strBy = " by " + strBy
        else:
            strBy = ""

        return (strLink, strTitle, strBy)

    def TruncatedDescription(self, intMaxLength):
        strResult = ""
        if self.BriefDescription:
            strResult = self.BriefDescription
            strResult = HTMLToText(strResult)
        elif self.Description:
            strResult = self.Description
            strResult = HTMLToText(strResult)
            strResult = TruncateLine(strResult, intMaxLength)
        return strResult

    def SummaryBlock(self, blnFullMember, blnEditLinks = False, blnWithName = True):

        if self.Type == "Event":
            (strLink, strTitle, strBy) = self.EventSummaryDetails(blnFullMember, blnEditLinks)
        else:
            (strLink, strTitle, strBy) = self.PnSSummaryDetails(blnFullMember, blnEditLinks)

        if not blnWithName:
            if self.IsOwn():
                strBy = "(own offering)"
            elif self.IsRecommendation():
                strBy = "(recommendation)"
            else:
                strBy = "(suggestion)"

        strDescription = self.TruncatedDescription(80)
        if strDescription:
            strDescription = "<p>%s</p>\n" % strDescription

        if blnFullMember and self.OfferForMembers:
            strOffer = "<p><b>Special offer:</b> %s</p>" % TruncateLine(self.OfferForMembers, 80)
        else:
            strOffer = ""

        strResult = """<a href="%(Link)s"><div id="MessageBox1">
                        <p><b>%(Title)s</b> %(Sender)s</p>
                        %(Description)s
                        %(Offer)s
                    </div></a>""" % {'Link': strLink,
                                    'Title': strTitle,
                                    'Sender': strBy,
                                    'Description': strDescription,
                                    'Offer': strOffer}
        return strResult

    def SetStartDate(self, dtmDate):
        self.StartDate = ToZopeDatePlusTime(self, dtmDate)

    def GetStartDate(self):
        return FromZopeDateTime(self.StartDate)

    def GetFirstAnnouncementDate(self):
        return FromZopeDatePlusTime(self.myFirstAnnouncementDate)

    def SetFirstAnnouncementDate(self, dtmDate):
        self.myFirstAnnouncementDate = ToZopeDatePlusTime(self, dtmDate)

    def SetReminderDate(self, dtmDate):
        self.myReminderDate = ToZopeDatePlusTime(self, dtmDate)

    def GetReminderDate(self):
        return FromZopeDateTime(self.myReminderDate)

    def HasReason(self, strReason):
#        print "HasReason: %s" % strReason
        if strReason == "Advert" or strReason == "own":
            return self.IsOwn()
        elif strReason == "Recommendation" or strReason == "recommend":
            return self.IsRecommendation()
        elif strReason == "Listing" or strReason == "interest":
            return self.IsListing()
        return False

    def IsOwn(self):
        if "own" in self.Relation:
            return True
        return False

    def IsRecommendation(self):
        if "recommend" in self.Relation:
            return True
        return False

    def IsListing(self):
        if "interest" in self.Relation:
            return True
        return False

    def IsGeneralListing(self):
        if "general" in self.Relation:
            return True
        return False

    def IsDraft(self):
        if self.Status == "Draft":
            return True
        return False

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def HasBeenPosted(self):
        return not (self.myFirstAnnouncementDate == DateTime.DateTime(cnEmptyZopeDate))

    def HasBeenPostedTwice(self):
#        print self.myFirstAnnouncementDate
#	print DateTime.DateTime(cnEmptyZopeDate)
        if self.myFirstAnnouncementDate == DateTime.DateTime(cnEmptyZopeDate):
            return False
        if self.myReminderDate == DateTime.DateTime(cnEmptyZopeDate):
            return False
        return True

    def DaysSincePosted(self):
        if self.myFirstAnnouncementDate == cnEmptyZopeDate:
            return None
        dtmToday = datetime.date.today()
        deltaDays = dtmToday - FromZopeDateTime(self.myFirstAnnouncementDate)
        return deltaDays.days

    def Live(self):
        if self.Deleted == "Yes":
            return False
        return self.unrestrictedTraverse('../../').Live()

    def GetMemberName(self, blnFullMember):
        objMember = self.unrestrictedTraverse('../..')
        if objMember.Name and objMember.Name <> 'Unknown':
            return objMember.Name
        if objMember.ShowFullName == 'Showtoall':
            return objMember.FullName
        if objMember.ShowFullName == 'Members' and blnFullMember:
            return objMember.FullName
        if objMember.Username:
            if (not '@' in objMember.Username or blnFullMember) and not 'E3Member' in objMember.Username:
                return objMember.Username
        return ""

    def GetFromAddress(self):
        objMember = self.unrestrictedTraverse('../..')
        strName = self.GetMemberName(True)
        strEmailAddress = objMember.PreferredEmailAddress()
        if strEmailAddress:
            if strName:
                return "%s <%s>" % (strName, strEmailAddress)
            else:
                return strEmailAddress

        return "Coen de Groot <coen@coachcoen.com>"

    def LocationDescription(self):
        return self.Location

#        lstLocation = []
#        if self.TelephoneBased:
#            lstLocation.append("by telephone")
#        if self.InternetBased:
#            lstLocation.append("by Internet")
#        if self.FaceToFace or self.Location:
#            lstSubLocation = []
#            if self.FaceToFace:
#                lstSubLocation.append("face to face")
#            if self.Country:
#                lstSubLocation.append(self.Country)
#            if self.Location:
#                lstSubLocation.append(self.Location)
#            lstLocation.append(", ".join(lstSubLocation))
#        strLocation = ListToText(lstLocation)
#        if strLocation:
#            strLocation = strLocation[0].upper() + strLocation[1:]
#        return strLocation

    def GetIntros(self):
        if self.IsOwn():
            strSubject = "Adv: "
            if self.HasBeenPosted():
                strMessage = "A reminder of the following:"
            else:
                strMessage = "Announcing the following:"
        elif self.IsRecommendation():
            strSubject = "Rec: "
            strMessage = "I would like to recommend the following:"
        else:
            strSubject = "Info: "
            strMessage = "The following might be of interest to you:"
        return (strSubject, strMessage)

def addE3OfferingForm(self):
    "New E3Offering form"
    return GenericAddForm('E3Offering')

def addE3Offering(self, id):
    "New E3Offering action"
    objNewE3Offering = E3Offering(id)
    self._setObject(id, objNewE3Offering)

    return "New E3Offering created."
