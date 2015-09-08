import xml.sax.saxutils
from libDatabase import GetDataFolder

def OneURL(strLocation):
    strLocation = xml.sax.saxutils.escape(strLocation)
    strResult = """
   <url>
    <loc>http://www.EuroCoachList.com/%s</loc>
    <changefreq>weekly</changefreq>
   </url>  
""" % strLocation
    return strResult

def StaticPages():
    strResult = ""
    for strLocation in ("",
        "Members/ListProfiles",
        "About",
        "CoachClassified",
        "About/Manage",
        "About/NewMembershipScreens",
        "About/Testimonials",
        "About/WeeklyWorkshopCompilation",
        "ContactDetails",
        "Help",
        "Legal/Copyright",
        "Legal/PrivacyPolicy",
        "Legal/TnCMembership",
        "Legal/TnCWebsite",
        "Archive",
        "Archive/AdvancedSearch",
        "Membership",
        "Rules",
        "SiteMap"):
        strResult += OneURL(strLocation)
    return strResult

def PublicListMessages(objHere):
    print "Adding public list messages"
    # For all messages
    # If public, return: Archive/ViewThread?ThreadId=..
    intPublicCount = 0
    strResult = ""
    objArchive = GetDataFolder(objHere, 'E3Messages')
    for objYear in objArchive.objectValues('Folder'):
        print objYear.id
        for objMonth in objYear.objectValues('Folder'):
            for objMessage in objMonth.objectValues('Folder'):
                if not objMessage.Private:
                    intPublicCount += 1
                    strResult += OneURL("Archive/ViewThread?ThreadId=%s" % objMessage.id)
    print "%s public message(s) found" % intPublicCount
    return strResult

def MemberProfiles(objHere):
    intProfileCount = 0
    strResult = ""
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == "Full":
                strResult += OneURL("Members/ViewProfile?MemberId=%s" % objMember.id)
                intProfileCount += 1
    print "%s profile(s) found" % intProfileCount
    return strResult 

def SubTopics(objTopic):
    intTopicCount = 0
    strResult = ""
    for objSubTopic in objTopic.objectValues("E3Topic"):
        if objSubTopic.ThreadCount > 0:
            strResult += OneURL("Forum/ShowTopic?TopicId=%s" % objSubTopic.id)
            (strSubTopics, intSubTopicCount) = SubTopics(objSubTopic)
            strResult += strSubTopics
            intTopicCount += 1 + intSubTopicCount
    return (strResult, intTopicCount)    

def ForumTopics(objHere):
    objTopics = GetDataFolder(objHere, "E3Topic")
    (strResult, intTopicCount) = SubTopics(objTopics)
    print "%s topics found" % intTopicCount
    return strResult

def Offerings(objHere):
    intOfferingCount = 0
    strResult = ""
    for objBatch in objHere.unrestrictedTraverse('/Data/E3/E3Members').objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == "Full":
                for objOffering in objMember.Offerings.objectValues("E3Offering"):
                    if objOffering.Status == "Published" and objOffering.Deleted == "No":
                        intOfferingCount += 1
                        strResult += OneURL("Offerings?Id=%s" % objOffering.id)
    print "%s offerings found" % intOfferingCount
    return strResult

def HelpPages(objHere):
    intHelpCount = 0
    strResult = ""
    for objPage in objHere.unrestrictedTraverse("/Data/E3/E3Help").objectValues("E3Help"):
        if objPage.Type <> "Rules":
            strResult += OneURL("Help/ShowOne?Id=%s" % objPage.HelpId)
            intHelpCount += 1
    print "%s help pages found" % intHelpCount
    return strResult

def GenerateSitemap(objHere):
    strURLs = ""
    strURLs += StaticPages()
    strURLs += PublicListMessages(objHere)
    strURLs += MemberProfiles(objHere)
    strURLs += ForumTopics(objHere)
    strURLs += Offerings(objHere)
    strURLs += HelpPages(objHere)
    strResult =   """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%s
</urlset>""" % strURLs
    print "New site map generated"
    return strResult
    
    
