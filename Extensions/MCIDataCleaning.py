import LocalPaths

from libDatabase import GetDataFolder
from libFolders import DeleteObject
from libDatabase import SearchOne
from libDatabase import VisitData
from libDatabase import GetDOD
from libString import AddToLines
from libDatabase import ReindexOne

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
#        DeleteObject(objLink)

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
#        DeleteObject(objLink)

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
#        DeleteObject(objLink)

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
        
        for objOldPresenter in objOld.objectValues('Presenter'):
            objNewPresenter = dodMCIPresenter.NewObject(objNew)
            objNewPresenter.PresenterName = objOldPresenter.PresenterName
            objNewPresenter.PresenterTitle = objOldPresenter.PresenterTitle
            objNewPresenter.Bio = objOldPresenter.Bio
            objNewPresenter.Website = objOldPresenter.Website
            objNewPresenter.EmailAddress = objOldPresenter.EmailAddress
            objNewPresenter.MCIPartner = objOldPresenter.MCIPartner

def CleanData(objHere):
    VisitData(objHere, 'MCIBook', BlankOneBook)

    blnCopyData = False
    blnSortCategories = False

    blnCopyData = True
    blnSortCategories = True
    

    if blnCopyData:
        CopyPersons(objHere)
        ReindexOne(objHere, 'MCIPerson')

        CopyBookReviews(objHere)
        ReindexOne(objHere, 'MCIBookReview')

        CopyNewsletters(objHere)
        ReindexOne(objHere, 'MCINewsletter')

        CopyMasterclasses(objHere)
        ReindexOne(objHere, 'MCIMasterclass')

    if blnSortCategories:
        SetCategories(objHere)
        VisitData(objHere, 'MCILink', ProcessOneBookCategoryLink)
        VisitData(objHere, 'MCILink', ProcessOneReaderCategoryLink)

    VisitData(objHere, 'MCILink', ProcessOneBookAuthorLink)
    VisitData(objHere, 'MCIEnrolment', ProcessOneEnrolment)
    VisitData(objHere, 'MCIBook', ProcessOneReview)

#    ReindexOne(objHere, 'MCIBook')

#    ReindexOne(objHere, 'MCIBookReview')
#    ReindexOne(objHere, 'MCIBookCategory')
#    ReindexOne(objHere, 'MCIReaderCategory')
    
