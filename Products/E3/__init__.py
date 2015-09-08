# encoding: utf-8
import clsE3Member
import clsE3Period
import clsE3UnclaimedEmailAddress
import clsE3EmailAddress
import clsE3List
import clsE3ListStat
import clsE3ListMembership
import clsE3Payment
import clsE3Event
import clsE3WorldPayCall
import clsE3WorldPayResult
import clsE3SessionData
import clsE3MailBoxerMembers
import clsE3Topic
import clsE3Offering
import clsE3EventRegistration
import clsE3Thread
import clsE3EventPreference
import clsE3AvailabilityStatement
import clsE3PlannedMessage
import clsE3SequenceInProgress
import clsE3Conf08Booking
import clsE3MultiOption
import clsE3OfferingCategory
import clsE3SearchQuery
import clsE3OrganisationType
import clsE3Organisation
import clsE3RoleType
import clsE3Role
import clsE3EventSeries
import clsE3OrganisingBody
import clsE3Help

def initialize(context):
    "Get started"
    context.registerClass(clsE3Member.E3Member, constructors = (clsE3Member.addE3MemberForm, clsE3Member.addE3Member))
    context.registerClass(clsE3Period.E3Period, constructors = (clsE3Period.addE3PeriodForm, clsE3Period.addE3Period))
    context.registerClass(clsE3UnclaimedEmailAddress.E3UnclaimedEmailAddress, constructors = (clsE3UnclaimedEmailAddress.addE3UnclaimedEmailAddressForm, clsE3UnclaimedEmailAddress.addE3UnclaimedEmailAddress))
    context.registerClass(clsE3List.E3List, constructors = (clsE3List.addE3ListForm, clsE3List.addE3List))
    context.registerClass(clsE3Payment.E3Payment, constructors = (clsE3Payment.addE3PaymentForm, clsE3Payment.addE3Payment))
    context.registerClass(clsE3Event.E3Event, constructors = (clsE3Event.addE3EventForm, clsE3Event.addE3Event))
    context.registerClass(clsE3WorldPayCall.E3WorldPayCall, constructors = (clsE3WorldPayCall.addE3WorldPayCallForm, clsE3WorldPayCall.addE3WorldPayCall))
    context.registerClass(clsE3WorldPayResult.E3WorldPayResult, constructors = (clsE3WorldPayResult.addE3WorldPayResultForm, clsE3WorldPayResult.addE3WorldPayResult))
    context.registerClass(clsE3SessionData.E3SessionData, constructors = (clsE3SessionData.addE3SessionDataForm, clsE3SessionData.addE3SessionData))
    context.registerClass(clsE3MailBoxerMembers.E3MailBoxerMembers, constructors = (clsE3MailBoxerMembers.addE3MailBoxerMembersForm, clsE3MailBoxerMembers.addE3MailBoxerMembers))
    context.registerClass(clsE3EmailAddress.E3EmailAddress, constructors = (clsE3EmailAddress.addE3EmailAddressForm, clsE3EmailAddress.addE3EmailAddress))
    context.registerClass(clsE3Topic.E3Topic, constructors = (clsE3Topic.addE3TopicForm, clsE3Topic.addE3Topic))
    context.registerClass(clsE3ListStat.E3ListStat, constructors = (clsE3ListStat.addE3ListStatForm, clsE3ListStat.addE3ListStat))
    context.registerClass(clsE3ListMembership.E3ListMembership, constructors = (clsE3ListMembership.addE3ListMembershipForm, clsE3ListMembership.addE3ListMembership))
    context.registerClass(clsE3AvailabilityStatement.E3AvailabilityStatement, constructors = (clsE3AvailabilityStatement.addE3AvailabilityStatementForm, clsE3AvailabilityStatement.addE3AvailabilityStatement))
    context.registerClass(clsE3EventPreference.E3EventPreference, constructors = (clsE3EventPreference.addE3EventPreferenceForm, clsE3EventPreference.addE3EventPreference))
    context.registerClass(clsE3Thread.E3Thread, constructors = (clsE3Thread.addE3ThreadForm, clsE3Thread.addE3Thread))
    context.registerClass(clsE3Offering.E3Offering, constructors = (clsE3Offering.addE3OfferingForm, clsE3Offering.addE3Offering))
    context.registerClass(clsE3EventRegistration.E3EventRegistration, constructors = (clsE3EventRegistration.addE3EventRegistrationForm, clsE3EventRegistration.addE3EventRegistration))
    context.registerClass(clsE3PlannedMessage.E3PlannedMessage, constructors = (clsE3PlannedMessage.addE3PlannedMessageForm, clsE3PlannedMessage.addE3PlannedMessage))
    context.registerClass(clsE3SequenceInProgress.E3SequenceInProgress, constructors = (clsE3SequenceInProgress.addE3SequenceInProgressForm, clsE3SequenceInProgress.addE3SequenceInProgress))
    context.registerClass(clsE3Conf08Booking.E3Conf08Booking, constructors = (clsE3Conf08Booking.addE3Conf08BookingForm, clsE3Conf08Booking.addE3Conf08Booking))
    context.registerClass(clsE3OrganisationType.E3OrganisationType, constructors = (clsE3OrganisationType.addE3OrganisationTypeForm, clsE3OrganisationType.addE3OrganisationType))    
    context.registerClass(clsE3MultiOption.E3MultiOption, constructors = (clsE3MultiOption.addE3MultiOptionForm, clsE3MultiOption.addE3MultiOption))
    context.registerClass(clsE3OfferingCategory.E3OfferingCategory, constructors = (clsE3OfferingCategory.addE3OfferingCategoryForm, clsE3OfferingCategory.addE3OfferingCategory))
    context.registerClass(clsE3SearchQuery.E3SearchQuery, constructors = (clsE3SearchQuery.addE3SearchQueryForm, clsE3SearchQuery.addE3SearchQuery))
    context.registerClass(clsE3OrganisationType.E3OrganisationType, constructors = (clsE3OrganisationType.addE3OrganisationTypeForm, clsE3OrganisationType.addE3OrganisationType))
    context.registerClass(clsE3Organisation.E3Organisation, constructors = (clsE3Organisation.addE3OrganisationForm, clsE3Organisation.addE3Organisation))
    context.registerClass(clsE3RoleType.E3RoleType, constructors = (clsE3RoleType.addE3RoleTypeForm, clsE3RoleType.addE3RoleType))
    context.registerClass(clsE3Role.E3Role, constructors = (clsE3Role.addE3RoleForm, clsE3Role.addE3Role))
    context.registerClass(clsE3EventSeries.E3EventSeries, constructors = (clsE3EventSeries.addE3EventSeriesForm, clsE3EventSeries.addE3EventSeries))
    context.registerClass(clsE3OrganisingBody.E3OrganisingBody, constructors = (clsE3OrganisingBody.addE3OrganisingBodyForm, clsE3OrganisingBody.addE3OrganisingBody))
    context.registerClass(clsE3Help.E3Help, constructors = (clsE3Help.addE3HelpForm, clsE3Help.addE3Help))

