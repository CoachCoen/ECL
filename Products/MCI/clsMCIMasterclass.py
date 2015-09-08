import OFS.Folder
import Globals
from Functions import *
import DateTime

from libConstants import cnEmptyDate

def IsPlural(intNumber):
    if intNumber == 1:
        return ""
    return "s"

class MCIMasterclass(OFS.Folder.Folder):
    "MCIMasterclass class"
    meta_type = 'MCIMasterclass'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('ClassDate', cnEmptyDate, 'date')
        self.manage_addProperty('ClassTime', '', 'string')
        self.manage_addProperty('ClassTitle', '', 'string')
        self.manage_addProperty('Description', '', 'text')
        self.manage_addProperty('BridgeNumber', '', 'string')
        self.manage_addProperty('BridgePin', '', 'string')
        self.manage_addProperty('BridgeInstructions', '', 'text')
        self.manage_addProperty('BackupBridgeNumber', '', 'string')
        self.manage_addProperty('BackupBridgePin', '', 'string')
        self.manage_addProperty('BackupBridgeInstructions', '', 'text')
        self.manage_addProperty('ClassInstructions', '', 'text')
        self.manage_addProperty('Review', '', 'text')
        self.manage_addProperty('ReviewPosted', cnEmptyDate, 'date')
        self.manage_addProperty('ReadyToPublish', False, 'boolean')
        self.manage_addProperty('ReviewWrittenBy', '', 'string')
        self.manage_addProperty('InstructionsReadyToSend', False, 'boolean')
        self.manage_addProperty('Cancelled', False, 'boolean')
        self.manage_addProperty('CancelMessage', '', 'text')
        self.manage_addProperty('Notes', '', 'text')
        self.manage_addProperty('NotesBy', '', 'string')
        self.manage_addProperty('NotesAdditional', '', 'string')
        self.manage_addProperty('ClassRecording', '', 'string')
        self.manage_addProperty('RecordingSize', 0, 'int')
        self.manage_addProperty('RecordingComments', '', 'text')
        self.manage_addProperty('ClassRecording2', '', 'string')
        self.manage_addProperty('RecordingSize2', 0, 'int')
        self.manage_addProperty('RecordingComments2', '', 'text')
        self.manage_addProperty('HTMLTitle', 'Masterclasses', 'string')
        self.manage_addProperty('IncludeEndImage', True, 'boolean')
        self.manage_addProperty('SourceId', '', 'string')

    def index_html(self):
            "Show details"
            return self.unrestrictedTraverse('MainTemplate')

    def GetPresentersList(self, blnIncludeBios = False):
        strResult = ""
        for objPresenter in self.objectValues('MCIPresenter'):
            if objPresenter.MCIPartner:
                strDetails = """<a href="%s">%s</a>""" % (objPresenter.Website, objPresenter.PresenterName)
            else:
                strDetails = objPresenter.PresenterName
            if objPresenter.PresenterTitle:
                strDetails = strDetails + ", " + objPresenter.PresenterTitle
            if not objPresenter.MCIPartner:
                if objPresenter.Website:
                    strDetails += """, <a href="http://%s" target="_blank">%s</a></span>""" % (objPresenter.Website, objPresenter.Website)
                else:
                    if objPresenter.EmailAddress:
                        strDetails = strDetails + """<span class="MainText">, <a href="mailto:%s">%s</a></span>""" % (objPresenter.EmailAddress, objPresenter.EmailAddress)

            strResult = strResult + strDetails + "<br>\n"
    
            if blnIncludeBios and objPresenter.Bio:
                strResult = strResult + objPresenter.Bio + "<br><br>"
        return strResult

    def GetBios(self):
        strResult = ""
        for objPresenter in self.objectValues('MCIPresenter'):
            if objPresenter.Bio:
                strResult = strResult + """
                 <tr>
                   <td class="MainText">%s</td>
                 </tr>""" % objPresenter.Bio
        return strResult

    def GetClassTime(self):
        if self.ClassTime:
            return self.ClassTime
        else:
            return "6pm UK time, 19:00 Central European Time, 1pm Eastern Standard Time"

    def BlockForPastList(self):
        strResult = """<tr><td colspan="2"><a href="/Masterclasses/ShowMasterclass?Id=%(Id)s" class="MenuItem"><span class="PageSubTitle">%(Title)s</span>, %(Date)s</a></td></tr>
<tr><td width="5%%">&nbsp;&nbsp;&nbsp;</td><td width="95%%">%(Presenter)s""" % {'Id': self.id,
    'Title': self.ClassTitle,
    'Date': self.ClassDate.strftime("%A %d %B %Y"),
    'Presenter': self.PlainPresentersList()}
        if self.Notes:
            strResult += """<br>
<a href="/Masterclasses/ShowMasterclass?Id=%s" class="MenuItem"><b>Read the notes</b></a>""" % self.id
        if self.ClassRecording:
            strResult += """<br>
<a href="/Masterclasses/ShowMasterclass?Id=%s" class="MenuItem"><b>Listen to the recording</b></a>""" % self.id
        strResult += "<br><br></td></tr>"
        return strResult

    def Advert(self):
        strPresenters = self.GetPresentersList()
        strClassTime = self.GetClassTime()
        strBios = GetBios(self)

        strResult = """<html>
    <head>
    <title>Untitled Document</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <STYLE TYPE="text/css">
    .MainTextWithLine { font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #000000 ; border: 1px #000000 solid}
    .MainText { font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #000000}
    .PageSubTitle { font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: bold; color: #EE5100 }
    .PageTitle {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 18px; font-weight: normal; color: #EE5100}
    .Testimonial { font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #000000 ; font-style: italic}
    .Quote { font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: 700; color: #000000 ; font-style: italic}
    a.WhiteLink:link {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #FFFFFF; text-decoration: none}
    a.WhiteLink:visited {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #FFFFFF; text-decoration: none}
    a.WhiteLink:hover {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #FFFFFF; text-decoration: underline}
    a.BlackLink:link {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #EE5100; text-decoration: none}
    a.BlackLink:visited {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #EE5100; text-decoration: none}
    a.BlackLink:hover {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px; font-weight: normal; color: #EE5100; text-decoration: underline}
    </style>
    </head>

<body bgcolor="#FFFFFF" text="#000000">
<table width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr> 
    <td width="45%">&nbsp;</td>
    <td> 
      <table width="600" border="0" cellspacing="0" cellpadding="0" class="MainTextWithLine">

        <tr>
          <td><a href="http://www.MentorCoaches.com"><img src="images/DropSmall3.jpg" width="600" height="90" border="0"></a></td>
        </tr>
        <tr>
          <td>&nbsp;</td>
        </tr>
        <tr>
          <td>
            <table width="100%" border="0" cellspacing="0" cellpadding="5">

              <tr> 
                <td class="MainText"> 
                  <p>Mentor Coaches International would like to announce another 
                    superb Coaching Masterclass</p>
                  <table width="100%" border="0" cellspacing="0" cellpadding="5" class="TableWithBorder">
                    <tr> 
                      <td colspan="2" class="PageTitle"><dtml-var ClassTitle><br>
          <span class="PageSubTitle">%(Presenters)s</span>
          </td>
                    <tr> 
                      <td class="MainText"> 
                        <p><b>%(ClassDate)s</b>, free<br>
                          %(ClassTime)s</p>
                        </td>
                    </tr>

                    <tr> 
                      <td class="MainText">%(Description)s</td>
                    </tr>
                    <tr>
                      <td class="MainText">%(Bios)s

                      </td>

                    </tr>
                    <tr> 
                      <td class="MainText">To book, visit <a href="http://www.MentorCoaches.com/Masterclasses.html">the 
                        website</a>. Or if you don't have easy website access, 
                        email us at <a href="mailto:masterclasses@mentorcoaches.com">masterclasses@mentorcoaches.com</a> 
                        and we'll do it for you. </td>
                    </tr>
                  </table>

                  <p>We look forward to meeting you on the Masterclass.</p>
                  <p>Warmly,</p>
                  <p><br>
                    The Mentor Coaches International Team</p>
                  <p><i>Coen de Groot, Edna Murdoch, Marianne Craig, Michael Sanson</i></p>
                </td>
              </tr>

              <tr>
                <td class="MainText" bgcolor="#336699"> 
                  <p><b><font color="#FFFFFF">Mentor Coaches </font></b><font color="#FFFFFF">International</font><b><font color="#FFFFFF"> 
                    &nbsp;&nbsp;-&nbsp;&nbsp; Guiding coaches on the path to mastery.<br>
                    </font></b><font color="#FFFFFF"><b>e: <a href="mailto:info@mentorcoaches.com" Class="WhiteLink">info@mentorcoaches.com</a> 
                    &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;w: <a href="http://www.mentorcoaches.com" Class="WhiteLink">www.mentorcoaches.com</a></b></font></p>

                  </td>
              </tr>
            </table>
          </td>
        </tr>
      </table></td>
    <td width="45%">&nbsp;</td>
  </tr>
</table>

</body>
</html>
""" % {'Presenters': strPresenters,
        'ClassDate': self.ClassDate.strftime("%A %d %B %Y"),
        'ClassTime': strClassTime,
        'Description': self.Description,
        'Bios': strBios}
        return strResult

    def ClassLive(self):
        if self.ClassDate > DateTime.DateTime('1 Jan 2000') and \
            self.ClassDate + 1 > DateTime.DateTime() and self.ReadyToPublish:
            return True
        return False

    def MasterclassDetails(self):
        strResult = "Title: %s<br>\n" % self.ClassTitle
    
        if self.ClassTitle:
            strClassTitle = """
            <tr> 
              <td colspan="2" class="PageSubTitle"><a name="%s"></a>%s</td>
            </tr>""" % (self.id, self.ClassTitle)
        else:
            strClassTitle = ""
    
        strClassDate = self.ClassDate.strftime("%A %d %B %Y")
        strClassTime = self.GetClassTime()
        strPresenters = self.GetPresentersList()

        if self.Cancelled:
            strCancellationMessage = """
            <tr>
              <td>&nbsp;</td>
              <td class="PageSubTitle">%s</td>
            </tr>""" % self.CancelMessage
            strBios = ""
            strBookNow = ""
        else:
            strCancellationMessage = ""
            strBios = self.GetBios()
            strBookNow = """
            <tr>
              <td class="MainText">&nbsp;</td>
              <td class="MainText"><a class = "MenuItem" href="#BookNow">Free, Book now</a></td>
            </tr>
        """

        if self.Description and not self.Cancelled:
            strDescription = """
            <tr> 
              <td class="MainText">&nbsp;</td>
              <td class="MainText">%s</td>
            </tr>""" % self.Description
        else:
            strDescription = ""

        if not self.ClassLive():
            strResult = strResult + """
          <table width="100%" border="0" cellspacing="0" cellpadding="5" class="TableWithBorder">
            %(ClassTitle)s
            <tr> 
              <td class="MainText">&nbsp;</td>
              <td class="MainText"><b>%(ClassDate)s</b>, free<br>%(ClassTime)</td>
            </tr>
            <tr> 
              <td class="MainText">&nbsp;</td>
              <td class="WhiteEmphasisedText">%(Presenters)s</td>
            </tr>
            %(CancellationMessage)s
            %(Description)s
            %(Bios)s
            %(BookNow)s
          </table>
          <br>
    """ % {'ClassTitle' : strClassTitle, 
        'ClassDate': strClassDate,
        'ClassTime': strClassTime,
        'Presenters': strPresenters,
        'CancellationMessage': strCancellationMessage,
        'Description': strDescription,
        'Bios': strBios,
        'BookNow': strBookNow}    

        return strResult

    def ShowFullDetails(self):
        strResult = self.ClassDate.strftime("%A %d %B %Y") + "<br>"

        if self.ClassLive():
            strResult = strResult + "Book now"
        else:
            if self.Cancelled:
                strResult = strResult + "<b>Class cancelled</b>: %s" % self.CancelMessage
            else:
                if self.Notes:
                    strResult = strResult + "<p>notes below</p>"

        if self.ClassRecording:
            strResult = strResult + """
    <br><br><a href="http://www.ForCoaches.com/Masterclasses/%s" class="MenuItem"><b>Click here to listen to the recording of this Masterclass (%sMB download)</b></a>""" % (self.ClassRecording, self.RecordingSize)
    
        if self.RecordingComments:
            strResult = strResult + "<br>%s" % self.RecordingComments

        if self.ClassRecording2:
            strResult = strResult + """
    <br><br><a href="http://www.ForCoaches.com/Masterclasses/%s" class="MenuItem"><b>Click here to listen to the second recording of this Masterclass (%sMB download)</b></a>""" % (self.ClassRecording2, self.RecordingSize2)
    
        if self.RecordingComments2:
            strResult = strResult + "<br>%s" % self.RecordingComments2

        if self.Description:
            strResult = strResult + """<p class="PageSubTitle">Original class announcement</p>
    %s
    <br>""" % self.Description

        strResult = strResult + """<p class="PageSubTitle">The speaker%s</p>
        """ % IsPlural(self.objectValues('MCIPresenter'))
        strResult = strResult + self.GetPresentersList(True)

        if self.Notes:
            strResult = strResult + """<br><span class="PageTitle2">Masterclass Notes</span><br>
    %s
    """ % self.Notes
     
        return strResult

    def PageTitle(self):
        return self.ClassTitle

    def PlainPresentersList(self):
        lstResult = []
        for objPresenter in self.objectValues('MCIPresenter'):
            strResult = objPresenter.PresenterName
            if objPresenter.PresenterTitle:
                strResult = strResult + ", " + objPresenter.PresenterTitle
            lstResult.append(strResult)
        return ", ".join(lstResult)

def addMCIMasterclassForm(self):
    "New MCIMasterclass form"
    return GenericAddForm('MCIMasterclass')

def addMCIMasterclass(self, id):
    "New MCIMasterclass action"
    objNewMCIMasterclass = MCIMasterclass(id)
    self._setObject(id, objNewMCIMasterclass)
    
    return "New MCIMasterclass created."

