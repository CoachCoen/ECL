import LocalPaths

import string
import time
import datetime
import DateTime

from libDatabase import GetDataFolder
from libDatabase import SearchMany
from libDatabase import SearchOne
from libDatabase import GetDOD
from libConstants import cnMCIRoot

from libGeneral import GetParameter

def DoDeleteBook(objHere, strISBN):
    objBook = Search(objHere, 'Book', 'ISBN', 'strISBN')
    if objBook:
        DeleteObject(objBook)
        return "Deleted %s" % strISBN
    else:
        return "Not deleted %s" % strISBN

def DeleteBook(objRequest):
    if objRequest.has_key("DeleteConfirm"):
        strISBN = objRequest["ISBN"]
        return DoDeleteBook(strISBN)
    else:
        return "Please confirm deletion"

def SaveNewBook(objRequest):
    objDatabase = pg.connect(dbname = 'mci')
    objBook = clsBook.Book()
    objBook.GetDataFromForm(objRequest)
    strISBN = objBook.Save(objDatabase, ('Title', 'SubTitle',
        'ISBN', 'Format', 'Pages', 'Year', 'Publisher',
        'Authors', 'ReviewLink', 
        'OnAmazonCom', 'OnAmazonCoUk',
        'AmazonComNumber', 'AmazonCoUkNumber',
        'OtherLink', 'OtherLinkName'))
    CheckOneLinks(objDatabase, objBook.BookId, objBook.ISBN)
    return "ISBN=%s" % strISBN

def UpdateBookDetails(objRequest):
    objDatabase = pg.connect(dbname = 'mci')
    objBook = clsBook.Book()
    objBook.GetDataFromForm(objRequest)
    objBook.Update(objDatabase, ('Title', 'SubTitle',
        'ISBN', 'Format', 'Pages', 'Year', 'Publisher',
        'Authors', 'ReviewLink', 
        'AmazonComNumber', 'AmazonCoUkNumber',
        'OnAmazonCom', 'OnAmazonCoUk',
        'OtherLink', 'OtherLinkName'))
    strSQL = """UPDATE Book 
        SET DetailsCorrect = TRUE,
            LinksChecked = TRUE
        WHERE BookId = %s""" % objBook.BookId
    DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    return ""

def UpdateBookCategories(objRequest):
    objDatabase = pg.connect(dbname = 'mci')
    strSQL = "SELECT BookCategoryId FROM BookCategory"
    objCategory = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    intBookId = int(objRequest["BookId"])
    for lstCategory in objCategory.getresult():
        intCategoryId = lstCategory[0]
        if objRequest.has_key("Category%s" % intCategoryId):
            blnHasCategory = 1
        else:
            blnHasCategory = 0
        BookDatabaseFunctions.SetCategory(objDatabase, intBookId, intCategoryId, blnHasCategory)

    strSQL = "SELECT ReaderCategoryId FROM ReaderCategory"
    objCategory = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    intBookId = int(objRequest["BookId"])
    for lstCategory in objCategory.getresult():
        intCategoryId = lstCategory[0]
        if objRequest.has_key("ReaderCategory%s" % intCategoryId):
            blnHasCategory = 1
        else:
            blnHasCategory = 0
        BookDatabaseFunctions.SetReaderCategory(objDatabase, intBookId, intCategoryId, blnHasCategory)

    strSQL = "SELECT BookRatingId FROM BookRating"
    objRating = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    intBookId = int(objRequest["BookId"])
    for lstRating in objRating.getresult():
        intRatingId = lstRating[0]
        if objRequest.has_key("BookRating%s" % intRatingId):
            blnHasRating = 1
        else:
            blnHasRating = 0
        BookDatabaseFunctions.SetBookRating(objDatabase, intBookId, intRatingId, blnHasRating)

    strSQL = "UPDATE Book SET CategoriesCorrect = TRUE WHERE BookId = %s" % intBookId
    DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)

    return ""

def CreateBookList(objQueryResult):
    strResult = "<table>\n"
    for lstResult in objQueryResult.getresult():
        strFullTitle = GeneralBookFunctions.GetFullTitle(lstResult[0], lstResult[1])
        strResult = strResult + """<tr>
            <td valign="top"><a href="EditOneBook?ISBN=%s">%s</a></td>
            <td>%s</td>
            </tr>
            """ % (lstResult[2], lstResult[2], strFullTitle)
    strResult = strResult + "</table>"
    return strResult

def ListByTitle():
    strResult = ""
    objDatabase = pg.connect(dbname = 'mci')
    strSQL = "SELECT Title, SubTitle, ISBN FROM Book ORDER BY Title, SubTitle"
    objResult = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    strResult = CreateBookList(objResult)
    return strResult

def GetReaderCategories(objDatabase, intBookId):
    strResult = "<table><tr><td>"
    strSQL = """SELECT ReaderCategoryId, Name
        FROM ReaderCategory
        ORDER BY ReaderCategoryId"""
    objReaderCategory = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    for lstReaderCategory in objReaderCategory.getresult():
        strResult = strResult + "%s %s<br>" % (BookDatabaseFunctions.ReaderCategoryTickBox(objDatabase, intBookId, lstReaderCategory[0]), lstReaderCategory[1])
    strResult = strResult + "</td></tr></table>"
    return strResult

def GetBookRatings(objDatabase, intBookId):
    strResult = "<table><tr><td>"
    strSQL = """SELECT BookRatingId, Rating
        FROM BookRating
        ORDER BY BookRatingId"""
    objBookRating = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    for lstBookRating in objBookRating.getresult():
        strResult = strResult + "%s %s<br>" % (BookDatabaseFunctions.BookRatingTickBox(objDatabase, intBookId, lstBookRating[0]), lstBookRating[1])
    strResult = strResult + "</td></tr></table>"
    return strResult

def GetCategories(objDatabase, intBookId):
    strResult = "<table>"
    strSQL = """SELECT BookCategoryId, Name 
        FROM BookCategory
        WHERE SubCategoryOfCategoryId = 0
        ORDER BY BookCategoryId"""
    objCategory = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    for lstCategory in objCategory.getresult():
        strResult = strResult + "<tr><td>%s %s<br>" % (BookDatabaseFunctions.CategoryTickbox(objDatabase, intBookId, lstCategory[0]), lstCategory[1])
        strSQL = """SELECT BookCategoryId, Name
            FROM BookCategory
            WHERE SubCategoryOfCategoryId = %s
            ORDER BY Name""" % lstCategory[0]
        objSubCategory = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
        for lstSubCategory in objSubCategory.getresult():
            strResult = strResult + ".. %s %s<br>" % (BookDatabaseFunctions.CategoryTickbox(objDatabase, intBookId, lstSubCategory[0]), lstSubCategory[1])
        strResult = strResult + "<br></td></tr>"
    strResult = strResult + "</table>"
    return strResult

def OpenBookInBrowser(objDatabase, strISBN):
    strLink = "http://www.amazon.com/exec/obidos/tg/detail/-/%s" % strISBN
    strSQL = "UPDATE WebPageToShow SET URL = '%s', Loaded = FALSE" % strLink
    DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)

def BookForm(objDatabase, objBook, strDetailsStatistics, strCategoriesStatistics, strNext):
    if objBook.BookId > 0:
        strResult = """<form method=post action="EditOneBook?ISBN=%s&Action=UpdateDetails&Next=%s">
    <table>
    <tr><td>Title:</td><td><input type="text" value="%s" name=Title size=70></td></tr>
    <tr><td>Subtitle:</td><td><input type="text" value="%s" name="SubTitle" size=70></td></tr>
    <tr><td>Author(s):</td><td><input type="text" value="%s" name=Authors size=50></td></tr>
    <tr><td>ISBN:</td><td><input type=text" value="%s" name=ISBN></td></tr>
    <tr><td>Format:</td><td><input type="text" value="%s" name=Format>, <input type="text" value="%s" name=Pages size=5> pages</td></tr>
    <tr><td>Published:</td><td><input type="text" value="%s" name=Year size=5> by <input type="text" value="%s" name=Publisher size=40></td></tr>
    <tr><td>On Amazon.com:</td><td><input type="checkbox" %s  name=OnAmazonCom>, <input type="text" value="%s" name=AmazonComNumber></td></tr>
    <tr><td>On Amazon.co.uk:</td><td><input type="checkbox" %s  name=OnAmazonCoUk>, <input type="text" value="%s" name=AmazonCoUkNumber></td></tr>
    <tr><td>Other link:</td><td><input type="text" value="%s" name="OtherLinkName" size=30> address: <input type="text" value="%s" name="OtherLink" size=40></td></tr>
    <tr><td>Review link:</td><td><input type="text" value="%s" name="ReviewLink" size=40><td></tr>
    </table>
    <input type=submit value="Details Correct"> %s
    <input type=hidden name="Action" value="UpdateDetails">
    <input type=hidden name="BookId" value="%s">
    </form>
    <form method=post action="EditOneBook?ISBN=%s&Action=DeleteBook&Next=%s">
    <input type="checkbox" name="DeleteConfirm">
    <input type="hidden" name="ISBN" value="%s">
    <input type=submit value="Delete Book">
    </form>
    """ % (objBook.ISBN, strNext, objBook.Title, objBook.SubTitle, objBook.Authors, objBook.ISBN, objBook.Format, objBook.Pages,
        objBook.Year, objBook.Publisher, 
        DatabaseFunctions.BooleanToCheckbox(objBook.OnAmazonCom),
        objBook.AmazonComNumber, 
        DatabaseFunctions.BooleanToCheckbox(objBook.OnAmazonCoUk),
        objBook.AmazonCoUkNumber,
        objBook.OtherLinkName, objBook.OtherLink, objBook.ReviewLink,
        strDetailsStatistics,
        objBook.BookId,
        objBook.ISBN, strNext, objBook.ISBN)
    strResult = strResult + """<form method=post action="EditOneBook?ISBN=%s&Action=UpdateCategories&Next=%s"><table><tr>""" % (objBook.ISBN, strNext)
    strResult = strResult + "<td valign=top>" + GetCategories(objDatabase, objBook.BookId) + "</td>"
    strResult = strResult + "<td valign=top>" + GetReaderCategories(objDatabase, objBook.BookId) + "<br><br>" + GetBookRatings(objDatabase, objBook.BookId) + '<input type=submit value="Categories Correct"> %s</td>' % strCategoriesStatistics
    strResult = strResult + """<input type=hidden name="BookId" value="%s">
        <input type=hidden name="Action" value="UpdateCategories">""" % objBook.BookId
    strResult = strResult + "</tr></table></form>"
    return strResult

def ExtractISBNFromQuery(strQuery):
    if "ISBN" in strQuery:
        for strSub in string.split(strQuery, "&"):
            if "ISBN" in strSub:
                (strDummy, strISBN) = string.split(strSub, "=")
                strISBN = string.strip(strISBN)
                return strISBN
    return ""

def EditOneBook(strQuery):
    objDatabase = pg.connect(dbname = 'mci')
    objBook = clsBook.Book()
    if 'CheckNextCategories' in strQuery:
        strNext = 'CheckNextCategories'
        strISBN = BookDatabaseFunctions.NextBookToCategorise(objDatabase)
        if not strISBN:
            return "No more books to categorise"
        objBook.Load(objDatabase, strISBN)
        if not objBook:
            return "No book found for ISBN=%s" % strISBN
    elif 'CheckNextDetails' in strQuery:
        strNext = 'CheckNextDetails'
        strISBN = BookDatabaseFunctions.NextBookToCheck(objDatabase)
        if not strISBN:
            return "All books are live"
        objBook.Load(objDatabase, strISBN)
        if not objBook:
            return "No book found for ISBN=%s" % strISBN
    elif 'ISBN' in strQuery:
        strNext = 'Same'
        strISBN = ExtractISBNFromQuery(strQuery)
        if not strISBN:
            return "No ISBN found for query=%s" % strQuery
        if not objBook.Load(objDatabase, strISBN):
            return "No book found for ISBN=%s" % strISBN
    elif 'NewBook' in strQuery:
        return ""
    else:
        return "Incorrect QueryString: %s" % strQuery

    OpenBookInBrowser(objDatabase, strISBN)
    (intTotal, intCategoriesDone, intDetailsDone) = BookDatabaseFunctions.GetStatisticsFromDatabase(objDatabase)
    strDetailsStatistics = "%s out of %s to do, %s done" % ((intTotal-intDetailsDone), intTotal, intDetailsDone)
    strCategoryStatistics = "%s out of %s to do, %s done" % ((intTotal-intCategoriesDone), intTotal, intCategoriesDone)

    strResult = BookForm(objDatabase, objBook, strDetailsStatistics, strCategoryStatistics, strNext)
    return strResult

def GetStatistics2():
    objDatabase = pg.connect(dbname = 'mci')
    (intTotal, intAreCategorised, intAreLive) = BookDatabaseFunctions.GetStatisticsFromDatabase(objDatabase)
    strResult = """<table>
        <tr>
            <td><b>%s Total</b></td>
            <td>&nbsp;</td>
            <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
            <td><a href="/cp/Books/ListByTitle">List by Title</a></td>
        </tr>
        <tr>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
            <td><a href="/cp/Books/ListByCategory">List by Category</a></td>
        </tr>
        <tr>
            <td><b>Categories</b></td>
            <td>%s done, %s to do</td>
            <td>&nbsp;</td>
            <td><a href="/cp/Books/EditOneBook?Action=CheckNextCategories">Check next categories</a></td>
        </tr>
        <tr>
            <td><b>Live</b></td>
            <td>%s done, %s to do</td>
            <td>&nbsp;</td>
            <td><a href="/cp/Books/EditOneBook?Action=CheckNextDetails">Check next set of details</a></td>
        </tr>
    </table>""" % (intTotal, intAreCategorised, (intTotal-intAreCategorised), intAreLive, (intTotal-intAreLive))
    return strResult

def ListBooksByCategory():
    objDatabase = pg.connect(dbname = 'mci')
    strResult = "<table>"
    strSQL = """SELECT BookCategoryId, Name 
        FROM BookCategory
        WHERE SubCategoryOfCategoryId = 0
        ORDER BY BookCategoryId"""
    objCategory = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    for (intCategoryId, strName) in objCategory.getresult():
        intCount = BookDatabaseFunctions.CountForCategory(objDatabase, intCategoryId)
        strResult = strResult + """<tr>
            <td><a href="ShowForCategory?CategoryId=%s">%s</a> (%s)</td>
            </tr>""" % (intCategoryId, strName, intCount)
        strSQL = """SELECT BookCategoryId, Name
            FROM BookCategory
            WHERE SubCategoryOfCategoryId = %s
            ORDER BY Name""" % intCategoryId
        objSubCategory = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
        for (intSubCategoryId, strSubName) in objSubCategory.getresult():
            intCount = BookDatabaseFunctions.CountForCategory(objDatabase, intSubCategoryId)
            strResult = strResult + """<tr>
            <td>...<a href="ShowForCategory?CategoryId=%s">%s</a> (%s)</td>
            </tr>""" % (intSubCategoryId, strSubName, intCount)
        strResult = strResult + "<tr><td>&nbsp;</td></tr>"
    strResult = strResult + "</table>"
    return strResult

def ShowForCategory(strCategoryId):
    intCategoryId = int(strCategoryId)
    objDatabase = pg.connect(dbname = 'mci')
    strSQL = "SELECT Name FROM BookCategory WHERE BookCategoryId = %s" % strCategoryId
    objResult = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    strCategoryName = objResult.getresult()[0][0]
    strResult = "<h3>Category: %s</h3>" % strCategoryName
    strSQL = """SELECT Book.Title, Book.SubTitle, Book.ISBN
                FROM Book, Book_BookCategory
                WHERE Book.BookId = Book_BookCategory.BookId
                AND Book_BookCategory.BookCategoryId = %s
                AND Book.CategoriesCorrect
                AND Book.DetailsCorrect
                AND Book.LinksChecked
                ORDER BY Book.Title""" % intCategoryId
    objResult = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    strResult = strResult + CreateBookList(objResult)
    return strResult

def ISBNExists(objDatabase, strISBN):
    strSQL = "SELECT BookId FROM Book WHERE ISBN='%s'" % strISBN
    objResult = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    if objResult.getresult():
        return 1
    return 0

def PrintBasicDetails(objBook):
    print "ISBN: |%s|" % objBook.ISBN
    print "Title: |%s|" % objBook.Title
    print "Authors: |%s|" % objBook.Authors
    print "Format: |%s|" % objBook.Format

def ImportOne(objDatabase, strLink):
    if 'www.amazon.com' in strLink:
        strISBN = BookImportFunctions.GetISBNFromAmazonLink(strLink)
        if strISBN:
            if ISBNExists(objDatabase, strISBN):
                print "Already saved, ISBN = '%s'" % strISBN
                return 0
            strAWSLink = """http://webservices.amazon.com/onca/xml?Service=AWSECommerceService&SubscriptionId=1A4N88VFDMF9AY3WH002&Operation=ItemLookup&ItemId=%s&ResponseGroup=Request,ItemAttributes""" %strISBN
            strPage = GeneralBookFunctions.LoadPage(strAWSLink)
            if strPage:
                objBook = clsBook.Book()
                objBook.ISBN = strISBN
                objBook.ReadFromAmazonComPage(strPage)
                objBook.OnAmazonCoUk = BookImportFunctions.CheckItsOnAmazonCoUk(strISBN)
                objBook.OnAmazonCom = 1
                intBookId = objBook.Save(objDatabase, ('Title', 'SubTitle',
        'ISBN', 'Format', 'Pages', 'Year', 'Publisher',
        'Authors', 'ReviewLink', 
        'OnAmazonCom', 'OnAmazonCoUk',
        'AmazonComNumber', 'AmazonCoUkNumber',
        'OtherLink', 'OtherLinkName'))
                print "New book saved, BookId = %s" % intBookId
                return 1
    print "'www.amazon.com' not found"
    return 0

def BatchImportFromZope(strToImport):
    strResult = "Importing<br><br>"
    lstToImport = string.split(strToImport)
    objDatabase = pg.connect(dbname = 'mci')
    for strLink in lstToImport:
        if ImportOne(objDatabase, strLink):
            strResult = strResult + 'Success: %s<br>' % strLink
            time.sleep(1)
        else:
            strResult = strResult + '!!!: %s<br>' % strLink
        # 1 second delay to make sure we're not in breach of Amazon's 1 per second limit
    return strResult

def CheckOneLinks(objDatabase, intBookId, strISBN):
    (blnOnAmazonCoUk, blnOnAmazonCom) = BookImportFunctions.CheckItIsOnAmazon("", strISBN)
    if blnOnAmazonCoUk and blnOnAmazonCom:
        blnLinksChecked = 1
    else:
        blnLinksChecked = 0
    strSQL = """UPDATE Book
        SET OnAmazonCom = %s,
            OnAmazonCoUk = %s,
            LinksChecked = %s
        WHERE BookId = %s""" % (DatabaseFunctions.StoreBoolean(blnOnAmazonCom), DatabaseFunctions.StoreBoolean(blnOnAmazonCoUk), DatabaseFunctions.StoreBoolean(blnLinksChecked), intBookId)
    DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)

def CheckAmazonLinks():
    strResult = "Checking Amazon links\n\n"
    objDatabase = pg.connect(dbname = 'mci')
    strSQL = """UPDATE Book
        SET LinksChecked = TRUE
        WHERE OnAmazonCom AND OnAmazonCoUk
            AND LENGTH(AmazonComNumber) > 0
            AND LENGTH(AmazonCoUkNumber) > 0
        """
    DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    strSQL = "SELECT BookId, ISBN FROM Book WHERE NOT LinksChecked"
    objBooks = DatabaseFunctions.ExecuteSQL(objDatabase, strSQL)
    if objBooks and objBooks.getresult():
        strResult = strResult + "%s done" % len(objBooks.getresult())
        for lstBook in objBooks.getresult():
            CheckOneLinks(objDatabase, lstBook[0], lstBook[1])
    else:
        strResult = strResult + "None found"
    # For all records where NOT LinksChecked
    # check the links
    return strResult

def BookTitleWithStats(objHere):
    intBooks = 0
    intReviews = 0
    objBooks = GetDataFolder(objHere, 'MCIBook')
    for objBatch in objBooks.objectValues():
        for objBook in objBatch.objectValues('MCIBook'):
            if objBook.Live():
                intBooks = intBooks + 1
                if objBook.ReviewLink:
                    intReviews = intReviews + 1

    strResult = "%s Books, %s Reviews" % (intBooks, intReviews)
    return strResult

def CategoryRow(strName, intId, strPage, intBooks, blnIndent, strCheckBoxName):
    if blnIndent:
        strTemplate = """<tr>
            <td width="1%%">&nbsp;&nbsp;&nbsp;&nbsp;</td>
            <td width="1%%" valign="top"><input type="checkbox" name="%s%s" value="Yes"></td>
            <td width="98%%"><a href="/Books/%s?CategoryId=%s&Offset=0" class="MenuItem">%s</a>&nbsp;(%s)</td>
        </tr>"""
    else:
        strTemplate = """<tr>
            <td colspan="3"><input type="checkbox" name="%s%s" value="Yes">&nbsp;<a href="/Books/%s?CategoryId=%s&Offset=0" class="MenuItem">%s</a>&nbsp;(%s)</td>
    </tr>"""
    strResult =  strTemplate % (strCheckBoxName, intId, strPage, intId, strName, intBooks)
    return strResult

def GetCategoryList(objHere):
    strResult = ""
    
    objCategories = GetDataFolder(objHere, 'MCIBookCategory')
    lstIds = GetOrderedIds(objCategories, 'MCIBookCategory')
    for strId in lstIds:
        objSubCategories = objCategories.unrestrictedTraverse(strId)
        lstSubIds = GetOrderedIds(objSubCategories, 'MCIBookCategory')
        objCategory = objCategories.unrestrictedTraverse(strId)
        strResult = strResult + CategoryRow("<b>%s</b>" % objCategory.CategoryName, strId, "ListForCategory", objCategory.BooksInCategory, 0, "BookCategory")
        for strSubId in lstSubIds:
            objSubCategory = objCategory.unrestrictedTraverse(strSubId)
            strResult = strResult + CategoryRow(objSubCategory.CategoryName, strSubId, "ListForCategory", objSubCategory.BooksInCategory, 1, "BookCategory")
        strResult = strResult + """<tr><td colspan="3">&nbsp;</td></tr>"""
    return strResult        

def CategorySearchList(objHere):
    strCategoryList = GetCategoryList(objHere)
    strResult = """
<table width="100%%" border="0" cellspacing="0" cellpadding="0" class="MainText">
        %s
    </table>""" % strCategoryList
    return strResult

def GetOrderedIds(objFolder, strItemType):
    dictItems = {}
    for objItem in objFolder.objectValues(strItemType):
        intOrder = objItem.DisplayOrder
        if not dictItems.has_key(intOrder):
            dictItems[intOrder] = []
        dictItems[intOrder].append(objItem.id)
    lstOrdered = dictItems.keys()
    lstOrdered.sort()
    lstResult = []
    for intOrder in lstOrdered:
        lstResult = lstResult + dictItems[intOrder]
    return lstResult

def GetAudienceList(objHere):
    objReaderCategories = GetDataFolder(objHere, 'MCIReaderCategory')
    lstIds = GetOrderedIds(objReaderCategories, 'MCIReaderCategory')
    strResult = ""
    for strId in lstIds:
        intCount = len(SearchMany(objHere, 'MCIBook', 'ReaderCategories', strId))
        objReaderCategory = SearchOne(objHere, 'MCIReaderCategory', 'id', strId)
        if objReaderCategory:
            strResult = strResult + CategoryRow(objReaderCategory.CategoryName, strId, "ListForAudience", intCount, 1, 'ReaderCategory')
        else:
            print "Reader category not found: %s" % strId
    return strResult

def AudienceSearchList(objHere):
    strAudienceList = GetAudienceList(objHere)
    strResult = """
<table width="100%%" border="0" cellspacing="0" cellpadding="0" class="MainText">
        <tr><td colspan="2"><b>Audience</b></td></tr>
        %s
    </table>""" % strAudienceList
    return strResult

def CategoryName(objHere, objRequest):
    strCategoryId = GetParameter(objRequest, 'CategoryId')
    objCategory = SearchOne(objHere, 'MCIBookCategory', 'id', strCategoryId)
    if objCategory:
        return objCategory.CategoryName
    else:
        return "Category not found"

def AudienceName(objHere, objRequest):
    strCategoryId = GetParameter(objRequest, 'CategoryId')
    objReaderCategory = SearchOne(objHere, 'MCIReaderCategory', 'id', strCategoryId)
    if objReaderCategory:
        return objReaderCategory.CategoryName
    else:
        return "Audience type not found"

def ListOneBook(objBook):
    strImage = objBook.GetImageLink()
    if objBook.Review:
        objReview = SearchOne(objBook, 'MCIBookReview', 'id', objBook.Review)
        strReviewLink = """<br><span class="PageSubTitle"><a href="/Books/ShowBook?Id=%s" class="MenuItem"><span class="PageSubTitle">Review: </span> %s ... More</a></span>""" % (objBook.id, objReview.ReviewSummary)
    else:
        strReviewLink = ""
    strFullTitle = objBook.GetFullTitle()
    strAuthors = ", ".join(objBook.Authors)
    strShoppingLinks = objBook.ShoppingLinks()
    strResult = """<table width="100%%" border="0" cellspacing="5" class="MainText">
        <tr>
            <td width="40" valign="top">%(Image)s</td>
            <td width="95%%" valign="top"><a href="/Books/ShowBook?Id=%(BookId)s" class="MenuItem">%(FullTitle)s - 
            %(Authors)s</a>%(ReviewLink)s</td>
        </tr>
    </table>""" % {'ReviewLink': strReviewLink,
        'Image': strImage,
        'FullTitle': strFullTitle,
        'BookId': objBook.id,
        'Authors': strAuthors,
        'ISBN': objBook.ISBN,
        'Publisher': objBook.Publisher,
        'Year': objBook.Year,
        'Format': objBook.Format,
        'Pages': objBook.Pages,
        'ShoppingLinks': strShoppingLinks}
    return strResult

def ShowPlural(intNumber):
    if intNumber == 1:
        return ""
    else:
        return "s"

def BuildNavigation(strCategoryId, intOffset, intMaxBooks, intRecords, strURL):
    strResult = ""
    if intOffset > 0:
        strResult = strResult + """<a href="%s?CategoryId=%s&Offset=%s">Previous</a> - """ % (strURL, strCategoryId, max(0, intOffset-intMaxBooks))
    strResult = strResult + "%s book%s found, showing %s to %s" % (intRecords, ShowPlural(intRecords), intOffset + 1, min(intOffset + intMaxBooks, intRecords))
    if intOffset + intMaxBooks < intRecords:
        strResult = strResult + """ - <a href="%s?CategoryId=%s&Offset=%s">Next</a>""" % (strURL, strCategoryId, intOffset+intMaxBooks)
    strResult = """<span class="MainText">%s</span>""" % strResult
    return strResult
    
def CreateListOfBooks(objHere, lstBooks, strCategoryId, intOffset):
    strNavigation = ""
    intMaxBooks = 20
    strURL = objHere.absolute_url()
    if lstBooks:
        strNavigation = BuildNavigation(strCategoryId, intOffset, intMaxBooks, len(lstBooks), strURL)
        lstBooks.sort(BookCategorySort)
        strList = ""
        for intI in range(intOffset, min(len(lstBooks), intOffset + intMaxBooks)):
            strList = strList + ListOneBook(lstBooks[intI])
    else:
        strList = "<tr><td>No books found for this category</td></tr>"
    strResult = """<table width="100%%" border="0" cellspacing="0" cellpadding="5" class="TableWithBorder">
        %s
        </table>""" % strList
    if strNavigation:
        strResult = strNavigation + "<br>" + strResult + "<br>" + strNavigation
    return strResult

def ListForAudience(objRequest, objHere):
    strCategoryId = GetParameter(objRequest, 'CategoryId')
    strOffset = GetParameter(objRequest, 'Offset')
    if strOffset:
        intOffset = int(strOffset)
    else:
        intOffset = 0

    lstBooks = SearchMany(objHere, 'MCIBook', 'ReaderCategories', strCategoryId)
    strResult = CreateListOfBooks(objHere, lstBooks, strCategoryId, intOffset)
    return strResult

def IsInt(strText):
    try:
        intText = int(strText)
    except:
        return 0
    return 1

def BookCategorySort(objBook1, objBook2):
    if objBook1.Review and not objBook2.Review:
        return -1
    if objBook2.Review and not objBook1.Review:
        return +1
    if objBook1.Title < objBook2.Title:
        return -1
    return +1

def MergeLists(lstLarge, lstToAdd):
    lstResult = lstLarge
    for varItem in lstToAdd:
        if not varItem in lstResult:
            lstResult = lstResult + [varItem, ]
    return lstResult

def ListForCategory(objRequest, objHere):
    strNavigation = ""
    intMaxBooks = 20
    intOffset = 0
    strCategoryId = GetParameter(objRequest, 'CategoryId')
    strOffset = GetParameter(objRequest, "Offset")
    if not strCategoryId:
        return "Incorrect category"
    objCategory = SearchOne(objHere, 'MCIBookCategory', 'id', strCategoryId)
    if not objCategory:
        return "Incorrect category"
    if strOffset and isinstance(strOffset, int):
        intOffset = int(strOffset)
    lstBooks = SearchMany(objHere, 'MCIBook', 'Categories', strCategoryId)
    for objSubCategory in objCategory.objectValues():
        lstBooks = MergeLists(lstBooks, SearchMany(objHere, 'MCIBook', 'Categories', objSubCategory.id))
    strResult = CreateListOfBooks(objHere, lstBooks, strCategoryId, intOffset)
    return strResult    

def HeapBookCount(dictBooks):
    intMaxCount = 0
    for intI in dictBooks.keys():
        if dictBooks[intI] > intMaxCount:
            intMaxCount = dictBooks[intI]
    dictResult = {}
    for intI in range(1, intMaxCount + 1):
        dictResult[intI] = []
    for objBook in dictBooks.keys():
        dictResult[dictBooks[objBook]].append(objBook)
    return dictResult

def ListForBooks(lstBooks):
    strResult = ""
    lstBooks.sort(BookCategorySort)
    for objBook in lstBooks:
        strResult = strResult + ListOneBook(objBook)
    return strResult

def ListForTextSearch(objRequest, objHere):
    strSearchFor = GetParameter(objHere.REQUEST, 'SearchFor')
    if not strSearchFor:
        return "No search criteria entered"

    lstWords = strSearchFor.split()
    dictBooks = {}

    for strWord in lstWords:
        for strLocation in ('Title', 'SubTitle', 'ISBN', 'Authors'):
            objBooks = SearchMany(objHere, 'MCIBook', strLocation, strWord)
            dictBooks = CountBooks(dictBooks, objBooks)

    strResult = GetBooklistFromDictionary(dictBooks, len(lstWords), "words", objHere)
    if not strResult:
        strResult = "No books found"
    return """<span class = "PageTitle2">All books for &quot;%s&quot;</span><br>%s""" % (strSearchFor, strResult)

def GetBooklistFromDictionary(dictBooks, intItems, strItemName, objHere):
    dictHeapedBooks = HeapBookCount(dictBooks)

    blnSaidSome = 0
    blnSaidAll = 0
    strResult = ""
    for intI in range(len(dictHeapedBooks), 0, -1):
        if dictHeapedBooks[intI]:
            if  intItems > 1:
                if intI == intItems:
                    strResult = strResult + """<span class="PageSubTitle">All %s found</span><br>""" % strItemName
                    blnSaidAll = 1
                else:
                    if not blnSaidSome:
                        if blnSaidAll:
                            strResult = strResult + "<br>"
                        strResult = strResult + """<span class="PageSubTitle">Some %s found<br>""" % strItemName
                        blnSaidSome = 1
        strResult = strResult + ListForBooks(dictHeapedBooks[intI])
    return strResult

def CountForOneCategory(objHere, strBookCategory, dictBooks):
    objBooks = SearchMany(objHere, 'MCIBook', 'Categories', strBookCategory)
#    print strBookCategory, len(objBooks), "found"
    return CountBooks(dictBooks, objBooks)

def CountBooks(dictBooks, objBooks):
    for objBook in objBooks:
        if objBook.Live():
            if not dictBooks.has_key(objBook):
                dictBooks[objBook] = 0
            dictBooks[objBook] = dictBooks[objBook] + 1
    return dictBooks

def CountForOneReaderType(objHere, strReaderCategory, dictBooks):
    objBooks = SearchMany(objHere, 'MCIBook', 'ReaderCategories', strReaderCategory)
#    print strReaderCategory, len(objBooks), "found"
    return CountBooks(dictBooks, objBooks)

def ListForCategorySearch(objQuery, objHere):
    dictBooks = {}
    lstCategories = []
    lstReaders = []

    for objCategory in GetDataFolder(objHere, 'MCIBookCategory').objectValues():
        if GetParameter(objQuery, "BookCategory" + objCategory.id):
            lstCategories.append(objCategory.id)
            dictBooks = CountForOneCategory(objHere, objCategory.id, dictBooks)
            for objSubCategory in objCategory.objectValues():
                dictBooks = CountForOneCategory(objHere, objSubCategory.id, dictBooks)
        else:
            for objSubCategory in objCategory.objectValues():
                if GetParameter(objQuery, "BookCategory" + objSubCategory.id):
                    lstCategories.append(objSubCategory.id)
                    dictBooks = CountForOneCategory(objHere, objSubCategory.id, dictBooks)

    for objReaderType in GetDataFolder(objHere, 'MCIReaderCategory').objectValues():
        if GetParameter(objQuery, "ReaderCategory" + objReaderType.id):
            lstReaders.append(objReaderType.id)
            dictBooks = CountForOneReaderType(objHere, objReaderType.id, dictBooks)
                    
    strResult = GetBooklistFromDictionary(dictBooks, len(lstCategories) + len(lstReaders), "selections", objHere)

    return strResult

def ShowBook(objHere, objRequest):

    strBookId = GetParameter(objRequest, 'Id')

    objBook = SearchOne(objHere, 'MCIBook', 'id', strBookId)
    if not objBook:
        return "Not found"

    strImage = objBook.GetFullImage()

    strAuthors = ", ".join(objBook.Authors)
    if "," in strAuthors:
        strAuthorPlural = "s"
    else:
        strAuthorPlural = ""

# 259 pages, Hardback, 2001, McGraw-Hill, Roseville, Australia
    strJoin = ""
    if objBook.Publisher and objBook.Year:
        strJoin = ", "
    strPublished = strJoin.join((objBook.Publisher, str(objBook.Year)))

    if strPublished:
        strPublished = """<tr>
                            <td valign="top"><b>Published</b>:</td>
                            <td valign="top">%s</td>
                        </tr>""" % strPublished

    strShoppingLinks = objBook.ShoppingLinks()

    if objBook.Review:
        objReview = SearchOne(objHere, 'MCIBookReview', 'id', objBook.Review)
        strReview = objReview.ShowOnWebsite(strBookId)
        strShoppingLinks2 = strShoppingLinks
    else:
        strReview = ""
        strShoppingLinks2 = ""

    strISBN = ""
    if objBook.ISBN:
        strISBN = """<tr>
                        <td><b>ISBN:</b></td>
                        <td>%s</td>
                    </tr>""" % objBook.ISBN
    strIssue = ", ".join(("%s pages" % objBook.Pages, objBook.Format))

    if strIssue:
        strIssue = """<tr>
                        <td valign="top"><b>Format</b>:</td>
                        <td valign="top">%s</td>
                    </tr>""" % strIssue

    strResult = """%(Image)s
                    <table width="100%%" class="MainText" cellspacing="2" cellpadding="0" border="0">
                    <tr>
                        <td valign="top"><b>Author%(AuthorPlural)s</b>:</td> 
                        <td valign="top">%(Authors)s</td>
                    </tr>%(Issue)s%(Published)s
                    %(ISBN)s
                    </table>
                    %(ShoppingLinks)s<br clear="all"><br>
                    %(Review)s%(ShoppingLinks2)s""" % {"Image": strImage,
                        "Authors": strAuthors,
                        "AuthorPlural": strAuthorPlural,
                        "Issue": strIssue,
                        "Published": strPublished,
                        "ISBN": strISBN,
                        "ShoppingLinks": strShoppingLinks,
                        "Review": strReview,
                        "ShoppingLinks2": strShoppingLinks2}
    return strResult

def BookTitle(objHere, objRequest):
    strBookId = GetParameter(objRequest, 'Id')

    objBook = SearchOne(objHere, 'MCIBook', 'id', strBookId)
    if objBook:
        strResult = objBook.GetFullTitle()
    else:
        strResult = ""
    return strResult

def LogShopAt(objHere, strBookId, intShopId):
    dodShopAt = GetDOD(objHere, 'MCIShopAt')
    objShopAt = dodShopAt.NewObject()
    objShopAt.BookId = strBookId
    objShopAt.ShopId = intShopId
    objShopAt.Date = DateTime.DateTime()

def GetShopLink(objHere, strBookId, intShopId):
    strResult = "http://www.MentorCoaches.com/"

    objBook = SearchOne(objHere, 'MCIBook', 'id', strBookId)
    if objBook:
        if (intShopId == 1) and (objBook.OnAmazonCom):
            if objBook.AmazonComNumber:
                strLink = objBook.AmazonComNumber
            else:
                strLink = objBook.ISBN
            strResult = "http://www.amazon.com/exec/obidos/ASIN/%s/mentorcoaches-20" % strLink
        if (intShopId == 2) and (objBook.OnAmazonCoUk):
            if objBook.AmazonCoUkNumber:
                strLink = objBook.AmazonCoUkNumber
            elif objBook.AmazonComNumber:
                strLink = objBook.AmazonComNumber
            else:
                strLink = objBook.ISBN
            strResult = "http://www.amazon.co.uk/exec/obidos/ASIN/%s/mentorcoaches-21" % strLink
        if (intShopId == 3) and (objBook.OtherLinkName) and (objBook.OtherLink):
            strResult = objBook.OtherLink
    return strResult

def ShopAt(objHere):
    # http://www.MentorCoaches.com/ShopAt?BookId=....&ShopId=1
    strLink = "http://www.MentorCoaches.com/"
    strBookId = GetParameter(objHere.REQUEST, 'Id')
    strShopId = GetParameter(objHere.REQUEST, 'ShopId')
    if strShopId.isdigit():
        intShopId = int(strShopId)
    else:
        intShopId = 0
    if strBookId and intShopId:
        LogShopAt(objHere, strBookId, intShopId)
        strLink = GetShopLink(objHere, strBookId, intShopId)
        
    return strLink

def ShowLatestBookReviewShort(objHere):
    fltLatestDate = datetime.date(2000, 1, 1).toordinal()
    for objBookReview in GetDataFolder(objHere, 'MCIBookReview').objectValues('MCIBookReview'):
        print objBookReview.ReviewId
        if objBookReview.Published and (objBookReview.ReviewPublished > fltLatestDate) and (objBookReview.ReviewPublished <= time.time()):
            fltLatestDate = objBookReview.ReviewPublished
            strBookTitle = objBookReview.BookTitle
            strAuthors = objBookReview.Authors
            strURL = PointURLAtMCI(objBookReview.absolute_url())
            
    strResult = """<a href="%s" class="MenuItem" target="_blank">&quot;%s&quot;<br>by %s<br>&gt; Read review</a>""" % (strURL,
                                                            strBookTitle, 
                                                            strAuthors)
    return strResult

def GetBookForReview(objHere, strBookReviewId):
    for objBatch in GetDataFolder(objHere, 'MCIBook').objectValues('Folder'):
        for objBook in objBatch.objectValues('MCIBook'):
            if objBook.Review == strBookReviewId:
                return objBook.id
    return None

def ShowLatestBookReview(objHere):
    fltLatestDate = datetime.date(2000, 1, 1).toordinal()
    for objBatch in GetDataFolder(objHere, 'MCIBookReview').objectValues():
        for objBookReview in objBatch.objectValues():
            if objBookReview.IsPublished and (objBookReview.ReviewPublished > fltLatestDate) and (objBookReview.ReviewPublished <= time.time()):
                fltLatestDate = objBookReview.ReviewPublished
                strBookTitle = objBookReview.BookTitle
                strAuthors = objBookReview.Authors
                strReviewSummary = objBookReview.ReviewSummary
                strReviewId = objBookReview.id
#                strURL = objBookReview.absolute_url()
    strURL = "/Books/ShowBook?Id=%s" % GetBookForReview(objHere, strReviewId)
            
    strResult = """<a href="%s" class="PageSubTitle">&quot;%s&quot;</a><br>by %s<br>
    <br><a href="%s" class="MenuItem">%s More ...</a>""" % (strURL,
                                                            strBookTitle, 
                                                            strAuthors, 
                                                            strURL,
                                                            strReviewSummary)
    return strResult

def CategoryNamesSelected(objHere, objQuery):
    lstResult = []
    objCategories = GetDataFolder(objHere, 'MCIBookCategory')
    for objCategory in objCategories.objectValues():
        if objQuery.has_key('BookCategory' + objCategory.id):
            lstResult.append(objCategory.CategoryName)
        for objSubCategory in objCategory.objectValues():
            if objQuery.has_key('BookCategory' + objSubCategory.id):
                lstResult.append(objSubCategory.CategoryName)
    
    objReaderCategories = GetDataFolder(objHere, 'MCIReaderCategory')
    for objReaderCategory in objReaderCategories.objectValues():
        if objQuery.has_key('ReaderCategory' + objReaderCategory.id):
            lstResult.append(objReaderCategory.CategoryName)

    strResult = ", ".join(lstResult)
    return strResult

def CountBookReviews(objHere):
    objBooks = GetDataFolder(objHere, 'MCIBook')
    intResult = 0
    for objBatch in objBooks.objectValues():
        for objBook in objBatch.objectValues('MCIBook'):
            if objBook.Review:
                intResult = intResult + 1
    return intResult

def CountBooksInDatabase(objHere):
    objBooks = GetDataFolder(objHere, 'MCIBook')
    intResult = 0
    for objBatch in objBooks.objectValues():
        intResult = intResult + len(objBatch.objectValues('MCIBook'))
    return intResult

def SortBookReviewsByIssue(objReview1, objReview2):
    if objReview1.ReviewPublished > objReview2.ReviewPublished:
        return -1
    return 1

def ListOneReview(objReview):
    objBook = SearchOne(objReview, 'MCIBook', 'Review', objReview.id)
    if not objBook:
#        print "Book not found"
        return ""
    strResult = """<li><a href="http://%s/Books/ShowBook?Id=%s" target="_blank">%s</a></li>""" % (cnMCIRoot, objBook.id, objBook.Title)
    return strResult

def ListRecentBookReviews(objHere):
    objReviews = GetDataFolder(objHere, 'MCIBookReview')
    lstReviews = []
    for objBatch in objReviews.objectValues():
        lstReviews = lstReviews + objBatch.objectValues()
    lstReviews.sort(SortBookReviewsByIssue)
    strResult = "<ul>\n"
    intDone = 0
    intI = 0
    while intDone < 3:
        strReview = ListOneReview(lstReviews[intI])
        intI = intI + 1
        if strReview:
            intDone = intDone + 1
            strResult = strResult + strReview
    strResult = strResult + "</ul>\n"
    return strResult
