import OFS.Folder
import Globals
from Functions import *
from libDatabase import SearchOne

class MCINewsletter(OFS.Folder.Folder):
    "MCINewsletter class"
    meta_type = 'MCINewsletter'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('DatePublished', '2000/01/01', 'date')
        self.manage_addProperty('Author', '', 'string')
        self.manage_addProperty('ShortTitle', '', 'string')
        self.manage_addProperty('EditorsIntro', '', 'text')
        self.manage_addProperty('Contents', '', 'text')
        self.manage_addProperty('FirstParagraph', '', 'text')
        self.manage_addProperty('StopPress', '', 'text')
        self.manage_addProperty('IssueNumber', 0, 'int')
        self.manage_addProperty('NextEventTitle', '', 'string')
        self.manage_addProperty('NextEventDate', '', 'string')
        self.manage_addProperty('NextEventTime', '6pm UK time, 19:00 Central European Time, by telephone', 'string')
        self.manage_addProperty('NextEventDetails', '', 'text')
        self.manage_addProperty('FutureEvents', '', 'text')
        self.manage_addProperty('FullTitle', '', 'string')
        self.manage_addProperty('IncludeEndImage', True, 'boolean')
        self.manage_addProperty('AuthorLink', '', 'string')

    def index_html(self):
        return self.unrestrictedTraverse('MainTemplate')

    def AuthorName(self):
        if self.Author == 'Marianne':
            return 'Marianne Craig'
        return ''

    def HTMLTitle(self):
        return "Newsletter - %s" % self.FullTitle

    def PageContents(self):
        objPerson = SearchOne(self, 'MCIPerson', 'PersonId', self.Author)
        strPersonPlusLink = objPerson.NamePlusLink()
        strResult = """Written by %s<br><br>
%s<br><br>
    %s""" % (strPersonPlusLink, self.Contents, self.PrevAndNextLinks())
        return strResult

    def PageTitle(self):
        return self.FullTitle

    def PageTitle2(self):
        return """"The Mentor Coach", Issue %s""" % self.IssueNumber

    def PrevAndNextLinks(self):
        strNextId = ""
        strPrevId = ""
    
        for objNewsletter in self.unrestrictedTraverse('..').objectValues('MCINewsletter'):
            if objNewsletter.IssueNumber == self.IssueNumber + 1:
                strNextId = objNewsletter.id
    
            if objNewsletter.IssueNumber == self.IssueNumber - 1:
                strPrevId = objNewsletter.id

        lstResult = []
    
        if strPrevId:
            lstResult.append("""<a href="/Newsletters/ShowOneNewsletter?Id=%s">&lt; Previous Newsletter</a>""" % strPrevId)

        if strNextId:
            lstResult.append("""<a href="/Newsletters/ShowOneNewsletter?Id=%s">Next Newsletter &gt;</a>""" % strNextId)

        return "&nbsp;&nbsp;&nbsp;&nbsp;--&nbsp;&nbsp;&nbsp;&nbsp;".join(lstResult)


def addMCINewsletterForm(self):
    "New MCINewsletter form"
    return GenericAddForm('MCINewsletter')

def addMCINewsletter(self, id):
    "New MCINewsletter action"
    objNewMCINewsletter = MCINewsletter(id)
    self._setObject(id, objNewMCINewsletter)
    
    return "New MCINewsletter created."

