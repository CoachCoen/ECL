import OFS.Folder
import Globals
from Functions import *

class MCIBook(OFS.Folder.Folder):
    "MCIBook class"
    meta_type = 'MCIBook'

    def __init__(self, id):
        "Initialization."
        self.id = id
        self.manage_addProperty('Title', '', 'string')
        self.manage_addProperty('SubTitle', '', 'string')
        self.manage_addProperty('Publisher', '', 'string')
        self.manage_addProperty('Year', 0, 'int')
        self.manage_addProperty('Pages', 0, 'int')
        self.manage_addProperty('Format', '', 'string')
        self.manage_addProperty('ISBN', '', 'string')
        self.manage_addProperty('OtherLink', '', 'string')
        self.manage_addProperty('OnAmazonCom', False, 'boolean')
        self.manage_addProperty('OnAmazonCoUk', False, 'boolean')
        self.manage_addProperty('AmazonComNumber', '', 'string')
        self.manage_addProperty('AmazonCoUkNumber', '', 'string')
        self.manage_addProperty('ReviewLink', '', 'string')
        self.manage_addProperty('OtherLinkName', '', 'string')
        self.manage_addProperty('CategoriesCorrect', False, 'boolean')
        self.manage_addProperty('DetailsCorrect', False, 'boolean')
        self.manage_addProperty('LinksChecked', False, 'boolean')
        self.manage_addProperty('Authors', [], 'lines')
        self.manage_addProperty('Categories', [], 'lines')
        self.manage_addProperty('ReaderCategories', [], 'lines')
        self.manage_addProperty('SourceId', 0, 'long')
        self.manage_addProperty('Review', '', 'string')

    def index_html(self):
        "Show details"
        return ShowFullDetails(self)

    def GetFullTitle(self):
        if self.SubTitle:
            return self.Title + ": " + self.SubTitle
        else:
            return self.Title

    def GetImageLink(self):
        if self.OnAmazonCom:
            return """<a href="/Books/ShowBook?Id=%s"><img src="http://images.amazon.com/images/P/%s.01.THUMBZZZ.jpg" width=40 height=60 border=0></a>""" % (self.id, self.ISBN)
        elif self.OnAmazonCoUk:
            return """<a href="/Books/ShowBook?Id=%s"><img src="http://images-eu.amazon.com/images/P/%s.01.THUMBZZZ.jpg" width=39 height=60 border=0></a>""" % (self.id, self.ISBN)
        else:
            return ""

    def FullImageLink(self):
        if self.OnAmazonCom:
            return "http://images.amazon.com/images/P/%s.01._AA240_SCLZZZZZZZ_.jpg" % self.ISBN
        elif self.OnAmazonCoUk:
            return "http://images-eu.amazon.com/images/P/%s.02._SCMZZZZZZZ_.jpg" % self.ISBN
        else:
            return ""

    def GetFullImage(self):
        if self.OnAmazonCom:
            return """<img src="http://images.amazon.com/images/P/%s.01._AA240_SCLZZZZZZZ_.jpg" width=240 height=240 border=0 align="left">""" % self.ISBN
        elif self.OnAmazonCoUk:
            return """<img src="http://images-eu.amazon.com/images/P/%s.02._SCMZZZZZZZ_.jpg" width=240 height=240 border=0 align="left">""" % self.ISBN
        else:
            return ""

# on Amazon.co.uk: http://images-eu.amazon.com/images/P/<ISBN>.02._SCMZZZZZZZ_.jpg
# on Amazon.com: http://images.amazon.com/images/P/<ISBN>.01._AA240_SCLZZZZZZZ_.jpg

    def ShoppingLinks(self, blnAbsolute = False):
        (strAmazonCom, strAmazonCoUk, strOther) = ("", "", "")

        if blnAbsolute:
            strAbsolute = "http://www.MentorCoaches.com"
        else:
            strAbsolute = ""

        if self.OnAmazonCom:
            strAmazonCom = """<a href="%s/ShopAt?Id=%s&ShopId=1" class="MenuItem" target="_blank"><span class="PageSubTitle">Buy</span> at Amazon.com</a>""" % (strAbsolute, self.id)
        if self.OnAmazonCoUk:
            strAmazonCoUk = """<a href="%s/ShopAt?Id=%s&ShopId=2" class="MenuItem" target="_blank"><span class="PageSubTitle">Buy</span> at Amazon.co.uk</a>""" % (strAbsolute, self.id)
        if self.OtherLinkName:
            strOther = """<a href="%s/ShopAt?Id=%s&ShopId=3" class="MenuItem" target="_blank"><span class="PageSubTitle">Buy</span> at %s</a>""" % (strAbsolute, self.id, self.OtherLinkName)
        strResult = "<br>".join((strAmazonCom, strAmazonCoUk, strOther))
        return strResult

    def Live(self):
        if self.CategoriesCorrect and \
            self.DetailsCorrect and \
            self.LinksChecked:
            return True
        return False

    def GetAuthors(self):
        return ", ".join(self.Authors)

def addMCIBookForm(self):
    "New MCIBook form"
    return GenericAddForm('MCIBook')

def addMCIBook(self, id):
    "New MCIBook action"
    objNewMCIBook = MCIBook(id)
    self._setObject(id, objNewMCIBook)
    
    return "New MCIBook created."
