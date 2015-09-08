from StringValidator import StringValidator

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.MIMEText import MIMEText

def ReenterCheckBox(objForm, strName):
    if objForm.has_key(strName):
        return "checked"
    else:
        return ""

def BlankField(objRequest, strFieldName):
    if not(objRequest.form.has_key(strFieldName)):
        return 1
    
    if objRequest.form[strFieldName] == "":
        return 1
        
    return 0

def CheckForm(objRequest):
    if BlankField(objRequest, "ContactName"):
        return(0, "No name entered.<br>Please enter your name and try again.")
    
    if BlankField(objRequest, "ContactEmailAddress") and BlankField(objRequest, "ContactPhoneNumber"):
        return(0, "No email address or phone number entered.<br>Please enter valid contact details and try again.")
        
    if objRequest.form.has_key('ContactEmailAddress') and (objRequest.form["ContactEmailAddress"] <> ""):
        objValidator = StringValidator(objRequest.form['ContactEmailAddress'])
        if not objValidator.isEmail():
            return(0, "Invalid email address entered.<br>Please correct your email address and try again.")
        
    return (1, "")

def ListFormDetails(objRequest, lstFieldList):
    strLine = "-" * 20
    strResult =  strLine + "\n"
    for strField in lstFieldList:
        if objRequest.form.has_key(strField) and objRequest.form[strField] != "":
            strResult = strResult + strField + ": " + objRequest.form[strField] + "\n"
    strResult = strResult + strLine + "\n"
    return strResult

def SendSimpleEmail(strToAddress, strFromAddress, strFromName, strMessage, strSubject):
    objSMTP = smtplib.SMTP()
    objMsg = MIMEText(strMessage)
    
    objMsg['Subject'] = strSubject
    objMsg['From'] = strFromAddress
    objMsg['To'] = strToAddress
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    objSMTP = smtplib.SMTP()
    objSMTP.connect()
    objSMTP.sendmail(strFromAddress, [strToAddress], objMsg.as_string())
    objSMTP.close()

def SubmitFormDetails(objRequest, lstFieldList):
    SendSimpleEmail("coen@coachcoen.com", "WebsiteForm@CoachCoen.com", "CoachCoen Website", 
    """Hi Coen,
    
Someone has just submitted a form on the website

The details are:

%s

Regards,

The CoachCoen.com website""" % (ListFormDetails(objRequest, lstFieldList)), "CoachCoen website - contact request")

def SendFormDetails(objRequest):
    SubmitFormDetails(objRequest, ("ContactName", "ContactEmailAddress", "ContactPhoneNumber", 
        "FreeTrialSession", "ContactComments"))

def ProcessForm(objRequest, cnRepeatForm):
    (intCorrect, strMessage) = CheckForm(objRequest)
    if intCorrect:
        strResult = "I will be in touch as soon as possible"
        SendFormDetails(objRequest)
    else:
        strResult = cnRepeatForm % (objRequest.form["ContactName"], objRequest.form["ContactEmailAddress"], 
            objRequest.form["ContactPhoneNumber"], ReenterCheckBox(objRequest.form, "FreeTrialSession"),
            objRequest.form["ContactComments"])
        strResult = '<span class="ErrorMessage">' + strMessage + '</span><br>' + strResult
        
    return strResult

def StartNowForm(objRequest):
    cnStartNowForm = """<form name="form1" method="post" action="/ThankYou.html">
                          <table width="100%%" border="0" cellspacing="0" cellpadding="5">
                            <tr> 
                              <td class="MainText"> 
                                <p>Name<br>
                                  <input type="text" name="ContactName" size="35" value="%s">
                                  <input type="hidden" name="FormTypeStartNow" value="yes">
                                </p>
                                <p>Email address<br>
                                  <input type="text" name="ContactEmailAddress" size="35" value="%s">
                                </p>
                                <p>Phone number<br>
                                  <input type="text" name="ContactPhoneNumber" size="35" value="%s">
                                </p>
                                <p> 
                                  <input type="checkbox" name="FreeTrialSession" value="Yes" %s>
                                  Please contact me to arrange a free trial session</p>
                                <p>Any additional comments<br>
                                  <textarea name="ContactComments" cols="25" rows="5">%s</textarea>
                                  <input type="submit" name="Submit" value="Submit">
                                </p>
                              </td>
                            </tr>
                          </table>
                        </form>"""
    strResult = ProcessForm(objRequest, cnStartNowForm)
    return strResult
    
def ContactMeForm(objRequest):
    cnContactMeForm = """<form name="form1" method="post" action="/ThankYou.html">
                          <table width="100%%" border="0" cellspacing="0" cellpadding="5">
                            <tr> 
                              <td class="MainText"> 
                                <p>Name<br>
                                  <input type="text" name="ContactName" size="35" value="%s">
                                  <input type="hidden" name="FormTypeContactMe" value="yes">
                                </p>
                                <p>Email address<br>
                                  <input type="text" name="ContactEmailAddress" size="35" value="%s">
                                </p>
                                <p>Phone number<br>
                                  <input type="text" name="ContactPhoneNumber" size="35" value="%s">
                                </p>
                                <p> 
                                  <input type="checkbox" name="FreeTrialSession" value="checkbox" %s>
                                  Please contact me to arrange a free trial session</p>
                                <p>Your question<br>
                                  <textarea name="ContactComments" cols="25" rows="5">%s</textarea>
                                  <input type="submit" name="Submit" value="Submit">
                                </p>
                              </td>
                            </tr>
                          </table>
                        </form>"""
    strResult = ProcessForm(objRequest, cnContactMeForm)
    return strResult

def ISCThankYouForm(objRequest):
    strResult = "Unknown form"

    if objRequest.form.has_key('FormTypeStartNow'):
        strResult = StartNowForm(objRequest)

    if objRequest.form.has_key('FormTypeContactMe'):
        strResult = ContactMeForm(objRequest)
        
    return strResult
    
  