# Import smtplib for the actual sending function
import smtplib

# Here are the email pacakge modules we'll need
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import datetime

def GetAmazonComNumber(objReview):
    if objReview.AmazonComNumber:
        intNumber = objReview.AmazonComNumber
    else:
        intNumber = objReview.AmazonNumber
    return intNumber

def ShoppingLinks(objReview):
    strResult = ""
    if objReview.OnAmazonCoUk:
        strResult = strResult + """<a href=3D"http://www.amazon.co.uk/exec/obidos/ASIN/%s/mentorcoaches-21">Buy 
                    this book at Amazon.co.uk</a><br>""" % objReview.AmazonNumber
                    
    if objReview.OnAmazonCom:
        strResult = strResult + """<a href=3D"http://www.amazon.com/exec/obidos/ASIN/%s/mentorcoaches-20">Buy 
                    this book at Amazon.com</a><br>""" % GetAmazonComNumber(objReview)
        
    if objReview.OtherShoppingLink:
        strResult = strResult + """You can buy this book at <a href=3D"http://%s">%s</a><br>""" % (objReview.OtherShoppingLink, objReview.OtherShoppingLink)
        
    return strResult

def ShoppingLinksWithImages(objReview):
    strResult = ""
    if objReview.OnAmazonCoUk or objReview.OnAmazonCom:
        strResult = strResult + """<table width=3D"100%" border=3D"0" cellspacing=3D"0" cellpadding=3D"5">
        <tr>"""
        if objReview.OnAmazonCoUk:
            strResult = strResult + """<td class=3D"MainText"><a href=3D"http://www.amazon.co.uk/exec/obidos/ASIN/%s/mentorcoaches-21"><img src=3D"cid:123AmazonCoUk@forcoaches.com" width=3D"100" height=3D"35" border=3D"0"><br>
                        Buy this book at Amazon.co.uk</a></td>""" % objReview.AmazonNumber

        if objReview.OnAmazonCom:
            strResult = strResult + """<td class=3D"MainText"><a href=3D"http://www.amazon.com/exec/obidos/ASIN/%s/mentorcoaches-20"><img src=3D"cid:123AmazonCom@forcoaches.com" width=3D"90" height=3D"28" border=3D"0"><br>
                        Buy this book at Amazon.com</a></td>""" % GetAmazonComNumber(objReview)
        strResult = strResult + "</tr></table>"
    return strResult

def ShoppingTextLinks(objReview):
    strResult = ""
    if objReview.OnAmazonCoUk:
        strResult = strResult + "Buy this book at Amazon.co.uk, go to www.MentorCoaches.com/GoTo/Book%sa\n" % objReview.ReviewNumber

    if objReview.OnAmazonCom:
        strResult = strResult + "Buy this book at Amazon.com, go to www.MentorCoaches.com/GoTo/Book%sb\n" % objReview.ReviewNumber

    if objReview.OtherShoppingLink:
        strResult = strResult + "You can buy this book at %s\n" % objReview.OtherShoppingLink

    return strResult

def GetReviewDetails(objReview, objHere):
    strHTMLResult = "<b>Issue:</b> %s<br>" % objReview.Issue
    strTextResult = "Issue: %s\n" % objReview.Issue

    if objReview.ReviewRead:
        strHTMLResult = strHTMLResult + "<b>Book read by:</b> %s<br>" % GetPersonDetails(objReview.ReviewRead, objHere).PersonName
        strTextResult = strTextResult + "Book read by: %s\n" % GetPersonDetails(objReview.ReviewRead, objHere).PersonName

    strHTMLResult = strHTMLResult + "<b>Review written by:</b> %s<br>" % GetPersonDetails(objReview.ReviewAuthor, objHere).PersonName
    strTextResult = strTextResult + "Review written by: %s\n" % GetPersonDetails(objReview.ReviewAuthor, objHere).PersonName
    
    strHTMLResult = strHTMLResult + ShoppingLinks(objReview)

    strHTMLResult = strHTMLResult + objReview.ReviewContents

    strTextResult = strTextResult + "\n" + GeneralFunctions.HTMLToText(objReview.ReviewContents)

    strHTMLResult = strHTMLResult + ShoppingLinksWithImages(objReview)
    strTextResult = strTextResult + ShoppingTextLinks(objReview)

    return (strHTMLResult, strTextResult)

def FormatFirstEvent(dictEvent):
    # For the first event with a date on or after today
    # PageTitle: Date Month, 'Title', presenter
    # Tuesday 15 February 2005, 6pm UK time, 19:00 Central European Time, by telephone, free 
    # Description
    strHTMLResult = """<span class=3D"PageTitle">%s, '%s', %s</span><br>
    %s, 6pm UK time, 19:00 Central European Time, by telephone, free<br>""" % (dictEvent["Date"].strftime('%d %B'),
        dictEvent["Title"], dictEvent["Presenters"], dictEvent["Date"].strftime('%a %d %B %Y'))
    
    strTextResult = """%s, '%s', %s
    
%s, 6pm UK time, 19:00 Central European Time, by telephone, free
    """ % (dictEvent["Date"].strftime('%d %B'),
        dictEvent["Title"], dictEvent["Presenters"], dictEvent["Date"].strftime('%a %d %B %Y'))
        
    if dictEvent["Description"]:
        strHTMLResult = strHTMLResult + "<br>" + dictEvent["Description"]
        strTextResult = strTextResult + "\n" + dictEvent["Description"]
        
    return (strHTMLResult, strTextResult)
    
def FormatFutureEvent(dictEvent):
    strResult = "%s, '%s', %s" % (dictEvent["Date"].strftime('%d %B'), dictEvent["Title"], dictEvent["Presenters"])
    return strResult
    
def GetEventsDetails(objHere):
    # Get details for current event
    # Get list of future events

    dictEvents = {}

    for objEvent in objHere.restrictedTraverse("/MCI/Masterclasses/").objectValues():
        blnIsAClass = 1
        try:
            dtmClassDate = objEvent.ClassDate
        except:
            blnIsAClass = 0
        if blnIsAClass and dtmClassDate >= datetime.datetime.today() and objEvent.ReadyToPublish and not objEvent.Cancelled:
            lstPresenters = []
            for objPresenter in objEvent.objectValues():
                lstPresenters.append(objPresenter.PresenterName)
            strPresenters = ", ".join(lstPresenters)
            dictOneEvent = {'Date': objEvent.ClassDate,
                            'Title': objEvent.ClassTitle,
                            'Description': objEvent.Description,
                            'Presenters': strPresenters}
            dictEvents[objEvent.ClassDate] = dictOneEvent
            
    lstDates = dictEvents.keys()
    lstDates.sort()
    blnFirstDate = 1
    strFutureEventsHTML = "<ul>\n"
    strFutureEventsText = ""
    for dtmDate in lstDates:
        if blnFirstDate:
            (strFirstEventHTML, strFirstEventText) = FormatFirstEvent(dictEvents[dtmDate])
            blnFirstDate = 0
        else:
            strFormattedFE = FormatFutureEvent(dictEvents[dtmDate])
            strFutureEventsHTML = strFutureEventsHTML + "<li>" +  strFormattedFE + "</li>\n"
            strFutureEventsText = "* %s\n" % strFormattedFE
    strFutureEventsHTML = strFutureEventsHTML + "</ul>\n"            

    return (strFirstEventHTML, strFutureEventsHTML, strFirstEventText, strFutureEventsText)

def GetPersonDetails(strShortName, objHere):
    return objHere.restrictedTraverse("/MCI/Persons/" + strShortName)

def GetReviewerDetails(objReview, objHere):
    strResult = ""

    objReviewAuthor = GetPersonDetails(objReview.ReviewAuthor, objHere)

    if objReview.ReviewRead:
        objReviewReader = GetPersonDetails(objReview.ReviewRead, objHere)
        strResultHTML = """This review written by %s, based on an interview with %s who was the reader<br><br>
                    %s<br><br>
                    %s""" % (GeneralFunctions.FormatForEmail(GeneralFunctions.PersonPlusLink(objHere, objReview.ReviewAuthor)), 
                            GeneralFunctions.FormatForEmail(GeneralFunctions.PersonPlusLink(objHere, objReview.ReviewRead)),
                        objReviewAuthor.ShortBio,
                        objReviewReader.ShortBio)
        strResultText = """This review written by %s, based on an interview with %s who was the reader
        
%s

%s""" % (objReviewAuthor.PersonName, objReviewReader.PersonName, 
                        GeneralFunctions.HTMLToText(objReviewAuthor.ShortBio),
                        GeneralFunctions.HTMLToText(objReviewReader.ShortBio))
    else:
        strResultHTML = """This review written by %s.<br><br>
        
                    %s""" % (GeneralFunctions.FormatForEmail(GeneralFunctions.PersonPlusLink(objHere, objReview.ReviewAuthor)), objReviewAuthor.ShortBio)
        strResultText = """This review written by %s<br><br>
                    %s""" % (objReviewAuthor.PersonName, GeneralFunctions.HTMLToText(objReviewAuthor.ShortBio))
        
    return (strResultHTML, strResultText)

def BuildReviewText(objReview, objHere):
    # Read the template
    # Insert the fields into the template
    # Return the results
    strHTMLTemplate = GetTemplate(objHere, "BookReviewHTML")
    strTextTemplate = GetTemplate(objHere, "BookReviewText")

    strAuthor = objReview.Authors
    (strReviewHTML, strReviewText) = GetReviewDetails(objReview, objHere)
    (strFirstEventHTML, strFutureEventsHTML, strFirstEventText, strFutureEventsText) = GetEventsDetails(objHere)
    strReviewNumber = "%s" % objReview.ReviewNumber
    strBookTitle = objReview.BookTitle
    (strAboutReviewersHTML, strAboutReviewersText) = GetReviewerDetails(objReview, objHere)
    if objReview.ReviewRead:
        strPlural = "s"
    else:
        strPlural = ""
    strHTMLResult = strHTMLTemplate % {'ReviewNumber': strReviewNumber,
                               'BookTitle': strBookTitle,
                               'Author': strAuthor, 
                               'Review': strReviewHTML,
                               'FirstEvent': strFirstEventHTML,
                               'FutureEvents': strFutureEventsHTML,
                               'Reviewers': strAboutReviewersHTML,
                               'Plural1': strPlural,
                               'Plural2': strPlural}

    strTextResult = strTextTemplate % {'ReviewNumber': strReviewNumber,
                               'BookTitle': strBookTitle,
                               'Author': strAuthor, 
                               'Review': strReviewText,
                               'FirstEvent': strFirstEventText,
                               'FutureEvents': strFutureEventsText,
                               'Reviewers': strAboutReviewersText,
                               'Plural1': strPlural,
                               'Plural2': strPlural}

    return (strHTMLResult, strTextResult)
    
def GetImage(strFullName, strShortName):
    objFile = open("/var/zope/Extensions/" + strFullName, 'rb')
    objImage = MIMEImage(objFile.read(), name=strFullName)
    objFile.close()
    objImage.add_header('Content-ID', '<123' + strShortName + '@forcoaches.com>')
    return objImage

def BuildReviewEmail(strReviewHTML, strReviewText, objReview, strFromAddress, strFromName, strToAddress, blnIncludeAmazonCoUk, blnIncludeAmazonCom):
    dictImages = {'DropSmall3.jpg':'DropSmall3',
            'BooksForCoaches4.gif':'BooksForCoaches'}
    objEmail = MIMEMultipart('related')
    objEmail['Subject'] = objReview.BookTitle
    objEmail['From'] = '"%s" <%s>' % (strFromName, strFromAddress)
    objEmail['To'] = strToAddress
    objMessage = MIMEMultipart('alternative')
    objHTMLMessage = MIMEText(strReviewHTML, 'html')
    objHTMLMessage.replace_header('Content-Transfer-Encoding', 'quoted-printable')
    objTextMessage = MIMEText(strReviewText)
    objMessage.attach(objHTMLMessage)
    objMessage.attach(objTextMessage)
    objEmail.attach(objMessage)
    
    for strFullName in dictImages.keys():
        objEmail.attach(GetImage(strFullName, dictImages[strFullName]))
        
    if blnIncludeAmazonCoUk:
        objEmail.attach(GetImage("AmazonCoUk.gif", "AmazonCoUk"))
        
    if blnIncludeAmazonCom:
        objEmail.attach(GetImage("AmazonCom.gif", "AmazonCom"))

    return objEmail

def GetTemplate(objHere, strName):
    strTemplate = objHere.restrictedTraverse("/MCI/Templates/%s" % strName).data + ""
    
    return strTemplate

def SendNiceEmail(objMessage, strFromAddress, strFromName, strToAddress):
    objSMTP = smtplib.SMTP()
    objSMTP.connect()
    objSMTP.sendmail('"%s" <%s>' % (strFromName, strFromAddress), strToAddress, objMessage.as_string())
    objSMTP.close()

def SendBookReview(objReview, objHere, strToAddress):
    strFromAddress = "Coen@MentorCoaches.com"
    strFromName = "Coen de Groot"

    (strReviewHTML, strReviewText) = BuildReviewText(objReview, objHere)
    objMessage = BuildReviewEmail(strReviewHTML, strReviewText, objReview, strFromAddress, strFromName, strToAddress, objReview.OnAmazonCom, objReview.OnAmazonCoUk)
    SendNiceEmail(objMessage, strFromAddress, strFromName, strToAddress)

def SendPrettyEmail(strEmailAddress, strMessage, strSubject, objHere, strTextMessage=""):
    strFromAddress = "Coen@MentorCoaches.com"
    strFromName = "Coen de Groot"
    strHTMLTemplate = objHere.restrictedTraverse("/MCI/Templates/GeneralMessageHTML").data + ""
    strTextTemplate = objHere.restrictedTraverse("/MCI/Templates/GeneralMessageText").data + ""
    strHTMLBody = strHTMLTemplate % strMessage
 
    if strTextMessage:
        strTextBody = strTextMessage
    else:
        strTextBody = strTextTemplate % GeneralFunctions.HTMLToText(strMessage)

    objEmail = MIMEMultipart('related')
    objEmail['Subject'] = strSubject
    objEmail['From'] = '"%s" <%s>' % (strFromName, strFromAddress)
    objEmail['To'] = strEmailAddress
    objMessage = MIMEMultipart('alternative')
    objHTMLMessage = MIMEText(strHTMLBody, 'html')
    objHTMLMessage.replace_header('Content-Transfer-Encoding', 'quoted-printable')
    objTextMessage = MIMEText(strTextBody)
    objMessage.attach(objHTMLMessage)
    objMessage.attach(objTextMessage)
    objEmail.attach(objMessage)
    
    objEmail.attach(GetImage('DropSmall3.jpg', 'DropSmall3'))
    SendNiceEmail(objEmail, strFromAddress, strFromName, strEmailAddress)
 
