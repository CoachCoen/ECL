import LocalPaths

import datetime
import time

from libBuildHTML import PointURLAtMCI
from libDatabase import GetDataFolder
from libDatabase import SearchOne
from libGeneral import GetParameter

def FindLatestNewsletter(objHere):
    fltLatestDate = datetime.date(2000, 1, 1).toordinal()
    for objNewsletter in GetDataFolder(objHere, 'MCINewsletter').objectValues('MCINewsletter'):
        if (objNewsletter.DatePublished > fltLatestDate) and (objNewsletter.DatePublished <= time.time()):
            fltLatestDate = objNewsletter.DatePublished
            objResult = objNewsletter
    return objResult

def CurrentNewsletter(objHere):
    strId = GetParameter(objHere.REQUEST, 'Id')
    objNewsletter = SearchOne(objHere, 'MCINewsletter', 'id', strId)
    if not objNewsletter:
        objNewsletter = FindLatestNewsletter(objHere)
    return objNewsletter

def ShowLatestNewsletterShort(objHere):
    fltLatestDate = datetime.date(2000, 1, 1).toordinal()
    for objNewsletter in GetDataFolder(objHere, 'MCINewsletter').objectValues():
        if (objNewsletter.DatePublished > fltLatestDate) and (objNewsletter.DatePublished <= time.time()):
            fltLatestDate = objNewsletter.DatePublished
            strShortTitle = objNewsletter.ShortTitle
            strAuthor = objNewsletter.Author
            strURL = PointURLAtMCI(objNewsletter.absolute_url())
            
    strResult = """<a href="%s" class="MenuItem" target="_blank">&quot;%s&quot;<br>by %s<br>&gt; Read newsletter</a>""" % (strURL,
                                                            strShortTitle, 
                                                            strAuthor)
    return strResult

def ShowLatestNewsletter(objHere):
    fltLatestDate = datetime.date(2000, 1, 1).toordinal()
    for objNewsletter in GetDataFolder(objHere, 'MCINewsletter').objectValues(['MCINewsletter']):
        if (objNewsletter.DatePublished > fltLatestDate) and (objNewsletter.DatePublished <= time.time()):
            fltLatestDate = objNewsletter.DatePublished
            strShortTitle = objNewsletter.ShortTitle
            strAuthor = objNewsletter.Author
            objAuthor = SearchOne(objHere, 'MCIPerson', 'PersonId', strAuthor)
            strAuthor = objAuthor.NamePlusLink()
            strFirstParagraph = objNewsletter.FirstParagraph
            strURL = "/Newsletters/ShowOneNewsletter?Id=%s" % objNewsletter.id
            
    strResult = """<a href="%s" class="PageSubTitle">&quot;%s&quot;</a><br>by %s<br>
    <br><a href="%s" class="MenuItem">%s More ....</a>""" % (strURL,
                                                            strShortTitle, 
                                                            strAuthor, 
                                                            strURL,
                                                            strFirstParagraph)
    return strResult

def FormatOneNewsletter(objNewsletter):
    strURL = objNewsletter.absolute_url()
    strAuthor = objNewsletter.Author
    objAuthor = SearchOne(objNewsletter, 'MCIPerson', 'PersonId', strAuthor)
    strLink = objAuthor.NamePlusLink()
    return """
<hr size="1">
                  <table width="100%%" border="0" cellspacing="0" cellpadding="5">
                    <tr> 
                      <td colspan="2"><a href="/Newsletters/ShowOneNewsletter?Id=%(Id)s" class="PageSubTitle">Issue 
                        %(IssueNumber)s - %(ShortTitle)s</td>
                    </tr>
                    <tr> 
                      <td class="MainText">&nbsp;</td>
                      <td class="MainText">By %(Link)s</td>
                    </tr>
                    <tr> 
                      <td class="MainText">&nbsp;</td>
                      <td class="MainText">%(FirstParagraph)s&nbsp;&nbsp;<a href="/Newsletters/ShowOneNewsletter?Id=%(Id)s">More ...</a></p>
                      </td>
                    </tr>
                  </table>
""" % {'Id': objNewsletter.id,
        'IssueNumber': objNewsletter.IssueNumber,
        'ShortTitle': objNewsletter.ShortTitle,
        'Link': strLink,
        'FirstParagraph': objNewsletter.FirstParagraph}

def NewsletterList(objHere):
    dictNewsletters = {}
    objNewsletters = GetDataFolder(objHere, 'MCINewsletter')
    for objNewsletter in objNewsletters.objectValues('MCINewsletter'):
        dictNewsletters[objNewsletter.IssueNumber] = FormatOneNewsletter(objNewsletter)
    strResult = ""
    lstIssues = dictNewsletters.keys()
    lstIssues.sort()
    for intIssue in lstIssues:
        strResult = strResult + dictNewsletters[intIssue]
    return """<span class="PageTitle2">&quot;The Mentor Coach&quot; - Newsletter Archive</span><br>""" + strResult
