# encoding: utf-8

import datetime
from E3Members import GetCurrentMember, UsernameInUse
from libConstants import cnFullDateFormat
from libConstants import cnShortDateFormat
from libConstants import cnAnnualAmount
from libConstants import cnUKAmount
from libConstants import cnEuroAmount
from libConstants import cnUSAmount
from libConstants import cnEuroBankCosts
from libGeneral import GetParameter
from libDatabase import GetDataFolder
from E3Members import ManagerLoggedIn
from E3Members import GetMemberForId
from libBuildHTML import PutInARow
from libBuildHTML import PutInFieldset
from libBuildHTML import IsPlural
from E3HTML import FullURL
from E3Offerings import SortOnTitle
from E3Offerings import FormatOneOffering
from E3Offerings import GetOrganisationsTab
from E3Offerings import GetEventsTab
from E3Offerings import GetEventSeriesTab
from libForms import LoadDataFromObject, GetDataFromForm
from libForms import UpdateObjectFromData, CreateForm, FormProcessing
from libForms import Fieldset, Tabset, OneTab, Paragraph
from libForms import TextControl, HiddenControl, TextArea
from libForms import SubmitControl, SelectControl, PureText
from libForms import RadioButtonControl, CheckboxControl
from libForms import PasswordControl
from libForms import CheckRequiredFields, ReportErrors
from E3TempData import SetMessage
from libDatabase import SearchOne
from libDatabase import GetDOD
from libEmail import SendEmail
from E3Membership import SaveLoginDetails
from E3Membership import ValidLoginDetails

def PutInTab(strTab, strContents, blnNeedsFieldset = True, strMainTitle = "", blnDefaultTab = False):
    if blnNeedsFieldset:
        if strMainTitle:
            strTitle = strMainTitle + " - " + strTab
        else:
            strTitle = strTab
        strContents = """
    <fieldset>
        <legend>%(Title)s</legend>
        %(Contents)s
    </fieldset>
""" % {'Title': strTitle,
            'Contents': strContents}

    if blnDefaultTab:
        strDefaultTab = " tabbertabdefault"
    else:
        strDefaultTab = ""
    strResult = """
<div class="tabbertab %(Default)s" title="%(Tab)s">
    %(Contents)s
</div>""" % {'Tab': strTab,
            'Default': strDefaultTab,
            'Contents': strContents}
    return strResult

def NoneMemberTemplate():
    """Returns main /MyECL template"""
    strResult = """<form method="post" action=".">
					<fieldset>
						<legend>Personal Details</legend>
						<p><label>Name</label>
                            <input type="hidden" name="MemberId" value="%(MemberId)s"/>
							<input type="text" name="Name" class="txt" value="%(MemberName)s"/>
						</p>
                	  	<p><label>Username</label>
							<input type="text" name="Username" class="txt" value="%(Username)s"/><input name="Action" value="UpdatePersonalDetails" type="hidden">
						</p>
						<p>
							<input type="submit" name="btnSubmit" id="btnSubmit" value="Update Personal Details" class="btn" />
						</p>
					</fieldset>
                </form>

                <form method="post" action=".">
					<fieldset>
		                <legend>Password</legend>
						<p><label>Old Password</label>
                            <input type="hidden" name="MemberId" value="%(MemberId)s"/>
							<input type="%(ShowPasswordField)s" name="OldPassword" class="txt" value="%(OldPassword)s"/>
						</p>
                	  	<p><label>New Password</label>
							<input type="%(ShowPasswordField)s" name="NewPassword" class="txt"/>
						</p>
        	          	<p><label>Confirm New Password</label>
							<input type="%(ShowPasswordField)s" name="ConfirmPassword" class="txt"/><input name="Action" value="UpdatePassword" type="hidden">
						</p>
						<p>
							<input type="submit" name="btnSubmit" id="btnSubmit" value="Update password" class="btn" />
						</p>
					</fieldset>
                </form>

                <form id="form1" name="form1" method="post" action="PayOnline.html">
					<fieldset>
		                <legend>Membership</legend>
                        %(MembershipDetails)s
                        %(PaymentLinks)s
                        %(PreviousPayments)s

					</fieldset>
                    %(HowToPay)s
                </form>
"""

    return strResult

def OnePaymentRow(objPayment, strMemberId):
    strResult = "<tr>\n"
    intInvoiceNumber = objPayment.InvoiceNumber
    strActionButtons = """<input type="submit" name="Update" value="Delete"><input type="submit" name="Update" value="Resend Invoice"></td>"""
    strResult = PutInARow((objPayment.GetDate().strftime(cnShortDateFormat), \
                objPayment.Months, \
                objPayment.BonusDays, \
                objPayment.PaymentType, \
                "%s %s" % (objPayment.Currency, objPayment.Amount), \
                objPayment.EmailAddress, \
                objPayment.Comments, \
                intInvoiceNumber, \
                "&nbsp;", \
                strActionButtons))
    strResult = """<form name="form" method="post" action=".">
        <input type="hidden" name="MemberId" value="%s">
        <input type="hidden" name="PaymentId" value="%s">
        <input type="hidden" name="Action" value="PaymentAction">
        %s
    </form>""" % (strMemberId, objPayment.id, strResult)
    return strResult

def NewPaymentRow(strMemberId, strEmailAddress):
    strDate = datetime.date.today().strftime(cnShortDateFormat)
    return """<tr>
    <form name="form" method="post" action=".">
        <input type="hidden" name="MemberId" value="%s">
        <input type="hidden" name="Action" value="NewPayment">
        <td><input type="text" name="PaymentDate" value="%s" size="10"></td>
        <td><input type="text" name="Duration" value="12" size="4"></td>
        <td>&nbsp;</td>
        <td><select name="PaymentType">
            <option>Cheque
            <option>Bank
            <option>Cash
            <option>2Checkout
            <option>WorldPay
            <option>PayPal
        </select></td>
        <td><input type="text" name="Amount" value="GBP 30.00" size="10"></td>
        <td><input type="text" name="EmailAddress" value="%s" size="10"></td>
        <td><input type="text" name="Identifier" value="00000000"></td>
        <td>&nbsp;</td>
        <td><input type="checkbox" name="SendReceipt" checked value="yes"></td>
        <td><input type="submit" name="Update" value="Add"></td>
    </form>
</tr>""" % (strMemberId, strDate, strEmailAddress)

def PaymentTable(objMember):
    strResult = """<table border = "1" cellpadding="5" cellspacing = "0">
    <tr>
        <td>Date</td>
        <td>Duration</td>
        <td>Bonus days</td>
        <td>Method</td>
        <td>Amount</td>
        <td>Email Address</td>
        <td>Identifier</td>
        <td>Invoice number</td>
        <td>Receipt</td>
        <td>Action</td>
    </tr>
"""
    dictPayments = {}
    for objPayment in objMember.Historic.objectValues('E3Payment'):
        dtmDate = objPayment.GetDate()
        if not dictPayments.has_key(dtmDate):
            dictPayments[dtmDate] = []
        dictPayments[dtmDate].append(objPayment)
    lstDates = dictPayments.keys()
    lstDates.sort()
    strEmailAddress = ""
    for dtmDate in lstDates:
        for objPayment in dictPayments[dtmDate]:
            strResult += OnePaymentRow(objPayment, objMember.id)
            if objPayment.EmailAddress:
                strEmailAddress = objPayment.EmailAddress
    if not strEmailAddress:
        strEmailAddress = objMember.EmailDeliveryAddress
    strResult += NewPaymentRow(objMember.id, strEmailAddress)
    strResult += "</table>"
    return strResult

def GetMembershipDetails(objMember):
    """Returns text which describes current membership status
        - You are a lifetime member
        - Your membership has expired
        - Your membership will exire <date>
        - Your trial membership will exire <date>"""
#Your (paid) membership will expire in .. days/weeks (by date)
#Membership is (amount) per year. Go to the secure online payment page
    if objMember.LifetimeMember:
        return 'You are a lifetime member'
    elif objMember.MembershipType == 'None':
        return 'Your membership has expired'

    dtmExpiryDate = objMember.GetNextExpiryDate()
    strExpiryDate = dtmExpiryDate.strftime(cnFullDateFormat)

    if objMember.OnHold:
        return 'Your expiry date is %s. However, the list owner has made sure that the expiry is being postponed. This may be because you recently made a payment by bank transfer and informed the list owner. In that case your list membership will remain active and you will receive a receipt once your payment has been received and processed' % strExpiryDate
    elif objMember.HasPayments:
        return 'Your membership is due to expire on %s' % strExpiryDate
    else:
        return 'Your trial membership will expire %s' % objMember.GetNextExpiryDate().strftime(cnFullDateFormat)

def GetHowToPay():
#     <script language="JavaScript" src="http://www.worldpay.com/cgenerator/cgenerator.php?instId=69595"></script>
#    <script language="JavaScript" src="https://select.worldpay.com/wcc/logo?instId=69595"></script>
#    <a href="http://www.WorldPay.com" target="_blank"><img src="/images/WorldPayLogos.gif" width="425" height = "87" border="0"></a>
    return """
<fieldset>
    <legend>Online payment</p>
    <form action="/MyECL/StartPayment">
        <p>Click on the "Pay online now" button to go to the secure payment page</p>
        <p><input type="Submit" value="Pay online now" ></p>
    </form>
</fieldset>

<fieldset>
    <legend>PayPal Payment</legend>
        <p>To pay using PayPal please send your payment for &pound;%(UKAmount)s to <a href="mailto:coen@coachcoen.com">coen@coachcoen.com</a></p>
</fieldset>
<fieldset>
    <legend>Bank or Cheque Payment</legend>
    <p>To pay by UK cheque or Dutch bank transfer:
        <ul>
            <li>By <b>UK cheque:</b> Post a cheque for &pound;%(UKAmount)s, payable to
                &quot;Compass Mentis&quot; to: Coen de Groot, 56 Fairfield Road,
                Bristol, BS6 5JP. Please include a note with your name and email
                address. You will receive a receipt via email within a week from
                me receiving your cheque
            </li>
            <li>By <b>&euro; cheque</b>: Post a cheque for &euro;%(EuroAmountPlusCosts)s, payable
                to &quot;Compass Mentis&quot; to: Coen de Groot, 56 Fairfield
                Road, Bristol, BS6 5JP. Please include a note with your name and
                email address. You will receive a receipt via email within a week
                from me receiving your cheque
            </li>
            <li>By <b>Dutch bank transfer:</b> Transfer &euro;%(EuroAmount)s to C.J.M. de
                Groot, Bristol, Engeland, 82.30.33.244, description: ECL
                and your email address. Please also send me an email address to
                let me know that you have paid. You will receive a receipt via
                email within a week from me receiving confirmation from my Dutch
                bank (this may take a month)
            </li>
            <li>By <b>UK bank transfer</b>: Transfer &pound;%(UKAmount)s to &quot;Compass
                Mentis&quot;, The Royal Bank of Scotland, Ayr Chief Office, sort
                code 83-15-26, account number 00683788. Add your email address as a reference. Please also
                <a href="/ContactDetails">contact me</a> to let me know that you have paid.
                You will receive
                a receipt via email within a week from the transfer showing up
                on my bank account</li>
        </ul>
    <p>And if none of these methods work for you <a href="/ContactDetails">contact me</a></p>
</fieldset>
<fieldset>
    <legend>Refund Policy</legend>
    <p>All new members start with a 3 months free trial period. Most members
        pay towards the end of the trial period, whilst some members pay
        at the start of the trial period</p>
    <p>Regardless of when or how you pay, you have 14 days to change your
        mind. All you need to do to claim a refund is to <a href="/ContactDetails">contact me</a> with your refund request. </p>
    <p>If possible I would appreciate it if you gave me the reason for
        requesting a refund, but this is not at all required</p>
    <p>After I receive your request I will refund you the full amount
        within 14 days</p>
</fieldset>

<fieldset>
    <p>Online payments are processed securely by RBS WorldPay (tm)</p>
    <script language="JavaScript" src="https://select.wp3.rbsworldpay.com/wcc/logo?instId=69595"></script>
</fieldset>

""" % {'UKAmount': cnUKAmount,
                    'EuroAmountPlusCosts': cnEuroAmount + cnEuroBankCosts,
                    'EuroAmount': cnEuroAmount,
                    'USAmount': cnUSAmount}

def GetOnePayment(objPayment):
    if objPayment.Amount == 0 and objPayment.Currency == 'Unknown':
        strAmount = 'and amount not recorded'
    else:
        try:
            strCurrency = {'GBP':'£', 'USD':'$', 'EUR':'€'}[objPayment.Currency]
        except:
            strCurrency = objPayment.Currency
        strAmount = "%s%0.2f" % (strCurrency, objPayment.Amount)
    strPaymentType = objPayment.PaymentType
    if strPaymentType == 'Unknown':
        strPaymentType = 'Payment type'
    return """
<tr>
    <td>%(PaymentDate)s</td>
    <td>%(PaymentType)s</td>
    <td>%(Amount)s</td>
</tr>""" % {'PaymentDate': objPayment.GetDate().strftime(cnShortDateFormat),
            'PaymentType': strPaymentType,
            'Amount': strAmount}

def GetPreviousPayments(objMember):
    objPayments = objMember.objectValues('E3Payment')
    if not objPayments:
        return ''
    strResult = """<p>Your payments</p>
        <table>"""
    for objPayment in objPayments:
        strResult = strResult + GetOnePayment(objPayment)
    strResult = strResult + "</table>"
    strResult = "Previous payments here please"
    return strResult

def AddToDateList(dictList, dtmDate, varToAdd):
    if not dictList.has_key(dtmDate):
        dictList[dtmDate] = []
    dictList[dtmDate].append(varToAdd)
    return dictList

def ListEvents(objMember):
    dictEvents = {}
    for objPayment in objMember.Historic.objectValues('E3Payment'):
        dictEvents = AddToDateList(dictEvents, objPayment.GetDate(), ('Payment', '%s months, %s bonus days' % (objPayment.Months, objPayment.BonusDays)))

    for objEvent in objMember.Historic.objectValues('E3Event'):
        dictEvents = AddToDateList(dictEvents, objEvent.GetDate(), (objEvent.EventType, '%s days' % objEvent.Days))

    lstDates = dictEvents.keys()
    lstDates.sort()

    strResult = "<ul>\n"
    for dtmDate in lstDates:
        for (strEvent, strDescription) in dictEvents[dtmDate]:
            if strDescription:
                strEvent = strEvent + " (%s)" % strDescription
            strResult += "<li>%s - %s\n" % (dtmDate.strftime(cnShortDateFormat), strEvent)
    strResult += "</ul>\n"
    strResult += "<p>Latest expiry: %s</p>\n" % objMember.GetLatestEvent('Expiry')
    return strResult

def ListPeriods(objMember):
    dictPeriods = {}
    try:
        for objPeriod in objMember.FromMailman.objectValues('E3Period'):
            dictPeriods[objPeriod.GetStartDate()] = objPeriod
    except:
        return "No periods imported from Mailman"
    lstDates = dictPeriods.keys()
    lstDates.sort()

    strResult = "<ul>\n"
    for dtmDate in lstDates:
        objPeriod = dictPeriods[dtmDate]
        strResult += "<li>%s - %s: %s</li>\n" % (objPeriod.GetStartDate().strftime(cnShortDateFormat), objPeriod.GetEndDate().strftime(cnShortDateFormat), objPeriod.PeriodType)
    strResult += "</ul>\n"
    return strResult

def ManagersIntro(objMember):
    if objMember.OnHold:
        strOnHold = "<p>On hold</p>"
        strButtonText = "Remove from hold"
    else:
        strOnHold = ""
        strButtonText = "Put on hold"

    strContents = CollapsibleForm("Manager Page", ".",
        """<p>Id: %(MemberId)s<p>
            %(OnHold)s
	      	<p><input type="submit" name="btnSubmit" id="btnSubmit" value="%(ButtonText)s" class="btn" /></p>
            <input type="hidden" name="MemberId" value="%(MemberId)s"/>
            <input name="Action" value="ToggleOnHold" type="hidden">
"""% {'MemberId': objMember.id,
            'OnHold': strOnHold,
            'ButtonText': strButtonText})

    return strContents

def GetDeliveryDetails(objMember):
    for objEmailAddress in objMember.objectValues('E3EmailAddress'):
        for objListMembership in objEmailAddress.objectValues('E3ListMembership'):
            if objListMembership.GetDeliveryMode() <> 'NoMail':
                return (objEmailAddress.EmailAddress, objListMembership.GetDeliveryMode())
    return ("", "")

def GetUnconfirmedBox(dictEmailAddresses, blnConfirmationRequestResent):
    lstUnconfirmed = []
    for strEmailAddress in dictEmailAddresses.keys():
        (strAddressId, blnDeliveryAddress, blnConfirmed, blnBouncing) = dictEmailAddresses[strEmailAddress]
        if not blnConfirmed:
            lstUnconfirmed.append(strEmailAddress)

    if not lstUnconfirmed:
        return ""

    if blnConfirmationRequestResent:
        strResult = """<p class="InfoMessage">Confirmation request(s) re-sent to %s</p>"""
    else:
        strResult = """
    <p class="GeneralError">The following email address(es) are unconfirmed: %s. You cannot receive list messages at these address(es) nor send messages from them</p>
<form action="." method="post">
    <p><input type="submit" name="SubmitButton" value="Send confirmation request(s)" class="btn"></p>
</form>"""
    strResult = strResult % ", ".join(lstUnconfirmed)

    strResult = PutInFieldset("Unconfirmed Email Address(es)", strResult)

    return strResult

def GetBouncingBox(dictEmailAddresses):
    lstBouncing = []
    for strEmailAddress in dictEmailAddresses.keys():
        (strAddressId, blnDeliveryAddress, blnConfirmed, blnBouncing) = dictEmailAddresses[strEmailAddress]
        if blnBouncing:
            lstBouncing.append(strEmailAddress)

    if not lstBouncing:
        return ""

    if len(lstBouncing) > 1:
        strPlural = "es"
        strThese = "these"
    else:
        strPlural = ""
        strThese = "this"

    strResult = """
<form action="." method="post">
    <p class="GeneralError">Too many list message to the following email address%s have been bounced back: %s. </p>
    <p>This may be because you have a problem with %s address%s. You will not be able to receive list messages at %s address%s until this is sorted. Click on the button below to resume sending emails<p>
    <p><input type="submit" name="SubmitButton" class="btn" value="Resume email address%s"></p>
</form>
""" % (strPlural, ", ".join(lstBouncing), strThese, strPlural, strThese, strPlural, strPlural)

    strResult = PutInFieldset("Bouncing Email Address(es)", strResult)

    return strResult

def EmailStatusSummary(dictSummary):
    if dictSummary.has_key('Unconfirmed'):
        lstUnconfirmed = dictSummary['Unconfirmed']
        if len(lstUnconfirmed) > 1:
            strPlural = "es"
            strThese = "these"
            strHave = "have"
        else:
            strPlural = ""
            strThese = "this"
            strHave = "has"
        strUnconfirmed = """<p><label>Warning</label><div class="WarningColumn">The following email address%s %s not yet been confirmed: %s</div><div class="FormColumn">You will not be able to send list messages from or receive list messages at %s address%s. See the "Email" tab for more details</div></p>""" % (strPlural, strHave, ", ".join(lstUnconfirmed), strThese, strPlural)
    else:
        strUnconfirmed = ""

    if dictSummary.has_key('Bouncing'):
        strBouncing = GetBouncingBox(dictSummary["Bouncing"])
    else:
        strBouncing = ""

    strEmailAddressSummary = ""
    lstAddresses = []
    intReceivingCount = 0
    for strMode in ("Direct", "TextDigest", "MIMEDigest", "StructuredDigest", "TopicsList"):
        if dictSummary.has_key(strMode):
            intReceivingCount += len(dictSummary[strMode])
            strAddresses = "(%s) %s" % ({"Direct": "direct delivery",
                                    "TextDigest": "text digest",
                                    "MIMEDigest": "MIME digest",
                                    "StructuredDigest": "structured digest",
                                    "TopicsList": "topics list"}[strMode],
                                    ", ".join(dictSummary[strMode]))
            lstAddresses.append(strAddresses)
    if lstAddresses:
        if intReceivingCount > 1:
            strPlural = "es"
        else:
            strPlural = ""
        strEmailAddressSummary += """<p><label>Email address%s</label><div class="FormColumn">You will receive list messages at the following address%s: %s</div></p>""" % (strPlural, strPlural, ", ".join(lstAddresses))

    if dictSummary.has_key("NoMail"):
        if len(dictSummary["NoMail"]) > 1:
            strPlural = "es"
            strThese = "these"
        else:
            strPlural = ""
            strThese = "this"
        strEmailAddressSummary += """<p><label>Posting only</label><div class="FormColumn">You can use the following email address%s for sending messages to the list: %s</div></p>""" % (strPlural, ", ".join(dictSummary["NoMail"]))

    if not lstAddresses and not dictSummary.has_key("NoMail"):
        strEmailAddressSummary += """<p><label>Warning</label><div class="WarningColumn">You have no confirmed email addresses. You do not currently receive list messages nor can you send messages to the list. See the "Email Addresses" block below to correct this</div></p>"""

    return (strUnconfirmed, strBouncing, strEmailAddressSummary)

#def SetDeliveryMode(dictFieldValues, strDeliveryMode):
#    for strDeliveryOption in ('TextDigest', 'MIMEDigest', 'Direct', 'NoMail', 'StructuredDigest', 'TopicsList'):
#        if strDeliveryMode == strDeliveryOption:
#            dictFieldValues[strDeliveryOption + 'Selected'] = 'checked'
#        else:
#            dictFieldValues[strDeliveryOption + 'Selected'] = ''
#    return dictFieldValues

def FreePeriodForm(strMemberId):
    return """
<form name="form" method="post" action=".">
    <p>
        <input type="hidden" name="MemberId" value="%s">
        <input type="hidden" name="Action" value="AddFreePeriod">
        Months: <input type="text" name="Months">
        <input type="submit" value="Add free months" class="btn">
    </p>
</form>
""" % (strMemberId)

def CancelledMessage(objMember):
    strResult = PutInFieldset("Cancelled membership",
"""<p>Your membership was cancelled %s. To resume your membership, click on the button below</p>
<form method="post" action=".">
    <input type= "hidden" value="ResumeMembership" name="Action">
    <input type = "submit" value = "Resume my membership" class="btn" name="SubAction">
</form>
""" % (objMember.GetCancellationDate().strftime(cnShortDateFormat)))
    return strResult

def ParkingMemberMessage(objMember):
    strResult = PutInFieldset("Posting address only",
"""<p>This is a temporary membership record, created to hold an email address which has been used to send email message(s) to the Euro CoachList. At the moment the list software does not know who this email address belongs to</p>
<p>To sort this out yourself:</p>
<ol>
    <li>Log out</li>
    <li>Log into MyECL with your other list membership. If you don't know which one this is, try requesting your password, using the email address at which you normally receive list messages. If that doesn't work, please <a href="/ContactDetails">contact the list owner</a></li>
    <li>Add this email address (%s) to your list membership. The system will automatically move the email address to your membership and remove this temporary list membership</li>
</ol>
<p>Alternatively, please <a href="/ContactDetails">contact the list owner</a>, asking him to combine your email addresses. Please tell him all your email addresses</p>""" % objMember.PreferredEmailAddress())
    return strResult

def MemberExpiredMessage(objMember):
    strMembershipDetails = GetMembershipDetails(objMember)
    strResult = GetMembershipTab(objMember, strMembershipDetails, True)
    return strResult

def GetSummaryTab(objMember, strMembershipDetails, dictEmailAddresses):

    if objMember.NoMail:
        strHolidayModeMessage = """<p><label>Warning</label><div class="WarningColumn">You are currently in holiday mode, which means that the system is not sending you list messages. To change this, select the "Message Delivery" sub tab (below) and click on "Resume sending emails"</div></p>"""
    else:
        strHolidayModeMessage = ""

# You can send from (any address which is confirmed)
# You will receive at (delivery address), once a day/directly, in MIME digest mode
# You have bouncing/unconfirmed addresses, see below
    strEmailAddressSummary = ""
    lstConfirmed = []
    blnHasBouncing = False
    blnHasUnconfirmed = False

    strDeliveryAddress = objMember.EmailDeliveryAddress
    strAdvertDeliveryStatus = ""

    for strEmailAddress in dictEmailAddresses.keys():
        (strAddressId, blnDeliveryAddress, blnConfirmed, blnBouncing) = dictEmailAddresses[strEmailAddress]
        if blnConfirmed:
            lstConfirmed.append(strEmailAddress)
        else:
            blnHasUnconfirmed = True
        if blnBouncing:
            blnHasBouncing = True

    if lstConfirmed:
        strSendFrom = "You can send messages from the following email address(es): %s" % (", ".join(lstConfirmed))
    else:
        strSendFrom = "You have no confirmed email addresses and cannot send messages to the list"
    if blnHasBouncing:
        if blnHasUnconfirmed:
            strEmailMessage = "unconfirmed and bouncing"
        else:
            strEmailMessage = "bouncing"
    elif blnHasUnconfirmed:
        strEmailMessage = "unconfirmed"
    else:
        strEmailMessage = ""

    if strEmailMessage:
        strEmailMessage = """<p><label>Warning</label><div class="WarningColumn">You have %s email addresses. See below for more details</div></p>\n""" % strEmailMessage

    (strAddressId, blnDeliveryAddress, blnConfirmed, blnBouncing) = dictEmailAddresses[strDeliveryAddress]
    if not blnConfirmed:
        strDeliveryStatus = "The delivery address (%s) is not yet confirmed, so you are not currently being sent any list messages. See below for more information" % strDeliveryAddress
    elif blnBouncing:
        strDeliveryStatus = "The delivery address (%s) seems to be bouncing messages back, so you are not currently being sent any list messages. See below for more information" % strDeliveryAddress
    else:
        strDeliveryStatus = "Messages are being sent to %s " % strDeliveryAddress
        if objMember.EmailFrequency_ECL == "Daily":
            strDeliveryStatus += " as a daily digest, in %s format" % \
            {'MIMEDigest': 'MIME',
            'TextDigest': 'text',
            'StructuredDigest': 'structured HTML',
            'TopicsList': 'topics list'}[objMember.EmailDigestMode]
        else:
            strDeliveryStatus += "directly as they come in"
        strAdvertDeliveryStatus = "Adverts are being sent to the same address "
        strAdvFreq = objMember.GetEmailFrequency("ECL", True)
        if strAdvFreq == "Daily":
            strAdvertDeliveryStatus += " as a daily digest, in %s format" % \
            {'MIMEDigest': 'MIME',
            'TextDigest': 'text',
            'StructuredDigest': 'structured HTML',
            'TopicsList': 'topics list'}[objMember.EmailDigestMode]
        else:
            strAdvertDeliveryStatus += "directly as they come in"

    strResult = """
<form action="." method="post">
    <p>
        <label>Membership</label>
        <div class="FormColumn">%(MembershipDetails)s</div>
    </p>
    %(HolidayModeMessage)s
    %(EmailMessage)s
    <p>
        <label>Sending messages</label>
        <div class="FormColumn">%(SendFrom)s</div>
    </p>
    <p>
        <label>Receiving messages</label>
        <div class="FormColumn">%(DeliveryStatus)s</div>
        <div class="FormColumn">%(AdvertDeliveryStatus)s</div>
    </p>
    <input type="submit" name="Action" value="Cancel my membership" class="btn">
</form>

""" % {'MemberName': objMember.Name,
    'Username': objMember.Username,
    'MembershipDetails': strMembershipDetails,
    'HolidayModeMessage': strHolidayModeMessage,
    'EmailMessage': strEmailMessage,
    'DeliveryStatus': strDeliveryStatus,
    'AdvertDeliveryStatus': strAdvertDeliveryStatus,
    'SendFrom': strSendFrom}

    strResult = PutInFieldset("Membership - Overview", strResult)

    return strResult

def ValidateLoginTab(dictData, objMember):
    dictErrors = CheckRequiredFields(dictData, ("Username", "Password", "ConfirmPassword", "OldPassword"))
    if dictErrors:
        return dictErrors

    if dictData["ConfirmPassword"] <> dictData["Password"]:
        dictErrors["ConfirmPassword"] = ("GeneralError", "Confirmation does not match the password")
        return dictErrors

    if dictData["OldPassword"] <> objMember.Password:
        dictErrors["OldPassword"] = ("GeneralError", "Incorrect old password")
        return dictErrors

    if UsernameInUse(objMember, dictData["Username"]):
        dictErrors["Username"] = ("GeneralError", "Username already in use")
        return dictErrors

    return dictErrors

def GetLoginTab(objMember, blnManagerLoggedIn, blnUpdate):

    if blnManagerLoggedIn:
        fnPwdControl = TextControl
        lstLoadFields = ('Username', "Password")
    else:
        fnPwdControl = PasswordControl
        lstLoadFields = ('Username')

    lstForm = (Fieldset("Login details", None,
        Paragraph(TextControl("User name", "Username")),
        Paragraph(PasswordControl("Old password", "OldPassword")),
        Paragraph(fnPwdControl("Password", "Password")),
        Paragraph(PasswordControl("Confirm Password", "PasswordConfirmation")),
        Paragraph(SubmitControl("Update login details"))),)

    if blnUpdate:
        lstFields = ("Username", "Password", "PasswordConfirmation", "OldPassword")
        dictData = GetDataFromForm(objMember, objMember.REQUEST.form, lstFields)
        dictErrors = ValidLoginDetails(objMember, dictData, True)

        if dictErrors:
            strMessage = ReportErrors(dictErrors)
            strForm = CreateForm(objMember, lstForm, dictData, dictErrors = dictErrors)
            return strMessage + strForm

        SaveLoginDetails(objMember, dictData)
        dictData = LoadDataFromObject(objMember, ("Username", ))
        strForm = CreateForm(objMember, lstForm, dictData)
        strMessage = """<p class="InfoMessage">Changes saved</p>\n"""
        return strMessage + strForm

    dictData = LoadDataFromObject(objMember, ("Username", ))
    strForm = CreateForm(objMember, lstForm, dictData)
    return strForm

def AddEmailAddress(objMember):
    strDeliveryAddress = GetParameter(objMember.REQUEST, "NewAddress")
    strNewAddressMode = GetParameter(objMember.REQUEST, "NewAddressMode")
    (objEmailAddress, strMessage) = objMember.AddEmailAddress(strDeliveryAddress)
    if objEmailAddress:
        if objEmailAddress.Confirmed:
            if strNewAddressMode == "Replace":
                objMember.ListMemberships.ECL.EmailAddress = strDeliveryAddress
        else:
            if strNewAddressMode == "Replace":
                objEmailAddress.ChangeToThisOne = True
            elif strNewAddressMode == "PostingOnly":
                objEmailAddress.ChangeToThisOne = False
            else:
                print "Unknown new address mode:", strNewAddressMode
    else:
        strMessage = "Warning: " + strMessage
    return strMessage

def CopyProperties(objOldObject, objNewObject):
    for (strId, valProperty) in objOldObject.propertyItems():
        if strId <> "id":
            objNewObject.manage_changeProperties({strId: valProperty})

def DeleteOneEmailAddress(objMember, strEmailAddressId):
    objEmailAddress = SearchOne(objMember, 'E3EmailAddress', 'id', strEmailAddressId)
    objEmailAddressCatalogue = GetDataFolder(objMember, "E3EmailAddress").Catalogue
    if not objEmailAddress:
        SetMessage(objMember, "Warning: Email address not found", "")
        return False
    if not objEmailAddress in objMember.objectValues('E3EmailAddress'):
        SetMessage(objMember, "Warning: Email address belongs to someone else. You cannot delete it", "")
        return False
    if not 'Deleted' in objMember.objectIds('Folder'):
        objMember.manage_addFolder('Deleted')
    dodEmailAddress = GetDOD(objMember, 'E3EmailAddress')
    objNewEmailAddress = dodEmailAddress.NewObject(objMember.Deleted)
    CopyProperties(objEmailAddress, objNewEmailAddress)
    strUID = objEmailAddress.absolute_url()
    strUID = strUID[strUID.find('/') + 2:]
    strUID = strUID[strUID.find('/'):]
    objEmailAddressCatalogue.uncatalog_object(strUID)
    objMember.manage_delObjects(objEmailAddress.id)
    return True

def DeleteEmailAddresses(objMember):
    objForm = objMember.REQUEST.form
    lstToDelete = []
    for strControl in objForm.keys():
        if "DeleteAddress" in strControl and objForm[strControl] == "on":
            lstToDelete.append(strControl[14:])
    for strEmailAddress in lstToDelete:
        if not DeleteOneEmailAddress(objMember, strEmailAddress):
            return

    if len(lstToDelete) == 1:
        strResult = "Email address deleted"
    elif len(lstToDelete) > 1:
        strResult = "Email addresses deleted"
    else:
        strResult = "Warning: Nothing to delete. Please select an email address and try again"
    return strResult

# Email Addresses tab:
#   - List of email addresses (identify posting address)

# Message delivery tab:
#   - Dropdown list of email addresses

# Summary block:
#   - List of registered addresses
#   - Delivery address, frequency and digest type
#   - Warning about unconfirmed addresses
#   - Warning about bouncing addresses

def GetEmailAddressList(objMember):
    dictResult = {}
    for objEmailAddress in objMember.objectValues('E3EmailAddress'):
        dictResult[objEmailAddress.EmailAddress] = (objEmailAddress.id,  objEmailAddress.EmailAddress == objMember.EmailDeliveryAddress, objEmailAddress.Confirmed, objEmailAddress.Bouncing)
    return dictResult

def GetEmailAddressesTab(objMember, strMessage):

    blnResult = False
    strMessage = ""

    if strMessage:
        if "warning" in strMessage.lower():
            strClass = "GeneralError"
        else:
            strClass = "InfoMessage"
        strMessage = """<p class="%s">%s</p>\n""" % (strClass, strMessage)

    dictEmailAddresses = GetEmailAddressList(objMember)

    blnCanDeleteSome = False
    strEmailAddressList = ""
    for strEmailAddress in dictEmailAddresses.keys():
        (strAddressId, blnDeliveryAddress, blnConfirmed, blnBouncing) = dictEmailAddresses[strEmailAddress]
        if blnDeliveryAddress:
            strDisabled = " disabled "
            strAddressMessage = "(<b>Delivery address</b> The delivery address cannot be deleted)"
        else:
            blnCanDeleteSome = True
            strDisabled = ""
            if blnConfirmed:
                strAddressMessage = ""
            else:
                strAddressMessage = """ (<b>Unconfirmed</b>. A confirmation request has been sent to this address. <a href=".?Action=ConfirmationEmail&EmailAddressId=%s">Resend confirmation email</a>). """ % strAddressId
        strEmailAddressList += """<p><input type="checkbox" %s name="DeleteAddress-%s"> %s %s</p>""" % (strDisabled, strAddressId, strEmailAddress, strAddressMessage)

    if blnCanDeleteSome:
        strDeleteButton = """<input type="submit" name="SubmitButton" value="Delete email address" class="btn">"""
    else:
        strDeleteButton = "The delivery address (%s) cannot be deleted. No email address(es) to delete" % objMember.EmailDeliveryAddress

    strResult = """
    %(Message)s
<form action = "." method="post" >
    <input type="hidden" name="MemberId" value="%(MemberId)s"/>
    <fieldset>
        <legend>Registered Addresses</legend>
        %(EmailAddressList)s
        <p>%(DeleteButton)s</p>
    </fieldset>
    <fieldset>
        <legend>New Email Address</legend>
        <p>
            <input type="text" name="NewAddress">
            <input type="radio" name="NewAddressMode" value="Replace" checked>
            Make this the new delivery address
            <input type="radio" name="NewAddressMode" value="PostingOnly">
            Posting only address
        </p>
        <p><input type="submit" name="SubmitButton" value="Add email address" class="btn"></p>
    </fieldset>
</form>
""" % {'MemberId': objMember.id,
        'EmailAddressList': strEmailAddressList,
        'DeleteButton': strDeleteButton,
        'Message': strMessage}

    return (strResult, blnResult, dictEmailAddresses)

def GetMembershipTab(objMember, strMembershipDetails, blnRenewal = False):
    strOverview = """
<p>%s</p>
<p>Membership is %s per year</p>
""" % (strMembershipDetails, cnAnnualAmount)

    if blnRenewal:
        strOverview = """
<p>Your membership has expired</p>
<p>You can renew your membership online, by UK or &euro; cheque, PayPal, or bank transfer to a UK or Dutch bank. For more information see below</p>
<p>Membership is %s per year</p>
""" % cnAnnualAmount

        strOverview = PutInFieldset("Membership expired", strOverview)
    else:
        strOverview = PutInFieldset("Membership - Pay", strOverview)
    strPreviousPayments = GetPreviousPayments(objMember)
    strHowToPay = GetHowToPay()
    strResult = """
    %(Overview)s
    %(HowToPay)s
    %(PreviousPayments)s
""" % {'Overview': strOverview,
        'HowToPay': strHowToPay,
        'PreviousPayments': strPreviousPayments}

    return strResult

def GetProfileTab(objMember):
    strResult = """
<p><a href="/Members/ViewProfile?MemberId=%s">View your full profile</a></p>
<p><a href="/MyECL/Profile">Maintain your profile</a></p>""" % objMember.id

    strResult += objMember.ProfilePersonalDetails(True)
    strResult += objMember.ProfileContactDetails(True)
    strResult += objMember.ProfileCommunityDetails(True)
    strResult += objMember.ProfilePersonalComments(True)
    strResult += objMember.ProfileProfessionalDetails(True)
    strResult = "<form>\n%s</form>\n" % strResult

    return strResult

def GetOfferingsTab(objMember):
    strResult = """
<fieldset>
    <legend>Add a new offering</legend>
    <p><a href="/MyECL/Offerings/Edit">Go to the new offerings page</a></p>
</fieldset>
"""

    lstOfferings = objMember.Offerings.objectValues("E3Offering")

    lstResult = []
    for objOffering in lstOfferings:
        if objOffering.Type <> "Event":
            lstResult.append(objOffering)

    if not lstResult or len(lstResult) == 0:
        return strResult

    lstResult.sort(SortOnTitle)
    intNumberOfOfferings = len(lstResult)
    lstResult = lstResult[:20]

    strList = ""
    if intNumberOfOfferings > 20:
        strList += """
<p>%s offerings found, first 20 shown - <a href="/MyECL/Offerings">List all my offerings</a></p>
<p></p>
""" % intNumberOfOfferings

    for objOffering in lstResult:
        strList += FormatOneOffering(objOffering, True, True)

    strResult += """
<fieldset>
    <legend>Offerings</legend>
    %s
</fieldset>""" % strList

    return strResult

def GetManagersIntro(objMember):
    strResult = ""

def GetMemberProperties(objMember):
    strPropertyList = ""
    for (strId, varValue) in objMember.propertyItems():
        strPropertyList += """<li>%s: %s</li>\n""" % (strId, varValue)

    strResult = """
<fieldset>
    <legend>Properties for member %s</legend>
    <ul>
    %s
    </ul>
</fieldset>""" % (objMember.id, strPropertyList)
    return strResult

def GetManagersEventsTab(objMember):
    strResult = PutInFieldset("Events and periods", ListEvents(objMember) + ListPeriods(objMember))
    return strResult

def GetManagersPaymentsTab(objMember):
    strResult = PutInFieldset("Payments", PaymentTable(objMember))
    return strResult

def GetManagersToolsTab(objMember):
    # On/off hold
    # Free membership period
    if objMember.OnHold:
        strOnHoldStatus = "on hold"
        strNewOnHoldStatus = "Back to normal"
    else:
        strOnHoldStatus = "not on hold"
        strNewOnHoldStatus = "Put on hold"
    strResult = """
<fieldset>
    <legend>Add free period</legend>
    <form name="form" method="post" action=".">
        <input type="hidden" name="MemberId" value="%s">
        <input type="hidden" name="Action" value="AddFreePeriod">
        Add <input type="text" name="Months" value="3"> free months<br>
        <td><input type="submit" name="Update" value="Add free period"></td>
    </form>
</fieldset>
<fieldset>
    <legend>Toggle on hold setting</legend>
    <p>This member is currently %s</p>
    <form name="form" method="post" action=".">
        <input type="hidden" name="MemberId" value="%s">
        <input type="hidden" name="Action" value="ToggleOnHold">
        <td><input type="submit" name="Update" value="%s"></td>
    </form>
</fieldset>
""" % (objMember.id, strOnHoldStatus, objMember.id, strNewOnHoldStatus)
    return strResult

def GetManagerTabSet(objMember):
    blnResult = False
    strMemberProperties = GetMemberProperties(objMember)
    strManagersPaymentsTab = GetManagersPaymentsTab(objMember)
    strManagersEventsTab = GetManagersEventsTab(objMember)
    strManagersToolsTab = GetManagersToolsTab(objMember)
    lstTabs = \
        (
            ("Payments", strManagersPaymentsTab, False),
            ("Tools", strManagersToolsTab, False),
            ("Properties", strMemberProperties, False),
            ("Events", strManagersEventsTab, False)
        )

    (strResult, blnResult) = BuildTabSet(lstTabs, True, "Manager")
    return (strResult, blnResult)

def MIMEDigestSample():
    return """
<fieldset>
    <legend>MIME Digest Sample</legend>
    <blockquote>
Euro Coach List Digest, 24 Mar 2008

Today's topics:
1. Re:  Feedback for  new coaches (Biana Babinsky <biana@avocadoconsulting.com>)
2. Help with Outlook? (Kate Edmonds <kate@inner-leader.com>)
3. RE:  Help with Outlook? ("Sharon Eden" <sharon.eden@womenofcourage.co.uk>)
    </blockquote>
<fieldset>"""

def GetStopResumeBlock(strMemberId, blnNoMail):
    if blnNoMail:
        strStopResumeButton = """<input type="submit" value="Resume sending emails" class="btn" name="SubmitButton"> Email delivery is currently disabled"""
    else:
        strStopResumeButton = """<input type="submit" value="Stop sending emails" class="btn" name="SubmitButton"> Stop email delivery, for instance during a holiday period"""

    strResult = """
<form action = "." method="post" >
    <input type="hidden" name="MemberId" value="%s"/>
    <fieldset>
        <legend>Disable Mail Delivery (holiday mode)</legend>
        <p>%s</p>
    </fieldset>
</form>""" % (strMemberId, strStopResumeButton)
    return strResult

def GetDeliveryAddressBlock(objMember, blnUpdate):

    lstEmailAddresses = objMember.ListEmailAddresses2()

    if len(lstEmailAddresses) == 1:
        strResult = """<p>You have one registered email address (%s)<p>
<p>This address will be used to send list messages to</p>
<p>If you want list messages to go to a different email address, please register the email address first on the "Email Addresses" tab</p>
""" % lstEmailAddresses[0]
        strResult = PutInFieldset("Delivery Address", strResult)
        return strResult

    lstFields = ("EmailDeliveryAddress", )

    lstForm = (Fieldset("Delivery Address", None,
        Paragraph(SelectControl("Address", "EmailDeliveryAddress", lstEmailAddresses)),
        Paragraph(SubmitControl("Update delivery address"))), )

    strResult = FormProcessing(objMember, lstFields, lstForm, blnUpdate)
    return strResult

def GetDeliveryFrequencyBlock(objMember, blnUpdate):
    lstFields = ("EmailFrequency_ECL", "EmailFrequency_ECL_Advert")

    lstFrequencyOptions = ( \
        ("Direct", "Separate messages - Most days you will receive between 5 and 15 list messages"),
        ("Daily", "Daily digest - Once a day you will receive a single digest message"))

    lstAdvertFrequencyOptions = ( \
        ("SameAsMain", "Same as list message delivery"),
        ("Direct", "Separate messages - Most days you will receive between 5 and 10 adverts"),
        ("Daily", "Daily digest - Once a day you will receive a single advert digest"))

    lstForm = (Fieldset("Frequency", None,
        Paragraph(RadioButtonControl("How often do you want to receive the <b>list messages</b>", "EmailFrequency_ECL", lstFrequencyOptions, True, True)),
        Paragraph(RadioButtonControl("How often do you want to receive the <b>adverts</b>", "EmailFrequency_ECL_Advert", lstAdvertFrequencyOptions, True, True)),
        Paragraph(SubmitControl("Update delivery frequency"))),)

    strResult = FormProcessing(objMember, lstFields, lstForm, blnUpdate)

    return strResult

def GetDigestFormatBlock(objMember, blnUpdate):
    lstFields = ("EmailDigestMode", )
    lstDigestOptions = ( \
        ("StructuredDigest", "Structured Digest: HTML digest, list of subjects followed by text of messages"),
        ("TextDigest", "Text Digest: text of messages in one long digest"),
        ("MIMEDigest", "MIME Digest: messages are an attachment of the digest"),
        ("TopicsList", "Daily Topics List: List of message subjects, pointing to the archived messages"))

    lstForm = (Fieldset("Digest type", None,
        Paragraph(RadioButtonControl("Which type of digest would you like to receive (see below for examples)", "EmailDigestMode", lstDigestOptions, True, True)),
        Paragraph(SubmitControl("Update digest type"))),)

    strResult = FormProcessing(objMember, lstFields, lstForm, blnUpdate)

    return strResult

def SendOneSampleDigest(objMember, strFilename, strType):
    strSubject = "Euro Coach List - Sample %s" % strType
    objFile = objMember.unrestrictedTraverse("/Data/E3/SampleDigests/%s" % strFilename)
    strContent = str(objFile)
    strAddress = objMember.EmailDeliveryAddress
    strFrom = "coen@coachcoen.com"
    SendEmail(objMember, strContent, strSubject, strAddress, strFrom, True)

def SendSampleDigests(objMember):
    SendOneSampleDigest(objMember, "MIMEDigest.txt", "MIME Digest")
    SendOneSampleDigest(objMember, "StructuredDigest.txt", "Structured Digest")
    SendOneSampleDigest(objMember, "TextDigest.txt", "Text Digest")
    SendOneSampleDigest(objMember, "TopicsList.txt", "Topics List")

def GetDigestSamplesBlock(objMember, blnSendSamples):
    if blnSendSamples:
        SendSampleDigests(objMember)
        strResult = ""
    else:
        strResult = """
<p>To receive a sample of each of the four different digest types, please use the button below</p>"""

    strResult = """<form action = "." method = "post">
    <fieldset>
        <legend>Digest samples</legend>
        %s
        <p><input type="submit" name="SubmitButton" value="Send me a set of sample digests" class="btn"></p>
    </fieldset>
</form>
""" % strResult
    return strResult

def GetMessageDeliveryTab(objMember, strSubmitButton):
    blnResult = False
    strResult = ""

    if strSubmitButton == "Stop sending emails":
        objMember.NoMail = True
        blnResult = True
        strResult = """<p class="InfoMessage">Message delivery stopped</p>"""
    elif strSubmitButton == "Resume sending emails":
        objMember.NoMail = False
        blnResult = True
        strResult = """<p class="InfoMessage">Message delivery restarted</p>"""

    blnUpdateDeliveryAddress = (strSubmitButton == "Update delivery address")
    blnUpdateDeliveryFrequency = (strSubmitButton == "Update delivery frequency")
    blnUpdateDigestType = (strSubmitButton == "Update digest type")
    blnSendSampleDigests = (strSubmitButton == "Send me a set of sample digests")
    if blnUpdateDeliveryAddress or blnUpdateDeliveryFrequency or blnUpdateDigestType or blnSendSampleDigests:
        blnResult = True

    if blnSendSampleDigests:
        strResult = """
<div class="InfoMessage">
    <p>A set of sample digests has been sent to %s</p>
    <p>Please check your email. If you haven't received the digests in a couple of minutes, please check any spam or quarantine folder. Also make sure that you can receive email from coen@coachcoen.com, for instance by adding coen@coachcoen.com to your anti-spam software's white list</p>
</div>""" % objMember.EmailDeliveryAddress

    strResult += GetStopResumeBlock(objMember.id, objMember.NoMail) + \
                GetDeliveryAddressBlock(objMember, blnUpdateDeliveryAddress) + \
                GetDeliveryFrequencyBlock(objMember, blnUpdateDeliveryFrequency)

    if objMember.EmailFrequency_ECL == "Daily" or objMember.GetEmailFrequency("ECL", True) == "Daily":
        strResult += \
            GetDigestFormatBlock(objMember, blnUpdateDigestType)

    strResult += GetDigestSamplesBlock(objMember, blnSendSampleDigests)

    return (strResult, blnResult)

def SendConfirmationRequests(objMember):
    for objEmailAddress in objMember.objectValues('E3EmailAddress'):
        if not objEmailAddress.Confirmed:
            objEmailAddress.SendConfirmationReminder()

def ResumeEmailAddresses(objMember):
    for objEmailAddress in objMember.objectValues('E3EmailAddress'):
        objEmailAddress.SetBouncing(False)

def GetMembershipTabSet(objMember, blnManagerLoggedIn, strSubmitButton):

    strMembershipDetails = GetMembershipDetails(objMember)

    # Get the tabs
    lstTabs = []

    blnUpdateLoginDetails = (strSubmitButton == "Update login details")
    strLoginTab = GetLoginTab(objMember, blnManagerLoggedIn, blnUpdateLoginDetails)
    lstTabs.append(("Login Details", strLoginTab, blnUpdateLoginDetails))

    if not objMember.LifetimeMember:
        lstTabs.append(("Pay", GetMembershipTab(objMember, strMembershipDetails), False))

    strEmailAddressesMessage = ""
    blnEmailAddressesTabDefault = False
    blnConfirmationRequestResent = False
    if strSubmitButton == "Delete email address":
        strEmailAddressesMessage = DeleteEmailAddresses(objMember)
        blnEmailAddressesTabDefault = True
    elif strSubmitButton == "Add email address":
        strEmailAddressesMessage = AddEmailAddress(objMember)
        blnEmailAddressesTabDefault = True
    elif strSubmitButton == "Send confirmation request(s)":
        SendConfirmationRequests(objMember)
        blnConfirmationRequestResent = True
    elif strSubmitButton == "Resume email address" or strSubmitButton == "Resume email addresses":
        ResumeEmailAddresses(objMember)

    (strMessageDeliveryTab, blnMessageDeliveryTabDefault) = GetMessageDeliveryTab(objMember, strSubmitButton)

    (strEmailAddressesTab, blnMyEmailAddressesTabDefault, dictEmailAddresses) = GetEmailAddressesTab(objMember, strEmailAddressesMessage)

    if strEmailAddressesMessage:
        if "Warning" in strEmailAddressesMessage:
            strEmailAddressesMessage = """<p class="GeneralError">%s</p>""" % strEmailAddressesMessage
        else:
            strEmailAddressesMessage = """<p class="InfoMessage">%s</p>""" % strEmailAddressesMessage

    strEmailAddressesTab = strEmailAddressesMessage + strEmailAddressesTab

    if blnMyEmailAddressesTabDefault:
        blnEmailAddressesTabDefault = True

    lstTabs.append(("Message Delivery", strMessageDeliveryTab, blnMessageDeliveryTabDefault))

    lstTabs.append(("Email Addresses", strEmailAddressesTab, blnEmailAddressesTabDefault))

    strResult = GetSummaryTab(objMember, strMembershipDetails, dictEmailAddresses)

    strResult += GetBouncingBox(dictEmailAddresses)

    strResult += GetUnconfirmedBox(dictEmailAddresses, blnConfirmationRequestResent)

    strResult += """</br><p><b>Your membership settings</b></p>
<p>Use the tabs below to update your membership settings</p>
"""

    (strTabSet, blnDefaultTabSet) = BuildTabSet(lstTabs, False, "Membership")
    strResult += strTabSet
    return (strResult, blnDefaultTabSet)

def GetOfferingsOverviewTab():
    strResult = """
<p><b>Events</b> include adverts, recommendations and listings for:</p>
<ul>
    <li>Networking events, such as coaching chapter (group, circle) meetings and general networking events</li>
    <li>Coach training, other training, workshops, talks, conferences</li>
</ul>
<p><b>Products and services</b> include adverts, recommendations and listings for:</p>
<ul>
    <li>Anything that doesn't have a date against it</li>
</ul>
"""
    return strResult

def GetOfferingsTabSet(objMember):
    strEventsTab = GetEventsTab(objMember)
    (strEventSeriesTab, blnEventSeriesTabDefault) = GetEventSeriesTab(objMember)
    strOfferingsTab = GetOfferingsTab(objMember)
    lstTabs = \
        (
            ("Events", strEventsTab, False),
            ("Event series", strEventSeriesTab, blnEventSeriesTabDefault),
            ("Products and services", strOfferingsTab, False)
        )
    strResult = PutInFieldset("Offerings - overview", GetOfferingsOverviewTab())
    (strTabSet, blnResult) = BuildTabSet(lstTabs, False, "Offerings")
    strResult += strTabSet
    return (strResult, blnResult)

def GetProfilePersonalTab(objMember, blnUpdate):
    lstShowOptions = ('Hide', 'Members', 'Show to all')
    lstFields = ('Name', 'ShowFullName', 'Country', 'ShowCountry', 'Location', 'ShowLocation', 'Postcode', 'ShowPostcode', 'Languages', 'CommunityComments', "ShowCommunityComments")
    lstForm = (Fieldset("Profile - Personal", None,
        Paragraph(TextControl('Name', 'Name')),
#        Paragraph(TextControl('Professional name', 'FullName', None, " (Including titles, shown on your profile and on the featured list member)")),
        Paragraph(RadioButtonControl('Show name', 'ShowFullName', lstShowOptions)),
        Paragraph(TextControl('Country', 'Country')),
        Paragraph(RadioButtonControl('Show country', 'ShowCountry', lstShowOptions)),
        Paragraph(TextControl('Location', 'Location')),
        Paragraph(RadioButtonControl('Show location', 'ShowLocation', lstShowOptions)),
        Paragraph(TextControl('Postcode', 'Postcode')),
        Paragraph(RadioButtonControl('Show postcode', 'ShowPostcode', lstShowOptions)),
        Paragraph(TextArea('Languages', 'Languages')),
        Paragraph(TextArea('Personal comments', 'CommunityComments', strComments = " (A bit more about yourself, to introduce yourself to your fellow members)")),
        Paragraph(RadioButtonControl('Show personal comments', 'ShowCommunityComments', lstShowOptions)),
        Paragraph(SubmitControl("Update personal details"))), )

    strResult = FormProcessing(objMember, lstFields, lstForm, blnUpdate)
    return strResult

def GetProfileContactDetailsTab(objMember, blnUpdate):
    lstShowOptions = ('Hide', 'Members', 'Show to all')

    lstEmailAddresses = []
    for objEmailAddress in objMember.objectValues('E3EmailAddress'):
        lstEmailAddresses.append(objEmailAddress.EmailAddress)
    lstEmailAddresses.sort()

    lstFields = ('ContactEmailAddress', 'ShowEmailAddress', 'WebsiteAddress', 'PhoneNumber', 'ShowPhoneNumber', "TwitterUsername")
    lstForm = (Fieldset("Profile - Contact details", None,
        Paragraph(SelectControl("Contact email address", "ContactEmailAddress", lstEmailAddresses, "To add an email address, use the Membership/Email Addresses tab")),
        Paragraph(RadioButtonControl("Show email address", "ShowEmailAddress", lstShowOptions)),
        Paragraph(TextControl("Website address", "WebsiteAddress")),
        Paragraph(TextControl("Phone number", "PhoneNumber")),
        Paragraph(RadioButtonControl("Show phone number", "ShowPhoneNumber", lstShowOptions)),
        Paragraph(TextControl("Twitter username", "TwitterUsername")),
        Paragraph(SubmitControl("Update contact details"))), )

    strResult = FormProcessing(objMember, lstFields, lstForm, blnUpdate)
    return strResult

def CheckFeaturedStatus(strTitle, strItem, strShowTo):
    if not strItem:
        return (False, "(<b>Missing</b>) %s" % strTitle)
    if strShowTo == "Hide":
        return (False, "(<b>Hidden</b>) %s" % strTitle)
    if strShowTo == "Members":
        return (False, "(<b>Members only</b>) %s" % strTitle)
    return (True, "(Correct) %s" % strTitle)

def GetProfileFeaturedTab(objMember):
    lstFeaturedItems = []
    lstFeaturedItems.append(CheckFeaturedStatus("Name", objMember.Name, objMember.ShowFullName))
    lstFeaturedItems.append(CheckFeaturedStatus("Tag line", objMember.TagLine, "Showtoall"))
    lstFeaturedItems.append(CheckFeaturedStatus("Comments for clients", objMember.CommercialComments, "Showtoall"))
    blnCanFeature = True
    strStatusList = ""
    for (blnItemCanFeature, strItemStatus) in lstFeaturedItems:
        if not blnItemCanFeature:
            blnCanFeature = False
        strStatusList += "<li>%s</li>\n" % strItemStatus

    if blnCanFeature:
        strOverallStatus = "You have set up all the required information, so you may be listed any day"
        strToDo = ""
    else:
        strOverallStatus = "You have not set up all the required information, so you will not be featured. See below for more information"
        strToDo = """<p>To be a featured member, you need to set up the following information, and make sure that it is visible to all</p>
    <ul>
    %s
    </ul>""" % strStatusList

    strResult = """
<fieldset>
    <legend>Profile - Featured</legend>
    <p>Once a day the system chooses a member at random, who will be featured on every page of the website</p>
    <p>%s</p>
    %s
</fieldset>""" % (strOverallStatus, strToDo)
    return strResult

def GetProfileCommercialTab(objMember, blnUpdate):
    lstFields = ("TagLine", "Testimonials", "CommercialComments", "Biography")
    lstForm = (Fieldset("Profile - Commercial", None,
        Paragraph(TextControl("Tag line or title", "TagLine")),
        Paragraph(TextArea("Testimonials", "Testimonials")),
        Paragraph(TextArea("Comments to potential clients", "CommercialComments")),
        Paragraph(TextArea("Biography", "Biography", strComments = "(Your professional training, experience and background)")),
        Paragraph(SubmitControl("Update commercial details"))), )

    strResult = FormProcessing(objMember, lstFields, lstForm, blnUpdate)
    return strResult

def GetProfileBioTab(objMember, blnUpdate):
    lstFields = ("Biography", )
    lstForm = (Fieldset("Profile - Bio", None,
        Paragraph(TextArea("Bio", "Biography")),
        Paragraph(SubmitControl("Update bio"))), )
    strResult = FormProcessing(objMember, lstFields, lstForm, blnUpdate)
    return strResult

#def UploadPhoto(objHere):
#    objData = objHere.unrestrictedTraverse("/Data/E3")
#    objPhoto = objHere.REQUEST.form["Photo"]
#
#    if not "Photo" in objData.objectIds():
#        objData.manage_addImage("Photo", objPhoto.read())
#        return "Image uploaded"
#    else:
#        return "Photo already exists"

def ScaleImage(objImageDir, strName):
    # No wider than 200 pixels
    # Save to a temporary file - how? where?
#    print objImageDir.unrestrictedTraverse(strName).data
    strImage = str(objImageDir.unrestrictedTraverse(strName).data)
    fileTemp = open("tempfile.jpg", "wb")
    fileTemp.write(strImage)
    fileTemp.close()
    # Run convert - how?
    # convert tempfile.jpg -resize 200x300\> tempfile2.jpg

    # Re-load temporary file - how?
    pass

def UploadPhoto(objMember):
    objImageDir = objMember.unrestrictedTraverse("/Websites/ECLv3/images/Members")
    objPhoto = objMember.REQUEST.form["Photo"]
    if objPhoto:
        strOldName = objMember.PhotoName
        if strOldName and strOldName in objImageDir.objectIds():
            objImageDir.manage_delObjects(strOldName)
        strUploadName = objPhoto.filename
        if "." in strUploadName:
            intIndex = strUploadName.rfind(".")
            strExtension = strUploadName[intIndex:]
        else:
            strExtension = ""
        strName = objMember.id + strExtension
        if strName in objImageDir.objectIds():
            objImageDir.manage_delObjects(strName)
        objImageDir.manage_addImage(strName, objPhoto.read())
        objMember.PhotoName = strName
        # ScaleImage(objImageDir, strName)
        return """<p class="InfoMessage">Photo uploaded</p>"""
    else:
        return """<p class="GeneralError">No photo specified. Use the "Browse" button to select a photo to upload</p>"""

def GetProfilePhotoTab(objMember, blnUploadPhoto, blnDeletePhoto):
    strMessage = ""
    if blnUploadPhoto:
        strMessage = UploadPhoto(objMember)

    if blnDeletePhoto:
        objMember.PhotoName = ""
        strMessage = "<p>Photo deleted</p>"

    if objMember.PhotoName:
        strDeleteButton = """<p><input type="submit" name="SubmitButton" value="Delete photo" class="btn"></p>"""
        strPhoto =  """<img src="/images/Members/%s" width="175" align="left">""" % objMember.PhotoName
    else:
        strDeleteButton = ""
        strPhoto = "<p>No photo uploaded</p>"

    strResult = """
<fieldset>
    <legend>Profile - Photo</legend>
%s
<form action = "." method="post" enctype="multipart/form-data">
   <p>Select a photo to upload <input type="file" name="Photo" class="btn"></p>
   <p>Photos will be scaled down to a maximum width of 200 pixels and height of 350 pixels</p>
   <p>After uploading a new photo refresh the browser page to see the new image</p>
   <p><input type="submit" name="SubmitButton" value="Upload photo" class="btn"></p>
</form>
</fieldset>
<fieldset>
    <legend>Current photo</legend>
    <form action = "." method="post" enctype="multipart/form-data">
        %s
        %s
    </form>
</fieldset>
    """ % (strMessage, strPhoto, strDeleteButton)
    return strResult

def GetProfileTabSet(objMember):
    strSubmitButton = GetParameter(objMember, "SubmitButton")

    blnPersonalTabDefault = (strSubmitButton == "Update personal details")
    blnUploadPhoto = (strSubmitButton == "Upload photo")
    blnDeletePhoto = (strSubmitButton == "Delete photo")
    blnPhotoTabDefault = blnUploadPhoto or blnDeletePhoto
    blnContactDetailsTabDefault = (strSubmitButton == "Update contact details")
    blnCommercialTabDefault = (strSubmitButton == "Update commercial details")
    lstTabs = \
        (
            ("Personal", GetProfilePersonalTab(objMember, blnPersonalTabDefault), blnPersonalTabDefault),
            ("Photo", GetProfilePhotoTab(objMember, blnUploadPhoto, blnDeletePhoto), blnPhotoTabDefault),
            ("Contact details", GetProfileContactDetailsTab(objMember, blnContactDetailsTabDefault), blnContactDetailsTabDefault),
            ("Commercial", GetProfileCommercialTab(objMember, blnCommercialTabDefault), blnCommercialTabDefault)
        )
    (strResult, blnResult) = BuildTabSet(lstTabs, False, "Profile")
    strResult = GetProfileFeaturedTab(objMember) + strResult
    return (strResult, blnResult)

def BuildTabSet(lstTabs, blnWithFieldset = True, strMainTitle = ""):
    strResult = u""
    blnResult = False
#    print lstTabs
    for (strTitle, strContents, blnDefaultTab) in lstTabs:
#        print "Title: |%s|, Contents: |%s|, Default: %s" % (strTitle, strContents[:30], blnDefaultTab)
        strResult += ToUnicode(PutInTab(strTitle, strContents, blnWithFieldset, strMainTitle, blnDefaultTab))
        if blnDefaultTab:
            blnResult = True
    strResult = """
<div class="tabber" id="tab1">
    %s
</div>""" % strResult
    return (strResult, blnResult)

def InsertMemberIdIntoLinks(strResult, strMemberId):
    # For every Action="." put in Action = ".?MemberId=...."
    strResult = strResult.replace('Action="."', 'Action=".?MemberId=%s"' % strMemberId)
    strResult = strResult.replace('action="."', 'Action=".?MemberId=%s"' % strMemberId)
    return strResult

def FullMyECL(objMember, blnManagerLoggedIn, strSubmitButton):
    # Gather the information
    (strMembershipTabSet, blnMembershipTabSetDefault) = GetMembershipTabSet(objMember, blnManagerLoggedIn, strSubmitButton)

    (strProfileTabSet, blnProfileTabSetDefault) = GetProfileTabSet(objMember)

    (strOfferingsTabSet, blnOfferingsTabSetDefault) = GetOfferingsTabSet(objMember)

    (strOrganisationsTab, blnOrganisationsTabDefault) = GetOrganisationsTab(objMember)


    if blnManagerLoggedIn:
        (strManagerTabSet, blnManagerTabSetDefault) = GetManagerTabSet(objMember)
        if not blnMembershipTabSetDefault and not blnProfileTabSetDefault and not blnOfferingsTabSetDefault and not blnOrganisationsTabDefault:
            blnManagerTabSetDefault = True
        lstAllTabs = \
            [('Membership', strMembershipTabSet, blnMembershipTabSetDefault),
            ('Profile', strProfileTabSet, blnProfileTabSetDefault),
            ('Offerings', strOfferingsTabSet, blnOfferingsTabSetDefault),
            ('Organisations', strOrganisationsTab, blnOrganisationsTabDefault),
            ('Manager', strManagerTabSet, blnManagerTabSetDefault)]
    else:
        lstAllTabs = \
            [('Membership', strMembershipTabSet, blnMembershipTabSetDefault),
            ('Profile', strProfileTabSet, blnProfileTabSetDefault),
            ('Offerings', strOfferingsTabSet, blnOfferingsTabSetDefault),
            ('Organisations', strOrganisationsTab, blnOrganisationsTabDefault)]

    (strTabSet, blnTabSetDefault) = BuildTabSet(lstAllTabs, False)

    strResult = \
        """<script type="text/javascript" src="/js/tabber.js"></script>""" + \
        strTabSet

    return strResult

def MyECL(objHere):
    strMemberId = GetParameter(objHere.REQUEST, 'MemberId')

    blnManagerLoggedIn = ManagerLoggedIn(objHere)

    strSubmitButton = GetParameter(objHere, "SubmitButton")

    if strMemberId and blnManagerLoggedIn:
        objMember = GetMemberForId(objHere, strMemberId)
    else:
        objMember = GetCurrentMember(objHere)

    if objMember.IsCancelled():
        strResult = CancelledMessage(objMember)

    elif objMember.ParkingMember():
        strResult = ParkingMemberMessage(objMember)

    elif not objMember.Live() and not blnManagerLoggedIn:
        strResult = MemberExpiredMessage(objMember)

    else:
        strResult = FullMyECL(objMember, blnManagerLoggedIn, strSubmitButton)

    if strMemberId and blnManagerLoggedIn:
        strResult = """
<fieldset>
    <legend>Manager mode</legend>
    <h3>You are logged in as the manager</h3>
</fieldset>""" + \
            InsertMemberIdIntoLinks(strResult, strMemberId)

    return strResult

def ToUnicode(strString):
#    try:
#        return unicode(strString, 'iso-8859-1', 'replace')
#    except:
#        pass

    try:
        return unicode(strString, 'utf-8', 'replace')
    except:
        pass

    return strString

