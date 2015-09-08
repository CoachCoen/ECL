import clsMCIAuthor
import clsMCIBookReview
import clsMCILink
import clsMCIListStat
import clsMCINewsletter
import clsMCIMasterclass
import clsMCIPerson
import clsMCIPresenter
import clsMCIBookCategory
import clsMCIBook
import clsMCIBookSearch
import clsMCIEnrolmentLog
import clsMCIEnrolment
import clsMCIListStat
import clsMCIParticipant
import clsMCIReaderCategory
import clsMCIShopAt

def initialize(context):
    "Get started"
    context.registerClass(clsMCIBookReview.MCIBookReview, constructors = (clsMCIBookReview.addMCIBookReviewForm, clsMCIBookReview.addMCIBookReview))
    context.registerClass(clsMCINewsletter.MCINewsletter, constructors = (clsMCINewsletter.addMCINewsletterForm, clsMCINewsletter.addMCINewsletter))
    context.registerClass(clsMCIMasterclass.MCIMasterclass, constructors = (clsMCIMasterclass.addMCIMasterclassForm, clsMCIMasterclass.addMCIMasterclass))
    context.registerClass(clsMCIPerson.MCIPerson, constructors = (clsMCIPerson.addMCIPersonForm, clsMCIPerson.addMCIPerson))
    context.registerClass(clsMCIPresenter.MCIPresenter, constructors = (clsMCIPresenter.addMCIPresenterForm, clsMCIPresenter.addMCIPresenter))
    context.registerClass(clsMCIBookCategory.MCIBookCategory, constructors = (clsMCIBookCategory.addMCIBookCategoryForm, clsMCIBookCategory.addMCIBookCategory))
    context.registerClass(clsMCIBook.MCIBook, constructors = (clsMCIBook.addMCIBookForm, clsMCIBook.addMCIBook))
    context.registerClass(clsMCIBookSearch.MCIBookSearch, constructors = (clsMCIBookSearch.addMCIBookSearchForm, clsMCIBookSearch.addMCIBookSearch))
    context.registerClass(clsMCIEnrolmentLog.MCIEnrolmentLog, constructors = (clsMCIEnrolmentLog.addMCIEnrolmentLogForm, clsMCIEnrolmentLog.addMCIEnrolmentLog))
    context.registerClass(clsMCIEnrolment.MCIEnrolment, constructors = (clsMCIEnrolment.addMCIEnrolmentForm, clsMCIEnrolment.addMCIEnrolment))
    context.registerClass(clsMCIListStat.MCIListStat, constructors = (clsMCIListStat.addMCIListStatForm, clsMCIListStat.addMCIListStat))
    context.registerClass(clsMCIParticipant.MCIParticipant, constructors = (clsMCIParticipant.addMCIParticipantForm, clsMCIParticipant.addMCIParticipant))
    context.registerClass(clsMCIReaderCategory.MCIReaderCategory, constructors = (clsMCIReaderCategory.addMCIReaderCategoryForm, clsMCIReaderCategory.addMCIReaderCategory))
    context.registerClass(clsMCIShopAt.MCIShopAt, constructors = (clsMCIShopAt.addMCIShopAtForm, clsMCIShopAt.addMCIShopAt))
    context.registerClass(clsMCIAuthor.MCIAuthor, constructors = (clsMCIAuthor.addMCIAuthorForm, clsMCIAuthor.addMCIAuthor))
    context.registerClass(clsMCILink.MCILink, constructors = (clsMCILink.addMCILinkForm, clsMCILink.addMCILink))
    context.registerClass(clsMCIListStat.MCIListStat, constructors = (clsMCIListStat.addMCIListStatForm, clsMCIListStat.addMCIListStat))
