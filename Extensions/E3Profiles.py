from libForms import CreateForm
from libForms import LoadDataFromObject
from E3Members import GetCurrentMember
from libConstants import cnProfileFieldNames
from libConstants import cnCountryNames

from libForms import Fieldset
from libForms import Paragraph
from libForms import CheckboxControl
from libForms import TextControl
from libForms import HiddenControl
from libForms import RadioButtonControl
from libForms import SelectControl
from libForms import TextArea
from libForms import SubmitControl
from libForms import PureText
from libForms import FileControl

from libGeneral import GetParameter
from libDatabase import SearchOne
from E3Members import IsFullMember
from libBuildHTML import InsertBrs
from E3Offerings import FormatOneOffering
from libString import TrimBlank
from libBuildHTML import PutInFieldset
from libString import PrepareMessageText
from libBuildHTML import IsPlural
from libBuildHTML import BuildPagingList

from libConstants import cnFirstDate
from E3Messages import FormatOneThread
from libDatabase import SearchManyBrains
from libString import ToUnicode

import random
import datetime
import cgi

#def GetPhoto(objHere):
#    objMember = None##

#    strId = GetParameter(objHere, "Id")

#    if strId:
#        objMember = SearchOne(objHere, "E3Member", "id", strId)

#    if not objMember or not "Photo" in objMember.objectIds() or not objMember.PhotoName:
#        objPhoto = objHere.unrestrictedTraverse("/Websites/ECLv3/images/NoPhoto.jpg")
#    else:
#        objPhoto = objMember.Photo

#    objHere.REQUEST.response.setHeader('content-type', """%s""" % (objPhoto.content_type))
    #objHere.REQUEST.response.setHeader('content-length', len(objPhoto.data))
#    objHere.REQUEST.response.setHeader('Accept-Ranges', 'bytes')

#    return objPhoto.data

def ShowAllMemberTweets(lstMembers):
    lstUsernames = []
    for objMember in lstMembers:
        lstUsernames.append(objMember.TwitterUsername.strip())

    strResult = """<div id="twitter_multi_div">
    <ul id="twitter_multi_update_list">
    </ul>
    </div>
    <script src="http://afterglide.googlepages.com/multitweet.js" type="text/javascript"></script>
    <script text="text/javascript">
    MultiTweetUsers = "%s";
    MultiTweetMask = "";
    TweetsPerUser = 2;
    getUserTweet(MultiTweetUsers, TweetsPerUser);
    </script>""" % ",".join(lstUsernames)

    strResult = PutInFieldset("Recent tweets by list members", strResult)
    return strResult

def SortMemberOnName(objMember1, objMember2):
    return cmp(objMember1.VisibleName(True), objMember2.VisibleName(True))

def ShowAllTwitters(objHere):
    lstMembers = []
    blnFullMember = IsFullMember(objHere)
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.TwitterUsername:
                lstMembers.append(objMember)

    if not lstMembers:
        return "<p>No members found with a Twitter username</p>"

    lstMembers.sort(SortMemberOnName)

    strList = ""
    for objMember in lstMembers:
        strName = objMember.VisibleName(blnFullMember)
        if strName == "Anonymous":
            strList += """<li><a href="http://Twitter.com/%(Username)s" target="_blank">%(Username)s</a></li>\n""" % {"Username": objMember.TwitterUsername}
        else:
            strList += """<li><a href="http://Twitter.com/%(Username)s" target="_blank">%(Name)s (%(Username)s)</a></li>\n""" % {"Username": objMember.TwitterUsername, "Name": strName}

    strResult = PutInFieldset("List members on Twitter", """<ul>
    %s
    </ul>
    """) % strList

    strResult += ShowAllMemberTweets(lstMembers)

    return strResult

def ListChapters(objHere):
    strResult = ""
    blnFullMember = IsFullMember(objHere)
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == "Full":
                strName = ""
                if objMember.Name and (objMember.ShowFullName == 'Showtoall' or (objMember.ShowFullName == 'Members' and blnFullMember)):
                    strName = objMember.Name
                if strName and objMember.HostOfChapter:
                    strResult += """<li><a href="/Members/ViewProfile?MemberId=%s">%s, hosted by %s</a></li>""" % (objMember.id, objMember.HostOfChapter, strName)

    if strResult:
        strResult = """
<ul>
    %s
</ul>
""" % strResult
    else:
        strResult = "<p>No chapters found</p>"
    return strResult

def ProfileTitle(objHere):
    strResult = "Member profile"

    strMemberId = GetParameter(objHere.REQUEST, "MemberId")
    if strMemberId:
        objMember = SearchOne(objHere, "E3Member", "id", strMemberId)

    if objMember:
        if objMember.Name and (objMember.ShowFullName == "Showtoall" or (objMember.ShowFullName == "Members" and IsFullMember(objHere))):
            strName = objMember.Name

        strTagLine = objMember.TagLine

        if strName:
            strResult = "Member profile for %s" % strName
            if strTagLine:
                strResult += ", %s" % strTagLine

    return strResult

def ListProfiles(objHere):
    blnFullMember = IsFullMember(objHere)
    dictMembers = {}
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == "Full":
                strName = ""
                if (objMember.ShowFullName == 'Showtoall' or (objMember.ShowFullName == 'Members' and blnFullMember)):
                    if objMember.Name and objMember.Name.lower() <> 'unknown' and objMember.Name.lower() <> 'none':
                        strName = objMember.Name
                if strName:
                    if not dictMembers.has_key(strName):
                        dictMembers[strName] = []
                    dictMembers[strName].append(objMember)

    lstNames = dictMembers.keys()
    lstNames.sort()
    strResult = ""
    for strName in lstNames:
        for objMember in dictMembers[strName]:
            if objMember.TagLine:
                strTagLine = " - " + objMember.TagLine
            else:
                strTagLine = ""
            strResult += """<p><a href="/Members/ViewProfile?MemberId=%s">%s%s</a></p>\n""" % (objMember.id, strName, strTagLine)

#    strResult = unicode(strResult, 'utf-8', 'replace')
    return strResult

def ChooseFeaturedMember(objHere):
    lstUnfeaturedMembers = []
    lstFeaturedMembers = []

    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.CanFeature():
                if objMember.GetLastFeatured() < cnFirstDate:
                    lstUnfeaturedMembers.append(objMember)
                else:
                    lstFeaturedMembers.append(objMember)
    if lstUnfeaturedMembers:
        objMember = random.choice(lstUnfeaturedMembers)
        return objMember

    dictFeaturedMembers = {}
    for objMember in lstFeaturedMembers:
        dictFeaturedMembers[objMember.GetLastFeatured] = objMember

    lstDates = dictFeaturedMembers.keys()
    lstDates.sort()
    objMember = dictFeaturedMembers[lstDates[0]]

    return objMember

def RecordFeaturedMember(objHere, strId):
    objData = objHere.unrestrictedTraverse("/Data/E3")
    objData.RecentFeaturedMembers = objData.RecentFeaturedMembers + (strId, )

def ShowFeaturedMember(objHere):
    objMember = ChooseFeaturedMember(objHere)
    objMember.SetLastFeatured(datetime.date.today())
    RecordFeaturedMember(objHere, objMember.id)
    (blnAbbreviated, strCommercialComments) = PrepareMessageText(objMember.CommercialComments, 200, False)
    strName = objMember.Name
    strName = cgi.escape(strName).replace('"', '&quot;')
#    strName = ToUnicode(strName)
    strPhoto = ""
    if objMember.PhotoName:
        strPhoto = """<img src="/images/Members/%s" width="120" align="left" border="0" alt="Photo of %s">""" % (objMember.PhotoName, strName)
    if blnAbbreviated:
        strCommercialComments += " ... More"

    strProfile = """<fieldset class="HomePage">
    <legend>Featured list member</legend>
    <a href="/Members/ViewProfile?MemberId=%s" class="HomePageBlock">
        %s
        <div class="HomePageTitle">%s</div>
        <div class="HomePageSubtitle">%s</div>
        <div class="HomePageText">%s</div>
    </a>
    <a href="/Members/ListProfiles" class="HomePageBlock2">
       <div class="HomePageSubtitle">Show all member profiles</div>
    </a>
</fieldset>
""" % (objMember.id, strPhoto, strName, objMember.TagLine, strCommercialComments)

    try:
        strProfile = unicode(strProfile, 'utf-8', 'replace')
    except:
        pass
    return strProfile

def ShowFeaturedMemberOld(objHere):
    objMember = ChooseFeaturedMember(objHere)
    objMember.SetLastFeatured(datetime.date.today())
    RecordFeaturedMember(objHere, objMember.id)
    (blnAbbreviated, strCommercialComments) = PrepareMessageText(objMember.CommercialComments, 200, False)
    strPhoto = ""
    if objMember.PhotoName:
        strPhoto = """<img src="/images/Members/%s" width="80" align="left" border="0" alt="Photo of %s">""" % (objMember.PhotoName, objMember.Name)
    if blnAbbreviated:
        strCommercialComments += " ... More"
    strName = objMember.Name
    strProfile = """
    <a href="/Members/ViewProfile?MemberId=%s">
        <h2>%s</h2>
        <div class="FeaturedMemberTitle">%s</div>
        %s
        <p>%s</p>
    </a>
""" % (objMember.id, strName, objMember.TagLine, strPhoto, strCommercialComments)
    try:
        strProfile = unicode(strProfile, 'utf-8', 'replace')
    except:
        pass
    return strProfile

def ShowProfileData(varData, strShowData, strLabel, blnFullMember, strFormat = ""):
#    print strShowData, blnFullMember
    if (strShowData == 'Showtoall' or (strShowData == 'Members' and blnFullMember)):
        if varData:
            strData = TrimBlank(varData)
            if strFormat == 'email':
                strData = """<a href="mailto:%s">%s</a>""" % (strData, strData)
            elif strFormat == 'website':
                if not '//' in strData:
                    strData = """<a href="http://%s" target="_blank">%s</a>""" % (strData, strData)
                else:
                    strData = """<a href="%s" target="_blank">%s</a>""" % (strData, strData)

            return """<p><label>%s</label><div class="ProfileData">%s</div></p>\n""" % (strLabel, InsertBrs(strData))
    return ""

def ProfileFieldset(blnFullMember, strLegend, objMember, lstFields):
    strDetails = ""
    for (strField, strLabel, strShowField) in lstFields:
        strDetails += ShowProfileData(strField, strShowField, strLabel, blnFullMember)
    if strDetails:
        return """
<fieldset>
    <legend>%s</legend>
    %s
</fieldset>""" % (strLegend, strDetails)
    return ""
def FoundBrainsDateOrder(objBrain1, objBrain2):
#    print "Comparing %s with %s" % (objBrain1.mailDate, objBrain2.mailDate)
    return cmp(objBrain2.mailDate, objBrain1.mailDate)

def FormatMessageBrains(lstMessageBrains, blnFullMember, intMaxMessages = 10, intOffset = 0):
    strResult = ""

    lstMessageBrains.sort(FoundBrainsDateOrder)

    if intOffset > 0:
        lstMessageBrains = lstMessageBrains[intOffset:]

    if intMaxMessages:
        lstMessageBrains = lstMessageBrains[:intMaxMessages]

    for objBrain in lstMessageBrains:
        try:
            objObject = objBrain.getObject()
        except:
            objObject = False
        if objObject:
            strResult += FormatOneThread(objObject, True, blnFullMember)

    return strResult

def ListBlockForProfile(strList, strType, strMemberId, intItemsFound, intOffset, blnFullList):
    strNavigation = ""
    if blnFullList:
        intMaxItems = 20
    else:
        intMaxItems = 10
    if blnFullList:
        if intOffset < 0:
            intOffset = 0
        intFirstItem = intOffset + 1
        intLastItem = intFirstItem + intMaxItems - 1
        strLink = "/Members/ViewProfile?Display=%ss&MemberId=%s&Offset=%%s" % (strType.capitalize(), strMemberId)
        strNavigation = BuildPagingList(intMaxItems, intItemsFound, intFirstItem, intLastItem, strLink, intOffset)

        strMessage = "%s %s%s found<br>\n%s" % (intItemsFound, strType, IsPlural(intItemsFound), strNavigation)
    else:
        if intItemsFound > intMaxItems:
            strMessage = """
                %(ItemsFound)s %(Type)s%(IsPlural)s found<br>First %(MaxItems)s %(Type)ss displayed.
                <a href="/Members/ViewProfile?Display=%(TypeCaps)ss&MemberId=%(MemberId)s">Show all %(Type)ss</a>
                """ % {"ItemsFound": intItemsFound,
                       "Type": strType,
                       "IsPlural": IsPlural(intItemsFound),
                       "TypeCaps": strType.capitalize(),
                       "MaxItems": intMaxItems,
                       "MemberId": strMemberId}
        else:
            strMessage = "%s %s%s found<br>\n%s" % (intItemsFound, strType, IsPlural(intItemsFound), strNavigation)

    if blnFullList:
        strResult = """<p>Showing %ss only for this member. <a href="/Members/ViewProfile?MemberId=%s">Return to the full profile</a></p>""" % (strType, strMemberId)
    else:
        strResult = ""

    strResult += "<p>%s</p>\n%s" % (strMessage, strList)
    if strNavigation:
        strResult += "<p>%s</p>\n" % strNavigation
    return PutInFieldset("%ss" % strType.capitalize(), strResult)

def ListMessagesForProfile(lstMessageBrains, blnFullMember, strMessage, strMemberId, intOffset, blnFullList):
    strNavigation = ""
    if blnFullList:
        intMaxMessages = 20
    else:
        intMaxMessages = 10
    strList = FormatMessageBrains(lstMessageBrains, blnFullMember, intMaxMessages, intOffset)
    if blnFullMember:
        strPublic = ""
    else:
        strPublic = "public"
    if blnFullList:
        if intOffset < 0:
            intOffset = 0
        intFirstThread = intOffset + 1
        intLastThread = intFirstThread + intMaxMessages - 1
        strLink = "/Members/ViewProfile?Display=Messages&MemberId=%s&Offset=%%s" % strMemberId
        strNavigation = BuildPagingList(intMaxMessages, len(lstMessageBrains), intFirstThread, intLastThread, strLink, intOffset)

        strMessage += "<br>" + strNavigation
    else:
        if len(lstMessageBrains) > intMaxMessages:
            strMessage += """<br>First %s %s messages displayed.
                <a href="/Members/ViewProfile?Display=Messages&MemberId=%s">Show all %s messages</a>""" % (intMaxMessages, strPublic, strMemberId, strPublic)

    if blnFullList:
        strResult = """<p>Showing messages only for this member. <a href="/Members/ViewProfile?MemberId=%s">Return to the full profile</a></p>""" % strMemberId
    else:
        strResult = ""

    strResult += "<p>%s</p>\n%s" % (strMessage, strList)
    if strNavigation:
        strResult += "<p>%s</p>\n" % strNavigation
    return PutInFieldset("List messages", strResult)

def ListMessagesForMember(objMember, blnFullMember, intOffset = -1, blnFullList = False):
    strResult = ""
    lstMessageBrains = SearchManyBrains(objMember, 'E3Messages', "UserId", objMember.id)
    if not lstMessageBrains:
        return ""

    if blnFullList:
        intMaxMessages = 20
    else:
        intMaxMessages = 10

    if not blnFullMember:
        lstPublicBrains = []
        for objBrain in lstMessageBrains:
            if not objBrain.Private:
                lstPublicBrains.append(objBrain)

        if not lstPublicBrains:
            return ""
#            return PutInFieldset("List messages",
#                                 "<p>%s message%s posted. No public messages posted" % \
#                                 (len(lstMessageBrains), IsPlural(len(lstMessageBrains))))

#        strMessage = "%s message%s posted, of which %s public message%s. " \
#            % (len(lstMessageBrains), IsPlural(len(lstMessageBrains)),
#               len(lstPublicBrains), IsPlural(len(lstPublicBrains)))
#        return ListMessagesForProfile(lstPublicBrains, blnFullMember, strMessage, objMember.id, intOffset, blnFullList)
        strList = FormatMessageBrains(lstPublicBrains, blnFullMember, intMaxMessages, intOffset)
        strResult = ListBlockForProfile(strList, "public message", objMember.id, len(lstPublicBrains), intOffset, blnFullList)
        return strResult

#    strMessage = "%s message%s posted" % (len(lstMessageBrains), IsPlural(len(lstMessageBrains)))
#    return ListMessagesForProfile(lstMessageBrains, blnFullMember, strMessage, objMember.id, intOffset, blnFullList)
    if not lstMessageBrains:
        return ""
    strList = FormatMessageBrains(lstMessageBrains, blnFullMember, intMaxMessages, intOffset)
    strResult = ListBlockForProfile(strList, "message", objMember.id, len(lstMessageBrains), intOffset, blnFullList)
    return strResult

# FormatOneOffering(objOffering, blnFullMember)

def OfferingsTitleOrder(objOffering1, objOffering2):
    return cmp(objOffering1.myTitle, objOffering2.myTitle)

def OfferingsDateOrder(objOffering1, objOffering2):
    return cmp(objOffering1.GetStartDate(), objOffering2.GetStartDate())

def ListOfferingsForMember(objMember, blnFullMember, blnEvents, intOffset = -1, blnFullList = False):
    if blnFullList:
        intMaxMessages = 20
    else:
        intMaxMessages = 10

    lstAllOfferings = objMember.Offerings.objectValues("E3Offering")
    lstOfferings = []
    for objOffering in lstAllOfferings:
        if objOffering.Live() and objOffering.IsPublished() and (objOffering.IsEvent() == blnEvents):
            lstOfferings.append(objOffering)

    if not lstOfferings:
        return ""

    if blnEvents:
        lstOfferings.sort(OfferingsDateOrder)
    else:
        lstOfferings.sort(OfferingsTitleOrder)
    if intOffset > len(lstOfferings) - intMaxMessages:
        intOffset = len(lstOfferings) - intMaxMessages + 1

    intNumberOfOfferings = len(lstOfferings)

    if intOffset >= 0:
        lstOfferings = lstOfferings[intOffset:]

    lstOfferings = lstOfferings[:intMaxMessages]

    strList = ""

    for objOffering in lstOfferings:
        strList += ToUnicode(objOffering.SummaryBlock(blnFullMember, blnWithName = False))

    if blnEvents:
        strType = "event"
    else:
        strType = "offering"

    return ListBlockForProfile(strList, strType, objMember.id, intNumberOfOfferings, intOffset, blnFullList)

def LOMToDo():

    strOffset = GetParameter(objMember.REQUEST, "Offset")
    if strOffset:
        intOffset = int(strOffset)
    else:
        intOffset = 0
    blnFullMember = IsFullMember(objMember)
    if blnShowDeleted:
        lstOfferings = objMember.Offerings.objectValues("E3Offering")
    else:
        lstOfferings = []
        for objOffering in objMember.Offerings.objectValues("E3Offering"):
            if objOffering.Deleted == "No":
                lstOfferings.append(objOffering)
    strResult = FormatList(lstOfferings, blnFullMember, intOffset, "/Members/ViewProfile?MemberId=%s" % objMember.id, "", intMaxEntries, blnTopNavigation)
    return strResult


def ViewProfile(objHere):
#    from E3TempData import GetUsername
#    strUsername = GetUsername(objHere)
#    print "Username: %s." % strUsername

    strId = GetParameter(objHere.REQUEST, "MemberId")
    if not strId:
        return "No member selected"

    blnFullMember = IsFullMember(objHere)

    strOffset = GetParameter(objHere.REQUEST, "Offset")
    if strOffset:
        intOffset = int(strOffset)
    else:
        intOffset = 0

    strDisplay = GetParameter(objHere.REQUEST, "Display")
    blnListOnly = ( len(strDisplay) > 0)

    objMember = SearchOne(objHere, "E3Member", "id", strId)
    if not objMember:
        return "<p>Member not found. Please contact the list owner</p>"

    if not objMember.MembershipType == "Full":
        return "<p>This person is no longer a member</p>"

    strResult = ""

    strResult += objMember.ProfilePersonalDetails(blnFullMember, blnSmall = blnListOnly)

    if not blnListOnly:
        strResult += objMember.ProfileContactDetails(blnFullMember)
        strResult += objMember.ProfileCommunityDetails(blnFullMember)
        strResult += objMember.ProfilePersonalComments(blnFullMember)
        strResult += objMember.ProfileProfessionalDetails(blnFullMember)

        strResult += objMember.ProfileTwitterWidget()
        strResult += ListOfferingsForMember(objMember, blnFullMember, True)
        strResult += ListOfferingsForMember(objMember, blnFullMember, False)
        strResult += ListMessagesForMember(objMember, blnFullMember)

    if strDisplay == "Messages":
        strResult += ListMessagesForMember(objMember, blnFullMember, intOffset, True)

    if strDisplay == "Offerings":
        strResult += ListOfferingsForMember(objMember, blnFullMember, False, intOffset, True)

    if strDisplay == "Events":
        strResult += ListOfferingsForMember(objMember, blnFullMember, True, intOffset, True)

    if strResult:
        strResult = "<form>%s</form>" % strResult
    else:
        if blnFullMember:
            strResult = "<p>This member does not have any public or members-only data</p>"
        else:
            strResult = "<p>This member does not have any public data</p>"

#    strResult = unicode(strResult, 'utf-8', 'replace')

    strResult = ToUnicode(strResult)

    return strResult

def EditProfileForm(objHere):
    objMember = GetCurrentMember(objHere)

    lstEmailAddresses = []
    for objEmailAddress in objMember.objectValues('E3EmailAddress'):
        lstEmailAddresses.append(objEmailAddress.EmailAddress)
    lstEmailAddresses.sort()

    lstPrivacyOptions = ('Hide', 'Members only', 'Show to all')

    lstForm = []

    lstForm.append(Fieldset('Your Privacy Settings', None,
        Paragraph(
            PureText('For some of your details you can choose whether they will be visible to everyone or to fellow list members only')),
        Paragraph(
            PureText('All the other details you enter below will automatically be visible to everyone'))))

    lstForm.append(Fieldset('Featured List Member', None,
        Paragraph(
            PureText('Once a day the system chooses a list member to feature on the website. For an example see the right hand side of this page')),
        Paragraph(
            PureText('You may be featured if you have entered your name, tag line and comments for potential clients. Your full name must be made visible to all if you want to be featured')),
        Paragraph(
            TextControl('Name', 'Name')),
        Paragraph(
            RadioButtonControl('Full name', 'ShowFullName', lstPrivacyOptions)),
        Paragraph(
            TextControl('Tagline or title', 'TagLine', strComments = '(for instance "Executive Coaching", "Coaching to be your best")')),
        Paragraph(
            TextArea('Comments for potential clients', 'CommercialComments'))))

    lstForm.append(Fieldset('Personal Details', None,
        Paragraph(
            SelectControl('Country', 'Country', cnCountryNames)),
        Paragraph(
            RadioButtonControl('Show country', 'ShowCountry', lstPrivacyOptions)),
        Paragraph(
            TextControl('Location', 'Location')),
        Paragraph(
            RadioButtonControl('Show location', 'ShowLocation', lstPrivacyOptions)),
        Paragraph(
            TextControl('Postcode', 'Postcode')),
        Paragraph(
            RadioButtonControl('Show postcode', 'ShowPostcode', lstPrivacyOptions)),
        Paragraph(
            TextArea('Languages', 'Languages'))))

    lstForm.append(Fieldset('Contact Details', None,
        Paragraph(
            SelectControl('Contact email address', 'ContactEmailAddress', lstEmailAddresses, strComments = 'Email addresses are entered on the <a href="/MyECL">MyECL page</a>')),
        Paragraph(
            RadioButtonControl('Show email address', 'ShowEmailAddress', lstPrivacyOptions)),
        Paragraph(
            TextControl('Website address', 'WebsiteAddress')),
        Paragraph(
            TextControl('Phone', 'PhoneNumber')),
        Paragraph(
            RadioButtonControl('Show phone number', 'ShowPhoneNumber', lstPrivacyOptions))))

    lstForm.append(Fieldset('Coaching communities', None,
            Paragraph(
                PureText("I am the host of the following coaching group (chapter, circle, network, etc):")),
            Paragraph(
                TextControl('Group name', 'HostOfChapter'))))

    lstForm.append(Fieldset('Personal comments', None,
            Paragraph(
                TextArea('Personal comments', 'CommunityComments')),
            Paragraph(
                RadioButtonControl('Show comments', 'ShowCommunityComments', lstPrivacyOptions))))

    lstForm.append(Fieldset('Your business or professional profile', None,
            Paragraph(
                TextArea('Biography', 'Biography')),
            Paragraph(
                RadioButtonControl('Show biography', 'ShowBiography', lstPrivacyOptions)),
            Paragraph(
                TextArea('Testimonials', 'Testimonials'))))
    lstForm.append(Fieldset('Save your changes', None,
            Paragraph(
                SubmitControl('Update profile'))))

    dictMemberProfile = LoadDataFromObject(objMember, cnProfileFieldNames)
    strForm = CreateForm(objHere, lstForm, dictMemberProfile, "", {'Action': 'UpdateProfile'})
#    strForm = unicode(strForm, 'utf-8', 'replace')
#    strResult = "Testing"
    return strForm

