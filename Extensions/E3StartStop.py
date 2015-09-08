# encoding: utf-8

import LocalPaths
# reload(LocalPaths)

import E3Security
# reload(E3Security)

import datetime
import random
import string

import os

import gc

from E3Members import GetCurrentMember
from E3Membership import GetMemberForEmailAddress
from E3Security import PasswordCorrect, LoginMember
from E3Security import DoEncrypt
from E3Security import SetLogInCookies
# from E3Security import JoinProcessing
from E3TempData import RemoveTempData
from E3TempData import StoreTempData
from E3Security import GetCookie
from libGeneral import GetParameter
from E3Security import MoreJoiningDetails
# from E3Security import EmailAddressExists
from E3Security import ShowLoginScreen
from E3TempData import SetMessage
from E3TempData import GetTempData
from libDatabase import Catalogue
from libDatabase import SearchOne
from libDatabase import GetDOD
from libDatabase import GetDataFolder
from E3Members import ManagerLoggedIn
from E3Members import GetMemberForId
from libDate import MonthToNumber
from E3TempData import SetErrorScreen
from libConstants import cnListNameECL
from libEmail import SendEmail
from libDatabase import SearchMany
from E3Messages import ChangeMonthCount
from E3Events import ValidAvailabilityStatement
from StringValidator import StringValidator
from E3HTML import UpdateCacheItem
from libConstants import cnProfileFieldNames
from libForms import GetDataFromForm
from libForms import UpdateObjectFromData
from libConstants import cnProductFieldNames
from libConstants import cnServiceFieldNames
from libConstants import cnEventFieldNames
from libDate import DateFromString
from libString import ValidEmailAddress

def OnLoad(objHere):
    try:
        strAutoSubmit = objHere.AutoSubmit
    except:
        strAutoSubmit = None
    try:
        strOnLoad = objHere.OnLoad
    except:
        strOnLoad = None
    objCurrentMember = GetCurrentMember(objHere)
    strResult = ""
    if strAutoSubmit and objCurrentMember:
        strResult = """%s.submit()""" % strAutoSubmit
    if strOnLoad:
        strResult = strOnLoad
    return strResult

def ProcessLogInRequest(objHere):
    blnLogInCorrect = False

    objRequest = objHere.REQUEST
    objResponse = objRequest.RESPONSE

    strUsername = GetParameter(objRequest, 'Username')
    strPassword = GetParameter(objRequest, 'Password')
    strKeepLoggedIn = GetParameter(objRequest, "KeepLoggedIn")
    blnKeepLoggedIn = (strKeepLoggedIn == "Yes")
   
    if strUsername and strPassword:
        strEncryptedPassword = DoEncrypt(strPassword)
        if PasswordCorrect(objHere, strEncryptedPassword, strUsername):
            blnLogInCorrect = True

    if blnLogInCorrect:
        SetLogInCookies(objResponse, strUsername, strEncryptedPassword, blnKeepLoggedIn)
        return (strUsername, '')
    else:
        return ('', ShowLoginScreen(objHere, objRequest, "Username or password incorrect"))

def ProcessLogOutRequest(objHere):
    objResponse = objHere.REQUEST.RESPONSE
    objResponse.expireCookie('E3Username', path='/')
    objResponse.expireCookie('E3Password', path='/')

def GetStatusFromCookies(objHere):
    strCookies = objHere.REQUEST.HTTP_COOKIE
    strUsername = GetCookie(strCookies, 'E3Username')
    strEncryptedPassword = GetCookie(strCookies, 'E3Password')
    if strUsername and strEncryptedPassword:
        if PasswordCorrect(objHere, strEncryptedPassword, strUsername):
            return strUsername
    return ''

def UpdateName(objMember, strName):
    if objMember.Name <> strName:
        if strName:
            objMember.Name = strName
            return True
        else:
            SetMessage(objMember, "The new name can't be empty", "")
    return False

def UpdatePersonalDetails(objHere):
    strUsername = GetParameter(objHere.REQUEST, 'Username')
    strName = GetParameter(objHere.REQUEST, 'Name')

    strMemberId = GetParameter(objHere.REQUEST, 'MemberId')
    if strMemberId:
        objMember = GetMemberForId(objHere, strMemberId)
    else:
        objMember = GetCurrentMember(objHere)

    blnUpdate = False
    if objMember.Username <> strUsername:
        if strUsername:
            if SearchMany(objHere, 'E3Member', 'Username', strUsername):
                SetMessage(objHere, "The new username is already in use by another member", "")
            else:
                objMember.Username = strUsername
                blnUpdate = True
        else:
            SetMessage(objHere, "The new username can't be empty", "")

    if UpdateName(objMember, strName):
        blnUpdate = True

    if blnUpdate:
        SetMessage(objHere, '', 'Personal details updated')
        Catalogue(objMember)
    return (objMember.Username, objMember.Name)

def CheckPasswordForm(objRequest, strCurrentPassword):
    strOldPassword = objRequest.form['OldPassword']
    strNewPassword = objRequest.form['NewPassword']
    strConfirmPassword = objRequest.form['ConfirmPassword']
    if not strOldPassword:
        return (False, "Old password must be entered")
    if not strNewPassword:
        return (False, "New password cannot be blank")
    if not strConfirmPassword:
        return (False, "Please confirm the password")
    if strOldPassword <> strCurrentPassword:
        return (False, "Old password incorrect")
    if strNewPassword <> strConfirmPassword:
        return (False, "Confirmation password doesn't match the new password")
    if strOldPassword == strNewPassword:
        return (False, "New password must be different from the old password")
    if len(strNewPassword) < 4:
        return (False, "New password must be at least four characters long")
    return (True, "")

def ToggleOnHold(objMember):
    objMember.OnHold = not objMember.OnHold

def NewPayment(objMember, objHere):
    dictForm = objHere.REQUEST.form
    strPaymentDate = dictForm['PaymentDate']
    dtmPaymentDate = DateFromString(strPaymentDate)
    intDuration = int(dictForm['Duration'])
    strMethod = dictForm['PaymentType']
    strAmount = dictForm['Amount']
    (strCurrency, strAmount) = strAmount.split()
    fltAmount = float(strAmount)
    strIdentifier = dictForm['Identifier']
    strEmailAddress = dictForm['EmailAddress']
    try:
        strSendReceipt = dictForm['SendReceipt']
        blnSendReceipt = (strSendReceipt == "yes")
    except:
        blnSendReceipt = False
    
    objMember.NewPayment(dtmPaymentDate, intDuration, strMethod, strCurrency, fltAmount, strIdentifier, blnSendReceipt, strEmailAddress)

def PasswordReminder(objHere):
    strForm = """<form method="post" action="%s">
					<fieldset>
						<legend>Password reminder</legend>
                        <p>Enter one or both of the following:</p>
						<p><label>Username</label>
                            <input type="hidden" name="Action" value="PasswordReminder"/>
							<input type="text" name="Username" class="txt""/>
						</p>
                	  	<p><label>Email address</label>
							<input type="text" name="EmailAddress" class="txt" />
						</p>
						<p>
							<input type="submit" name="btnSubmit" id="btnSubmit" value="Email the password reminder" class="btn" />
						</p>
                        <p>Your password and username will be emailed to you at all your registered email addresses</p>
					</fieldset>
                </form>
""" % objHere.absolute_url()
    strNotFoundError = """<p class="ErrorMessage">Log in details not found. Please try another username or email address</h2>"""
    strNoDetailsError = """<p class="ErrorMessage">No user name or email address entered. Try again</p>"""
    strUsername = GetParameter(objHere.REQUEST, "Username")
    strEmailAddress = GetParameter(objHere.REQUEST, "EmailAddress")
    objMember = None

    if not "PasswordReminder" in objHere.REQUEST.HTTP_REFERER:
        SetErrorScreen(objHere, strForm)
        return

    if not strUsername and not strEmailAddress:
        SetErrorScreen(objHere, strNoDetailsError + strForm)
        return

    if strUsername:
        objMember = SearchOne(objHere, 'E3Member', 'Username', strUsername)

    if not objMember and strEmailAddress:
        objMember = SearchOne(objHere, 'E3EmailAddress', 'EmailAddress', strEmailAddress)

    if objMember:
        objMember.SendPasswordReminder()
        SetMessage(objHere, '', """Log in details sent""")
    else:
        SetErrorScreen(objHere, strNotFoundError + strForm)

def SendConfirmationEmail(objHere, strEmailId):
    if not strEmailId:
        objMember = GetCurrentMember(objHere)
        for objEmailAddress in objMember.objectValues("E3EmailAddress"):
            if not objEmailAddress.Confirmed:
                objEmailAddress.RequestConfirmation()
                SetMessage(objHere, '', 'Confirmation request sent to %s' % objEmailAddress.EmailAddress)
    else:
        objEmailAddress = SearchOne(objHere, 'E3EmailAddress', 'id', strEmailId)
        if objEmailAddress:
            objEmailAddress.RequestConfirmation()
            SetMessage(objHere, '', 'Confirmation request sent to %s' % objEmailAddress.EmailAddress)
        else:
            print "Email address not found: ", strEmailId

def Unbounce(objMember):
    strEmailAddress = GetParameter(objMember.REQUEST, "SubmitButton")
    strEmailAddress = strEmailAddress.split()[1]
    objMember.Unbounce(strEmailAddress)
    SetMessage(objMember, '', '%s resumed' % strEmailAddress)

def ProcessContactForm(objHere):
    strName = GetParameter(objHere.REQUEST, 'Name')
    strEmailAddress = GetParameter(objHere.REQUEST, 'EmailAddress')
    strComments = GetParameter(objHere.REQUEST, 'Comments')
    if not strEmailAddress:
        SetMessage(objHere, 'Please enter an email address and resubmit', '')
        return

    objValidator = StringValidator(strEmailAddress)
    if not objValidator.isEmail():
        SetMessage(objHere, """'%s' is not a valid email address. Please enter a valid email address and resubmit. Alternatively, please send an email to <a href="mailto:coen@coachcoen.com">coen@coachcoen.com</a>""" % strEmailAddress)
        return
    if not strComments:
        SetMessage(objHere, 'Please enter your comments and resubmit', '')
        return    
    strMessage = """Someone has just filled in the Euro Coach List comments form. Here are the details:

Name: %s
Email Address: %s
Comments:
%s""" % (strName, strEmailAddress, strComments)
    SendEmail(objHere, strMessage, "ECL Form", "coen@coachcoen.com")
    SetMessage(objHere, '', 'Thanks for your comments. They have been sent to the list owner')

def SetPublicPrivate(objHere, objMember, blnMakeItPublic):
    strThreadId = GetParameter(objHere.REQUEST, 'ThreadId')
    if not strThreadId:
        SetMessage(objHere, "Message not found", "")
        return

    intThreadId = str(strThreadId)
    strMessageId = GetParameter(objHere.REQUEST, 'MessageId')
    if strMessageId:
        intMessageId = int(strMessageId)
    else:
        intMessageId = 0

    strThreadId = GetParameter(objHere.REQUEST, 'ThreadId')
    objThread = SearchOne(objHere, 'E3Messages', 'id', strThreadId)
    if not objThread:
        SetMessage(objHere, "Message not found", "")
        return

    if intMessageId:
        strMessageId = GetParameter(objHere.REQUEST, 'MessageId')
        objMessage = SearchOne(objHere, 'E3Messages', 'id', strMessageId)
    else:
        objMessage = objThread

    if not objMessage:
        SetMessage(objHere, "Message not found", "")
        return

    if objMessage.UserId <> objMember.id:
        SetMessage(objHere, "Message belongs to someone else", "")
        return

    dtmDate = objMessage.mailDate
    intMonth = dtmDate.month()
    intYear = dtmDate.year()
    if blnMakeItPublic:
        objMessage.Private = False
        SetMessage(objHere, "", "Message set to public")
        ChangeMonthCount(objHere, intYear, intMonth, 1, True)
    else:
        objMessage.Private = True
        SetMessage(objHere, "", "Message set to private")
        ChangeMonthCount(objHere, intYear, intMonth, -1, True)

def UpdateEventWillCome(objMember, strNewValue, strNewName):
    try:
        objPreferences = objMember.Events.ECL07
    except:
        objPreferences = None
    blnChanged = False
    if objPreferences:
        if strNewValue:
            if objPreferences.WillCome <> strNewValue:
                objPreferences.WillCome = strNewValue[0]
                blnChanged = True
        if objMember.Name <> strNewName:
            objMember.Name = strNewName
            blnChanged = True
    if blnChanged:
        SetMessage(objMember, "", "Details updated")
        UpdateCacheItem(objMember, "LHBlockConference")

def UpdateEventPreferences(objHere, objMember):
    try:
        objPreferences = objMember.Events.ECL07
    except:
        return

    objPreferences.PreparationOffers = GetParameter(objHere.REQUEST, "PreparationOffers")
    objPreferences.OnDayOffers = GetParameter(objHere.REQUEST, "OnDayOffers")
    objPreferences.Wishes = GetParameter(objHere.REQUEST, "Wishes")
    objPreferences.Comments = GetParameter(objHere.REQUEST, "Comments")

    SetMessage(objHere, "", "Details updated")

def UpdateEventLocations(objHere, objMember):
    lstLocations = []
    objForm = objHere.REQUEST.form
    for strControlName in objForm.keys():
        if "Location-" in strControlName:
            strName = strControlName[9:].replace("~", " ")
            lstLocations.append(strName)
    for strName in objForm['OtherLocations'].splitlines():
        if strName.strip():
            lstLocations.append(strName.strip())
    objMember.Events.ECL07.Locations = lstLocations
    SetMessage(objHere, "", "Location(s) updated")

def BuildAvailabilityInfo(objRequest):
    dictForm = objRequest.form
    if dictForm.has_key('AddWeekday'):
        strResult = dictForm['Weekday']

    elif dictForm.has_key('AddDate'):
        strResult = "%s %s" % (dictForm['Month'], dictForm['Date'])

    elif dictForm.has_key('AddPeriod'):
        strResult = "%s %s - %s %s" % (dictForm['FromMonth'], dictForm['FromDate'], dictForm['ToMonth'], dictForm['ToDate'])
    return strResult

def AddAvailabilityStatement(objHere, objMember):
    try:
        objPreferences = objMember.Events.ECL07
    except:
        SetMessage(objHere, "Failed to store the information. Please contact the list owner", "")
        return

    strType = GetParameter(objHere.REQUEST, "AvailabilityType")
    strInfo = BuildAvailabilityInfo(objHere.REQUEST)

    if not ValidAvailabilityStatement(objPreferences, strType, strInfo):
        return

    dodAvailabilityStatement = GetDOD(objHere, "E3AvailabilityStatement")
    objStatement = dodAvailabilityStatement.NewObject(objPreferences)
    objStatement.Type = strType
    objStatement.Info = strInfo
    SetMessage(objHere, "", "Information added")

def DeleteAvailabilityStatements(objHere, objMember):
    try:
        objPreferences = objMember.Events.ECL07
    except:
        SetMessage(objHere, "Failed to update the information. Please contact the list owner", "")
        return

    blnDeleted = False
    for strName in objHere.REQUEST.form.keys():
        if "Delete-" in strName and objHere.REQUEST.form[strName] == "Yes":
            strName = strName[7:]
            try:
                objPreferences.manage_delObjects(strName)
                blnDeleted = True
            except:
                SetMessage(objHere, "Couldn't delete the information. Please contact the list owner", "")
    if blnDeleted:
        SetMessage(objHere, "", "Information deleted")

def AddFreePeriod(objHere, objMember):
    strMemberId = objMember.id
    if not objHere.REQUEST.form.has_key('Months') or not objHere.REQUEST.form['Months']:
        SetMessage(objHere, "Number of months not specified", "")
        return
    intMonths = int(objHere.REQUEST.form['Months'])
    dtmNow = datetime.date.today()
    objMember.GiveFreeMembershipPeriod(dtmNow, intMonths * 31, blnRecalculate = True)

def LogMemory(objHere, blnStart = False):
    if blnStart:
        os.system("""echo >> memory.log""")
        os.system("""echo %s >> memory.log""" % objHere.REQUEST.VIRTUAL_URL)
    os.system("""free | grep "Mem" >> memory.log""")
#    os.system("""free >> memory.log""")

def UpdateProfile(objHere, objMember):
    dictProfile = GetDataFromForm(objHere, objHere.REQUEST.form, cnProfileFieldNames)
    UpdateObjectFromData(objMember, dictProfile, cnProfileFieldNames)
#    objNewPhoto = objHere.REQUEST.form['NewPhoto']
#    if str(objNewPhoto):
#        print "New photo: ", objNewPhoto
#        print "Length: ", len(objHere.REQUEST.read())
#    print objHere.REQUEST

def UpdateThread(objHere, objMember):
    if not ManagerLoggedIn(objHere):
        SetMessage(objHere, "Only a manager can change this", "")
        return

    strThreadId = GetParameter(objHere.REQUEST, "ThreadId")
    strSubject = GetParameter(objHere.REQUEST, "ThreadSubject")
    strSummary = GetParameter(objHere.REQUEST, "ThreadSummary")
    blnPublish = objHere.REQUEST.has_key("ThreadPublish")
    strTopicId = GetParameter(objHere.REQUEST, "TopicId")

    objThread = SearchOne(objHere, "E3Thread", "id", strThreadId)
    if not objThread:
        SetMessage(objHere, "Thread not found", "")
        return

    objThread.Subject = strSubject
    objThread.Summary = strSummary
    objThread.Publish = blnPublish
    objThread.TopicId = strTopicId

    Catalogue(objThread)
    
    SetMessage(objHere, "", """Details updated. <a href="/admin/E3ThreadMaintenance">Return to list</a>""")
    
def NeedsMember(objMember):
    if objMember:
        return True
    else:
        SetMessage(objHere, """Failed to make the requested changes. Please contact the list owner""", "")
        return False

def UsernameExists(objHere, strUsername):
    objMembers = GetDataFolder(objHere, "E3Member")
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.Username.lower() == strUsername.lower():
                return True
    return False

def RegisterNewMember(objHere, strEmailAddress):
    dodMember = GetDOD(objHere, 'E3Member')
    objMember = dodMember.NewObject()

    strUsername = strEmailAddress
    if UsernameExists(objHere, strEmailAddress):
        strUsername = objMember.id

    objMember.Username = strUsername
    objMember.Name = ""
    objMember.Password = RandomPassword()

    (objNewEmailAddress, strErrorMessage) = objMember.AddEmailAddress(strEmailAddress)
        
    objMember.CreateTrialPeriod()
    objMember.NoMail = False
    objMember.EmailDigestMode = "StructuredDigest"
    objMember.EmailFrequency_ECL = "Direct"
    objMember.EmailFrequency_ECL_Advert = "Daily"
    objMember.EmailDeliveryAddress = strEmailAddress
    Catalogue(objMember)
    return objMember

def RandomPassword():
    strResult = ""
    for intI in range(1, 6):
        strResult += random.choice(string.letters + string.digits)
    return strResult

def JoinProcessing(objHere):
    strEmailAddress = GetParameter(objHere, "EmailAddress")
    strEmailAddress = strEmailAddress.lower().replace(" ", "")
    if strEmailAddress and ValidEmailAddress(strEmailAddress):
        if not GetMemberForEmailAddress(objHere, strEmailAddress):
            objMember = RegisterNewMember(objHere, strEmailAddress)
            LoginMember(objMember)
            objMember.SendPasswordReminder()
            return objMember.Username
    return ""

def E3Start(objHere):
#    gc.enable()
#    LogMemory(objHere, True)
    strPageTitle = ""
    objRequest = objHere.REQUEST
    objResponse = objRequest.RESPONSE
    if objRequest.has_key('Action'):
        strAction = objRequest['Action']
    else:
        strAction = ''

#    print "Action: ", strAction

    if strAction == 'LogIn':
        (strUsername, strErrorScreen) = ProcessLogInRequest(objHere)
    elif strAction == 'LogOut':
        ProcessLogOutRequest(objHere)
        (strUsername, strErrorScreen) = ('', '')
    elif strAction == 'QuickJoin':
        dictFields = {}
        strUsername = ''
        strErrorScreen = MoreJoiningDetails(objHere)
#    elif strAction == 'Join':
#        (strUsername, strErrorScreen, strPageTitle) = JoinProcessing(objHere)
    else:
        strUsername = GetStatusFromCookies(objHere)
        strErrorScreen = ''

    if strAction == "JoinNow":
#        print "JoinNow in StartStop"
        strUsername = JoinProcessing(objHere)

    StoreTempData(objHere, strUsername, strErrorScreen, strPageTitle)

    strMemberId = GetParameter(objHere.REQUEST, 'MemberId')
    if strMemberId and not ManagerLoggedIn(objHere):
        return

    if strAction == "UpdatePersonalDetails":
        (strNewUsername, strNewName) = UpdatePersonalDetails(objHere)
        if strNewUsername <> strUsername and not strMemberId:
            objTempData = GetTempData(objHere)
            objTempData.Username = strNewUsername
            objTempData.ErrorScreen = strErrorScreen
            objResponse.setCookie('E3Username', strNewUsername, path='/')
        return

    elif 'PasswordReminder' in strAction:
        PasswordReminder(objHere)
        return

    elif strAction == "ContactForm":
        ProcessContactForm(objHere)
        return

    if strMemberId:
        objMember = GetMemberForId(objHere, strMemberId)
    else:
        objMember = GetCurrentMember(objHere)
        if objMember:
            objMember.RecordVisit()

    if strAction == "UpdatePassword":
        if not NeedsMember(objMember):
            return
        (blnPasswordFormCorrect, strErrorMessage) = CheckPasswordForm(objRequest, objMember.Password)
        if blnPasswordFormCorrect:
            strNewPassword = objRequest.form['NewPassword'].strip()
            if objMember.Password <> strNewPassword:
                objMember.Password = strNewPassword
                SetMessage(objHere, '', 'Password changed')
                if not strMemberId:
                    objResponse.setCookie('E3Password', DoEncrypt(strNewPassword), path='/')
        else:
            SetMessage(objMember, strErrorMessage)

    elif strAction == 'UpdateEmailAddresses':
        if not NeedsMember(objMember):
            return
        UpdateEmailAddresses(objHere, objMember)

    elif strAction == 'UpdateEmailAddressesAdvanced':
        if not NeedsMember(objMember):
            return
        UpdateEmailAddressesAdvanced(objHere, objMember)

    elif strAction == "Cancel my membership":
        if not NeedsMember(objMember):
            return
        objMember.CancelMembership()

    elif strAction == "ResumeMembership":
        if not NeedsMember(objMember):
            return
        objMember.UncancelMembership()

    elif strAction == "Unbounce":
        if not NeedsMember(objMember):
            return
        Unbounce(objMember)

    elif strAction == 'ToggleOnHold':
        if not NeedsMember(objMember):
            return
        ToggleOnHold(objMember)

    elif strAction == 'PaymentAction':
        if not NeedsMember(objMember):
            return
        strSubAction = objHere.REQUEST.form['Update']
        strPaymentId = objHere.REQUEST.form['PaymentId']
        if strSubAction == 'Delete':
            objMember.DeletePayment(strPaymentId)
        elif strSubAction == 'Resend Invoice':
            objMember.ResendInvoice(strPaymentId)

    elif strAction == 'NewPayment':
        if not NeedsMember(objMember):
            return
        NewPayment(objMember, objHere)

    elif strAction == 'ConfirmationEmail':
        if not NeedsMember(objMember):
            return
        strEmailId = GetParameter(objHere.REQUEST, 'EmailAddressId')
        SendConfirmationEmail(objHere, strEmailId)

    elif strAction == 'SetPublic':
        if not NeedsMember(objMember):
            return
        SetPublicPrivate(objHere, objMember, True)

    elif strAction == 'SetPrivate':
        SetPublicPrivate(objHere, objMember, False)

    elif strAction == "UpdateEventWillCome":
        if not NeedsMember(objMember):
            return
        strNewValue = GetParameter(objHere.REQUEST, "WillCome")
        strNewName = GetParameter(objHere.REQUEST, "Name")
        UpdateEventWillCome(objMember, strNewValue, strNewName)

    elif strAction == "UpdateEventPreferences":
        if not NeedsMember(objMember):
            return
        UpdateEventPreferences(objHere, objMember)    

    elif strAction == "UpdateEventLocations":
        if not NeedsMember(objMember):
            return
        UpdateEventLocations(objHere, objMember)

    elif strAction == "AddAvailabilityStatement":
        if not NeedsMember(objMember):
            return
        AddAvailabilityStatement(objHere, objMember)

    elif strAction == "DeleteAvailabilityStatements":
        if not NeedsMember(objMember):
            return
        DeleteAvailabilityStatements(objHere, objMember)

    elif strAction == "AddFreePeriod":
        if not NeedsMember(objMember):
            return
        AddFreePeriod(objHere, objMember)

    elif strAction == "UpdateThread":
        if not NeedsMember(objMember):
            return
        UpdateThread(objHere, objMember)

    elif strAction == "UpdateProfile":
        if not NeedsMember(objMember):
            return
        UpdateProfile(objHere, objMember)

def E3Stop(objHere):
    RemoveTempData(objHere)
#    LogMemory(objHere)
#    print "before: ", len(gc.get_objects())
#    gc.collect()
#    print "after: ", len(gc.get_objects())
