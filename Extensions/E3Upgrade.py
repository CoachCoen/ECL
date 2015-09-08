from libDatabase import GetDataFolder
from libConstants import cnDeliveryModes
from libConstants import cnListNameECL
from E3MailingList import GetList
from libDatabase import GetDOD
from libDatabase import SearchOne
from E3Messages import CountMessages
from MetaHelp import ImportHelpFile
from datetime import date
from datetime import timedelta
from libConstants import cnStatsList
from libConstants import cnEmptyZopeDate
# from MetaStart import AddTagDefinitions
from MetaStart import AddThreadDefinitions
# from E3Threading import CreateInitialTopics
from MetaStart import NewFieldIndex
from MetaStart import AddDataObjectDefinition
from E3Offerings import ReadInitialMultiOptions
from E3Offerings import ImportMCIBooks
from E3Offerings import UpdateCounts
from E3Offerings import CreateInitialCategories
from libDatabase import Catalogue
from libString import ToUnicode
from libConstants import cnShortDateFormat

def u30to31AddPrivateProperty(objHere, blnSkip = False):
    # Add new property 'Private' to all list messages, unless it's already got one
    if blnSkip:
        print "Skipped: Adding new property: Private to all messages"
        return

    print "Adding new property: Private to all messages"
    objArchive = GetDataFolder(objHere, 'E3Messages')
    for objYear in objArchive.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            for objMessage in objMonth.objectValues('Folder'):
                if not 'Private' in objMessage.propertyIds():
                    objMessage.manage_addProperty('Private', True, 'boolean')

def u30to31NewDeliveryModes(objHere, blnSkip = False):
    # Make sure all required MailBoxerMembers records exist:
    if blnSkip:
        print "Skipped: Adding new MailBoxerMembers objects"
        return

    print "Adding new MailBoxerMembers objects"
    dictFound = {}
    for strDeliveryMode in cnDeliveryModes:
        dictFound[strDeliveryMode] = False
    objList = GetList(objHere, cnListNameECL)
    for objMailBoxerMembers in objList.objectValues('E3MailBoxerMembers'):
        dictFound[objMailBoxerMembers.DeliveryMode] = True
    dodMailBoxerMembers = GetDOD(objHere, 'E3MailBoxerMembers')
    for strDeliveryMode in cnDeliveryModes:
        if not dictFound[strDeliveryMode]:
            objMailBoxerMembers = dodMailBoxerMembers.NewObject(objList)
            objMailBoxerMembers.DeliveryMode = strDeliveryMode
            print "Added MailBoxerMembers object for %s" % strDeliveryMode
        else:
            print "Already exists: %s" % strDeliveryMode

def u30to31CheckForMultipleDeliveryAddresses(objHere, blnSkip = False):
    if blnSkip:
        print "Skipped: Checking for multiple delivery addresses"
        return

    print "Checking for multiple delivery addresses"
    for objBatch in GetDataFolder(objHere, "E3Member").objectValues('Folder'):
        for objMember in objBatch.objectValues("E3Member"):
            if objMember.MembershipType == "Full":
                intFound = 0
                lstAddresses = []
                for objEmailAddress in objMember.objectValues("E3EmailAddress"):
                    if not objEmailAddress.Bouncing and objEmailAddress.Confirmed:
                        for objListMembership in objEmailAddress.objectValues("E3ListMembership"):
                            if objListMembership.GetDeliveryMode() <> "NoMail":
                                lstAddresses.append(objEmailAddress.EmailAddress)
                if len(lstAddresses) > 1:
                    print "Multiple addresses for %s, %s: %s" % (objMember.id, objMember.Name, ", ".join(lstAddresses))

def u30to31NewStructureForDeliveryDetails(objHere, blnSkip = False):
    if blnSkip:
        print "Skipped: New structure for delivery details"
        return

    print "New structure for delivery details"
    dodListMembership = GetDOD(objHere, "E3ListMembership")

    for objBatch in GetDataFolder(objHere, "E3Member").objectValues('Folder'):
        for objMember in objBatch.objectValues("E3Member"):
            objListMembership = None
            if "ListMembership-ECL" in objMember.objectIds():
                objListMembership = objMember.unrestrictedTraverse("ListMembership-ECL")
                objMember.manage_delObjects("ListMembership-ECL")
                print "Deleted old ListMembership-ECL first"

            if not "ListMemberships" in objMember.objectIds("Folder"):
                objMember.manage_addFolder("ListMemberships")

            if "ECL" in objMember.ListMemberships.objectIds():
                objMember.ListMemberships.manage_delObjects("ECL")

            if not "ListMembership-ECL" in objMember.objectIds():
                blnFound = False
                for objEmailAddress in objMember.objectValues("E3EmailAddress"):
                    strLastEmailAddress = ""
                    for objListMembership in objEmailAddress.objectValues("E3ListMembership"):
                        strLastEmailAddress = objListMembership.EmailAddress
                        if objListMembership.GetDeliveryMode() <> "NoMail":
                            strDeliveryMode = objListMembership.GetDeliveryMode()
                            strEmailAddress = objListMembership.EmailAddress
                            blnFound = True
                        objEmailAddress.manage_delObjects(objListMembership.id)
                if not blnFound:
                    if objListMembership:
                        strEmailAddress = objListMembership.EmailAddress
                        strDeliveryMode = objListMembership.GetDeliveryMode()
                    else:
                        strEmailAddress = strLastEmailAddress
                        strDeliveryMode = "NoMail"
                objNewListMembership = dodListMembership.NewObject(objMember.ListMemberships, "ECL")
                objNewListMembership.myDeliveryMode = strDeliveryMode
                objNewListMembership.EmailAddress = strEmailAddress

def u30to31NewPropertyForEmailAddress(objHere, blnSkip = False):
    if blnSkip:
        print "Skipped: New property for email addresses"
        return

    print "New property: clsE3EmailAddress.myConfirmationReminderSent"
    dodListMembership = GetDOD(objHere, "E3ListMembership")

    for objBatch in GetDataFolder(objHere, "E3Member").objectValues('Folder'):
        for objMember in objBatch.objectValues("E3Member"):
            for objEmailAddress in objMember.objectValues('E3EmailAddress'):
                if not 'myConfirmationReminderSent' in objEmailAddress.propertyIds():
                    objEmailAddress.manage_addProperty('myConfirmationReminderSent', cnEmptyZopeDate, 'date')
                if not 'ChangeToThisOne' in objEmailAddress.propertyIds():
                    if not objEmailAddress.Confirmed and objEmailAddress.myChangedFrom:
                        blnChangeToThisOne = True
                    else:
                        blnChangeToThisOne = False
                    objEmailAddress.manage_addProperty('ChangeToThisOne', blnChangeToThisOne, 'boolean')

def SaveStats(objContext, dictStats):
    print "Saving stats"

    # Update all existing stats
    objStats = GetDataFolder(objContext, "E3ListStat")
    for objStat in objStats.objectValues("E3ListStat"):
        dtmDate = objStat.GetDateOfCount()
        if dictStats.has_key(dtmDate):
            for strItem in ("JoinedYesterday", "PaymentYesterday", "ExpiredYesterday", "AdvertPostedYesterday", "NonAdvertPostedYesterday"):
                if not objStat.hasProperty(strItem):
                    objStat.manage_addProperty(strItem, dictStats[dtmDate][strItem], 'int')
            del(dicStats[dtmDate])
        for strItem in cnStatsList:
            if not objStat.hasProperty(strItem):
                objStat.manage_addProperty(strItem, 0, "int")

    dodListStat = GetDOD(objContext, "E3ListStat")

    for dtmDate in dictStats.keys():
        objStat = dodListStat.NewObject()
        objStat.SetDateOfCount(dtmDate)
        for strItem in ("JoinedYesterday", "PaymentYesterday", "ExpiredYesterday", "AdvertPostedYesterday", "NonAdvertPostedYesterday"):
            if dictStats[dtmDate].has_key(strItem):
                objStat.manage_addProperty(strItem, dictStats[dtmDate][strItem], 'int')
        for strItem in cnStatsList:
            if not objStat.hasProperty(strItem):
                objStat.manage_addProperty(strItem, 0, "int")

def AddPastStat(dictStats, dtmDate, strType):
    if "Yesterday" in strType:
        dtmDate = dtmDate + timedelta(days = 1)

    if not dictStats.has_key(dtmDate):
        dictStats[dtmDate] = {}

    if not dictStats[dtmDate].has_key(strType):
        dictStats[dtmDate][strType] = 0

    dictStats[dtmDate][strType] += 1

def u30to31StorePastStats(objContext, blnSkip = False):
    """ Done as upgrade from 3.0 to 3.1
        Gather data that is easy and reliable accessible:
        * Payments
        * Messages sent (advert/non-advert)
        * Expiries
        * Members joining"""
    # Create empty dictionary (date:eventtype:count)
    # Go through members, count events found
    # Go through messages, count them
    # Store results
    #  (notes: some records may already exists, if so add new properties, otherwise create new record)
    if blnSkip:
        print "Skipped: Get and store past statistics"
        return

    print "Get and store past statistics"
    dictStats = {}

    objMembers = GetDataFolder(objContext, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            # Check starting date
            if objMember.ImportedFromMailman:
                for objPeriod in objMember.FromMailman.objectValues('E3Period'):
                    if objPeriod.PeriodType == "Free":
                        AddPastStat(dictStats, objPeriod.GetStartDate(), "JoinedYesterday")
            else:
                AddPastStat(dictStats, objMember.GetCreatedDate(), "JoinedYesterday")
            # Get payments
            for objPayment in objMember.Historic.objectValues("E3Payment"):
                AddPastStat(dictStats, objPayment.GetDate(), "PaymentYesterday")
            for objEvent in objMember.Historic.objectValues("E3Event"):
                if objEvent.EventType == "ExpiryMessageSent":
                    AddPastStat(dictStats, objEvent.GetDate(), "ExpiredYesterday")

    # Now do the message count
    objMessages = GetDataFolder(objContext, 'E3Messages')
    for objYear in objMessages.objectValues('Folder'):
        print objYear.id
        for objMonth in objYear.objectValues('Folder'):
            print objMonth.id
            for objMessage in objMonth.objectValues('Folder'):
                dtmDate = date(year = objMessage.mailDate.year(), month = objMessage.mailDate.month(), day = objMessage.mailDate.day())
                if 'adv' in objMessage.mailSubject.lower():
                    AddPastStat(dictStats, dtmDate, "AdvertPostedYesterday")
                else:
                    AddPastStat(dictStats, dtmDate, "NonAdvertPostedYesterday")

    SaveStats(objContext, dictStats)

def DoOrSkip(objHere, fnFunction, strText, blnSkip = False):
    if blnSkip:
        print "Skipped: %s" % strText
        return

    print strText
    fnFunction(objHere)

def u30to31SmallChanges(objHere, blnSkip = False):
    if blnSkip:
        print "Skipped: Small changes"
        return

    print "Small changes"
    objECLv3 = objHere.unrestrictedTraverse("/Websites/ECLv3")
    if not "js" in objECLv3.objectIds():
        print "Adding /Websites/ECLv3/js"
        objECLv3.manage_addFolder('js')

    print "Changing /Websites/ECLv3/admin/Statistics into a folder"
    objAdmin = objECLv3.admin
    objAdmin.manage_delObjects("Statistics")
    objAdmin.manage_addFolder("Statistics")

    objMeta = objHere.unrestrictedTraverse("/Meta")
    if not "DoImportSite" in objMeta.objectIds():
        print "Creating DoImportSite External Method"
        objMeta.manage_addProduct['ExternalMethod'].manage_addExternalMethod("DoImportSite", "", "MetaVC", "ImportSite")

    if not "VCCheckChanges" in objMeta.objectIds():
        print "Creating VCCheckChanges Page Template"
        objObject = objMeta.manage_addProduct['PageTemplates'].manage_addPageTemplate("VCCheckChanges")
        objObject.pt_edit("""<span tal:replace="structure python:here.DoImportSite(here)"></span>""", "")

    if not "VCImport" in objMeta.objectIds():
        print "Creating VCImport Page Template"
        objObject = objMeta.manage_addProduct['PageTemplates'].manage_addPageTemplate("VCImport")
        objObject.pt_edit("""<span tal:replace="structure python:here.DoImportSite(here, True)"></span>""", "")

    objMember = objHere.unrestrictedTraverse("/Data/E3/E3Members/Batch024/E3Member024051")
    objHistoric = objMember.Historic
    if len(objHistoric.objectIds("E3Event")) < 2:
        print "Adding free period for member 024051"
        dodEvent = GetDOD(objHere, "E3Event")
        objEvent = dodEvent.NewObject(objHistoric)
        objEvent.SetDate(date(year = 2007, month = 12, day = 20))
        objEvent.EventType = "FreePeriod"
        objEvent.Days = 7

    print "Updating MailBoxer/mail_reply"
    objMailReply = objHere.unrestrictedTraverse("/Websites/ECLv3/MailBoxer/mail_reply")
    strContents = """
<dtml-comment>
 This script sends an 'error' reply to the sender.
</dtml-comment>

<dtml-sendmail mailhost="MailHost">
To: <dtml-var "mail.get('from')">
From: <dtml-var "getValueFor('moderator')[0]">
Reply-To: noreply-eurocoach-list@forcoaches.com
X-Mailer: <dtml-var "getValueFor('xmailer')">
Subject: Your message to the Euro Coach List could not be sent

Your email to the Euro Coach List sent from  <dtml-var "parseaddr(mail.get('from'))[1]"> with the subject
"<dtml-var "mime_decode_header(mail.get('subject','No subject'))">"
could not be sent

This is usually for one of the following reasons:
* You sent the email from an email address which isn't registered
* You sent the email from an email address which is not yet confirmed
* Your membership has expired
* You are not a member of the Euro Coach List

Please see www.EuroCoachList.com/Help for tips on how to sort this out

<dtml-var "getValueFor('Signature')">
</dtml-sendmail>"""
    objMailReply.manage_edit(strContents, "")

def Upgrade3p0To3p1(objHere):

    blnSkip = True

    print "Upgrading from 3.0 to 3.1"
    u30to31SmallChanges(objHere, blnSkip)
    u30to31StorePastStats(objHere, blnSkip)
    u30to31AddPrivateProperty(objHere, blnSkip)
    DoOrSkip(objHere, CountMessages, "Re-counting public and private messages", blnSkip)
    DoOrSkip(objHere, ImportHelpFile, "Re-importing help, rules and FAQs", blnSkip)
    u30to31NewDeliveryModes(objHere, blnSkip)
    u30to31CheckForMultipleDeliveryAddresses(objHere)
    u30to31NewStructureForDeliveryDetails(objHere, blnSkip)
    u30to31NewPropertyForEmailAddress(objHere)
    print "All done"


def u31to32NewPropertyForMembers(objHere, blnSkip = False):
    if blnSkip:
        print "Skipping: NewPropertyForMembers"
        return

    print "NewPropertyForMembers"

    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not objMember.hasProperty('Tags'):
                objMember.manage_addProperty('Tags', [], 'lines')

def u31to32NewPropertyForMessages(objHere, blnSkip = False):
    if blnSkip:
        print "Skipping: NewPropertyForMessages"
        return

    print "New properties for messages"
    objMessages = GetDataFolder(objHere, 'E3Messages')
    for objYear in objMessages.objectValues('Folder'):
        print objYear.id
        for objMonth in objYear.objectValues('Folder'):
            print objMonth.id
            for objMessage in objMonth.objectValues('Folder'):
                if not objMessage.hasProperty('ThreadId'):
                    objMessage.manage_addProperty('ThreadId', '', 'string')

def u31to32AddForumFolders(objHere, blnSkip = False):
    if blnSkip:
        print "Skipping: AddForumFolders"
        return

    print "AddForumFolders"

    objECL = objHere.unrestrictedTraverse("/Websites/ECLv3")
    if not "Forum" in objECL.objectIds("Folder"):
        objECL.manage_addFolder('Forum')
        objForum = objECL.Forum
        objForum.manage_addFolder('ShowTopics')
        objForum.manage_addFolder('ShowThreads')

def u31to32AddMessageIndex(objHere, blnSkip = False):
    if blnSkip:
        print "Skipping: AddMessageIndex"
        return

    NewFieldIndex(GetDataFolder(objHere, 'E3Messages'), "ThreadId", "")

def AddProperties(objObject, lstNewProperties):
    for (strName, valDefault, strType) in lstNewProperties:
        if not objObject.hasProperty(strName):
            objObject.manage_addProperty(strName, valDefault, strType)

def u32to33AddProfileProperties(objHere, blnSkip = False):
    if blnSkip:
        print "Skipping: AddProfileProperties"
        return

    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            AddProperties(objMember,
                (('FullName', '', 'ustring'),
                ('TagLine', '', 'ustring'),
                ('Biography', '', 'utext'),
                ('Testimonials', '', 'utext'),
                ('Country', '', 'ustring'),
                ('Location', '', 'ustring'),
                ('Postcode', '', 'ustring'),
                ('CommercialComments', '', 'utext'),
                ('CommunityComments', '', 'utext'),
                ('ContactEmailAddress', '', 'ustring'),
                ('PhoneNumber', '', 'ustring'),
                ('Languages', '', 'utext'),
                ('WebsiteAddress', '', 'ustring'),
                ('HostOfChapter', '', 'ustring'),
                ('ShowFullName', 'Hide', 'string'),
                ('ShowCountry', 'Hide', 'string'),
                ('ShowLocation', 'Hide', 'string'),
                ('ShowPostcode', 'Hide', 'string'),
                ('ShowEmailAddress', 'Hide', 'string'),
                ('ShowPhoneNumber', 'Hide', 'string'),
                ('ShowBiography', 'Hide', 'string'),
                ('ShowCommunityComments', 'Hide', 'string')))



def uTo35AddOfferingsFolder(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not "Offerings" in objMember.objectIds():
                objMember.manage_addFolder('Offerings')

def u32to33AddVariousFolders(objHere, blnSkip = False):
    if blnSkip:
        print "Skipping: AddVariousFolders"
        return

    print "AddVariousFolders"

    objECL = objHere.unrestrictedTraverse("/Websites/ECLv3")
    if not "Offerings" in objECL.objectIds("Folder"):
        objECL.manage_addFolder('Offerings')
        objECL.Offerings.manage_addFolder('Edit')

    if not "Products" in objECL.objectIds("Folder"):
        objECL.manage_addFolder('Products')
        objECL.Products.manage_addFolder('Edit')

    if not "Services" in objECL.objectIds("Folder"):
        objECL.manage_addFolder('Services')
        objECL.Services.manage_addFolder('Edit')

    if not "Members" in objECL.objectIds("Folder"):
        objECL.manage_addFolder('Members')
        objECL.Members.manage_addFolder('ListProfiles')
        objECL.Members.manage_addFolder('ViewProfile')

def Upgrade3p1To3p2(objHere):
    blnSkip = False

    print "Upgrading from 3.1 to 3.2"
    u31to32AddForumFolders(objHere)
    u31to32AddMessageIndex(objHere)
    u31to32NewPropertyForMessages(objHere, blnSkip)
    DoOrSkip(objHere, AddThreadDefinitions, "Adding thread definitions", blnSkip)

def Upgrade3p2To3p3(objHere):
    blnSkip = True

    print "Upgrading from 3.2 to 3.3"
    u32to33AddProfileProperties(objHere)
    u32to33AddVariousFolders(objHere)
#    DoOrSkip(objHere, AddOfferingDefinitions, "Adding offering definition", False)
#    u32To33AddOfferingsFolder(objHere)

def UpgradeTo3p4(objHere):
    print "Upgrading to 3.4"
    print "Adding data object defs"
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    AddDataObjectDefinition(objDefs, 'E3SequenceInProgress', True, 100, 'E3SequenceInProgress', 'E3', {})
    AddDataObjectDefinition(objDefs, 'E3PlannedMessage', False, 0, '', 'E3', {})

def UpgradeTo3p5(objHere):
    print "Upgrading to 3.5"
    print "Adding Offerings folders for each member"
    uTo35AddOfferingsFolder(objHere)
    print "Adding data object definition for E3MultiOption"
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    AddDataObjectDefinition(objDefs, "E3MultiOption", True, 100, "E3MultiOption", "E3", {'FieldName': 'Field', 'id': 'Field'})
    print "Adding data object definition for E3Offering"
    AddDataObjectDefinition(objDefs, 'E3Offering', False, 0, 'E3Offering', 'E3',
    {'Type': 'Field',
    'Category': 'Field',
    'id': 'Field',
    'Relation': 'Text',
    'TargetAudienceCoaches': 'Text',
    'TargetAudienceGeneral': 'Text',
    'TopicsBusinessAndCareer': 'Text',
    'TopicsPersonalSuccess': 'Text',
    'DeliveryMechanismService': 'Text',
    'DeliveryMechanismProduct': 'Text',
    'GroupSize': 'Text'})
    AddDataObjectDefinition(objDefs, "E3OfferingCategory", False, 0, "E3OfferingCategory", "E3", {'id': 'Field'})
    AddDataObjectDefinition(objDefs, "E3SearchQuery", True, 100, "E3SearchQuery", "E3", {"id": "Field"})

    print "Reading initial multi options"
    ReadInitialMultiOptions(objHere)

    print "Creating initial categories"
    CreateInitialCategories(objHere)

    print "Importing MCI Books"
    ImportMCIBooks(objHere)

    print "Counting offerings against categories and multi options"
    UpdateCounts(objHere)

def FillVersion(lstVersion, intLength):
    lstResult = []
    for intI in range(0, intLength):
        if intI < len(lstVersion):
            lstResult.append(lstVersion[intI])
        else:
            lstResult.append(0)
    return lstResult

def VersionIsLater(strOldestVersion, strNewestVersion):
    lstOldestVersion = strOldestVersion.split(".")
    lstOldestVersion = FillVersion(lstOldestVersion, 4)
    lstNewestVersion = strNewestVersion.split(".")
    lstNewestVersion = FillVersion(lstNewestVersion, 4)

    print "Comparing %s to %s" % (lstOldestVersion, lstNewestVersion)
    for intI in range(0, 4):
        if int(lstOldestVersion[intI]) > int(lstNewestVersion[intI]):
            return False
        elif int(lstOldestVersion[intI]) < int(lstNewestVersion[intI]):
            return True
    return False

def UpgradeTo3p4p1(objHere):
    print "Upgrading to 3.4.1"
    print "Adding data object defs"
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    AddDataObjectDefinition(objDefs, 'E3Conf08Booking', False, 0, 'E3Conf08Booking', 'E3', {'id': 'Field'})

def CreateInitialFolders3p5p4(objHere):
    strInitialMessage = "Initial message goes here please"
    strInitialSubject = "Subject for initial message goes here please"

    objE3Data = objHere.unrestrictedTraverse("/Data/E3")
    if "EmailsToMembers" in objE3Data.objectIds():
        return "<p>Already created</p>"

    objE3Data.manage_addFolder("EmailsToMembers")
    objMainFolder = objE3Data.EmailsToMembers

    objMainFolder.manage_addFolder("Message1")
    objMessage1 = objMainFolder.Message1
    objMessage1.manage_addProperty("Message", strInitialMessage, "utext")
    objMessage1.manage_addProperty("Subject", strInitialSubject, "ustring")
    objMessage1.manage_addProperty("AlreadyDone", [], "ulines")

    return "<p>New folders and properties created</p>"

def AddNewProperties3p5p4(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            AddProperties(objMember,
                (
                    ('NoCommercialEmails', False, 'boolean'),
                    ('DuplicateMembership', False, 'boolean'),
                    ('DoLaterDone', [], 'lines')
                ))


def UpgradeTo3p5p4(objHere):
    print "Upgrading to 3.5.4"
    print "Creating initial folders"
    CreateInitialFolders3p5p4(objHere)

    print "Adding new properties"
    AddNewProperties3p5p4(objHere)
    return "<p>Done</p>"

def CreateChapters(objHere):
    # For each objMember who has .HostOfChapter:
        # Create a new organisation
        # Add a new role - host of chapter
    dodOrganisation = GetDOD(objHere, "E3Organisation")
    dodRole = GetDOD(objHere, "E3Role")
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.HostOfChapter:
                objOrganisation = dodOrganisation.NewObject()
                objOrganisation.CreatedBy = objMember.id
                objOrganisation.Name = objMember.HostOfChapter
                objOrganisation.title = 'Local coaches network: ' + objMember.HostOfChapter
                objOrganisation.OrganisationType = 'Local coaches network'
                Catalogue(objOrganisation)
                objRole = dodRole.NewObject()
                objRole.MemberId = objMember.id
                objRole.ItemId = objOrganisation.id
                objRole.RoleType = 'Host'
                Catalogue(objRole)

def ChangeEmailSettings(objHere):
    # Old setting:
    #   (member).ListMemberships.ECL.myDeliveryMode
    #   (member).ListMemberships.ECL.EmailAddress

    # New settings:
    #   (member).EmailDigestMode
    #   (member).EmailFrequency-ECL
    #   (member).EmailDeliveryAddress

    # Unchanged:
    #   (member).NoMail
    #   (member).ContactEmailAddress

    # Might happen later:
    #   (member).EmailFrequency-ECL-Adverts, etc

    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not objMember.hasProperty("EmailDigestMode"):
                strDeliveryMode = objMember.ListMemberships.ECL.GetDeliveryMode()
                strEmailAddress = objMember.ListMemberships.ECL.EmailAddress
                objMember.manage_addProperty("EmailDeliveryAddress", strEmailAddress, "ustring")
                if "Digest" in strDeliveryMode:
                    strFrequency = "Daily"
                    strDigestMode = strDeliveryMode
                else:
                    strFrequency = "Direct"
                    strDigestMode = "StructuredDigest"
                objMember.manage_addProperty("EmailDigestMode", strDigestMode, "string")
                objMember.manage_addProperty("EmailFrequency_ECL", strFrequency, "string")

def ChangeFromMembersOnly(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for strField in ('ShowCountry', 'ShowLocation', 'ShowPostcode', 'ShowEmailAddress', 'ShowPhoneNumber', 'ShowBiography', 'ShowFullName', 'ShowCommunityComments'):
                strValue = objMember.getProperty(strField)
                if strValue == "MembersOnly":
                    objMember.setProperty(strField, "Members")

def AddOneFolder(objHere, strPath, strFolder):
    objPath = objHere.unrestrictedTraverse(strPath)
    if not strFolder in objPath.objectIds():
        objPath.manage_addFolder(strFolder)

def Add3p6Folders(objHere):
    for (strPath, strFolder) in (("", "Organisations"), ("", "Networks"), ("Membership", "Welcome"), ("MyECL", "Events"), ("MyECL/Events", "Edit")):
        AddOneFolder(objHere, "/Websites/ECLv3/" + strPath, strFolder)
    AddOneFolder(objHere, "/Data/E3/", "SampleDigests")

def AddPhotoNameProperty(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not objMember.hasProperty("PhotoName"):
                objMember.manage_addProperty("PhotoName", "", "ustring")

def ConvertNameToUstring(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            strName = ToUnicode(objMember.Name)
            objMember.manage_delProperties(("Name", ))
            objMember.manage_addProperty("Name", strName, "ustring")

def AddEventSeriesIdIndex(objHere):
    NewFieldIndex(GetDataFolder(objHere, 'E3Offering'), "EventSeriesId", "")

def UpgradeTo3p6(objHere):
    print "Upgrading to 3.6"
    print "Adding data object defs"
    objDefs = objHere.unrestrictedTraverse('/Data/Meta/DataObjectDefinitions')
    AddDataObjectDefinition(objDefs, "E3Organisation", True, 100, "E3Organisation", "E3", {'id': 'Field', 'CreatedBy': 'Field', 'OrganisationType': 'Field'})
    AddDataObjectDefinition(objDefs, "E3Role", True, 100, "E3Role", "E3", {'MemberId': 'Field', 'ItemId': 'Field', 'RoleType': 'Field'})
    AddDataObjectDefinition(objDefs, "E3EventSeries", False, 0, "E3EventSeries", "E3", {'id': 'Field'})
    AddDataObjectDefinition(objDefs, "E3OrganisingBody", True, 100, "E3OrganisingBody", "E3", {'id': 'Field', 'CreatedBy': 'Field', 'OrganisationId': 'Field'})

    print "Converting clsE3Member.Name to ustring"
    ConvertNameToUstring(objHere)

    print "Creating organisations for chapters"
    CreateChapters(objHere)

    print "Changing structure of list email settings"
    ChangeEmailSettings(objHere)

    print "Changing 'MembersOnly' to 'Members'"
    ChangeFromMembersOnly(objHere)

    print "Adding new folders"
    Add3p6Folders(objHere)

    print "Adding PhotoName property to members"
    AddPhotoNameProperty(objHere)

def UpgradeTo3p6p4(objHere):
    print "Upgrading to 3.6.4"
    print "Adding EventSeriesId index on E3Offering"
    AddEventSeriesIdIndex(objHere)

def HasDuplicateBookings(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if len(objMember.Events.objectValues("E3Conf08Booking")) > 1:
                print "Duplicates for: ", objMember.id
                return True
    return False

def WriteBookingHistory(objBooking):
    lstResult = []
    strBookingDate = objBooking.GetDateCreated().strftime(cnShortDateFormat)

    strBooking = "%s: Core Conference booked" % strBookingDate
    lstResult.append(strBooking)

    if objBooking.PayLaterAmount:
        strPayment = "%s: %s, GBP%s deposit, GBP%s later, GBP%s total" % (strBookingDate, objBooking.RegistrationType, objBooking.PayNowAmount, objBooking.PayLaterAmount, objBooking.PayNowAmount + objBooking.PayLaterAmount)
    else:
        strPayment = "%s: %s, GBP%s" % (strBookingDate, objBooking.RegistrationType, objBooking.PayNowAmount)
    lstResult.append(strPayment)

    if objBooking.PaymentMethod == "Online":
        strPayment = "%s: GBP%s paid online" % (strBookingDate, objBooking.PayNowAmount)
        lstResult.append(strPayment)
    elif objBooking.HasDepositPaid():
        if objBooking.HasRemainderPaid():
            strPayment = "%s: full amount of GBP%s paid, %s" % (objBooking.GetDepositPaid().strftime(cnShortDateFormat), objBooking.PayNowAmount + objBooking.PayLaterAmount, objBooking.PaymentMethod)
            lstResult.append(strPayment)
        else:
            strPayment = "%s: deposit of GBP%s paid, %s" % (objBooking.GetDepositPaid().strftime(cnShortDateFormat), objBooking.PayNowAmount, objBooking.PaymentMethod)
            lstResult.append(strPayment)

    return lstResult

def UpgradeBooking(objBooking):
    if not objBooking.hasProperty("BookedForCC"):
        objBooking.manage_addProperty("BookedForCC", True, "boolean")
        objBooking.manage_addProperty("BookedForSatEve", False, "boolean")
        objBooking.manage_addProperty("BookedForSunAm", False, "boolean")
        lstHistory = WriteBookingHistory(objBooking)
        objBooking.manage_addProperty("History", lstHistory, "lines")
        objBooking.manage_addProperty("RemainingAmount", objBooking.PayLaterAmount, "int")
        intPaidAmount = 0
        if objBooking.HasDepositPaid():
            intPaidAmount += objBooking.PayNowAmount
        if objBooking.HasRemainderPaid():
            intPaidAmount += objBooking.PayLaterAmount
        objBooking.manage_addProperty("PaidAmount", intPaidAmount, "int")
        objBooking.manage_addProperty("InProgressForCC", False, "boolean")
        objBooking.manage_addProperty("InProgressForSatEve", False, "boolean")
        objBooking.manage_addProperty("InProgressForSunAm", False, "boolean")

def UpgradeTo3p6p5(objHere):
    print "Upgrading to 3.6.5"
    print "New structure for conference bookings"
    if HasDuplicateBookings(objHere):
        print "WARNING: Duplicate bookings found. Could not continue"
        return

    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objBooking in objMember.Events.objectValues("E3Conf08Booking"):
                UpgradeBooking(objBooking)

    for objBooking in objHere.unrestrictedTraverse("/Data/E3/E3Conf08Booking").objectValues("E3Conf08Booking"):
        UpgradeBooking(objBooking)
    print "Done"

def UpgradeTo3p6p8(objHere):
    print "Upgrading to 3.6.8"
    print "New properties"
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.ListConfirmedEmailAddresses():
                blnConfirmed = True
            else:
                blnConfirmed = False
            AddProperties(objMember, \
                (("myLastVisit", cnEmptyZopeDate, 'date'), \
                 ("VisitCount", 0, "int"),
                ("HasConfirmedEmailAddress", blnConfirmed, "boolean")))

def UpgradeTo3p8p1(objHere):
    print "Upgrading to 3.8.1"
    print "New ThreadId property for messages"
    objArchive = GetDataFolder(objHere, 'E3Messages')
    for objYear in objArchive.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            print objMonth.id
            for objMessage in objMonth.objectValues('Folder'):
                if not 'ThreadId' in objMessage.propertyIds():
                    objMessage.manage_addProperty('ThreadId', '', 'string')
    print "Adding ToMove property"
    objData = objHere.unrestrictedTraverse('/Data/E3')
    if not "ToMove" in objData.propertyIds():
        objData.manage_addProperty("ToMove", [], "lines")

def CreateNewListMembers(objHere):
    objListMembers = objHere.unrestrictedTraverse("/Data/E3/E3Lists")
    if not "ECL_Adv" in objListMembers.objectIds():
        print "Creating new list members"
        dodList = GetDOD(objHere, "E3List")
        objAdvFolder = dodList.NewObject(objListMembers, "ECL_Adv")
#        objListMembers.manage_addFolder("ECL_Adv")
#        objAdvFolder = objListMembers.ECL_Adv
        dodMailBoxerMembers = GetDOD(objHere, "E3MailBoxerMembers")
        for strDeliveryMode in ("Direct", "TextDigest", "MIMEDigest", "NoMail", "StructuredDigest", "TopicsList"):
            objMailBoxerMembers = dodMailBoxerMembers.NewObject(objAdvFolder)
            objMailBoxerMembers.DeliveryMode = strDeliveryMode
            print strDeliveryMode

def UpgradeTo3p8p4(objHere):
    print "Upgrading to 3.8.4"
    print "New EmailFrequency_ECL_Advert property"
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not "EmailFrequency_ECL_Advert" in objMember.propertyIds():
                objMember.manage_addProperty("EmailFrequency_ECL_Advert", "SameAsMain", "string")
    CreateNewListMembers(objHere)

def AddPropertyToMembers(objHere, strPropertyName, varDefault, strType):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if not strPropertyName in objMember.propertyIds():
                objMember.manage_addProperty(strPropertyName, varDefault, strType)

def AddPropertyToOfferings(objHere, strPropertyName, varDefault, strType):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objOffering in objMember.Offerings.objectValues("E3Offering"):
                if not strPropertyName in objOffering.propertyIds():
                    objOffering.manage_addProperty(strPropertyName, varDefault, strType)

def RemoveProfessionalName(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if "FullName" in objMember.objectIds():
                if not objMember.Name:
                    objMember.Name = objMember.FullName

def UpgradeTo3p8p7(objHere):
    print "Upgrading to 3.8.7"

    print "New featured digest list properties"
    objData = objHere.unrestrictedTraverse("/Data/E3")
    for strProperty in ("RecentFeaturedMembers", "RecentFeaturedOfferings"):
        if not strProperty in objData.propertyIds():
            objData.manage_addProperty(strProperty, [], "lines")

    print "New member property: myLastFeatured"
    AddPropertyToMembers(objHere, "myLastFeatured", cnEmptyZopeDate, 'date')

    print "New offering property: myLastFeatured"
    AddPropertyToOfferings(objHere, "myLastFeatured", cnEmptyZopeDate, 'date')

    print "Removing professional name from profile"
    RemoveProfessionalName(objHere)

    print "New member property: TwitterUsername"
    AddPropertyToMembers(objHere, "TwitterUsername", "", "ustring")

def SimplifyEventLocations(objHere):
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            for objOffering in objMember.Offerings.objectValues("E3Offering"):
                lstOffering = []
                print "From ", objOffering.InternetBased, objOffering.TelephoneBased, objOffering.FaceToFace, objOffering.Country, objOffering.Location, " to ",
                if objOffering.InternetBased:
                    lstOffering.append("Internet")
                if objOffering.TelephoneBased:
                    lstOffering.append("telephone")
                if objOffering.Country and objOffering.Country[:5] <> "Enter":
                    lstOffering.append(objOffering.Country)
                if objOffering.Location:
                    lstOffering.append(objOffering.Location)
                objOffering.Location = ", ".join(lstOffering)
                print objOffering.Location

def UpgradeTo3p8p7p1(objHere):
    print "Upgrading to 3.8.7.1"

    print "New indexes for E3EventSeries"
    objEventSeries = GetDataFolder(objHere, 'E3EventSeries')
    NewFieldIndex(objEventSeries, "CreatedBy", "")
    NewFieldIndex(objEventSeries, "OrganisationId", "")

    print "Simplifying event locations"
    SimplifyEventLocations(objHere)

    print "Adding folders"
    AddOneFolder(objHere, "/Websites/ECLv3", "BooksByMembers")
    AddOneFolder(objHere, "/Websites/ECLv3/images", "RTE")
    AddOneFolder(objHere, "/Websites/ECLv3/Members", "ViewTwitters")

def UpgradeToTheLatestVersion(objHere):
    objData = objHere.unrestrictedTraverse('/Data/E3')
    try:
        strCurrentVersion = objData.CurrentVersion
    except:
        strCurrentVersion = "3.3.1"
        objData.manage_addProperty('CurrentVersion', strCurrentVersion, 'string')

    strLatestVersion = strCurrentVersion

    for strVersion in ("3.4", "3.4.1", "3.5", "3.5.4", "3.6", "3.6.4", "3.6.5", "3.6.8", "3.8.1",
                       "3.8.4", "3.8.7", "3.8.7.1"):
        if VersionIsLater(strCurrentVersion, strVersion):
            eval("UpgradeTo%s(objHere)" % (strVersion.replace(".", "p")))
            strLatestVersion = strVersion
    objData.CurrentVersion = strLatestVersion

