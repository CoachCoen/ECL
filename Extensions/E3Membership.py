from libForms import Fieldset, Paragraph, TextControl, SubmitControl, HiddenControl
from libForms import CreateForm, PureText, SelectControl, CheckboxControl
from libForms import PasswordControl, TextArea, GetDataFromForm
from libForms import CheckRequiredFields, ReportErrors, UpdateObjectFromData
from libForms import LoadDataFromObject
from libGeneral import GetParameter
from E3HTML import FullURL
from libString import ValidEmailAddress
from libDatabase import SearchMany, GetDOD, Catalogue
from E3Security import DoEncrypt, SetLogInCookies, LoginMember
from E3Members import GetCurrentMember, UsernameInUse
from libString import ToUnicode
from libGeneral import AffiliateSalesTracking

import random
import string

def JoiningForm(objHere, strCallingURL, strEmailAddress, strMessage = ""):
#1.If a blank email address, assume that they got to this page directly. In that case
#1.Show a mini ad - encouraging them to sign up
    if strEmailAddress == "emailaddress":
        strEmailAddress = ""
    lstFields = ("EmailAddress")
    dictHiddenFields = {'CallingURL': strCallingURL,
                'Action': "JoinNow"}
    lstForm = (Fieldset("Join Now", None,
                Paragraph(TextControl("Email Address", "EmailAddress")),
                Paragraph(SubmitControl("Join Now"))),)
    dictData = {'EmailAddress': strEmailAddress}

    strForm = CreateForm(objHere, lstForm, dictData, "", dictHiddenFields)
    if strMessage:
        if "warning" in strMessage.lower():
            strClass = "GeneralError"
        else:
            strClass = "InfoMessage"
        strMessage = """<p class="%s">%s</p>\n""" % (strClass, strMessage)
    strResult = strMessage + strForm
    return strResult

def WelcomeScreen(objMember, strCallingURL, dictLoginDetailsData, dictErrors = {}, strLoginMessage = "", strDeliveryMessage = ""):
    strIntro = """
<fieldset>
    <legend>Welcome</legend>
    <p>You are now a member of the Euro Coach List</p>
    <p>Your user name is %s</p>
    <p>Your password is %s</p>
    <p>A copy of these details has been sent to your email address (%s)</p>
    <p>You need to confirm your email address. Please follow the instructions in the confirmation request email that has just been sent to you. This is to stop anyone signing up an email address which doesn't belong to them</p>
    <p>Once you have confirmed your email address you will start receiving list messages, in one daily digest message</p>
</fieldset>""" % (objMember.Username, objMember.Password, objMember.EmailDeliveryAddress)

    if objMember.EmailFrequency_ECL == "Daily":
        strListButtonText = "Switch to seperate list messages"
        strListCurrentDelivery = "Daily list digest"
        strListStep = "SwitchToDirectListDelivery"
    else:
        strListButtonText = "Switch to daily list digest"
        strListCurrentDelivery = "Seperate list messages"
        strListStep = "SwitchToDailyListDigest"

    if objMember.GetEmailFrequency("ECL", True) == "Daily":
        strAdvertButtonText = "Switch to seperate adverts"
        strAdvertCurrentDelivery = "Daily advert digest"
        strAdvertStep = "SwitchToDirectAdvertDelivery"
    else:
        strAdvertButtonText = "Switch to daily advert digest"
        strAdvertCurrentDelivery = "Seperate adverts"
        strAdvertStep = "SwitchToDailyAdvertDigest"

    if strDeliveryMessage:
        strDeliveryMessage = """<p class="InfoMessage">%s</p>""" % strDeliveryMessage

    strEmailDeliveryForm = """
<fieldset>
    <legend>List message delivery</legend>
    <p>Member send in between 5 and 15 <b>list messages</b> most weekdays. You can receive this as seperate list messages or in one daily list digest</p>
    <p>Current setting: %s</p>
    <form action="." method="post">
        <p><input type="submit" value="%s" class="btn"></p>
        <input type="hidden" value="%s" name="JoinStep">
        <input type="hidden" value="%s" name="CallingURL">
    </form>
</fieldset>
<fieldset>
    <legend>Advert delivery</legend>
    <p>Members also submit in between 5 and 10 <b>adverts</b> most weekdays. You can receive this as seperate adverts or in one daily advert digest</p>
    <p>Current setting: %s</p>
    <form action="." method="post">
        <p><input type="submit" value="%s" class="btn"></p>
        <input type="hidden" value="%s" name="JoinStep">
        <input type="hidden" value="%s" name="CallingURL">
    </form>
    <p>(This only applies to adverts which have been submitted on the website. Adverts which have been emailed in are treated as list messages. From 1st January 2009 all adverts must be submitted via the website)</p>
</fieldset>""" % (strListCurrentDelivery, strListButtonText, strListStep, strCallingURL, strAdvertCurrentDelivery, strAdvertButtonText, strAdvertStep, strCallingURL)

    lstLoginDetailsForm = (Fieldset("Login details", None,
        Paragraph(TextControl("User name", "Username")),
        Paragraph(PasswordControl("Password", "Password")),
        Paragraph(PasswordControl("Confirm Password", "PasswordConfirmation")),
        Paragraph(SubmitControl("Update login details"))),)

    strLoginDetailsForm = CreateForm(objMember, lstLoginDetailsForm, dictLoginDetailsData, dictHiddenFields = {"JoinStep": "UpdateLoginDetails", "CallingURL": strCallingURL}, dictErrors = dictErrors)

    if strLoginMessage:
        strLoginMessage = """<p class="InfoMessage">%s</p>""" % strLoginMessage

    strMessage = ReportErrors(dictErrors)
    strResult = strIntro + strMessage + strDeliveryMessage + strEmailDeliveryForm + strLoginMessage + strLoginDetailsForm + WhatsNextScreen(strCallingURL)
    strResult += AffiliateSalesTracking("ECL-T01", objMember.id, 0)
    return strResult

def WhatsNextScreen(strCallingURL):
    strResult = """
<fieldset>
    <legend>Your first message</legend>
    <p>Make sure you have read the <a href="/Rules">list rules</a> before posting your message</p>
    <p>To send a message to the list members, simply write an email and send it to <a href="mailto:eurocoach-list@forcoaches.com">EuroCoach-List@forcoaches.com</a></p>
</fieldset>
<fieldset>
    <legend>Your profile</legend>
    <p>Tell your future clients about yourself, and you may be tomorrow's Featured Member</p>
    <p>Go to your <a href="/MyECL">profile page</a> now</p>
</fieldset>
<fieldset>
    <legend>Your products, services and events</legend>
    <p>List your products, services, workshops and other events, so list members, potential clients and other website visitors can see what you have to offer</p>
    <p>Go to your <a href="/MyECL">products, services and event pages</a> now</p>
</fieldset>
<fieldset>
    <legend>Continue</legend>
    <p>Or you can <a href="%s">continue on the page you were before you signed up</a></p>
</fieldset>
""" % strCallingURL
    return strResult

def GetMemberForEmailAddress(objHere, strEmailAddress):
    strToSearch = '%s' % strEmailAddress.lower()
    lstAddresses = SearchMany(objHere, 'E3EmailAddress', 'EmailAddressField', strToSearch)
    if lstAddresses:
        objMember = lstAddresses[0].unrestrictedTraverse("..")
        return objMember
    return None

def ValidLoginDetails(objMember, dictLoginDetails, blnCheckOldPassword = False):
#1.Username must be entered
#2.Username must not be used by anyone else - regardless of case (upper/lower/mixed)
#3.No spaces in Username - starting and trailing spaces automatically trimmed
#4.Password must be entered, and at least 5 characters long
    dictErrors = CheckRequiredFields(dictLoginDetails, ("Username", ))

    if dictErrors:
        return dictErrors

    strUsername = dictLoginDetails["Username"]
    strUsername = strUsername.decode('ascii', 'ignore')
    dictLoginDetails["Username"] = strUsername
    if UsernameInUse(objMember, strUsername):
        dictErrors["Username"] = ("GeneralError", "Username already in use")

    if " " in strUsername:
        dictErrors["Username"] = ("GeneralError", "The username must not have any spaces")

    if dictLoginDetails["Password"] or dictLoginDetails["PasswordConfirmation"]:
        if len(dictLoginDetails["Password"]) < 5:
            dictErrors["Password"] = ("GeneralError", "The password must be at least 5 characters long")
        elif dictLoginDetails["Password"] <> dictLoginDetails["PasswordConfirmation"]:
            dictErrors["PasswordConfirmation"] = ("GeneralError", "Password confirmation does not match the password")

    if blnCheckOldPassword:
        if objMember.Password <> dictLoginDetails["OldPassword"]:
            dictErrors["OldPassword"] = ("GeneralError", "Incorrect old password entered")
    return dictErrors

def SaveLoginDetails(objMember, dictBasicSettings):
    if dictBasicSettings["Password"]:
        objMember.Password = dictBasicSettings["Password"]
    objMember.Username = dictBasicSettings["Username"]
    Catalogue(objMember)
    LoginMember(objMember, False)

def RemoveAction(strURL):
    if not "?" in strURL:
        return strURL
    strQueryString = strURL[(strURL.find("?") + 1):]
    lstItems = strQueryString.split('&')
    lstResult = []
    for strItem in lstItems:
        lstParts = strItem.split('=')
        if 'action' <> lstParts[0].lower():
            lstResult.append(strItem)
    strQueryString = "&".join(lstResult)

    strResult = strURL[:strURL.find("?") ]
    if strQueryString:
        strResult += "?" + strQueryString
    return strResult

def JoiningPage(objHere):
    # If doesn't have a form, or blank email address, assume they got to this page directly
    strStep = GetParameter(objHere, "JoinStep")
    if not strStep:
        strStep = "JoinNow"

    strEmailAddress = GetParameter(objHere, "EmailAddress")
    strEmailAddress = strEmailAddress.lower().replace(" ", "")
    strCallingURL = GetParameter(objHere, "CallingURL")
    if not strCallingURL:
        strCallingURL = objHere.REQUEST.HTTP_REFERER
        strCallingURL = RemoveAction(strCallingURL)

    if strStep == "JoinNow":
        if not strEmailAddress:
            return JoiningForm(objHere, strCallingURL, strEmailAddress)

        if strEmailAddress.lower().replace(" ", "") == "emailaddress":
            return JoiningForm(objHere, strCallingURL, strEmailAddress)

        if not ValidEmailAddress(strEmailAddress):
            return JoiningForm(objHere, strCallingURL, strEmailAddress, "Warning: Invalid email address entered. Please submit a correct email address")

        objMember = GetCurrentMember(objHere)
        if not objMember:
            objMember = GetMemberForEmailAddress(objHere, strEmailAddress)
            if objMember:
                objMember.SendPasswordReminder("someone just tried to register using your email address: %s" % strEmailAddress)
                strErrorMessage = "Warning: This email address is already registered. Please log in (using the form on the left hand side) instead of (re-)joining or enter the correct email address. A reminder of your log in details has been sent to %s" % strEmailAddress
            else:
                strErrorMessage = """An unknown error occurred. Please try again or <a href="/ContactDetails">contact the list owner</a>"""
            return JoiningForm(objHere, strCallingURL, strEmailAddress, strErrorMessage)


        # Note: Actual creating of new member happens in E3StartStop.JoinProcessing
        dictLoginDetails = LoadDataFromObject(objMember, ("Username", ))
        return WelcomeScreen(objMember, strCallingURL, dictLoginDetails)

    elif strStep == "UpdateLoginDetails":
        objMember = GetCurrentMember(objHere)
        lstFields = ("Username", "Password", "PasswordConfirmation")
        dictLoginDetails = GetDataFromForm(objHere, objHere.REQUEST.form, lstFields)
        dictErrors = ValidLoginDetails(objMember, dictLoginDetails)
        if dictErrors:
            return WelcomeScreen(objMember, strCallingURL, dictLoginDetails, dictErrors = dictErrors)

        SaveLoginDetails(objMember, dictLoginDetails)
        dictLoginDetails = LoadDataFromObject(objMember, ("Username", ))
        objMember.SendPasswordReminder()
        return WelcomeScreen(objMember, strCallingURL, dictLoginDetails, strLoginMessage = "Log in details updated")

    elif "SwitchTo" in strStep:
        objMember = GetCurrentMember(objHere)

        if strStep == "SwitchToDirectListDelivery":
            objMember.EmailFrequency_ECL = "Direct"

        elif strStep == "SwitchToDailyListDigest":
            objMember.EmailFrequency_ECL = "Daily"

        elif strStep == "SwitchToDirectAdvertDelivery":
            objMember.EmailFrequency_ECL_Advert = "Direct"

        elif strStep == "SwitchToDailyAdvertDigest":
            objMember.EmailFrequency_ECL_Advert = "Daily"

        dictLoginDetails = LoadDataFromObject(objMember, ("Username", ))
        return WelcomeScreen(objMember, strCallingURL, dictLoginDetails, strDeliveryMessage = "Email delivery updated")

    return "<p>This is the joining page</p>"


