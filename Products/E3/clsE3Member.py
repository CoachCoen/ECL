import LocalPaths

import OFS.Folder
import Globals
from Functions import *
import datetime
import DateTime

from libConstants import cnEmptyZopeDate
from libConstants import cnEmptyDate
from libConstants import cnFirstDate
from libConstants import cnLastDate
from libDatabase import GetDOD
from libDatabase import GetDataFolder
from libDatabase import Catalogue
from libConstants import cnShortDateFormat
from libConstants import cnFullDateFormat
from libConstants import cnTrialPeriodExpired
from libConstants import cnPaidPeriodExpired
from libConstants import cnTrialPeriodDue
from libConstants import cnPaidPeriodDue
from libConstants import cnBonus
from libConstants import cnHowToPay
from libConstants import cnSignature
from libEmail import SendEmail
from libEmail import SendAnyEmail
from libDatabase import SearchOne
from libDatabase import SearchMany
from E3TempData import SetMessage
from StringValidator import StringValidator
from E3Payments import NextInvoiceNumber
from libBuildHTML import InsertBrs
from libBuildHTML import PutInFieldset
from libString import TrimBlank
from libString import GetMessage

class E3Member(OFS.Folder.Folder):
    "E3Member class"
    meta_type = 'E3Member'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Username', '', 'ustring')
        self.manage_addProperty('Name', '', 'ustring')
        self.manage_addProperty('Password', '', 'ustring')
        self.manage_addProperty('myNextExpiryDate', cnEmptyZopeDate, 'date')
        self.manage_addProperty('MembershipType', 'None', 'string')
        self.manage_addProperty('LifetimeMember', False, 'boolean')
        self.manage_addProperty('HasPayments', False, 'boolean')
        self.manage_addProperty('Manager', False, 'boolean')
        self.manage_addProperty('OnHold', False, 'boolean')
        self.manage_addProperty('NoMail', False, 'boolean')
        self.manage_addProperty('Tags', [], 'lines')
        self.manage_addProperty('myCreatedDate', DateTime.DateTime(), 'date')
        self.manage_addProperty('ImportedFromMailman', False, 'boolean')
        self.manage_addProperty('myNextExpiryFromMailman', cnEmptyZopeDate, 'date')
        self.manage_addFolder('Historic')
        self.manage_addFolder('Events')
        self.manage_addFolder('Deleted')
        self.manage_addFolder('Offerings')
#        self.manage_addProperty('FullName', '', 'ustring')
        self.manage_addProperty('TagLine', '', 'ustring')
        self.manage_addProperty('Biography', '', 'utext')
        self.manage_addProperty('Testimonials', '', 'utext')
        self.manage_addProperty('Country', '', 'ustring')
        self.manage_addProperty('Location', '', 'ustring')
        self.manage_addProperty('Postcode', '', 'ustring')
        self.manage_addProperty('CommercialComments', '', 'utext')
        self.manage_addProperty('CommunityComments', '', 'utext')
        self.manage_addProperty('ContactEmailAddress', '', 'ustring')
        self.manage_addProperty('PhoneNumber', '', 'ustring')
        self.manage_addProperty('Languages', '', 'utext')
        self.manage_addProperty('WebsiteAddress', '', 'ustring')
        self.manage_addProperty('HostOfChapter', '', 'ustring')
        self.manage_addProperty('ShowCountry', 'Hide', 'string')
        self.manage_addProperty('ShowLocation', 'Hide', 'string')
        self.manage_addProperty('ShowPostcode', 'Hide', 'string')
        self.manage_addProperty('ShowEmailAddress', 'Hide', 'string')
        self.manage_addProperty('ShowPhoneNumber', 'Hide', 'string')
        self.manage_addProperty('ShowFullName', 'Hide', 'string')
        self.manage_addProperty('ShowCommunityComments', 'Hide', 'string')
        self.manage_addProperty('NoCommercialEmails', False, 'boolean')
        self.manage_addProperty('DuplicateMembership', False, 'boolean')
        self.manage_addProperty('DoLaterDone', [], 'lines')
        self.manage_addProperty("EmailDigestMode", "StructuredDigest", "string")
        self.manage_addProperty("EmailFrequency_ECL", "Direct", "string")
        self.manage_addProperty("EmailDeliveryAddress", "", "ustring")
        self.manage_addProperty("EmailFrequency_ECL_Advert", "Daily", "string")
        self.manage_addProperty("PhotoName", "", "ustring")
        self.manage_addProperty("myLastVisit", cnEmptyZopeDate, 'date')
        self.manage_addProperty("VisitCount", 0, "int")
        self.manage_addProperty("HasConfirmedEmailAddress", False, "boolean")
        self.manage_addProperty("myLastFeatured", cnEmptyZopeDate, 'date')
        self.manage_addProperty("TwitterUsername", "", "ustring")

    def GetEmailFrequency(self, strList, blnAdvert = False):
        if strList == "ECL":
            if blnAdvert:
                if self.EmailFrequency_ECL_Advert == "SameAsMain":
                    return self.EmailFrequency_ECL
                else:
                    return self.EmailFrequency_ECL_Advert
            else:
                return self.EmailFrequency_ECL
        return ""

    def CancelMembership(self):
        if not self.hasProperty('myCancellationDate'):
            self.manage_addProperty('myCancellationDate', DateTime.DateTime(), 'date')
        else:
            self.myCancellationDate = DateTime.DateTime()
        self.MembershipType = 'Cancelled'

    def UncancelMembership(self):
        self.myCancellationDate = cnEmptyZopeDate
        self.MembershipType = 'Full'

    def IsCancelled(self):
        return (self.MembershipType == 'Cancelled')

    def GetCancellationDate(self):
        return FromZopeDateTime(self.myCancellationDate)

    def SetLastFeatured(self, dtmDate):
        self.myLastFeatured = ToZopeDateTime(self, dtmDate)

    def GetLastFeatured(self):
        return FromZopeDateTime(self.myLastFeatured)

    def CanFeature(self):
        return (self.ShowFullName == 'Showtoall' and self.Name and self.TagLine and self.CommercialComments and self.MembershipType == 'Full')

    def SetCreatedDate(self, dtmDate):
        self.myCreatedDate = ToZopeDateTime(self, dtmDate)

    def GetCreatedDate(self):
        return FromZopeDateTime(self.myCreatedDate)

    def GetNextExpiryFromMailman(self):
        return FromZopeDateTime(self.myNextExpiryFromMailman)

    def SetNextExpiryFromMailman(self, dtmDate):
        self.myNextExpiryFromMailman = ToZopeDateTime(self, dtmDate)

    def GetNextExpiryDate(self):
        return FromZopeDateTime(self.myNextExpiryDate)

    def SetNextExpiryDate(self, dtmDate):
        self.myNextExpiryDate = ToZopeDateTime(self, dtmDate)

    def GetLatestPaymentDate(self):
        dtmResult = cnEmptyDate
        for objPayment in self.Historic.objectValues('E3Payment'):
            if objPayment.GetDate() > dtmResult:
                dtmResult = objPayment.GetDate()
        return dtmResult

    def GetLatestEvent(self, strEventType):
        dtmResult = cnEmptyDate
        strEventType = strEventType.lower()
        for objEvent in self.Historic.objectValues('E3Event'):
            if strEventType in objEvent.EventType.lower() and objEvent.GetDate() > dtmResult:
                dtmResult = objEvent.GetDate()
        return dtmResult

    def RecordVisit(self):
        dtmNow = datetime.datetime.today()
        deltaSince = dtmNow - self.GetLastVisit()
        if deltaSince.days > 0 or deltaSince.seconds > 3600:
            self.VisitCount += 1
        self.myLastVisit = DateTime.DateTime()

    def GetLastVisit(self):
        return FromZopeDatePlusTime(self.myLastVisit)

    def SendPasswordReminder(self, strReason = ""):
        if strReason:
            strReason = "You have been sent this reminder because %s\n\n" % strReason
        strMessage = strReason + """Your log in details for the Euro Coach List are as follows:
Username: %s
Password: %s

Note: this message was sent out to all your registered email addresses, to make sure you receive at least one copy

""" % (self.Username, self.Password)
        strSubject = "Euro Coach List password reminder"
        strMessage += cnSignature

        strEmailAddress = ""
        blnSent = False

        for objEmailAddress in self.objectValues('E3EmailAddress'):
            if objEmailAddress.Confirmed:
                SendEmail(self, strMessage, strSubject, objEmailAddress.EmailAddress)
                blnSent = True
            else:
                strEmailAddress = objEmailAddress.EmailAddress
        if not blnSent:
            SendEmail(self, strMessage, strSubject, strEmailAddress)


    def SetNoMail(self, blnOn):
        if self.NoMail == blnOn:
            return
        self.NoMail = blnOn

    def SetMembershipType(self, strType):
        if self.MembershipType <> strType:
            self.MembershipType = strType

    def Confirm(self):
        if self.HasConfirmedEmailAddress:
            return
        self.HasConfirmedEmailAddress = True
        strWelcomeMessage = GetMessage(self, "WelcomeMessage")
        strSubject = "Welcome to the Euro Coach List"
        SendAnyEmail(self, strWelcomeMessage, strSubject, self.EmailDeliveryAddress)

    def RemindToConfirm(self):
        if self.HasConfirmedEmailAddress:
            return
        for objEmailAddress in self.objectValues("E3EmailAddress"):
            if objEmailAddress.TimeToRemind():
                objEmailAddress.SendConfirmationReminder()

    def ShowProfileData(self, strFieldName, blnFullMember, strLabel = "", strShowData = ""):
        if not strLabel:
            strLabel = strFieldName
        if strFieldName == "ContactEmailAddress":
            strShowFieldName = "ShowEmailAddress"
        else:
            strShowFieldName = "Show" + strFieldName
        if not strShowData:
            strShowData = self.getProperty(strShowFieldName)
        if (strShowData == 'Showtoall' or (strShowData == 'Members' and blnFullMember)):
            varData = self.getProperty(strFieldName)
            if varData:
                strData = TrimBlank(varData)
                if "email" in strFieldName.lower():
                    strData = """<a href="mailto:%s">%s</a>""" % (strData, strData)
                elif "website" in strFieldName.lower():
                    if not '//' in strData:
                        strData = """<a href="http://%s" target="_blank">%s</a>""" % (strData, strData)
                    else:
                        strData = """<a href="%s" target="_blank">%s</a>""" % (strData, strData)

                return """<p><label>%s</label><div class="ProfileData">%s</div></p>\n""" % (strLabel, InsertBrs(strData))
        return ""

    def CanShowName(self, blnFullMember):
        strShowFullName = "%s" % self.ShowFullName
        strShowFullName = strShowFullName.upper()
        if "ALL" in strShowFullName:
            return True

        if "MEMBER" in strShowFullName and blnFullMember:
            return True

        return False

    def VisibleName(self, blnFullMember):
        if self.CanShowName(blnFullMember):
#            if self.FullName:
#                return self.FullName
            if self.Name <> "Name unknown" and self.Name:
                return self.Name
        return "Anonymous"

    def ProfilePersonalDetails(self, blnFullMember, strTitle = None, blnIncludeLinkToProfile = False, blnSmall = False):

        strName = ""
        if self.CanShowName(blnFullMember):
#            if self.FullName:
#                strName = self.FullName
            if self.Name and not 'unknown' in self.Name.lower():
                strName = self.Name

        if strName:
            strPhotoAlt = "Photo of %s" % strName
        else:
            strPhotoAlt = ""

        if blnSmall:
            intPhotoWidth = 100
        else:
            intPhotoWidth = 200

        if self.PhotoName:
            strPhoto = """<img src="/images/Members/%s" align="right" border="0" width="%s" alt="%s">""" % (self.PhotoName, intPhotoWidth, strPhotoAlt)
        else:
            strPhoto = ""

        if strName and blnIncludeLinkToProfile:
            strName = """<a href="/Members/ViewProfile?MemberId=%s">%s</a>""" % (self.id, strName)

        strResult = strPhoto + \
                    strName + \
                    self.ShowProfileData("Country", blnFullMember) + \
                    self.ShowProfileData("Location", blnFullMember) + \
                    self.ShowProfileData("Postcode", blnFullMember) + \
                    self.ShowProfileData("Languages", blnFullMember, None, "Showtoall")

        if not strTitle:
            strTitle = "Personal Details"
        return PutInFieldset(strTitle, strResult)

    def ProfileContactDetails(self, blnFullMember):
        strResult = self.ShowProfileData("ContactEmailAddress", blnFullMember, "Email address") + \
                    self.ShowProfileData("WebsiteAddress", blnFullMember, "Website", "Showtoall") + \
                    self.ShowProfileData("PhoneNumber", blnFullMember, "Telephone")
        return PutInFieldset("Contact Details", strResult)

    def ProfileCommunityDetails(self, blnFullMember):
        strResult = self.ShowProfileData("HostOfChapter", blnFullMember, "Host of")
        return PutInFieldset("Coaching Communities", strResult)

    def ProfilePersonalComments(self, blnFullMember):
        strResult = self.ShowProfileData("CommunityComments", blnFullMember, "Comments")
        return PutInFieldset("Personal Comments", strResult)

    def ProfileProfessionalDetails(self, blnFullMember):
        strResult = self.ShowProfileData("TagLine", blnFullMember, "Tagline or title", "Showtoall") + \
                    self.ShowProfileData("Biography", blnFullMember, None, "Showtoall") + \
                    self.ShowProfileData("Testimonials", blnFullMember, None, "Showtoall") + \
                    self.ShowProfileData("CommercialComments", blnFullMember, "Comments", "Showtoall")
        return PutInFieldset("Business or Professional Profile", strResult)

    def ProfileTwitterWidget(self):
        if not self.TwitterUsername:
            return ""

        strResult = \
            PutInFieldset("Twitter Updates", """<ul id="twitter_update_list"></ul>
                    <a href="http://twitter.com/%(Username)s" id="twitter-link" style="display:block;text-align:right;" target="_blank">follow me on Twitter</a>
                """) + """
                <script type="text/javascript" src="http://twitter.com/javascripts/blogger.js"></script>
            <script type="text/javascript" src="http://twitter.com/statuses/user_timeline/%(Username)s.json?callback=twitterCallback2&amp;count=8"></script>
            """
        strResult = strResult % {"Username": self.TwitterUsername}
        return strResult

    def BasicDetails(self):
    # username, name, membershiptype, email addresses
        strEmailAddresses = self.ListEmailAddresses()
        strResult = """<p>%s, %s, %s<br>%s</p>""" % (self.Username, self.Name, self.MembershipType, strEmailAddresses)
        return strResult

    def CalculateNextExpiryDate(self, objPayment):
        # if currently expired, start from today
        # if nextexpirydate in the past (even if not yet expired), start from today
        # if next expirydate in future, start from nextexpirydate
        dtmToday = datetime.date.today()
        if self.GetNextExpiryDate() < dtmToday:
            dtmStartDate = dtmToday
        else:
            dtmStartDate = self.GetNextExpiryDate()
        dtmExpiryDate = AddMonths(dtmStartDate, objPayment.Months)
        dtmExpiryDate = AddDays(dtmExpiryDate, objPayment.BonusDays)
        return dtmExpiryDate

    def NewPayment(self, dtmPaymentDate, intDuration, strMethod, strCurrency, fltAmount, strIdentifier, blnSendReceipt, strEmailAddress):
        dodPayment = GetDOD(self, 'E3Payment')
        objPayment = dodPayment.NewObject(self.Historic)
        objPayment.SetDate(dtmPaymentDate)
        objPayment.Months = intDuration
        objPayment.PaymentType = strMethod
        objPayment.Currency = strCurrency
        objPayment.Amount = fltAmount
        objPayment.Comments = strIdentifier
        if self.HasPayments:
            intBonusDays = CalculateBonusPeriod(objPayment.GetDate(), self.GetNextExpiryDate())
        else:
            intBonusDays = 0
        objPayment.BonusDays = intBonusDays
        self.SetNextExpiryDate(self.CalculateNextExpiryDate(objPayment))
        objPayment.InvoiceNumber = NextInvoiceNumber(self)
        objPayment.EmailAddress = strEmailAddress
        self.SetMembershipType('Full')
        self.HasPayments = True
        if blnSendReceipt:
            objPayment.SendReceipt()

    def DeletePayment(self, strPaymentId):
        if strPaymentId in self.Historic.objectIds():
            self.Historic.manage_delObjects(strPaymentId)
            self.UpdateMembershipStatus()

    def ResendInvoice(self, strPaymentId):
        if strPaymentId in self.Historic.objectIds():
            self.Historic.unrestrictedTraverse(strPaymentId).SendReceipt()

    def SendClaimedMessage(self, strEmailAddress):
        strMessage = """Important - Please read carefully. Thanks

In the past you have sent message(s) to the Euro Coach List using your email address %s

Someone has just claimed this address as their own, by adding it as an email address to their Euro Coach List account, on the My Euro Coach List (MyECL) screen. If you have not just changed your email details on the MyECL screen then please contact me immediately. Thanks

""" % strEmailAddress
        strMessage = strMessage + cnSignature
        strSubject = "Important: Euro Coach List and this email address"
        SendEmail(self, strMessage, strSubject, strEmailAddress)

    def ClaimEmailAddress(self, objExistingAddress, objExistingMember):
        # Remember the details of the old address
        strOldId = objExistingAddress.id
        strEmailAddress = objExistingAddress.EmailAddress

        # Remove the old address from the catalogue
        objCatalogue = GetDataFolder(self, 'E3EmailAddress').Catalogue
        strUID = objExistingAddress.absolute_url()
        strUID = strUID[strUID.find('/') + 2:]
        strUID = strUID[strUID.find('/'):]
        objCatalogue.uncatalog_object(strUID)

        # Remove the old address
        objExistingMember.manage_delObjects(strOldId)

        # Remove the old member from the catalogue
        objCatalogue = GetDataFolder(self, 'E3Member').Catalogue
        strUID = objExistingMember.absolute_url()
        strUID = strUID[strUID.find('/') + 2:]
        strUID = strUID[strUID.find('/'):]
        objCatalogue.uncatalog_object(strUID)

        # Remove the old member
        objBatch = objExistingMember.unrestrictedTraverse('..')
        objBatch.manage_delObjects(objExistingMember.id)

        # Create a new address
        dodEmailAddress = GetDOD(self, 'E3EmailAddress')
        objNewAddress = dodEmailAddress.NewObject(self)
        objNewAddress.EmailAddress = strEmailAddress
        objNewAddress.Confirmed = True
        Catalogue(objNewAddress)

        # Find all list messages which pointed to the old id
               # Replace the id with the new id
               # Update the catalogue
        objCatalogue = GetDataFolder(self, 'E3Messages').Catalogue
        for objListMessage in SearchMany(self, 'E3Messages', 'UserId', strOldId):
            objListMessage.UserId = self.id
            objCatalogue.Catalog(objListMessage)

        # Send an email to the email address, to let them know that it has been added, and to contact me if that isn't right
        self.SendClaimedMessage(strEmailAddress)
        return objNewAddress

    def AddEmailAddress(self, strEmailAddress):
        if not strEmailAddress:
            return (None, "No email address entered")
        strEmailAddress = strEmailAddress.strip().replace(" ", "").lower()
        objValidator = StringValidator(strEmailAddress)
        if not objValidator.isEmail():
            return (None, """'%s' is not a valid email address. Please try again or <a href="/ContactDetails">contact the list owner</a>""" % strEmailAddress)

        objOldEmailAddress = SearchOne(self, "E3EmailAddress", "EmailAddress", strEmailAddress)
        if objOldEmailAddress:
            if objOldEmailAddress in self.objectValues():
                return (None, "You have already registered this address (%s)" % strEmailAddress)
            else:
                objOldMember = objOldEmailAddress.unrestrictedTraverse('..')
                if objOldMember.ParkingMember():
                    self.ClaimEmailAddress(objOldEmailAddress, objOldMember)
                    return (objOldEmailAddress, "New email address registered")
                else:
                    return(None, """This email address belongs to someone else. Please <a href="/ContactDetails">contact the list owner</a>""")
        else:
            dodEmailAddress = GetDOD(self, "E3EmailAddress")
            objNewEmailAddress = dodEmailAddress.NewObject(self)
            objNewEmailAddress.EmailAddress = strEmailAddress
            objNewEmailAddress.Confirmed = False
            objNewEmailAddress.RequestConfirmation()
            objCatalogue = GetDataFolder(self, 'E3EmailAddress').Catalogue
            Catalogue(objNewEmailAddress)
            return (objNewEmailAddress, """New email address registered<br>
A confirmation request has been sent to you. Please confirm your email address by following the instructions in the email""")

    def ParkingMember(self):
        if self.Name == 'Unknown' and self.GetNextExpiryFromMailman() < cnFirstDate:
            return True
        return False

    def EnsureAddressIsMine(self, strEmailAddress):
        objExistingEmailAddress = SearchOne(self, 'E3EmailAddress', 'EmailAddress', strEmailAddress)
        if objExistingEmailAddress:
            objExistingMember = objExistingEmailAddress.unrestrictedTraverse('..')
            if objExistingMember.ParkingMember():
                objEmailAddress = self.ClaimEmailAddress(objExistingEmailAddress, objExistingMember)
                return (True, False, objEmailAddress)
            elif objExistingMember == self:
                return (True, False, objExistingEmailAddress)
            else:
                SetMessage(self, """%s is already in use by someone else. Please <a href="/ContactDetails">contact the list owner</a>""" % strEmailAddress, "")
                return (False, False, None)
        else:
            dodEmailAddress = GetDOD(self, 'E3EmailAddress')
            objEmailAddress = dodEmailAddress.NewObject(self)
            objEmailAddress.EmailAddress = strEmailAddress
            Catalogue(objEmailAddress)

            return (True, True, objEmailAddress)

    def ContainsString(self, strSearchFor):
        if strSearchFor in self.Name.lower():
            return True
        if strSearchFor in self.Username.lower():
            return True
        for objEmailAddress in self.objectValues('E3EmailAddress'):
            if strSearchFor in objEmailAddress.EmailAddress:
                return True
        return False

    def ListEmailAddresses(self):
        lstResult = []
        for objEmailAddress in self.objectValues('E3EmailAddress'):
            lstResult.append(objEmailAddress.EmailAddress)
        return ", ".join(lstResult)

    def ListEmailAddresses2(self):
        lstResult = []
        for objEmailAddress in self.objectValues('E3EmailAddress'):
            lstResult.append(objEmailAddress.EmailAddress)
        return lstResult

    def ListConfirmedEmailAddresses(self):
        lstResult = []
        for objEmailAddress in self.objectValues('E3EmailAddress'):
            if objEmailAddress.Confirmed:
                lstResult.append(objEmailAddress.EmailAddress)
        return lstResult

    def CreateTrialPeriod(self):
        self.RecordEvent("Trial", intDays = 92)
        self.MembershipType = "Full"
        self.UpdateMembershipStatus()

    def CreateAdditionalTrialPeriod(self, intDays):
        self.RecordEvent("Trial", intDays = intDays)
        self.UpdateMembershipStatus()
        self.MembershipType = "Full"

    def RecordPaymentStart(self, intCartId):
        dodWorldPayCall = GetDOD(self, 'E3WorldPayCall')
        objWorldPayCall = dodWorldPayCall.NewObject(self.Historic)
        objWorldPayCall.SetDateCalled(datetime.date.today())
        objWorldPayCall.CartId = intCartId
        objWorldPayCall.Status = 'Called'
        objWorldPayCall.PaymentType = "ECL"
        Catalogue(objWorldPayCall)

    def GiveLifetimeMembership(self, dtmEventDate):
        self.LifetimeMember = True
        self.RecordEvent('LifetimeMember', dtmEventDate = dtmEventDate)
        self.SetMembershipType('Full')

    def GiveFreeMembershipPeriod(self, dtmStartDate, intDays, blnRecalculate = True):
        self.SetMembershipType('Full')
        self.RecordEvent("FreePeriod", dtmEventDate = dtmStartDate, intDays = intDays)
        if blnRecalculate:
            self.UpdateMembershipStatus()

    def CheckExcessiveBouncing(self):
        for objEmailAddress in self.objectValues('E3EmailAddress'):
            objEmailAddress.CheckExcessiveBouncing()

    def PreferredEmailAddress(self):
        if self.EmailDeliveryAddress:
            return self.EmailDeliveryAddress
        elif self.ContactEmailAddress:
            return self.ContactEmailAddress

        strResult = ""

        for objEmailAddress in self.objectValues('E3EmailAddress'):
            if objEmailAddress.Confirmed:
                return objEmailAddress.EmailAddress
            else:
                strResult = objEmailAddress.EmailAddress
        return strResult

    def GetEmailAddress(self, strEmailAddress):
        for objEmailAddress in self.objectValues('E3EmailAddress'):
            if objEmailAddress.EmailAddress == strEmailAddress:
                return objEmailAddress
        return None

    def Unbounce(self, strEmailAddress):
        for objEmailAddress in self.objectValues('E3EmailAddress'):
            if objEmailAddress.EmailAddress == strEmailAddress:
                objEmailAddress.SetBouncing(False)

    def AddEventDate(self, dictEvents, dtmDate, intMonths, intDays, strType):
        if not dictEvents.has_key(dtmDate):
            dictEvents[dtmDate] = []
        dictEvents[dtmDate].append((intMonths, intDays, strType))
        return dictEvents

    def UpdateMembershipStatus(self, blnCheckOnly = False):
#        print "Update membership status"
        # We need: NextExpiryDate, MembershipStatus
        if self.LifetimeMember:
#            print "Lifetime member"
            self.SetMembershipType("Full")
            return

        if self.ParkingMember():
#            print "Parking member"
            self.SetMembershipType("None")
            return

        if self.MembershipType == "None":
            return

#        if self.NoMail:
#            return

        if self.ImportedFromMailman:
            dtmNextExpiry = self.GetNextExpiryFromMailman()
        else:
            dtmNextExpiry = self.GetCreatedDate()

#        print "Starting from ", dtmNextExpiry
#        print datetime.date(year=2006, month=9, day=22)

        # Events that effect the expiry date:
        # Payment
        #   Whilst still a member
        #   After membership expired
        # Free period
        #   Whilst still a member
        #   After membership expired
        # Build up the following dictionary:
        #   {Date: [list of (months, days)]}

        dictEvents = {}

        blnHasPayments = False
        for objPayment in self.Historic.objectValues('E3Payment'):
            blnHasPayments = True
            if not self.ImportedFromMailman or objPayment.GetDate() > self.GetCreatedDate():
                dictEvents = self.AddEventDate(dictEvents, objPayment.GetDate(), objPayment.Months, objPayment.BonusDays, "Payment")
#                if objPayment.GetDate() > dtmNextExpiry:
#                    dtmNextExpiry = objPayment.GetDate()
#                    print "Payment after expiry date, new date", dtmNextExpiry
#                dtmNextExpiry = dtmNextExpiry + datetime.timedelta(days = objPayment.BonusDays)
#                dtmNextExpiry = AddMonths(dtmNextExpiry, objPayment.Months)
#                print "Payment added ", dtmNextExpiry

        for objEvent in self.Historic.objectValues('E3Event'):
            if not self.ImportedFromMailman or objEvent.GetDate() > self.GetCreatedDate():
                dictEvents = self.AddEventDate(dictEvents, objEvent.GetDate(), 0, objEvent.Days, objEvent.EventType)
 #               dtmNextExpiry = dtmNextExpiry + datetime.timedelta(days = objEvent.Days)
 #               print "Free period added", dtmNextExpiry

        lstDates = dictEvents.keys()
        lstDates.sort()
        for dtmDate in lstDates:
            for (intMonths, intDays, strEventType) in dictEvents[dtmDate]:
#                print "Event at %s, %s months, %s days" % (dtmDate, intMonths, intDays)
                if intMonths + intDays > 0:
                    if dtmNextExpiry < dtmDate:
                        dtmNextExpiry = dtmDate
                if strEventType == "WarningSent":
                    dtmPostWarning = dtmDate + datetime.timedelta(days = 21)
                    if dtmPostWarning > dtmNextExpiry:
                        dtmNextExpiry = dtmPostWarning
#                    print "Payment after expiry date, new date", dtmNextExpiry
                dtmNextExpiry = AddMonths(dtmNextExpiry, intMonths)
                dtmNextExpiry = dtmNextExpiry + datetime.timedelta(days = intDays)
#                print "New expiry date" , dtmNextExpiry

#        print "Final expiry date", dtmNextExpiry

        self.HasPayments = blnHasPayments

        dtmPeriod = self.GetNextExpiryDate() - dtmNextExpiry
        if abs(dtmPeriod.days) > 1:
            if blnCheckOnly:
                print "Expiry date changed from %s to %s for %s" % (self.GetNextExpiryDate(), dtmNextExpiry, self.id)
            else:
                self.SetNextExpiryDate(dtmNextExpiry)

        if dtmNextExpiry < datetime.date(year=2006, month=9, day=22):
            self.SetMembershipType('None')
            return

        if dtmNextExpiry > dtmDate:
            self.SetMembershipType("Full")
            return

        strMembershipStatus = 'Full'
        dtmLatestExpiryDate = self.GetLatestEvent('Expiry')
        dtmLatestPaymentDate = self.GetLatestPaymentDate()
        if dtmLatestExpiryDate and not dtmLatestExpiryDate in [cnFirstDate, cnEmptyDate]:
            if dtmLatestPaymentDate and not dtmLatestPaymentDate in [cnFirstDate, cnEmptyDate]:
                if AddMonths(dtmLatestPaymentDate, 6) < dtmLatestExpiryDate:
                    strMembershipStatus = 'None'
            else:
                strMembershipStatus = 'None'
        self.SetMembershipType(strMembershipStatus)

    def RecordEvent(self, strEventType, strComments = "", strEmailAddress = "", dtmEventDate = None, intDays = 0):
        dodEvent = GetDOD(self, 'E3Event')
        objEvent = dodEvent.NewObject(self.Historic)
        if dtmEventDate:
            objEvent.SetDate(dtmEventDate)
        else:
            objEvent.SetDate(datetime.date.today())
        objEvent.EventType = strEventType
        objEvent.Comments = strComments
        objEvent.EmailAddress = strEmailAddress
        objEvent.Days = intDays

    def RecordEmailEvent(self, strEventType, strComments = ""):
        self.RecordEvent(strEventType, strComments, self.PreferredEmailAddress())

    def DaysSinceLastEvent(self, strEventType):
        intResult = 0
        blnHasEvent = False
        dtmNow = datetime.date.today()
        for objEvent in self.Historic.objectValues('E3Event'):
            if objEvent.EventType == strEventType:
                blnHasEvent = True
                deltaEvent = dtmNow - objEvent.GetDate()
                if intResult == 0:
                    intResult = deltaEvent.days
                else:
                    intResult = min(intResult, deltaEvent.days)
        return (intResult, blnHasEvent)

    def SendMemberEmail(self, strMessage, strSubject):
        strEmailAddress = self.PreferredEmailAddress()
        SendEmail(self, strMessage, strSubject, strEmailAddress)

    def Live(self):
        if self.MembershipType == 'None':
            return False
        if self.MembershipType == "Cancelled":
            return False
        return True

    def DaysSinceLastVisit(self):
        dtmNow = datetime.datetime.today()
        deltaSince = dtmNow - self.GetLastVisit()
        return deltaSince.days

    def CheckMembershipStatus(self, blnReportOnly = False):
        print "Check membership statis for %s" % self.id
        if self.LifetimeMember:
            print "Life time member"
            return

        if self.MembershipType <> 'Full':
            print "Expired"
            return

        if self.OnHold:
            print "On hold"
            return

        if self.ParkingMember():
            print "Parking member"
            return

        dtmNow = datetime.date.today()
        dtmExpiryDate = self.GetNextExpiryDate()
        (intDaysSinceWarning, blnHasWarning) = self.DaysSinceLastEvent('WarningSent')

        if dtmExpiryDate < dtmNow:
            if not self.HasConfirmedEmailAddress:
                self.Expire()
                print "No confirmed address, quiet expiry"
                return

            if blnHasWarning and intDaysSinceWarning > 21 and intDaysSinceWarning < 100:
                if blnReportOnly:
                    return """<li><a href="http://www.EuroCoachList.com/MyECL?MemberId=%s">Expired: %s</a></li>
""" % (self.id, self.id)
                else:
                    if self.HasConfirmedEmailAddress:
                        print "Expiry message sent"
                        self.Expire()
                return

        deltaRemaining = dtmExpiryDate - dtmNow
        if deltaRemaining.days <= 21:
            if not blnHasWarning or intDaysSinceWarning > 100:
                if blnReportOnly:
                    return """<li><a href="http://www.EuroCoachList.com/MyECL?MemberId=%s">Warning: %s</a></li>
""" % (self.id, self.id)
                else:
                    print "Less than 21 days remaining, %s days since last visit" % self.DaysSinceLastVisit()
                    if self.HasConfirmedEmailAddress or self.DaysSinceLastVisit() < 22:
                        self.SendWarningMessage()
                return

        elif deltaRemaining.days <= 100:
            (intDaysSinceBonusMessage, blnHasBonusMessage) = self.DaysSinceLastEvent('BonusSent')
            if (not blnHasBonusMessage or intDaysSinceBonusMessage > 150) and self.HasPayments:
                if blnReportOnly:
                    return """<li><a href="http://www.EuroCoachList.com/MyECL?MemberId=%s">Bonus: %s</a></li>
""" % (self.id, self.id)
                else:
                    self.SendBonusMessage()

    def SendExpiryMessage(self):
        strEmailAddress = self.PreferredEmailAddress()
        if not strEmailAddress:
            return
        if self.HasPayments:
            strMessage = cnPaidPeriodExpired % strEmailAddress
        else:
            strMessage = cnTrialPeriodExpired % strEmailAddress
        strHowToPay = cnHowToPay % (self.Username, self.Password)
        strMessage = strMessage + strHowToPay + cnSignature
        SendEmail(self, strMessage, 'Your Euro Coach List membership has expired', strEmailAddress)
        self.RecordEvent('ExpiryMessageSent')

    def SendWarningMessage(self):
        strEmailAddress = self.PreferredEmailAddress()
        if not strEmailAddress:
            return
        if self.HasPayments:
            strMessage = cnPaidPeriodDue % strEmailAddress
        else:
            strMessage = cnTrialPeriodDue % strEmailAddress
        strHowToPay = cnHowToPay % (self.Username, self.Password)
        strMessage = strMessage + strHowToPay + cnSignature
        SendEmail(self, strMessage, 'Your Euro Coach List membership is due to expire', strEmailAddress)
        self.RecordEvent('WarningSent')

    def SendBonusMessage(self):
        strEmailAddress = self.PreferredEmailAddress()
        if not strEmailAddress:
            return
        strEndOfMembership = (self.GetNextExpiryDate() - datetime.timedelta(days=1)).strftime(cnFullDateFormat)
        strPayBy = (self.GetNextExpiryDate() - datetime.timedelta(days=92)).strftime(cnFullDateFormat)
        strMessage = cnBonus % (strEndOfMembership, strPayBy)
        strHowToPay = cnHowToPay % (self.Username, self.Password)
        strMessage = strMessage + strHowToPay + cnSignature
        SendEmail(self, strMessage, 'Bonus Euro Coach List membership period', strEmailAddress)

        self.RecordEvent('BonusSent')

    def Expire(self):
        """ Send expiry message
            Record expiry
            Change status to Expired

            If no confirmed email address, give up on this member
                don't send them any commection email addresses
                don't send the expiry message
            """
        if self.HasConfirmedEmailAddress:
            self.SendExpiryMessage()
        else:
            self.NoCommercialEmails = True
        self.SetMembershipType('None')

    def ExpireQuietly(self):
        self.SetMembershipType('None')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

def addE3MemberForm(self):
    "New E3Member form"
    return GenericAddForm('E3Member')

def CleanEventDate(dtmDate):
    if dtmDate.year < 1900:
        dtmDate = datetime.date(year = dtmDate.year + 2000, month = dtmDate.month, day = dtmDate.day)
    return dtmDate

def CalculateBonusPeriod(dtmDate, dtmNextExpiryDate):
    # Payment at dtmDate, even though won't expire until dtmNextExpiryDate
    deltaPeriod = dtmNextExpiryDate - dtmDate
    intDays = max(0, min(deltaPeriod.days, 91))
#    intWeeks = int((deltaPeriod.days) / 7)
#    intResult = max(0, min(intWeeks, 13))
    return intDays

def AddMonths(dtmStart, intMonths):
    intYear = dtmStart.year
    intMonth = dtmStart.month
    intDay = dtmStart.day
    intMonth += intMonths
    while intMonth > 12:
        intMonth -= 12
        intYear += 1
    for intI in range(0, 5):
        try:
            dtmResult = datetime.date(year=intYear, month=intMonth, day=intDay - intI)
            return dtmResult
        except:
            pass

def AddDays(dtmStart, intDays):
    deltaPeriod = datetime.timedelta(days=intDays)
    return dtmStart + deltaPeriod

def addE3Member(self, id):
    "New E3Member action"
    objNewE3Member = E3Member(id)
    self._setObject(id, objNewE3Member)

    return "New E3Member created."


