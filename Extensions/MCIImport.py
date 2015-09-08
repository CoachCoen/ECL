import LocalPaths

from libString import GetChunk
from libDatabase import GetDOD
from libDatabase import GetDataFolder
from libDatabase import VisitData
from libDatabase import ReindexOne
from libDatabase import Catalogue
from libFolders import DeleteObject
from libDatabase import SearchOne
from libDatabase import SearchMany
from libString import AddToLines
from MetaStart import CreateDataObjectDefinitions
from types import *


# Read /root/Downloads/MCI Postgresql data/mcifull.sql
# one line at a time
# When the first line starts with COPY, start saving the data
#   The word after COPY identifies which table we're reading
#   Next it gives the field names, between brackets
#   Then come the rows
#       Fields are separated by tabs
#   Stop when the line starts with \.

def ParseHeader(strLine):
    lstWords = strLine.split()
    strTableName = lstWords[1]
    strColumnNames = GetChunk(strLine, '(', ')')
    strColumnNames = strColumnNames[1:-1]
    lstColumnNames = strColumnNames.split(", ")
    return (strTableName, lstColumnNames)

def GetMapping(strTableName):
    if strTableName == 'shopat':
        return {'shopatit': 'SourceId', 
                        'bookid': 'BookId', 
                        'shopid': 'ShopId', 
                        '"when"': 'Date'}
    if strTableName == 'readercategory':
        return {'readercategoryid': 'SourceId', 
                            'name': 'CategoryName', 
                            'displayorder': 'DisplayOrder'}

    if strTableName in ['participant', 'removedparticipant']:
        return {'participantid': 'SourceId', 
                        'participantname': 'ParticipantName', 
                        'emailaddress': 'EmailAddress', 
                        'nomailings': 'NoMailings'}

    if strTableName == 'liststat':
        return {'liststatid': 'SourceId',
                        'listid': 'ListId', 
                        'count': 'Count',
                        'dateofcount': 'Date'}

    if strTableName in ['enrolment', 'removedenrolment']:
        return {'enrolmentid': 'SourceId',
                        'participantid': 'ParticipantId', 
                        'classid': 'ClassId', 
                        'welcomemessagesent': 'WelcomeMessageSent', 
                        'instructionssent': 'InstructionsSent'}

    if strTableName == 'enrolmentlog':
        return {'enrolmentlogid': 'SourceId', 
                            'participantname': 'ParticipantName', 
                            'emailaddress': 'EmailAddress',
                            'classidlist': 'ClassIdList', 
                            'dateentered': 'DateEntered'}

    if strTableName == 'booksearch':
        return {'bookid': 'BookId', 
                            'searchline': 'SearchLine'}
    
    if strTableName == 'book':
        return {'bookid': 'SourceId', 
                'title': 'Title', 
                'subtitle': 'SubTitle', 
                'publisher': 'Publisher', 
                '"year"': 'Year',
                'pages': 'Pages', 
                'format': 'Format', 
                'isbn': 'ISBN', 
                'otherlink': 'OtherLink', 
                'onamazoncom': 'OnAmazonCom', 
                'onamazoncouk': 'OnAmazonCoUk', 
                'amazoncomnumber': 'AmazonComNumber', 
                'amazoncouknumber': 'AmazonCoUkNumber', 
                'reviewlink': 'ReviewLink', 
                'otherlinkname': 'OtherLinkName', 
                'categoriescorrect': 'CategoriesCorrect', 
                'detailscorrect': 'DetailsCorrect', 
                'linkschecked': 'LinksChecked'}

    if strTableName == 'bookcategory':
        return {'bookcategoryid': 'SourceId', 
                        'subcategoryofcategoryid': 'SubCategoryOfCategoryId', 
                        'name': 'CategoryName', 
                        'displayorder': 'DisplayOrder'}
    
    if strTableName == 'author':
        return {'authorid': 'SourceId', 
                    'name': 'Name'}

    print "Unknown tablename: ", strTableName

    return None

def TranslateColumnNames(strTableName, lstColumnNames):
    lstResult = []
    dictMapping = GetMapping(strTableName)
    for strColumnName in lstColumnNames:
        lstResult.append(dictMapping[strColumnName])
    return lstResult

def ConvertBoolean(varValue, varProperty):
    if type(varProperty) == BooleanType:
        varValue = varValue.strip()
        if varValue == 'f':
            return False
        else:
            return True
    else:
        return varValue

def StoreOneRow(dodObject, lstPropertyNames, lstColumnValues):
    objObject = dodObject.NewObject()
    for intI in range(0, len(lstPropertyNames)):
        strCommand = "objObject.%(Property)s = ConvertBoolean(lstColumnValues[intI], objObject.%(Property)s)" % {'Property': lstPropertyNames[intI]}
        exec strCommand
    Catalogue(objObject)
    return objObject

def StoreOneLink(dodObject, strTableName, lstColumnValues):
# COPY book_author (bookid, authorid) FROM stdin;
# COPY book_bookcategory (bookid, bookcategoryid) FROM stdin;
# COPY book_bookrating (bookid, bookratingid) FROM stdin;
# COPY book_readercategory (bookid, readercategoryid) FROM stdin;
    objLink = dodObject.NewObject()
    objLink.TableName = strTableName
    objLink.FromId = lstColumnValues[0]
    objLink.ToId = lstColumnValues[1]
    Catalogue(objLink)

def SkipTable(fileSQL):
    strLine = 'abcd'
    while len(strLine) > 3:
        strLine = fileSQL.readline()
    return fileSQL

def ImportOneTable(objHere, strLine, fileSQL, blnSkipSome):
    (strTableName, lstColumnNames) = ParseHeader(strLine)
    print strTableName
    if blnSkipSome:
        if strTableName in ['enrolmentlog', 'shopat', 'liststat', 'booksearch']:
            return SkipTable(fileSQL)

    if strTableName in ['book_author', 'book_bookcategory', 'book_bookrating', 'book_readercategory']:
        strTargetType = 'MCILink'
    elif strTableName in ['webpagetoshow', 'list', 'bookrating', 'removeparticipant']:
        strTargetType = ''
    else:
        strTargetType = {'author': 'MCIAuthor',
        'bookcategory': 'MCIBookCategory',
        'book': 'MCIBook',
        'booksearch': 'MCIBookSearch',
        'enrolment': 'MCIEnrolment',
        'removedenrolment': 'MCIEnrolment',
        'enrolmentlog': 'MCIEnrolmentLog',
        'liststat': 'MCIListStat',
        'participant': 'MCIParticipant',
        'removedparticipant': 'MCIParticipant',
        'readercategory': 'MCIReaderCategory',
        'shopat': 'MCIShopAt'}[strTableName]
        lstPropertyNames = TranslateColumnNames(strTableName, lstColumnNames)
    if strTargetType:
        dodObject = GetDOD(objHere, strTargetType)
    intDone = 0
    while len(strLine) > 3:
        intDone = intDone + 1
        strLine = fileSQL.readline()
        if len(strLine) > 3:
            lstColumnValues = strLine.split('\t')
            if True:
                if strTableName in ['webpagetoshow', 'list', 'bookrating', 'removeparticipant']:
                    pass
                elif strTableName in ['book_author', 'book_bookcategory', 'book_bookrating', 'book_readercategory']:
                    StoreOneLink(dodObject, strTableName, lstColumnValues)
                else:
                    objObject = StoreOneRow(dodObject, lstPropertyNames, lstColumnValues)
                if strTableName == 'removedparticipant':
                    objObject.Removed = True
                if strTableName == 'removedenrolment':
                    objObject.Removed = True
    return fileSQL

def ImportSQLData(objHere):
    print "Importing SQL data"
    blnSkipSome = True
    fileSQL = open("/var/lib/zope/Extensions/mcifull.sql")
    strLine = 'start'
    while strLine:
        strLine = fileSQL.readline()
        if strLine[:4] == 'COPY':
            fileSQL = ImportOneTable(objHere, strLine, fileSQL, blnSkipSome)

def BlankOneBook(objBook):
    objBook.Authors = ()
    objBook.Categories = ()
    objBook.ReaderCategories = ()

def CleanLinkId(strId):
    return strId.strip().replace('\n', '')

def ProcessOneBookAuthorLink(objLink):
    if objLink.TableName == 'book_author':
        strBookId = CleanLinkId(objLink.FromId)
        objBook = SearchOne(objLink, 'MCIBook', 'SourceId', strBookId)
        if not objBook:
            print "Book not found: %s" % strBookId
        else:
            strAuthorId = CleanLinkId(objLink.ToId)
            objAuthor = SearchOne(objLink, 'MCIAuthor', 'SourceId', strAuthorId)
            if not objAuthor:
                print "Author not found: %s" % strAuthorId
            else:
                objBook.Authors = AddToLines(objBook.Authors, objAuthor.Name.strip())
                Catalogue(objBook)
        DeleteObject(objLink)

def ProcessOneBookCategoryLink(objLink):
    if objLink.TableName == 'book_bookcategory':
        strBookId = CleanLinkId(objLink.FromId)
        strCategoryId = CleanLinkId(objLink.ToId)
        objBook = SearchOne(objLink, 'MCIBook', 'SourceId', strBookId)
        objCategory = SearchOne(objLink, 'MCIBookCategory', 'SourceId', strCategoryId)
        if not objBook:
            print "Book not found: %s" % strBookId
        if not objCategory:
            print "Category not found: %s" % strCategoryId
        if objBook and objCategory:
            objBook.Categories = AddToLines(objBook.Categories, objCategory.id)
            Catalogue(objBook)
        DeleteObject(objLink)

def SetCategories(objHere):
    objCategories = GetDataFolder(objHere, "MCIBookCategory")
    dodBookCategory = GetDOD(objHere, 'MCIBookCategory')
    for objCategory in objCategories.objectValues('MCIBookCategory'):
        if objCategory.SubCategoryOfCategoryId <> '0':
            strParentId = CleanLinkId(objCategory.SubCategoryOfCategoryId)
            objParentCategory = SearchOne(objHere, 'MCIBookCategory', 'SourceId', strParentId)
            if objParentCategory:
                objSubCategory = dodBookCategory.NewObject(objParentCategory)
                objSubCategory.DisplayOrder = objCategory.DisplayOrder
                objSubCategory.CategoryName = objCategory.CategoryName
                objSubCategory.SourceId = objCategory.SourceId
                DeleteObject(objCategory)
                Catalogue(objSubCategory)
            else:
                print "Parent %s not found for %s" % (strParentId, objCategory.id)
    ReindexOne(objHere, 'MCIBookCategory')

def ProcessOneReaderCategoryLink(objLink):
    if objLink.TableName == 'book_readercategory':
        strBookId = CleanLinkId(objLink.FromId)
        strReaderCategoryId = CleanLinkId(objLink.ToId)
        objBook = SearchOne(objLink, 'MCIBook', 'SourceId', strBookId)
        objReaderCategory = SearchOne(objLink, 'MCIReaderCategory', 'SourceId', strReaderCategoryId)
        if not objBook:
            print "Reader category, book not found: %s" % strBookId
        if not objReaderCategory:
            print "ReaderCategory not found: %s" % strReaderCategoryId
        if objBook and objReaderCategory:
            objBook.ReaderCategories = AddToLines(objBook.ReaderCategories, objReaderCategory.id)
            Catalogue(objBook)
        DeleteObject(objLink)

def ProcessOneEnrolment(objEnrolment):
    strMasterclassId = objEnrolment.ClassId.strip()
    objMasterclass = SearchOne(objEnrolment, 'MCIMasterclass', 'SourceId', strMasterclassId)
    strParticipantId = CleanLinkId(objEnrolment.ParticipantId)
    objParticipant = SearchOne(objEnrolment, 'MCIParticipant', 'SourceId', strParticipantId)
    if not objParticipant:
        print "Participant not found: %s" % strParticipantId
    if not objMasterclass:
        print "Masterclass not found: %s" % strMasterclassId
    if objParticipant and objMasterclass:
        dodEnrolment = GetDOD(objEnrolment, 'MCIEnrolment')
        objNewEnrolment = dodEnrolment.NewObject(objMasterclass)
        objNewEnrolment.ParticipantId = objParticipant.id
        objNewEnrolment.WelcomeMessageSent = objEnrolment.WelcomeMessageSent
        objNewEnrolment.InstructionsSent = objEnrolment.InstructionsSent
        objNewEnrolment.Removed = objEnrolment.Removed
        Catalogue(objNewEnrolment)

def ProcessOneReview(objBook):
    if objBook.ReviewLink:
        objReviews = GetDataFolder(objBook, 'MCIBookReview')
        strReviewLink = objBook.ReviewLink
        strReviewLink = strReviewLink[13:]
        objReview = SearchOne(objBook, 'MCIBookReview', 'ReviewId', strReviewLink)
        if not objReview:
            print "Review not found: %s" % strReviewLink
        else:
            objBook.Review = objReview.id
            Catalogue(objBook)

def CopyPersons(objHere):
    objSource = objHere.unrestrictedTraverse('/Temp/MCI/Persons')
    dodMCIPerson = GetDOD(objHere, 'MCIPerson')
    for objPerson in objSource.objectValues('Person'):
        objNewPerson = dodMCIPerson.NewObject()
        objNewPerson.PersonId = objPerson.id
        objNewPerson.PersonName = objPerson.PersonName
        objNewPerson.WebPage = objPerson.WebPage
        objNewPerson.WebSite = objPerson.WebSite
        objNewPerson.ShortBio = objPerson.ShortBio
        objNewPerson.MCIPartner = objPerson.MCIPartner
        objNewPerson.EmailAddress = objPerson.EmailAddress
        objNewPerson.ShortName = objPerson.id
        Catalogue(objNewPerson)

def CopyBookReviews(objHere):
    objSource = objHere.unrestrictedTraverse('/Temp/MCI/BookReviews')
    dodMCIReview = GetDOD(objHere, 'MCIBookReview')
    for objReview in objSource.objectValues('BookReviewClass'):
        objNewReview = dodMCIReview.NewObject()
        objNewReview.BookTitle = objReview.BookTitle
        objNewReview.ReviewNumber = objReview.ReviewNumber
        objNewReview.Authors = objReview.Authors
        objNewReview.Issue = objReview.Issue
        objNewReview.AmazonNumber = objReview.AmazonNumber
        objNewReview.ReviewAuthor = objReview.ReviewAuthor
        objNewReview.ReviewRead = objReview.ReviewRead
        objNewReview.ReviewContents = objReview.ReviewContents
        objNewReview.ReviewPublished = objReview.ReviewPublished
        objNewReview.OtherAffiliateLink = objReview.OtherAffiliateLink
        objNewReview.OtherShoppingLink = objReview.OtherShoppingLink
        objNewReview.ReviewSummary = objReview.ReviewSummary
        objNewReview.SubTitle = objReview.SubTitle
        objNewReview.OnAmazonCom = objReview.OnAmazonCom
        objNewReview.OnAmazonCoUk = objReview.OnAmazonCoUk
        objNewReview.IsPublished = objReview.IsPublished
        objNewReview.ReviewId = objReview.id
        Catalogue(objNewReview)

def CopyNewsletters(objHere):
    objSource = objHere.unrestrictedTraverse('/Temp/MCI/Newsletters')
    dodMCINewsletter = GetDOD(objHere, 'MCINewsletter')
    for objOld in objSource.objectValues('MCINewsletterClass'):
        objNew = dodMCINewsletter.NewObject()
        objNew.DatePublished = objOld.DatePublished
        objNew.Author = objOld.Author
        objNew.ShortTitle = objOld.ShortTitle
        objNew.EditorsIntro = objOld.EditorsIntro
        objNew.Contents = objOld.Contents
        objNew.FirstParagraph = objOld.FirstParagraph
        objNew.IssueNumber = objOld.IssueNumber
        objNew.FullTitle = objOld.FullTitle
        objNew.IncludeEndImage = objOld.IncludeEndImage
        objNew.AuthorLink = objOld.AuthorLink
        if not objNew.FullTitle:
            objNew.FullTitle = objNew.ShortTitle
        Catalogue(objNew)

def CopyMasterclasses(objHere):
    objSource = objHere.unrestrictedTraverse('/Temp/MCI/Masterclasses')
    dodMCIMasterclass = GetDOD(objHere, 'MCIMasterclass')
    dodMCIPresenter = GetDOD(objHere, 'MCIPresenter')
    for objOld in objSource.objectValues('Masterclass'):
        objNew = dodMCIMasterclass.NewObject()
        objNew.ClassDate = objOld.ClassDate
        objNew.ClassTime = objOld.ClassTime
        objNew.ClassTitle = objOld.ClassTitle
        objNew.Description = objOld.Description
        objNew.BridgeNumber = objOld.BridgeNumber
        objNew.BridgePin = objOld.BridgePin
        objNew.BridgeInstructions = objOld.BridgeInstructions
        objNew.BackupBridgeNumber = objOld.BackupBridgeNumber
        objNew.BackupBridgePin = objOld.BackupBridgePin
        objNew.BackupBridgeInstructions = objOld.BackupBridgeInstructions
        objNew.ClassInstructions = objOld.ClassInstructions
        objNew.Review = objOld.Review
        objNew.ReviewPosted = objOld.ReviewPosted
        objNew.ReadyToPublish = objOld.ReadyToPublish
        objNew.ReviewWrittenBy = objOld.ReviewWrittenBy
        objNew.InstructionsReadyToSend = objOld.InstructionsReadyToSend
        objNew.Cancelled = objOld.Cancelled
        objNew.CancelMessage = objOld.CancelMessage
        objNew.Notes = objOld.Notes
        objNew.NotesBy = objOld.NotesBy
        objNew.NotesAdditional = objOld.NotesAdditional
        objNew.ClassRecording = objOld.ClassRecording
        objNew.RecordingSize = objOld.RecordingSize
        objNew.RecordingComments = objOld.RecordingComments
        objNew.ClassRecording2 = objOld.ClassRecording2
        objNew.RecordingSize2 = objOld.RecordingSize2
        objNew.RecordingComments2 = objOld.RecordingComments2
        objNew.SourceId = objOld.id
        Catalogue(objNew)
        
        for objOldPresenter in objOld.objectValues('Presenter'):
            objNewPresenter = dodMCIPresenter.NewObject(objNew)
            objNewPresenter.PresenterName = objOldPresenter.PresenterName
            objNewPresenter.PresenterTitle = objOldPresenter.PresenterTitle
            objNewPresenter.Bio = objOldPresenter.Bio
            objNewPresenter.Website = objOldPresenter.Website
            objNewPresenter.EmailAddress = objOldPresenter.EmailAddress
            objNewPresenter.MCIPartner = objOldPresenter.MCIPartner
            Catalogue(objNewPresenter)

def CleanData(objHere):
    print "CleanData"
    VisitData(objHere, 'MCIBook', BlankOneBook)

    print "CopyPersons"
    CopyPersons(objHere)
    ReindexOne(objHere, 'MCIPerson')

    print "CopyBookReviews"
    CopyBookReviews(objHere)
    ReindexOne(objHere, 'MCIBookReview')

    print "CopyNewsletters"
    CopyNewsletters(objHere)
    ReindexOne(objHere, 'MCINewsletter')

    print "CopyMasterclasses"
    CopyMasterclasses(objHere)
    ReindexOne(objHere, 'MCIMasterclass')

    print "SetCategories"
    SetCategories(objHere)

    print "Links"
    VisitData(objHere, 'MCILink', ProcessOneBookCategoryLink)
    VisitData(objHere, 'MCILink', ProcessOneReaderCategoryLink)
    VisitData(objHere, 'MCILink', ProcessOneBookAuthorLink)
    VisitData(objHere, 'MCIEnrolment', ProcessOneEnrolment)
    VisitData(objHere, 'MCIBook', ProcessOneReview)
    print "Done"

def CountBooksForOneCategory(objCategory):
    lstBooks = SearchMany(objCategory, 'MCIBook', 'Categories', objCategory.id)
    for objSubCategory in objCategory.objectValues('MCIBookCategory'):
        lstSubBooks = SearchMany(objSubCategory, 'MCIBook', 'Categories', objSubCategory.id)
        for objBook in lstSubBooks:
            if not objBook in lstBooks:
                lstBooks.append(objBook)
    return len(lstBooks)

def CountBooksForCategories(objHere):
    print "Counting books for categories"
    objCategories = GetDataFolder(objHere, 'MCIBookCategory')
    for objCategory in objCategories.objectValues('MCIBookCategory'):
        objCategory.BooksInCategory = CountBooksForOneCategory(objCategory)
        print objCategory.CategoryName, objCategory.BooksInCategory
        for objSubCategory in objCategory.objectValues('MCIBookCategory'):
            objSubCategory.BooksInCategory = CountBooksForOneCategory(objSubCategory)
            print objSubCategory.CategoryName, objSubCategory.BooksInCategory

def ReindexAll(objHere):
    for strObjectType in ('MCIBookCategory', 'MCIBook', 'MCILink', 'MCIEnrolment', 'MCINewsletter', 'MCIAuthor', 'MCIBookReview', 'MCIMasterclass', 'MCIParticipant', 'MCIPerson', 'MCIPresenter', 'MCIShopAt', 'MCIReaderCategory'):
        ReindexOne(objHere, strObjectType)

def MCIImport(objHere):
    CreateDataObjectDefinitions(objHere, 'MCI')
    ImportSQLData(objHere)
    CleanData(objHere)
    CountBooksForCategories(objHere)
#    ReindexAll(objHere)
