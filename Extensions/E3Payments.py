# encoding: utf-8

import datetime

from libDatabase import GetDataFolder
from libDatabase import SearchOne
from libDatabase import GetDOD
from libConstants import cnShortDateFormat
from libConstants import cnECLRoot
from libConstants import cnUKAmount
from E3Members import GetCurrentMember
from libEmail import SendEmail
import datetime
from libDatabase import Catalogue
from E3Events import RecordEventRegistration
from libGeneral import GetParameter
from libGeneral import GetNextCartId
from E3Events import ConferencePreferencesPage
from E3Events import GetWelcomeBlock
from E3Events import SendConfStatistics
from E3Events import SendConf08Receipt
from E3Events import AddToRegistrationHistory
from E3Events import GetBookedFor
from E3Events import SendBookingEmails
from libConstants import cnConf08FullPaymentDate
from libConstants import cnGeneralReceipt
from libDatabase import NextInvoiceNumber
from libGeneral import AffiliateSalesTracking

def ThisMonthsPayments(objHere):
    dtmNow = datetime.datetime.today()
    intYear = dtmNow.year
    intMonth = dtmNow.month
    strResult = ""
    for objBatch in GetDataFolder(objHere, "E3Member").objectValues('Folder'):
        for objMember in objBatch.objectValues("E3Member"):
            for objPayment in objMember.Historic.objectValues("E3Payment"):
                dtmDate = objPayment.GetDate()
                if dtmDate.year == intYear and dtmDate.month == intMonth:
                    strResult += "<p>%s: %s</p>\n" % (dtmDate, objMember.Username)
    return strResult

def StartPayment(objHere):
    # Get the next cardId and any other details that we can pass on to WorldPay
    # Record start of payment session
    # Show forwarding page (this page should automatically go through to WorldPay, click here if not)

    # Note: must be logged in, otherwise ask to log in first
    # But if not logged in can't call the form

    intCartId = GetNextCartId(objHere)
    objMember = GetCurrentMember(objHere)
    strEmailAddress = objMember.PreferredEmailAddress()
    objMember.RecordPaymentStart(intCartId)

    # Was: action="/test/WorldPay"

    strResult = """
    <form action="https://secure.wp3.rbsworldpay.com/wcc/dispatcher" name="PaymentForm" method="post">
        <fieldset>
            <legend>Online payment</legend>
            <p>You should be automatically forwarded to the secure online payment system within a few seconds. However, if nothing happens, please click on the button below</p>
            <input type="hidden" name="instId" value="69595">
            <input type="hidden" name="cartId" value="%s">
            <input type="hidden" name="amount" value="30">
            <input type="hidden" name="currency" value="GBP">
            <input type="hidden" name="desc" value="Euro Coach List Membership, 1 year">
            <input type="hidden" name="testMode" value="0">
            <input type="hidden" name="email" value="%s">
            <p><input type="submit" name="Submit" value="Continue to the payment system" class="btn"></p>
        </fieldset>
    </form>
    """ % (intCartId, strEmailAddress)
    return strResult

def PaymentTestPage(objHere, objRequest):
    objForm = objRequest.form
    strResult = """<form action="/MyECL/FinishPayment" method="post">
    <fieldset>
        <legend>WorldPay details</legend>
"""
    for strField in objForm.keys():
        strResult = strResult + """<p>%s <input type="text" name="%s" value="%s"></p>\n""" % (strField, strField, objForm[strField])
    strResult = strResult + """
        <p>Email address <input type="text" name="email" value="coen@coachcoen.com"></p>
        <p>transStatus (Y/C) <input type="text" name="transStatus" value="Y"></p>
        <p>testMode <input type="text" name="testMode" value="0"></p>
        <p>transId <input type="text" name="transId" value="1"></p>
        <p>cartId <input type="text" name="cartId" value="1"></p>
        <p>amount <input type="text" name="amount" value="20"></p>
        <p>authAmount <input type="text" name="authAmount" value="20"></p>
        <p>currency <input type="text" name="currency" value="GPB"></p>
        <p>authCurrency <input type="text" name="authCurrency" value="GBP"></p>
        <p>name <input type="text" name="name" value="Joe Bloggs"></p>
        <p><input type="submit" name="Submit" value="Continue"></p>
    </legend>
        </form>"""
    return strResult

def SavePaymentDetails(objWorldPayCall, objForm):
    dodWorldPayResult = GetDOD(objWorldPayCall, 'E3WorldPayResult')
    for strField in objForm.keys():
        objField = dodWorldPayResult.NewObject(objWorldPayCall)
        objField.title = "%s: %s" % (strField, objForm[strField])
        objField.AttributeName = strField
        objField.AttributeValue = objForm[strField]

def CheckPaymentForm(objForm):
    lstMissing = []
    for strField in ('cartId', 'amount', 'currency', 'testMode', 'email', 'transId', 'transStatus', 'authAmount', 'authCurrency', 'name'):
        if not objForm.has_key(strField):
            lstMissing.append(strField)
        elif not objForm[strField]:
            lstMissing.append(strField)
    if lstMissing:
        return (0, "Missing field(s): %s" % ", ".join(lstMissing))

    try:
       fltAmount = float(objForm['amount'])
    except:
        return (0, "Incorrect amount: %s" % objForm['amount'])

    if not fltAmount:
        return (0, "Amount is 0")

    try:
        intTestMode = int(objForm['testMode'])
    except:
        return (0, "Incorrect test mode: %s" % objForm['testMode'])

    if not intTestMode in [0, 100, 101, 102]:
        return (0, "Incorrect test mode: %s" % intTestMode)

    if not objForm['transStatus'] in ['C', 'Y']:
        return (0, "Incorrect transStatus: %s" % objForm['transStatus'])

    return (1, "correct")

def SendErrorEmail(objHere, strErrorMessage):
    SendEmail(objHere, strErrorMessage, "ECL Error message", "coen@coachcoen.com")

def FinishE3Conf08Booking(objWorldPayCall, strCurrency, fltAmount, strPaymentType, strWPContents):
    strConfBookingId = objWorldPayCall.PaymentType
    objConfBooking = SearchOne(objWorldPayCall, "E3Conf08Booking", "id", strConfBookingId)
    dtmNow = datetime.datetime.today()
    intAmount = objWorldPayCall.Amount
    AddToRegistrationHistory(objConfBooking, "Online payment of GBP%s" % intAmount)
    objConfBooking.PaidAmount += intAmount
    objConfBooking.RemainingAmount -= intAmount
    if objConfBooking.RemainingAmount:
        AddToRegistrationHistory(objConfBooking, "Total payment(s): GBP%s, remaining: GBP%s" % (objConfBooking.PaidAmount, objConfBooking.RemainingAmount))
    else:
        AddToRegistrationHistory(objConfBooking, "Total payment(s): GBP%s, fully paid" % objConfBooking.PaidAmount)

    strResult = GetWelcomeBlock(objConfBooking.InProgressForCC, objConfBooking.InProgressForSatEve, objConfBooking.InProgressForSunAm, objConfBooking, False)

    if objConfBooking.RemainingAmount:
        strExtraPaymentLine = "<p>The remaining amount of &pound;%s must be paid by Wednesday 10th September</p>" % objConfBooking.RemainingAmount
    else:
        strExtraPaymentLine = ""
    strResult += """
<fieldset>
    <legend>Thanks for your payment</legend>
    <p>Thanks for your payment of %s%s for the conference. A receipt has been emailed to %s</p>
%s
%s
</fieldset>""" % (strCurrency, fltAmount, objConfBooking.EmailAddress, strExtraPaymentLine, strWPContents)

    objConfBooking.InvoiceNumber = NextInvoiceNumber(objWorldPayCall)
    blnFullAmount = (objConfBooking.RemainingAmount == 0)
    SendConf08Receipt(objWorldPayCall, objConfBooking.EmailAddress, objConfBooking.Name, objConfBooking.InvoiceNumber, intAmount, blnFullAmount, objConfBooking.RemainingAmount)
    SendBookingEmails(objWorldPayCall, objConfBooking, "Online", objConfBooking.InProgressForCC, objConfBooking.InProgressForSatEve, objConfBooking.InProgressForSunAm, intAmount)
    return strResult

def FinishPayment(objHere, objRequest):
    strWPContents = """<p>&nbsp;</p>
<p>Here is the response from WorldPay:</p>
<WPDISPLAY ITEM=banner>
"""
    strErrorPage = """<h2>Payment problem</h2>
<p>There was a problem processing your payment</p>
<p>The site owner will contact you at %s to find out what happened, to help him solve the problem</p>""" + strWPContents

    strErrorPageNoDetails = """<h2>Payment problem</h2>
<p>There was a problem processing your payment</p>
<p>Please go to <a href="/ContactDetails">the contact page</a> to contact the list owner with a brief description of what happened, to help him solve the problem for you. Go to the contact page</p>""" + strWPContents

    strCancellationPage = """<h2>Payment cancelled</h2>
<p>It seems that you have cancelled your payment</p>
<p>If you have any questions please <a href="/ContactDetails">contact the list owner</a></p>""" + strWPContents

    objForm = objRequest.form
    try:
        intCartId = int(objForm['cartId'])
        strEmailAddress = objForm['email']
    except:
        SendErrorEmail(objHere, "WorldPayCall problem, no contact details")
        return strErrorPageNoDetails

    objWorldPayCall = SearchOne(objHere, 'E3WorldPayCall', 'CartId', intCartId)
    if not objWorldPayCall:
        SendErrorEmail(objHere, "Can't find WorldPayCall, for cartId = %s, email address = %s" % (intCartId, strEmailAddress))
        return strErrorPage % strEmailAddress

    if objWorldPayCall.Status == "Success":
        SendErrorEmail(objHere, "WorldPayCall processed twice, for cartId = %s, email address = %s" % (intCartId, strEmailAddress))
        return strErrorPage % strEmailAddress

    SavePaymentDetails(objWorldPayCall, objForm)
    (blnCorrect, strErrorMessage) = CheckPaymentForm(objForm)
    if blnCorrect:
        if objForm['transStatus'] == 'C':
            objWorldPayCall.Status = 'Cancelled'
            return strCancellationPage

        objWorldPayCall.Status = 'Success'
        strCurrency = objForm['authCurrency']
        strAmount = objForm['authAmount']
        fltAmount = float(strAmount)
        strEmailAddress = objForm['email']
        strName = objForm['name']
        try:
            strPaymentType = objWorldPayCall.PaymentType
        except:
            strPaymentType = "ECL"
        if strPaymentType == "ECL":
            return FinishECLPayment(objWorldPayCall, strCurrency, fltAmount, strEmailAddress) + strWPContents
        elif strPaymentType[:3] == "CBA":
            return FinishCBAPayment(objWorldPayCall, strCurrency, fltAmount, strEmailAddress, strName, strPaymentType) + strWPContents
        elif strPaymentType[:15] == "E3Conf08Booking":
            return FinishE3Conf08Booking(objWorldPayCall, strCurrency, fltAmount, strPaymentType, strWPContents)
        else:
            objWorldPayCall.Status = "Failed"
            SendErrorEmail(objHere, "Payment processing, unknown payment type: %s, %s" % (strPaymentType, objWorldPayCall.id))
            return strErrorPage % strEmailAddress
    else:
        objWorldPayCall.Status = 'Failed'
        SendErrorEmail(objHere, strErrorMessage + ", for cartId = %s, email address = %s" % (intCartId, strEmailAddress))
        return strErrorPage % (strEmailAddress)

def FinishCBAPayment(objWorldPayCall, strCurrency, fltAmount, strEmailAddress, strName, strPaymentType):
    # Split into components: [CBA][Number][Version]
#    strNumber = strPaymentType[3:4]
#    strVersion = strPaymentType[5]
#    strDetails = strPayment[6:]
    # Options:
    # CBA01S (£25)
    # CBA01G (£157)
    # CBA01GEarlyBird (£132)
    # CBA01SFromGQ (Book bonus - free, so no payment entry created)
    # CBA01GFromGQ (£132)
    return RecordEventRegistration(objWorldPayCall, strPaymentType[:5], strPaymentType[5], strEmailAddress, strName, objWorldPayCall.id, strPaymentType, objWorldPayCall.RegistrationToUpgrade)


def FinishECLPayment(objWorldPayCall, strCurrency, fltAmount, strEmailAddress):
    strSuccessPage = """<h2>Thanks for your payment</h2>
<p>Your payment has been successfully processed. Your membership now runs until %s</p>
<p>A receipt has been emailed to %s</p>
%s"""

    strWarning = ""

    objMember = objWorldPayCall.unrestrictedTraverse('../..')
    objMember.NewPayment(datetime.date.today(), 12, 'WorldPay', strCurrency, fltAmount, "n/a", True, strEmailAddress)
    strResult = strSuccessPage % (objMember.GetNextExpiryDate().strftime(cnShortDateFormat), strEmailAddress, strWarning)
    strResult += AffiliateSalesTracking("ECL-M02", objMember.id, cnUKAmount)

    return strResult

def FinishCBAPayment(objWorldPayCall, strCurrency, fltAmount, strEmailAddress, strName, strPaymentType):
    # Split into components: [CBA][Number][Version]
#    strNumber = strPaymentType[3:4]
#    strVersion = strPaymentType[5]
#    strDetails = strPayment[6:]
    # Options:
    # CBA01S (£25)
    # CBA01G (£157)
    # CBA01GEarlyBird (£132)
    # CBA01SFromGQ (Book bonus - free, so no payment entry created)
    # CBA01GFromGQ (£132)
    return RecordEventRegistration(objWorldPayCall, strPaymentType[:5], strPaymentType[5], strEmailAddress, strName, objWorldPayCall.id, strPaymentType, objWorldPayCall.RegistrationToUpgrade)

def StartCBA01GQUpgradePayment(objHere):
    # Get registration id
    strRegistrationId = GetParameter(objHere.REQUEST, "id")
    # If no id or id not found, store "NotFound" as registration id
    # Then when payment comes back, see if we can find the email address entered during
    # the payment process. If so, upgrade that one
    # If still not found, send me an email and I'll need to sort it out
    if strRegistrationId:
        objRegistration = SearchOne(objHere, "E3EventRegistration", "id", strRegistrationId)
        if objRegistration and objRegistration.RegistrationType[5] == "G":
            return """<p>As far as the system can tell, you have already paid for the Gold e-Workshop. No need to pay again</p>
<p>If you have not yet upgraded to the Gold e-Workshop, please contact the list owner. For contact details see the <a href="http://www.eurocoachlist.com/ContactDetails">Contact Details page</a></p>"""
    else:
        strRegistrationId = "NotFound"

    return StartPublicPayment(objHere, 116, "Coaching Business Accelerator Gold e-Workshop Upgrade", "CBA01GUpgrade", "", strRegistrationId)

def StartPublicPayment(objHere, intAmount, strDescription, strPaymentType, strEmailAddress = "", strRegistrationToUpgrade = ""):
    # For payments by non members, such as for a workshop
    intCartId = GetNextCartId(objHere)
    objPayments = objHere.unrestrictedTraverse("/Data/Public/Payments")
    dodWorldPayCall = GetDOD(objHere, "E3WorldPayCall")
    objWorldPayCall = dodWorldPayCall.NewObject(objPayments)
    objWorldPayCall.SetDateCalled(datetime.date.today())
    objWorldPayCall.CartId = intCartId
    objWorldPayCall.Status = "Called"
    objWorldPayCall.PaymentType = strPaymentType
    objWorldPayCall.Amount = intAmount
    objWorldPayCall.RegistrationToUpgrade = strRegistrationToUpgrade
    Catalogue(objWorldPayCall)
    strResult = """
    <form action="https://secure.wp3.rbsworldpay.com/wcc/dispatcher" name="PaymentForm" method="post">
        <fieldset>
            <legend>Online payment</legend>
            <p>You should be automatically forwarded to the secure online payment system within a few seconds. However, if nothing happens, please click on the button below</p>
            <input type="hidden" name="instId" value="69595">
            <input type="hidden" name="cartId" value="%s">
            <input type="hidden" name="amount" value="%s">
            <input type="hidden" name="currency" value="GBP">
            <input type="hidden" name="desc" value="%s">
            <input type="hidden" name="testMode" value="0">
            <input type="hidden" name="email" value="%s">
            <p><input type="submit" name="Submit" value="Continue to the payment system" class="btn"></p>
        </fieldset>
    </form>
    """ % (intCartId, intAmount, strDescription, strEmailAddress)
    return strResult


