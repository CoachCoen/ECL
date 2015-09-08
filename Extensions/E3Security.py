# encoding: utf-8

# Cookies used:
# - E2Username
# - E2Password
# - E2LoggedIn - Checksum, based on Username and current date, to allow quick checking that the user is indeed logged in, without having to check the password again. The password will only be (re-)checked if the Hash key is incorrect (presumably because the date has changed)

import os
import string
import datetime
import hmac
import random
import crypt

import LocalPaths
reload(LocalPaths)

from libDatabase import SearchOne
from libDatabase import SearchMany
from libGeneral import GetParameter
from libDatabase import GetDataFolder
from libDatabase import GetDOD
from libDatabase import Catalogue
from E3HTML import GetPageTemplate
from E3TempData import SetPageTitle
# from E3MyECL import SetDeliveryMode
from StringValidator import StringValidator

def DoEncrypt(strPassword):
    return crypt.crypt(strPassword, '8q')

def CleanCookieText(strText):
    print "Cleaning: ", strText
    strResult = strText.replace('"', '')
    while "%" in strResult:
        intPos = strResult.find("%")
        try:
            strCode = strResult[(intPos + 1):(intPos + 3)]
            intCode = int(strCode, 16)
            strResult = strResult[:intPos] + chr(intCode) + strResult[(intPos + 3):]
        except:
            strResult = strResult.replace('%', '')
    print "Result: |%s|" % strResult
    return strResult

def GetCookie(strCookieString, strName):
    lstCookieList = strCookieString.split('; ')
    (strCookieName, strValue) = ('', '')
    for strCookie in lstCookieList:
        try:
            (strCookieName, strValue) = strCookie.split('=')
        except:
            pass
        if strCookieName == strName:
            return CleanCookieText(strValue)
            # return str(strValue).replace('"', '')
    return ''

def SetLogInCookies(objResponse, strUsername, strEncryptedPassword, blnStayLoggedIn = False):
    if blnStayLoggedIn:
        strManyYears = "Wednesday, 01-Jan-25 12:00:00 GMT"
        objResponse.setCookie('E3Username', strUsername, path='/', expires=strManyYears)
        objResponse.setCookie('E3Password', strEncryptedPassword, path='/', expires=strManyYears)
    else:
        objResponse.setCookie('E3Username', strUsername, path='/')
        objResponse.setCookie('E3Password', strEncryptedPassword, path='/')

def LoginMember(objMember, blnStayLoggedIn = False):
    strEncryptedPassword = DoEncrypt(objMember.Password)
    SetLogInCookies(objMember.REQUEST.RESPONSE, objMember.Username, strEncryptedPassword, blnStayLoggedIn)

def PasswordCorrect(objHere, strEncryptedPassword, strUsername):
    objMember = SearchOne(objHere, 'E3Member', 'Username', strUsername)
    if objMember:
        if DoEncrypt(objMember.Password) == strEncryptedPassword:
            return True
    return False

def JoiningFormTemplate():
    return """
    %(ErrorMessage)s
<form action="/Membership/Welcome" method="post">
    <fieldset>
        <legend>If you have been a member before</legend>
        <h2>For current or past members</h2>
        <p>If you have been a member before then the system still knows about you. Please log in instead of creating a second membership</p>
        <p>To receive a password reminder, go to the <a href="%(URL)s?Action=PasswordReminder">password reminder screen</a></p>
    </fieldset>
	<fieldset>
		<legend>Join now</legend>
        <h2>New members only</h2>
		<p>Membership is free for the first 3 months</p>
		<p>
			<label>Email address</label>
           	<input type="text" name="EmailAddress" class="txt" value="%(EmailAddress)s"/>
            <input type="hidden" name="Action" value="JoinNow">
		</p>
        <p><input name="Input" type="submit" value="Join" class="btn"/> By joining the Euro Coach List you agree to follow the <a href="/Rules">list rules</a> and the <a href="/Legal/TnCMembership">terms and conditions of list membership</a></p>
    </fieldset>
</form>"""


def JoiningScreenCheck(objHere, strUsername, strPassword, strPasswordRepeat, strName, strEmailAddress):
    lstErrors = []
    blnClearPassword = False
    if not strEmailAddress:
        lstErrors.append('Email address must be entered')
    elif EmailAddressExists(objHere, strEmailAddress):
        lstErrors.append('Email address %s already in use by another user' % strEmailAddress)
    else:
        objValidator = StringValidator(strEmailAddress)
        if not objValidator.isEmail():
            lstErrors.append("'%s' is not a valid email address" % strEmailAddress)
    return '<br>'.join(lstErrors)

def ShowJoiningScreen(objHere, dictForm, strErrorMessage = "", strPlainMessage = "", blnClearPassword = False):
    dictFields = {}
    if "EmailAddress" in dictForm.keys():
        dictFields["EmailAddress"] = dictForm["EmailAddress"]
    else:
        dictFields["EmailAddress"] = ''
    if strErrorMessage:
        strErrorMessage = '<p class="ErrorMessage">%s</p>' % strErrorMessage
    dictFields['ErrorMessage'] = strErrorMessage
    dictFields['PlainMessage'] = strPlainMessage
    dictFields['URL'] = objHere.absolute_url()
    return JoiningFormTemplate() % dictFields

def MoreJoiningDetails(objHere):
    objRequest = objHere.REQUEST
    dictFields = {}
    dictFields['EmailAddress'] = GetParameter(objRequest, 'EmailAddress')
    strPlainMessage = 'Final step, just a few more details. Thanks'
    return ShowJoiningScreen(objHere, dictFields, strPlainMessage = strPlainMessage)

def EmptyJoiningScreen(objHere):
    return ShowJoiningScreen(objHere, {})

def LoginFormTemplate():
    return """
    %(ErrorMessage)s
    %(PlainMessage)s
<form action="%(URL)s" method="post">
	<fieldset>
		<legend>Log in</legend>
		<p>
			<label>Username</label>
            <input type="text" name="Username" value="%(Username)s" class="txt"/>
		</p>
		<p>
			<label>Password</label>
            <input type="password" name="Password" value="%(Password)s" class="txt"/>
            <input type="hidden" name="Action" value="LogIn">
		</p>
		<p><input type="checkbox" name="KeepLoggedIn" value="Yes"> Keep me logged in</p>
        <p class="FormComment"><a href="%(URL2)sAction=PasswordReminder">(Forgot your password?)</a></p>
        <p><input name="Input" type="submit" value="Log in" class="btn"/></p>
	</fieldset>
</form>"""

def ShowLoginScreen(objHere, dictForm, strErrorMessage = "", strPlainMessage = ""):
    dictFields = {}
    for strKey in ('Username', 'Password'):
        if strKey in dictForm.keys():
            dictFields[strKey] = dictForm[strKey]
        else:
            dictFields[strKey] = ''
    if strErrorMessage:
        strErrorMessage = """<p class="ErrorMessage">%s</p>""" % strErrorMessage
    if strPlainMessage:
        strPlainMessage = """<p>%s</p>""" % strPlainMessage
    dictFields['ErrorMessage'] = strErrorMessage
    dictFields['PlainMessage'] = strPlainMessage
#    dictFields['URL'] = objHere.absolute_url()
    strURL = objHere.REQUEST.URL1
    strQueryString = objHere.REQUEST.QUERY_STRING
#    print "Show log in screen, url: ", strURL
#    print objHere.REQUEST
    if strQueryString:
        dictFields['URL2'] = strURL + "?" + strQueryString + "&"
        dictFields['URL'] = strURL + "?" + strQueryString
    else:
        dictFields['URL2'] = strURL + "?"
        dictFields['URL'] = strURL
#    print "URL2", dictFields['URL2']

    return LoginFormTemplate() % dictFields

def EmptyLoginScreen(objHere):
    return ShowLoginScreen(objHere, {})

def GetFieldValue(objForm, strFieldName):
    if objForm.has_key(strFieldName):
        return objForm[strFieldName]
    return ""

def JoinProcessing(objHere):
    print "Join processing"
    objRequest = objHere.REQUEST
    objResponse = objRequest.RESPONSE
    strUsername = GetFieldValue(objRequest.form, 'Username')
    strPassword = GetFieldValue(objRequest.form, 'Password')
    strPasswordRepeat = GetFieldValue(objRequest.form, 'PasswordRepeat')
    strName = GetFieldValue(objRequest.form, 'Name')
    strDeliveryMode = GetFieldValue(objRequest.form, 'DeliveryMode')
    strEmailAddress = GetFieldValue(objRequest.form, 'EmailAddress').lower()
    (strErrorMessage, blnClearPassword) = JoiningScreenCheck(objHere, strUsername, strPassword, strPasswordRepeat, strName, strEmailAddress)
    if strErrorMessage:
        return ('', ShowJoiningScreen(objHere, objRequest, blnClearPassword = blnClearPassword, strErrorMessage = strErrorMessage), "")
    dodMember = GetDOD(objHere, 'E3Member')
    objMember = dodMember.NewObject()
    objMember.Username = strUsername
    objMember.Name = strName
    objMember.Password = strPassword

    (objNewEmailAddress, strErrorMessage) = objMember.AddEmailAddress(strEmailAddress)
    if not objNewEmailAddress:
        objMember.unrestrictedTraverse('..').manage_delObjects(objMember.id)
        return ('', ShowJoiningScreen(objHere, objRequest, blnClearPassword = blnClearPassword, strErrorMessage = strErrorMessage), "")

    objMember.CreateTrialPeriod()
    if strDeliveryMode == "NoMail":
        objMember.NoMail = True
        objMember.EmailDigestMode = "StructuredDigest"
        objMember.EmailFrequency_ECL = "Direct"
    elif strDeliveryMode == "Direct":
        objMember.NoMail = False
        objMember.EmailDigestMode = "StructuredDigest"
        objMember.EmailFrequency_ECL = "Direct"
    else:
        objMember.NoMail = False
        objMember.EmailDigestMode = strDeliveryMode
        objMember.EmailFrequency_ECL = "Daily"

    objMember.EmailDeliveryAddress = strEmailAddress
    objMember.ContactEmailAddress = strEmailAddress

    Catalogue(objMember)
    strEncryptedPassword = DoEncrypt(strPassword)
    SetLogInCookies(objResponse, strUsername, strEncryptedPassword)
    return (strUsername, GetPageTemplate(objHere, 'WelcomeScreen'), "Welcome")
