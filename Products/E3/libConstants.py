# encoding: utf-8

import datetime

cnConf08Price = 99
cnConf08EBDiscount = 15
cnConf08EBDate = datetime.date(2008, 5, 1)
cnConf08FullPaymentDate = datetime.date(2008, 8, 20)
cnConf08Deposit = 35
cnConf08MembersDiscount = 10

cnOrganisationTypes = ('Local coaches network', 'Other coaches network', 'Other network', 'Coaching provider', 'Training provider', 'Other organisation')

cnRoles = ('Host', 'Employee', 'Contractor', 'Owner', 'Associate', 'Organiser', 'Administrator', 'Contact person', 'Other')

cnEventRoles = ('Host', 'Presenter', 'Organiser', 'Administrator', 'Contact person', 'Other')

cnRelationOptions = ('This is my own service or product which I want to advertise', 'I have used this service or product and want to recommend it', 'This service or product is purely aimed at coaches and might be of interest to others', 'This is a general product or service which may be of interest to others')

cnEventRelationOptions = ('This is my own event which I want to advertise', 'I have attended this event in the past and want to recommend it', 'This event is purely aimed at coaches and might be of interest to others', 'This is a general event which may be of interest to others')

cnDictRelationOptions = {'Own': cnRelationOptions[0],
    'Recommend': cnRelationOptions[1],
    'Coaches': cnRelationOptions[2],
    'List': cnRelationOptions[3]}

cnEventMOGroups = (  ("For Coaches",
                    'If this is an event mainly for coaches, choose what type of coach(es) it is for',
                    'TargetAudienceCoaches'),
                    ("For Others",
                    'Who is this event for? Note: if this is specifically for coaches then also see the next box',
                    'TargetAudienceGeneral'),
                    ("Business &amp; Career",
                    'If this is an event to help people in their business or career, what does it cover?',
                    'TopicsBusinessAndCareer'),
                    ("Personal",
                    'If this is an event to help people in their personal lives, what does it cover?',
                    'TopicsPersonalSuccess'))

cnMOGroups = (  ("For Coaches",
                    'If this is a product or service mainly for coaches, choose what type of coach(es) it is for',
                    'TargetAudienceCoaches'),
                    ("For Others",
                    'Who is this product or service for? Note: if this is specifically for coaches then also see the next box',
                    'TargetAudienceGeneral'),
                    ("Business &amp; Career",
                    'If this is a product or service to help people in their business or career, what does it cover?',
                    'TopicsBusinessAndCareer'),
                    ("Personal",
                    'If this is a product or service to help people in their personal lives, what does it cover?',
                    'TopicsPersonalSuccess'),
                    ("Books for Coaches",
                    "",
                    "BooksForCoaches"),
                    ("Service Delivery",
                    'If this is a service, how do you get the service to the customer(s)',
                    'DeliveryMechanismService'),
                    ("Product Delivery",
                    'If this is a product, how do you get the product to the customer(s)',
                    'DeliveryMechanismProduct'),
                    ("Group size",
                    'If this is a service, is it offered to individuals or to groups. For instance, group coaching versus one-to-one coaching',
                    'GroupSize')    )

cnPnSCategories = ('Coaching', 'Mentoring', 'Supervision', 'Training', 'Website design and creation', 'Marketing, PR and advertising', 'Internet or computing support, programming, other', 'Other personal service (personally delivered)', 'Broadband, other telecommunications', 'Other service', 'Software', 'Headsets, telephones, other phone equipment', 'Cards and other gifts', 'Books, e-books, other publications', 'Training materials', 'Other product')

cnEventCategories = ('Coach training', 'Other training', 'Conference', 'Talk or presentation', 'Coaches meeting or networking', 'Other meeting or networking', 'Other')

cnProfileFieldNames = ('Name', 'Country', 'Location', 'Postcode', 'Languages', 'ContactEmailAddress', 'WebsiteAddress', 'PhoneNumber', 'HostOfChapter', 'CommunityComments', 'TagLine', 'Biography', 'Testimonials', 'CommercialComments', 'ShowFullName', 'ShowCountry', 'ShowLocation', 'ShowPostcode', 'ShowEmailAddress', 'ShowPhoneNumber', 'ShowBiography', "ShowCommunityComments", "TwitterUsername")

cnProductFieldNames = ('id', 'Type', 'myTitle', 'Category', 'Description', 'OfferForMembers', 'Relation', 'RelationDetails', 'Status')

cnServiceFieldNames = ('id', 'Type', 'myTitle', 'Category', 'Description', 'OfferForMembers', 'Relation', 'RelationDetails', 'Status', 'TargetAudienceCoaches', 'TargetAudienceGeneral', 'TopicsBusinessAndCareer', 'TopicsPersonalSuccess', 'DeliveryMechanismService', 'DeliveryMechanismProduct', 'GroupSize', 'WebsiteAddress', 'Deleted', "BooksForCoaches")

cnEventFieldNames = ('id', 'myTitle', 'Category', 'Description', 'OfferForMembers', 'Relation', 'RelationDetails', 'Status', 'TargetAudienceCoaches', 'TargetAudienceGeneral', 'TopicsBusinessAndCareer', 'TopicsPersonalSuccess','WebsiteAddress', 'Deleted', 'FaceToFace', 'InternetBased', 'TelephoneBased', 'Country', 'Location', 'StartDate-year', 'StartDate-month', 'StartDate-date', 'StartDate', 'OrganisationId', 'EventSeriesId', 'Role', 'DateDescription', 'Type')

cnCountryNames = ("Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burma", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo, Democratic Republic", "Congo, Republic of the", "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Greenland", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", "Korea, South", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Morocco", "Monaco", "Mozambique", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Norway", "Oman", "Pakistan", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", " Sao Tome", "Saudi Arabia", "Senegal", "Serbia and Montenegro", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "Spain", "Sri Lanka", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe")

cnTopTopics = ('E3Topic00330', 'E3Topic00324', 'E3Topic00320')

cnSearchResultsLimit = 250

cnMCIRoot = "www.MentorCoaches.com"
cnECLRoot = "www.EuroCoachList.com"

cnListNameECL = 'ECL'

# Amounts in v3.0
# cnEuroAmount = 30
# cnEuroBankCosts = 7
# cnUSAmount = 37
# cnUKAmount = 20

# Amounts in v3.1, from XE.com, 19/3/07
#cnEuroAmount = 25
#cnEuroBankCosts = 7
#cnUSAmount = 40
#cnUKAmount = 20

# Updated in v8.3.1, from XE.com, 13/11/08
#cnEuroAmount = 24
#cnEuroBankCosts = 7
#cnUSAmount = 30
#cnUKAmount = 20


# Updated in v3.8.7, from XE.com, 2/1/09
#cnEuroAmount = 23
#cnEuroBankCosts = 7
#cnUSAmount = 29
#cnUKAmount = 20

#Updated 24/3/11, increase to GBP30
cnUKAmount = 30
cnUSAmount = 48
cnEuroAmount = 35
cnEuroBankCosts = 7

cnAnnualAmount = "&pound;%s (about &euro;%s or US$%s)" % (cnUKAmount, cnEuroAmount, cnUSAmount)
cnAnnualAmountEmail = "GBP%s (about Euro%s or USD%s)" % (cnUKAmount, cnEuroAmount, cnUSAmount)

cnDeliveryModes = ('Direct', 'MIMEDigest', 'TextDigest', 'StructuredDigest', 'TopicsList', 'NoMail')

cnModeNoDigest = 0
cnModeTextDigest = 1
cnModeMIMEDigest = 2

cnStatsList = ('Live', 'MIMEDigest', 'TextDigest', 'Direct', 'HolidayMode', 'Paid', 'Trial', 'Lifetime', 'Expired', 'Total', 'BonusSentYesterday', 'WarningSentYesterday', 'PaymentYesterday', 'NonAdvertPostedYesterday', 'AdvertPostedYesterday', 'JoinedYesterday', 'ExpiredYesterday', 'TotalPostings', 'Postings3Months', 'TotalPublicPostings', 'PublicPostings3Months', 'LiveProfiles', 'LiveOfferings', 'FirstPaymentYesterday', 'RenewalYesterday', 'TrialExpiredYesterday', "Unconfirmed", "UnconfirmedLive")

cnNoError = 0
cnErrorAlreadySubscribed = 1
cnErrorSubscribingTheListAddress = 2
cnErrorMemberIsBanned = 3
cnErrorIncorrectEmailAddress = 4
cnErrorHostileAddress = 5
cnErrorNeedApproval = 6
cnErrorUnknown = 7
cnErrorUnknownList = 8

cnEmailListOwner = '<a href="mailto:coen@coachcoen.com">coen@coachcoen.com</a>'

cnMailmanEmptyDate = (0, 0, 0)
cnEmptyDate = datetime.date(1, 1, 1)
cnEmptyZopeDate = "01 Jan 1901"
cnMailmanLastDate = (1, 1, 3000)
cnLastDate = datetime.date(3000, 1, 1)
cnMailmanFirstDate = (1, 1, 1980)
cnFirstDate = datetime.date(1980, 1, 1)
cnFirstZopeDate = "1 Jan 1980"
cnLastZopeDate = "31 Dec 3000"
cnShortDateFormat = '%d %b %Y'
cnFullDateFormat = '%A %d %B %Y'

cnTrialPeriodExpired = """Hi there,

I hope you have enjoyed your Euro Coach List trial membership. Your free trial period has now expired

You were subscribed with address: %%s

If you have already paid please let me know when and how you paid so I can trace your payment and reinstate your membership. Thanks

If you have decided not to continue your membership please let me know how I might improve the list to make you change your mind

Or please rejoin now, the annual membership fee is %s

""" % cnAnnualAmountEmail

cnPaidPeriodExpired = """Hi there,

According to my records, your Euro Coach List membership has now expired

I hope you have enjoyed your membership and that it has been beneficial to your business

You were subscribed with address: %%s

If you have already paid please let me know when and how you paid so I can trace your payment and reinstate your membership. Thanks

If you have decided not to continue your membership please let me know how I might improve the list to make you change your mind

Or please rejoin now, the annual membership fee is %s

""" % cnAnnualAmountEmail

cnTrialPeriodDue = """Hi there,

As you may know, the Euro Coach List is a paid-for list. New members get a free three month trial period

Your trial period is due to expire in 3 weeks' time

You are subscribed with address: %%s

If you have already paid please let me know when and how you paid so I can trace your payment. Thanks

As fellow top UK coach George Metcalfe put it "The EuroCoach List is absolutely central to my professional career as a coach". And Denise Taylor said "I am proud to be a member of such a supportive group as this, I have got so much out of it, it is worth every penny!"

In case you have found the volume of list messages too much, you will find lots of tips on how to manage the volume at www.EuroCoachList.com/Help

The annual membership fee is %s. Please pay your membership now

""" % cnAnnualAmountEmail

cnPaidPeriodDue = """Hi there,

Thanks again for paying your Euro Coach List membership. According to my records, your current membership is due for renewal within the next three weeks

You are subscribed with address: %%s

If you have already paid please let me know when and how you paid so I can trace your payment. Thanks

As fellow top UK coach George Metcalfe put it "The EuroCoach List is absolutely central to my professional career as a coach". And Denise Taylor said "I am proud to be a member of such a supportive group as this, I have got so much out of it, it is worth every penny!"

The annual membership fee is %s. Please pay your membership now

""" % cnAnnualAmountEmail

cnBonus = """Hi there,

Thanks again for being a member of the Euro Coach List

Your current membership runs until %%s

As a valued member of our community, I would like to offer you up to three months' extra membership for free. All you have to do is pay soon

Here is how it works:
If you pay 13 weeks (3 months) early, you get an extra 13 weeks' membership for free
If you pay 12 weeks early, you get 12 weeks for free
If you pay 11 weeks early, you get 11 weeks for free
etc.

To get the maximum free period, please pay by %%s

A fellow list member recently told me "The List is an important part of my development as a coach. I am learning heaps and getting lots of support. I  paid my membership with gratitude and thanks for such a great site."

The annual membership fee is %s

""" % cnAnnualAmountEmail

cnSignature = """Sunshine and butterflies,

Coen

-----------------------------------------
Technical services for coaches and coaching organisations :-
 website creation, application programming, online communities - www.coachcoen.com
Owner of Europe's premier coaching community - www.EuroCoachList.com

Telephone: +44 (0)117 9550062
"""


cnReceipt = """Compass Mentis
Coen de Groot
56 Fairfield Road
Bristol BS6 5JP
Tel: +44 (0)117 955 0062
---------------------------------

Invoice Number: ECL%(InvoiceNumber)s
Invoice Date:   %(InvoiceDate)s
Invoice Due:    - Paid in full -


Receipt to:
%(Name)s
%(EmailAddress)s

Payment received for Euro Coach List Membership, 1 year

Total %(Amount)s. No VAT charged

Payment received %(InvoiceDate)s, with thanks :-)

Your membership now runs until %(EndOfMembershipDate)s

Any questions, please email me at coen@coachcoen.com

"""

cnGeneralReceipt = """Compass Mentis
Coen de Groot
56 Fairfield Road
Bristol BS6 5JP
Tel: +44 (0)117 955 0062
---------------------------------

Invoice Number: ECL%(InvoiceNumber)s
Invoice Date:   %(InvoiceDate)s
Invoice Due:    - Paid in full -


Receipt to:
%(Name)s
%(EmailAddress)s

Payment received for %(Description)s

Total %(Amount)s. No VAT charged

Payment received %(InvoiceDate)s, with thanks :-)

Any questions, please email me at coen@coachcoen.com

"""


cnHowToPay = """You can pay online, by cheque or bank transfer

Online: Go to www.EuroCoachList.com/MyECL and log in with username "%%s" and password "%%s"
At the top you'll see a row of tabs. This should already be on "Membership"
Further down the screen is another set of (sub)tabs. Select the "Pay" tab. Now click on the "Pay online now" button

PayPal: Email your payment to coen@coachcoen.com

UK cheque: Post a cheque for GBP%s, payable to "Compass Mentis" to:
Coen de Groot, 56 Fairfield Road, Bristol, BS6 5JP
Include a note with your name and email address

UK bank transfer: Transfer GBP%s to
"Compass Mentis"
The Royal Bank of Scotland, Ayr Chief Office
Sort code 83-15-26, account number 00683788
Reference: Your email address

Euro Cheque: Post a cheque for Euro%s, payable to "Compass Mentis" to:
Coen de Groot, 56 Fairfield Road, Bristol, BS6 5JP, United Kingdom
Include a note with your name and email address

Dutch bank transfer: Transfer Euro%s to
C.J.M. de Groot, Bristol, Engeland
82.30.33.244
Reference: Your email address

Unless you pay online or via PayPal, send me an email to let me know how you've paid, so I can look out for your payment. You will receive a receipt via email. This can take up to a month

""" % (cnUKAmount, cnUKAmount, (cnEuroAmount + cnEuroBankCosts), cnEuroAmount)
