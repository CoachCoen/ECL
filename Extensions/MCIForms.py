import sys
sys.path.append('/var/zope/Extensions')
sys.path.append('/var/mailman')

from Mailman import MailList

from StringValidator import StringValidator

from libEmail import SendEmail

def IndividualCoachPageCorrect(objRequest):
    """    - Error: No contact details (telephone number and/or email address)
    - Error: Incorrect email address"""
    if (objRequest.form['EmailAddress'] == "") and (objRequest.form['PhoneNumber'] == ""):
        return (0, "Insufficient contact details given. Please enter a phone number or an email address.")
        
    if (objRequest.form['EmailAddress'] != ""):
        objValidator = StringValidator(objRequest.form['EmailAddress'])
        if not objValidator.isEmail():
            return(0, "Invalid email address entered.<br>Please correct your email address and try again.")
    return (1, "")

def IndividualCoachPageRepeat(objRequest):
    strResult = """<form name="form" method="post" action="/ThankYou.html">
                    <table width="100%%" border="0" cellspacing="0" cellpadding="5" class="TableWithBorder">
                      <tr valign="top" class="TableWithBorder"> 
                        <td class="MainText"> 
                          <input type="hidden" name="AboodiContactForm" value="Yes">
                          Name</td>
                        <td class="MainText"> 
                          <input type="text" name="ContactName" size="50" value="%s">
                        </td>
                      </tr>
                      <tr valign="top" class="TableWithBorder"> 
                        <td class="MainText">Telephone number</td>
                        <td class="MainText"> 
                          <input type="text" name="PhoneNumber" size="50" value="%s">
                        </td>
                      </tr>
                      <tr valign="top" class="TableWithBorder"> 
                        <td class="MainText">Email address</td>
                        <td class="MainText"> 
                          <input type="text" name="EmailAddress" size="50" value="%s">
                        </td>
                      </tr>
                      <tr valign="top" class="TableWithBorder"> 
                        <td class="MainText">Comments</td>
                        <td class="MainText"> 
                          <textarea name="Comments" cols="50" rows="10">%s</textarea>
                        </td>
                      </tr>
                      <tr valign="top" class="TableWithBorder"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="checkbox" name="SubscribeToNewsletter" value="Yes" %s>
                          Please sign me up for the free &quot;The Mentor Coach&quot; 
                          newsletter</td>
                      </tr>
                      <tr valign="top" class="TableWithBorder"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="checkbox" name="SubscribeToBooksForCoaches" value="Yes" %s>
                          Please sign me up for the free &quot;Books for Coaches&quot; 
                          weekly book reviews</td>
                      </tr>
                      <tr valign="top" class="TableWithBorder"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="submit" name="Submit" value="Aboodi, please contact me">
                        </td>
                      </tr>
                    </table>
                  </form>""" % (objRequest.form["ContactName"],
                                objRequest.form["PhoneNumber"], 
                                objRequest.form["EmailAddress"], 
                                objRequest.form["Comments"], 
                                ReenterCheckBox(objRequest.form, "SubscribeToNewsletter"),
                                ReenterCheckBox(objRequest.form, "SubscribeToBooksForCoaches"))

    return strResult

def IndividualCoachPage(objHere, objRequest, strName):
    """Individual Coaches' pages
    * [ Name ]
    * [ Telephone number ]
    * [ Email address ]
    * [ Comments ]
    * [ ] Sign up for TMC
    * [ ] Sign up for B4C
    - Do: Email coach with request to contact the sender
    - Extra: Invite to sign up for Masterclasses (those not already signed-up for)
    - Extra (on Aboodi's): Invite to sign up for Aboodi's newsletter"""
    
    (blnFormCorrect, strErrorMessage) =  IndividualCoachPageCorrect(objRequest)
    if not blnFormCorrect:
        return ShowErrorMessage(strErrorMessage) + IndividualCoachPageRepeat(objRequest)

    strResult = ""

    strResult = strResult + ProcessSignups(objHere, objRequest)

    GetCoachToContactVisitor(objHere, objRequest, ("ContactName", "PhoneNumber", "EmailAddress", "Comments"), strName, 
        "Someone has filled in the form on your personal page, requesting that you contact them") 
    strResult = strResult + "%s will contact you as soon as possible<br><br>" % (strName)

    return strResult

def MasterClassesPage(objRequest, objHere):
    """Masterclasses
    * [ Name ]
    * [ Email address ]
    * [ ] Class(es) to attend
    * [ ] Sign up for TMC
    * [ ] Sign up for B4C
    * [ ] Sign up for MCI News
    - Error: No option or class requested
    - Error: Missing email address
    - Error: Incorrect email address
    - Process sign up, see separate python script
    - Do, if TMC, sign up for TMC
    - Do, if B4C, sign up for B4C
    - Do, if MCI news, add to database"""
    strResult = ""
#    strResult = MasterclassesFunctions.ProcessMasterClassSignUp(objRequest, objHere)
    return strResult

def SignUpFormCorrect(objRequest):
    if objRequest.form['EmailAddress'] == "":
        return(0, "No email address entered.<br>Please enter a valid email address and try again.")

    objValidator = StringValidator(objRequest.form['EmailAddress'])
    if not objValidator.isEmail():
        return(0, "Invalid email address entered.<br>Please correct your email address and try again.")
        
    return (1, "")

def SignUpFormRepeat(objRequest):
    strResult = """<form name="form1" method="post" action="/ThankYou.html">
    <table width="100%%" border="0" cellspacing="0" cellpadding="5" class="TableWithBorder">
      <tr> 
        <td class="MainText">
          <input type="hidden" name="%s" value="Yes">
          Your email address</td>
        <td class="MainText"> 
          <input type="text" name="EmailAddress" size="50" value="%s">
        </td>
      </tr>
      <tr> 
        <td class="MainText">&nbsp;</td>
        <td class="MainText"> 
          <input type="submit" name="Submit" value="Submit">
        </td>
      </tr>
    </table>
  </form>"""

    if objRequest.form.has_key("BooksForCoachesForm"):
        strFormName = "BooksForCoachesForm"
    else:
        strFormName = "TheMentorCoachForm"
    
    strResult = strResult % (strFormName, objRequest.form["EmailAddress"])
    
    return strResult

def ProcessMailingListSignUpForm(objHere, objRequest):
    """B4C or TMC Sign up page
    * [ Email address ]
    - Error: Missing email address
    - Error: Incorrect email address
    - Do: Sign up """
    (blnFormCorrect, strErrorMessage) =  SignUpFormCorrect(objRequest)
    if not blnFormCorrect:
        return ShowErrorMessage(strErrorMessage) + SignUpFormRepeat(objRequest)
    return ProcessSignups(objHere, objRequest)
    
def ContactFormCorrect(objRequest):
    """- Error: Missing contact details
    - Error: subscription requested but no email address
    - Error: Incorrect email address"""

    if (objRequest.form["PhoneNumber"] == "") and (objRequest.form["EmailAddress"] == ""):
        return(0, "Contact details missing. Please enter a phone number or email address")

    if objRequest.form.has_key("SubscribeToBooksForCoaches") or objRequest.form.has_key("SubscribeToNewsletter"):
        if objRequest.form["EmailAddress"] == "":
            return(0, "Email address missing. Please enter a valid email address")
     
    if (objRequest.form["EmailAddress"] != ""):
        objValidator = StringValidator(objRequest.form['EmailAddress'])
        if not objValidator.isEmail():
            return(0, "Invalid email address entered.<br>Please correct your email address and try again.")

    return(1, "")        

def ContactFormRepeat(objRequest):
    strResult = """<form name="form1" method="post" action="/ThankYou.html">
                          <input type="hidden" name="ContactUsForm" value="Yes">
                    <table width="100%%" border="0" cellspacing="0" cellpadding="5" class="TableWithBorder">
                      <tr valign="top"> 
                        <td class="MainText">Name</td>
                        <td class="MainText"> 
                          <input type="text" name="ContactName" size="50" value="%s">
                        </td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">Telephone number</td>
                        <td class="MainText"> 
                          <input type="text" name="PhoneNumber" size="50" value="%s">
                        </td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">email address</td>
                        <td class="MainText"> 
                          <input type="text" name="EmailAddress" size="50" value="%s">
                        </td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText" colspan="2">If you are interested 
                          in working with any particular MCI coach then please 
                          select the coach below. Otherwise we will contact you 
                          to discuss who might be most suitable for you</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="checkbox" name="AboodiPlease" value="AboodiPlease" %s>
                          Aboodi Shabi</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="checkbox" name="CoenPlease" value="CoenPlease" %s>
                          Coen de Groot</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="checkbox" name="EdnaPlease" value="EdnaPlease" %s>
                          Edna Murdoch</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="checkbox" name="MariannePlease" value="MariannePlease" %s>
                          Marianne Craig</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="checkbox" name="MichaelPlease" value="MichaelPlease" %s>
                          Michael Sanson</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">Comments</td>
                        <td class="MainText"> 
                          <textarea name="Comments" cols="50" rows="10">%s</textarea>
                        </td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp; </td>
                        <td class="MainText"> 
                          <input type="checkbox" name="SubscribeToNewsletter" value="Yes" %s>
                          Please sign me up for the free &quot;The Mentor Coach&quot; 
                          newsletter</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp; </td>
                        <td class="MainText"> 
                          <input type="checkbox" name="SubscribeToBooksForCoaches" value="Yes" %s>
                          Please sign me up for the free &quot;Books for Coaches&quot; 
                          book reviews</td>
                      </tr>
                      <tr valign="top"> 
                        <td class="MainText">&nbsp;</td>
                        <td class="MainText"> 
                          <input type="submit" name="Submit" value="Submit">
                        </td>
                      </tr>
                    </table>
                  </form>"""
    
    strResult = strResult % (objRequest.form["ContactName"],
                             objRequest.form["PhoneNumber"],
                             objRequest.form["EmailAddress"],
                             ReenterCheckBox(objRequest.form, "AboodiPlease"),
                             ReenterCheckBox(objRequest.form, "CoenPlease"),
                             ReenterCheckBox(objRequest.form, "EdnaPlease"),
                             ReenterCheckBox(objRequest.form, "MariannePlease"),
                             ReenterCheckBox(objRequest.form, "MichaelPlease"),
                             objRequest.form["Comments"],
                             ReenterCheckBox(objRequest.form, "SubscribeToNewsletter"),
                             ReenterCheckBox(objRequest.form, "SubscribeToBooksForCoaches"))

    return strResult

def BuildNamesString(lstNames):
    if len(lstNames) == 0:
        strNames = "We"
        
    if len(lstNames) == 1:
        strNames = lstNames[0]
        
    if len(lstNames) > 1:
        strNames = ""
        for intI in range(0, len(lstNames)):
            if intI == len(lstNames) - 1:
                strNames = strNames + " and "
            else:
                if intI > 0:
                    strNames = strNames + ", "
            strNames = strNames + lstNames[intI]
            
    return strNames
            
def ProcessContactUsRequests(objHere, objRequest):
    lstCoaches = []
    for strName in ["Aboodi", "Coen", "Edna", "Marianne", "Michael"]:
        if objRequest.form.has_key(strName + "Please"):
            lstCoaches.append(strName)

    strNames = BuildNamesString(lstCoaches)
            
    if len(lstCoaches) == 0:
        strIntro = "Someone has requested that we contact them to discuss who would be the best coach for them"
        strName = "Marianne"
        strReply = "We"
    
    if len(lstCoaches) == 1:
        strIntro = "Someone is interested in you coaching them (whoopie!)"
        strName = lstCoaches[0]
        strReply = strName
        
    if len(lstCoaches) > 1:
        strIntro = "Someone is interested in being coached by one of our coaches. They are interested in %s." % (strNames)
        strName = "Marianne"
        strReply = "We"
        
    GetCoachToContactVisitor(objHere, objRequest, ("ContactName", "PhoneNumber", "EmailAddress", "Comments"), strName, strIntro)

    return strReply + " will contact you as soon as possible"

def ContactUsPage(objHere, objRequest):
    """Contact Us page
    * [ Name ]
    * [ Telephone number ]
    * [ Email address ]
    * [ ] Aboodi, etc
    * [ Comments ]
    * [ ] TMC sign up
    * [ ] B4C sign up
    - Do, for each of the coaches selected:
      . Email request to the coach to contact as per details
    - If no coach selected:
      . Email Marianne request to contact as per details
    - If TMC sign up, sign up for TMC
    - If B4C sign up, sign up for B4C"""
    (blnFormCorrect, strErrorMessage) =  ContactFormCorrect(objRequest)
    if not blnFormCorrect:
        return ShowErrorMessage(strErrorMessage) + ContactFormRepeat(objRequest)

    strResult = ProcessContactUsRequests(objHere, objRequest) + "<br><br>" + ProcessSignups(objHere, objRequest)
    
    return strResult

def SideBarFormCorrect(objRequest):
    """- Error: None of the options ticked
    - Error: No email address entered (blank or standard text still there)
    - Error: Incorrect email address entered"""
    
    if not(objRequest.form.has_key('SubscribeToNewsletter')) and not(objRequest.form.has_key('SubscribeToBooksForCoaches')) and not(objRequest.form.has_key('ContactMeAboutCoaching')):
        return (0, "No option selected.<br>Please choose at least on of the options below and try again.")

    if not(objRequest.form.has_key('EmailAddress')):
        return(0, "No email address entered.<br>Please enter a valid email address and try again.")
        
    if objRequest.form['EmailAddress'] == "":
        return(0, "No email address entered.<br>Please enter a valid email address and try again.")

    if objRequest.form['EmailAddress'] == "My email address":
        return(0, "No email address entered.<br>Please enter a valid email address and try again.")

    objValidator = StringValidator(objRequest.form['EmailAddress'])
    if not objValidator.isEmail():
        return(0, "Invalid email address entered.<br>Please correct your email address and try again.")
        
    return (1, "")

def ReenterCheckBox(objForm, strName):
    if objForm.has_key(strName):
        return "checked"
    else:
        return ""

def SideBarFormRepeat(objRequest):
    strResult="""<form name="Form" method="post" action="/ThankYou.html">
        <table width="100%%" border="0" cellspacing="0" cellpadding="3" class="TableWithBorder">
          <tr> 
            <td class="MainText" nowrap><b> 
              <input type="hidden" name="FormTypeSideForm" value="Yes">
              Subscribe me</b> to <br>
              <input type="checkbox" name="SubscribeToNewsletter" value="Yes" %s>
              &quot;<a href="/Newsletter.html" class="MenuItem">The 
              Mentor Coach</a>&quot;<br>
              <input type="checkbox" name="SubscribeToBooksForCoaches" value="Yes" %s>
              &quot;<a href="BooksForCoaches.html" class="MenuItem">Books for Coaches</a>&quot;</td>
          </tr>
          <tr> 
            <td class="MainText" nowrap><b> 
              <input type="checkbox" name="ContactMeAboutCoaching" value="Yes" %s>
              Contact me</b> about Coaching</td>
          </tr>
          <tr> 
            <td class="MainText"> 
              <input type="text" size="30" name="EmailAddress" value="%s" class="SideBarForm">
            </td>
          </tr>
          <tr> 
            <td class="MainText"> 
              <input type="submit" name="Submit" value="Submit">
            </td>
          </tr>
        </table>
    </form>"""
    
    strSubscribeToNewsletter = ReenterCheckBox(objRequest.form, "SubscribeToNewsletter")
    strSubscribeToBooksForCoaches = ReenterCheckBox(objRequest.form, "SubscribeToBooksForCoaches")
    strContactMeAboutCoaching = ReenterCheckBox(objRequest.form, "ContactMeAboutCoaching")
 
    strResult = strResult % (strSubscribeToNewsletter, strSubscribeToBooksForCoaches, strContactMeAboutCoaching, objRequest.form["EmailAddress"])

    return strResult

def DoSubscribeToMailingList(objHere, strEmailAddress, strListName, strFullListName):
    # Check if they are already a member, by looking at the database
    objMailingList = MailList.MailList(strListName, lock = 0)
    strEmailAddress = strEmailAddress.lower()
    if objMailingList.digest_members.has_key(strEmailAddress) or objMailingList.members.has_key(strEmailAddress):
        return(0, "You are already subscribed to " + strFullListName)

    # If not, send a message to <list-name>-join@forcoaches.com, as if coming from this email address
#    SendSimpleEmail(strListName + "-join@forcoaches.com", strEmailAddress, "", "", "")
    SendEmail(objHere, "", "", strListName + "-join@mentorcoaches.com", strEmailAddress)
    return(1, "")
    

def ListFormDetails(objRequest, lstFieldList):
    strLine = "-" * 20
    strResult =  strLine + "\n"
    for strField in lstFieldList:
        if objRequest.form[strField] != "":
            strResult = strResult + strField + ": " + objRequest.form[strField] + "\n"
    strResult = strResult + strLine + "\n"
    return strResult

def GetEmailAddress(strName):
    return "coen@coachcoen.com"

def Dummy():
    return {"Aboodi": "mail@aboodi.net",
            "Coen": "coen@coachcoen.com",
            "Edna": "edna1@gotadsl.co.uk",
            "Marianne": "coach@coachlifeandcareer.com",
            "Michael": "msanson@unlimited.com"}[strName]
    
def GetCoachToContactVisitor(objHere, objRequest, lstFieldList, strName, strIntro):
#    SendSimpleEmail(GetEmailAddress(strName), "WebsiteForm@MentorCoaches.com", "MCI Website", 

    strMessage = """Dear %s,
    
%s

Please attend to this as soon as you can

The details are:

%s

Regards,

The MCI website""" % (strName, strIntro, ListFormDetails(objRequest, lstFieldList))

    SendEmail(objHere, strMessage, "MCI website - contact request", GetEmailAddress(strName), "WebsiteForm@MentorCoaches.com")

def ProcessSignups(objHere, objRequest):
    strResult = ""
    intJoinedCount = 0
    if objRequest.form.has_key("SubscribeToNewsletter") or objRequest.form.has_key("TheMentorCoachForm"):
        (blnAddedToTMC, strErrorMessage) = DoSubscribeToMailingList(objHere, objRequest.form["EmailAddress"], "thementorcoach", "The Mentor Coach")
        if blnAddedToTMC:
            intJoinedCount += 1
            strResult = strResult + 'Your subscription request for "The Mentor Coach" has been processed. '
        else:
            strResult = strResult + strErrorMessage + "<br><br>"
    
    if objRequest.form.has_key("SubscribeToBooksForCoaches") or objRequest.form.has_key("BooksForCoachesForm"):
        (blnAddedToB4C, strErrorMessage) = DoSubscribeToMailingList(objHere, objRequest.form["EmailAddress"], "booksforcoaches", "Books for Coaches")
        if blnAddedToB4C:
            intJoinedCount += 1
            strResult = strResult + 'Your subscription request for "Books for Coaches" has been processed. '
        else:
            strResult = strResult + strErrorMessage + "<br><br>"

    if intJoinedCount == 1:
        strResult += "You will soon receive an email asking you to confirm your request. Please follow the instructions in the email.<br>"
    
    if intJoinedCount > 1:
        strResult += "You will soon receive %s emails asking you to confirm your requests. Please follow the instructions in the emails.<br>" % (intJoinedCount)
        
    if intJoinedCount > 0:
        strResult += "This 'double opt-in' is common practice to stop people from subscribing others without their permission<br><br>"
    
    return strResult

def ShowErrorMessage(strErrorMessage):
    return '<span class="ErrorMessage">' + strErrorMessage + '</span><br><br>'

def DueBookReviewFormCorrect(objRequest):
    """- Error: None of the options ticked
    - Error: No email address entered (blank or standard text still there)
    - Error: Incorrect email address entered"""
    
    if not(objRequest.form.has_key('SubscribeToNewsletter')) and not(objRequest.form.has_key('SubscribeToBooksForCoaches')) and not(objRequest.form.has_key('ContactMeAboutCoaching')):
        return (0, "No option selected.<br>Please choose at least on of the options below and try again.")

    if not(objRequest.form.has_key('EmailAddress')):
        return(0, "No email address entered.<br>Please enter a valid email address and try again.")
        
    if objRequest.form['EmailAddress'] == "":
        return(0, "No email address entered.<br>Please enter a valid email address and try again.")

    if objRequest.form['EmailAddress'] == "My email address":
        return(0, "No email address entered.<br>Please enter a valid email address and try again.")

    objValidator = StringValidator(objRequest.form['EmailAddress'])
    if not objValidator.isEmail():
        return(0, "Invalid email address entered.<br>Please correct your email address and try again.")
        
    return (1, "")

def DueBookReviewFormRepeat(objRequest):
    strResult = """<form name="Form" method="post" action="/ThankYou.html">
        <table width="100%%" border="0" cellspacing="0" cellpadding="3" class="TableWithBorder">
          <tr> 
            <td class="MainText" nowrap>Please make sure I receive this review when it comes out<br>
            <b>Subscribe me</b> to <br>
              <input type="hidden" name="FormTypeDueBookReview" value="Yes">
              <input type="checkbox" name="SubscribeToBooksForCoaches" value="Yes" %s> &quot;<a href="BooksForCoaches.html" class="MenuItem">Books for Coaches</a>&quot;<br>
              <input type="checkbox" name="SubscribeToNewsletter" value="Yes" %s>
              &quot;<a href="/Newsletter.html" class="MenuItem">The 
              Mentor Coach</a>&quot;<br></td>
          </tr>
          <tr> 
            <td class="MainText"> 
              <input type="text" name="EmailAddress" value="%s" size="40">
            </td>
          </tr>
          <tr> 
            <td class="MainText"> 
              <input type="submit" name="Submit" value="Submit">
            </td>
          </tr>
        </table>
      </form>"""
      
    strSubscribeToNewsletter = ReenterCheckBox(objRequest.form, "SubscribeToNewsletter")
    strSubscribeToBooksForCoaches = ReenterCheckBox(objRequest.form, "SubscribeToBooksForCoaches")
    strResult = strResult % (strSubscribeToBooksForCoaches, strSubscribeToNewsletter, objRequest.form["EmailAddress"])

    return strResult

def DueBookReview(objHere, objRequest):
    (blnFormCorrect, strErrorMessage) =  DueBookReviewFormCorrect(objRequest)
    if not blnFormCorrect:
        return ShowErrorMessage(strErrorMessage) + DueBookReviewFormRepeat(objRequest)

    strResult = ""

    strResult = strResult + ProcessSignups(objHere, objRequest)

    return strResult

def SideBarForm(objHere, objRequest):
    """All pages
    * [ ] Subscribe me to The Mentor Coach
    * [ ] Subscribe me to Books for Coaches
    * [ ] Contact me about coaching
    * [ Email address ]
    - Ignore: Already subscribed to The Mentor Coach
    - Ignore: Already subscribed to Books for Coaches
    - Do: Subscribe to The Mentor Coach
    - Do: Subscribe to Books for Coaches
    - Do: Email Marianne with request to contact the sender
    - Extra: Invite to subscribe to Aboodi's newsletter
    - Extra: Invite to sign up for Masterclasses (if not already signed-up)"""
    
    intJoinedCount = 0
    
    (blnFormCorrect, strErrorMessage) =  SideBarFormCorrect(objRequest)
    if not blnFormCorrect:
        return ShowErrorMessage(strErrorMessage) + SideBarFormRepeat(objRequest)

    strResult = ""

    strResult = strResult + ProcessSignups(objHere, objRequest)

    if objRequest.form.has_key("ContactMeAboutCoaching"):
        GetCoachToContactVisitor(objHere, objRequest, ("EmailAddress",), "Marianne", "Someone has asked us to contact them")
        strResult = strResult + "Someone will contact you as soon as possible<br><br>"
    
    return strResult

def ThankYouForm(objHere, objRequest):
    strResult = "Unknown form"

    if objRequest.form.has_key('FormTypeSideForm'):
        strResult = SideBarForm(objHere, objRequest)

    if objRequest.form.has_key('AboodiContactForm'):
        strResult = IndividualCoachPage(objHere, objRequest, "Aboodi")

    if objRequest.form.has_key('CoenContactForm'):
        strResult = IndividualCoachPage(objHere, objRequest, "Coen")
    
    if objRequest.form.has_key('EdnaContactForm'):
        strResult = IndividualCoachPage(objHere, objRequest, "Edna")
    
    if objRequest.form.has_key('MarianneContactForm'): 
        strResult = IndividualCoachPage(objHere, objRequest, "Marianne")
    
    if objRequest.form.has_key('MichaelContactForm') :        
        strResult = IndividualCoachPage(objHere, objRequest, "Michael")

    if objRequest.form.has_key('TheMentorCoachForm'):
        strResult = ProcessMailingListSignUpForm(objHere, objRequest)
        
    if objRequest.form.has_key('BooksForCoachesForm'):
        strResult = ProcessMailingListSignUpForm(objHere, objRequest)

    if objRequest.form.has_key('ContactUsForm'):
        strResult = ContactUsPage(objHere, objRequest)

    if objRequest.form.has_key('MasterclassesForm'):
        strResult = MasterClassesPage(objRequest, objHere)
        
    if objRequest.form.has_key('FormTypeDueBookReview'):
        strResult = DueBookReview(objHere, objRequest)

    return strResult
