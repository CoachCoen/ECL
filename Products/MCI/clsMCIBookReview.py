import OFS.Folder
import Globals
from Functions import *

import LocalPaths

from libDatabase import SearchOne
from libDatabase import SearchMany

class MCIBookReview(OFS.Folder.Folder):
    "MCIBookReview class"
    meta_type = 'MCIBookReview'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('BookTitle', '', 'string')
        self.manage_addProperty('ReviewNumber', 0, 'int')
        self.manage_addProperty('Authors', '', 'string')
        self.manage_addProperty('Issue', '', 'string')
        self.manage_addProperty('AmazonNumber', '', 'string')
        self.manage_addProperty('ReviewAuthor', 'AnthonyWarren', 'string')
        self.manage_addProperty('ReviewRead', 'Coen', 'string')
        self.manage_addProperty('ReviewContents', '', 'text')
        self.manage_addProperty('ReviewPublished', '2000/01/01', 'date')
        self.manage_addProperty('OtherAffiliateLink', '', 'text')
        self.manage_addProperty('OtherShoppingLink', '', 'text')
        self.manage_addProperty('ReviewSummary', '', 'text')
        self.manage_addProperty('SubTitle', '', 'string')
        self.manage_addProperty('OnAmazonCom', True, 'boolean')
        self.manage_addProperty('OnAmazonCoUk', True, 'boolean')
        self.manage_addProperty('AmazonComNumber', '', 'string')
        self.manage_addProperty('IsPublished', False, 'boolean')
        self.manage_addProperty('ReviewId', '', 'string')

    def index_html(self):
        return self.unrestrictedTraverse('MainTemplate')

    def AuthorName(self):
        if self.Author == 'Marianne':
            return 'Marianne Craig'
        return ''

    def HTMLTitle(self):
        return "Books for Coaches - %s" % self.BookTitle

    def GetAmazonComNumber(self):
        if self.AmazonComNumber:
            return self.AmazonComNumber
        return self.AmazonNumber

    def HowToBuy(self):
        strResult = ""
        if self.OnAmazonCoUk:
            strResult = strResult + """<a href="http://www.amazon.co.uk/exec/obidos/ASIN/%s/mentorcoaches-21" target="_blank">Buy 
                    this book at Amazon.co.uk</a><br>
        """ % self.AmazonNumber

        if self.OnAmazonCom:
            strResult = strResult + """<a href="http://www.amazon.com/exec/obidos/ASIN/%s/mentorcoaches-20" target="_blank">Buy 
                        this book at Amazon.com</a><br>
        """ % GetAmazonComNumber(self)

        if self.OtherShoppingLink:
            strResult = strResult + """You can buy this book at <a href="http://%s" target="_blank">%s</a><br>
        """ % (self.OtherShoppingLink, self.OtherShoppingLink)
        return strResult

    def HowToBuyWithImages(self):
        strResult = ""

        if self.OnAmazonCoUk or self.OnAmazonCom:
            strResult = strResult + """
                <table width="100%" border="0" cellspacing="0" cellpadding="5">
                        <tr> 
        """
    
            if self.OnAmazonCoUk:
                strResult = strResult + """<td class="MainText"><a href="http://www.amazon.co.uk/exec/obidos/ASIN//mentorcoaches-21"   target="_blank"><img src="/images/AmazonCoUk.gif" width="100" height="35" border="0"><br>
                            Buy this book at Amazon.co.uk</a></td>
        """ % self.AmazonNumber

            if self.OnAmazonCom:
                strResult = strResult + """<td class="MainText"><a href="http://www.amazon.com/exec/obidos/ASIN/%s/mentorcoaches-20" target="_blank"><img src="/images/AmazonCom.gif" width="90" height="28" border="0"><br>
                            Buy this book at Amazon.com</a></td>
                        </tr>
        """ % GetAmazonComNumber(self)
            strResult = strResult + """</tr>
                          </table>
            """
    
        if self.OtherShoppingLink:
            strResult = strResult + """You can buy this book at <a href="http://%s" target="_blank">%s</a><br>
        """ % (self.OtherShoppingLink, self.OtherShoppingLink)
    
        return strResult

    def PageContents(self):
        if self.ReviewPublished > DateTime():
            return """
            <b>Author(s):</b> %(Authors)s<br>
            <br>
            <b>Summary</b>: %(Summary)s<br><br>
            The full review is due %(DueDate)s<br><br>
            <form name="Form" method="post" action="/About/ThankYou">
                <table width="100%" border="0" cellspacing="0" cellpadding="3" class="TableWithBorder">
                    <tr> 
                        <td class="MainText" nowrap>Please make sure I receive this review when it comes out<br>
                            <b>Subscribe me</b> to <br>
                            <input type="hidden" name="FormTypeDueBookReview" value="Yes">
                            <input type="checkbox" name="SubscribeToBooksForCoaches" value="Yes" checked> &quot;<a href="/Books"   class="MenuItem">Books for Coaches</a>&quot;<br>
                            <input type="checkbox" name="SubscribeToNewsletter" value="Yes">&quot;<a href="/Newsletter" class="MenuItem">The Mentor Coach</a>&quot;<br>
                        </td>
                    </tr>
                    <tr> 
                        <td class="MainText"> 
                            <input type="text" name="EmailAddress" value="My email address" size="40">
                        </td>
                    </tr>
                    <tr> 
                        <td class="MainText"> 
                            <input type="submit" name="Submit" value="Submit">
                        </td>
                    </tr>
                </table>
            </form>
            %(BuyWithImages)s<br><br>
            %(PrevAndNext)s""" % {'Authors': self.Authors,
                    'Summary': self.ReviewSummary,
                    'DueDate': self.ReviewPublished.strftime('%A %d %B %Y'),
                    'BuyWithImages': self.HowToBuyWithImages(),
                    'PrevAndNext': self.PreviousAndNextReviewLinks()}
        else:
            return """
            <b>Author(s):</b> %(Authors)s<br>
            <b>Issue:</b> %(Issue)s<br>
            %(ReviewerInfo)s<br>
            %(HowToBuy)s<br><br>
            %(ReviewContents)s<br><br>
            %(BuyWithImages)s<br><br>
            %(PrevAndNext)s
            """ % {'Authors': self.Authors,
                'Issue': self.Issue,
                'ReviewerInfo': self.ReviewerInfo(),
                'HowToBuy': self.HowToBuy(),
                'ReviewContents': FormatLinksForHTML(self.ReviewContents),
                'BuyWithImages': self.HowToBuyWithImages(),
                'PrevAndNext': self.PreviousAndNextReviewLinks()}

    def PageTitle(self):
        return "Book Review %s" % self.ReviewNumber

    def PageTitle2(self):
        strResult = self.BookTitle
        if self.SubTitle:
            strResult = strResult + """<br>
        %s""" % self.SubTitle
        return strResult
        
    def PreviousAndNextReviewLinks(self):
    
        blnFirstReview = True
        blnLastReview = True

        for objBookReview in self.unrestrictedTraverse('/Date/MCI/Books/Reviews').objectValues(['M2BookReview']):
            if objBookReview.ReviewNumber == self.ReviewNumber + 1:
                 strNextLink = objBookReview.absolute_url()
                 blnLastReview = False
            if objBookReview.ReviewNumber == self.ReviewNumber - 1:
                 strPreviousLink = objBookReview.absolute_url()
                 blnFirstReview = False

        strResult = ""
        if not blnFirstReview:
            strResult = strResult + '<a href="' + strPreviousLink + '">&lt; Previous review</a>'
        if not blnLastReview:
            if len(strResult) > 0:
                strResult = strResult + "&nbsp;&nbsp;&nbsp;&nbsp;--&nbsp;&nbsp;&nbsp;&nbsp;"
        strResult = strResult + '<a href="' + strNextLink + '">Next Review &gt</a>'

        return strResult

    def ReviewBy(self):
        if self.ReviewRead:
            objReviewRead = SearchOne(self, 'MCIPerson', 'PersonId', self.ReviewRead)
        else:
            objReviewRead = None

        if self.ReviewAuthor:
            objReviewAuthor = SearchOne(self, 'MCIPerson', 'PersonId', self.ReviewAuthor)
        else:
            objReviewAuthor = None
        return (objReviewRead, objReviewAuthor)

    def ReviewInfo(self):
        (objReviewRead, objReviewAuthor) = self.ReviewBy()
        strResult = ""
        if objReviewRead:
            strResult = strResult + "<b>Book read by:</b> %s" % objReviewRead.NamePlusLink()

        if objReviewAuthor:
            strResult = strResult + "<b>Review written by:</b> %s" % objReviewAuthor.NamePlusLink()
        return strResult

    def ShowOnWebsite(self, intBookId):
        (objReviewRead, objReviewAuthor) = self.ReviewBy()
        (strReviewRead, strReviewAuthor) = ("", "")
        if objReviewRead:
            strReviewRead = "<b>Book read by:</b> %s<br>" % objReviewRead.NamePlusLink()
    
        if objReviewAuthor:
            strReviewAuthor = "<b>Review written by:</b> %s<br>" % objReviewAuthor.NamePlusLink()

        lstOtherBooks = SearchMany(self, 'MCIBook', 'Review', self.id)

        strOtherBooks = ""
        if lstOtherBooks and len(lstOtherBooks) > 1:
            strOtherBooks = """<br><span class="PageSubTitle">Also mentioned in this review</span><br>
                <table width="100%" border="0" class="MainText" cellpadding="0" cellspacing="0">
                """
            for objOtherBook in lstOtherBooks:
                if objOtherBook.id <> intBookId:
                    strDetails = """<a href="/Books/ShowBook?BookId=%s" class="MenuItem"><b>%s</b> by %s</a>""" % (objOtherBook.id, objOtherBook.GetFullTitle(), objOtherBook.GetAuthors())
                    strOtherBooks = strOtherBooks + """<tr>
                <td>&nbsp;&nbsp;</td>
                <td width="100%%">%s</td>
            </tr>""" % strDetails
            strOtherBooks = strOtherBooks + "</table>"
   
        strReviewContents = self.ReviewContents
        strResult = """
        <span class="PageTitle">Book Review</span><br>
        %s
        %s
        %s
        %s""" % (strReviewRead, strReviewAuthor, strOtherBooks, strReviewContents)
        return strResult

def addMCIBookReviewForm(self):
    "New MCIBookReview form"
    return GenericAddForm('MCIBookReview')

def addMCIBookReview(self, id):
    "New MCIBookReview action"
    objNewMCIBookReview = MCIBookReview(id)
    self._setObject(id, objNewMCIBookReview)
    
    return "New MCIBookReview created."

