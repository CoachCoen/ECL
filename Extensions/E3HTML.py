# encoding: utf-8

"""Functions for pulling together the HTML (pages)"""

import LocalPaths
reload(LocalPaths)

from E3TempData import GetErrorScreen
from E3Members import GetCurrentMember
from E3TempData import GetUsername
from E3TempData import GetMessages
from E3TempData import IsLoggedIn
from libDatabase import GetWebsiteRoot
from libGeneral import GetParameter
from libDatabase import GetDataFolder
from libDatabase import SearchOne
from E3Search import SearchResults
from E3Members import ManagerLoggedIn
from E3TempData import SetPageTitle
from E3TempData import GetPageTitle
from libConstants import cnECLRoot
from E3Members import IsFullMember
from libConstants import cnUKAmount, cnUSAmount, cnEuroAmount
from libString import ToUnicode
from E3Offerings import GeneralOfferingsSearch
from libBuildHTML import FullURL

def MembershipFee():
    return "&pound;%s (about US$%s or &euro;%s)" % (cnUKAmount, cnUSAmount, cnEuroAmount)

def UpdateCacheItem(objHere, strName):
    print "Looking for |%s|" % strName
    objSourceItem = objHere.unrestrictedTraverse("/Websites/ECLv3/%s" % strName)
    varSourceItem = objSourceItem.__call__(objSourceItem)

    objTargetItem = objHere.unrestrictedTraverse("/Websites/ECLv3/cache/%s" % strName)
    blnDone = False
    try:
        objTargetItem.pt_edit(varSourceItem, 'text/html', 'utf-8')
        blnDone = True
    except:
        pass

    if not blnDone:
        try:
            objTargetItem.pt_edit(unicode(varSourceItem, 'utf-8'), 'text/html', 'utf-8')
            blnDone = True
        except:
            pass
    print strName
    if not blnDone:
        objTargetItem.pt_edit(varContents, 'text/html', 'utf-8')
        print " ... not done"

def UpdateAllCacheItems(objHere):
#    UpdateCacheItem(objHere, "LHBlockMessages")
#    UpdateCacheItem(objHere, "LHBlockConference")
    UpdateCacheItem(objHere, "LHBlockManager")
#    UpdateCacheItem(objHere, "RHBlockMCIBooks")
#    UpdateCacheItem(objHere, "RHBlockMCIMasterclasses")
#    UpdateCacheItem(objHere, "LHBlockTopicsTree")
    UpdateCacheItem(objHere, "HPBlockFeaturedMember")
    UpdateCacheItem(objHere, "HPBlockFeaturedOfferings")
    UpdateCacheItem(objHere, "HPBlockRecentDiscussions")
#    UpdateCacheItem(objHere, 'HomePageContents')

def NewFeaturedMember(objHere):
    UpdateCacheItem(objHere, "HPBlockFeaturedMember")

def UpdateSitemap(objHere):
    UpdateCacheItem(objHere, "Sitemap.inc")

def PageTitle(objHere):
    strPageTitle = GetPageTitle(objHere)
    if not strPageTitle:
        try:
            strPageTitle = objHere.PageTitle.__call__(client=objHere)
        except:
            strPageTitle = objHere.title_or_id()
    return strPageTitle

def PresentWebTree(lstResult):
    strResult = ""
    if lstResult:
        lstResult.sort(ByFirstItem)
        for (strTitle, strHTML) in lstResult:
            strResult = strResult + strHTML
        strResult = "<ul>\n%s</ul>\n" % strResult
    return strResult

def OneMapItem(objItem, blnLinkTo = True):
    return """<li><a href="%s">%s</a></li>\n""" % (objItem.absolute_url(), objItem.title_or_id())

def ByFirstItem(lstItem1, lstItem2):
    return cmp(lstItem1[0], lstItem2[0])

def TravelWebsite(objFolder):
    lstResult = []
    for objItem in objFolder.objectValues('Folder'):
        if objItem.unrestrictedTraverse('Mapped'):
            lstResult.append((objItem.title, OneMapItem(objItem) + TravelWebsite(objItem)))
    strResult = ""
    if lstResult:
        lstResult.sort(ByFirstItem)
        for (strTitle, strHTML) in lstResult:
            strResult = strResult + strHTML
        strResult = "<ul>\n%s</ul>\n" % strResult
    return strResult

def SearchNode(objItem, strSearchText):
    """Return True if strSearchText is found in objItem
        Note: objItem may have a special function that returns its content"""
    if 'PageContents' in objItem.objectIds():
        varContents = objItem.PageContents.__call__(objItem)
        strContents = ToUnicode(varContents)
        if strSearchText.lower() in strContents.lower():
            return (True, objItem.title, OneMapItem(objItem))
    return (False, '', '')

def BuildSitemap(objHere):
    objStart = GetWebsiteRoot(objHere, 'E3')
    strResult = TravelWebsite(objStart)
    return strResult

def SearchHomePage(objHere, strSearchText):
    objHomePage = objHere.unrestrictedTraverse('/Websites/ECLv3')
    (blnTextInNode, strTitle, strHTMLCode) = SearchNode(objHomePage, strSearchText)
    if blnTextInNode:
        return PresentWebTree([(strTitle, strHTMLCode), ])
    return ""

def SearchWebBranch(objBranch, strSearchText):
    lstResult = []
    blnFullMember = IsFullMember(objBranch)
    for objItem in objBranch.objectValues('Folder'):
        try:
            blnNeedsFullMembership = objItem.unrestrictedTraverse('NeedsFullMembership')
        except:
            blnNeedsFullMembership = False
#        print objItem, blnNeedsFullMembership, blnFullMember
        if objItem.unrestrictedTraverse('Mapped') and objItem.unrestrictedTraverse('MaySearch') and (blnFullMember or not blnNeedsFullMembership):
            strSubResult = SearchWebBranch(objItem, strSearchText)
            (blnTextInNode, strTitle, strHTMLCode) = SearchNode(objItem, strSearchText)
            if blnTextInNode:
                lstResult.append((strTitle, strHTMLCode + strSubResult))
            else:
                if strSubResult:
                    lstResult.append((objItem.title, OneMapItem(objItem, False) + strSubResult))
    return PresentWebTree(lstResult)

def SearchHelp(objHere, strSearchText):
    objHelpFolder = GetDataFolder(objHere, 'E3Help')
    lstResult = []
    for objHelp in objHelpFolder.objectValues('E3Help'):
        if not objHelp.Type == 'Rules' and \
            (strSearchText in " ".join(objHelp.Lines).lower() or
            strSearchText in objHelp.title):
            lstResult.append((objHelp.title, """<li><a href="/Help/ShowOne?Id=%s">%s</a></li>\n""" % (objHelp.HelpId, objHelp.title)))
    return PresentWebTree(lstResult)

def SearchRules(objHere, strSearchText):
    objRules = GetWebsiteRoot(objHere, 'E3').Rules
    lstResult = []
    for (strId, varValue) in objRules.propertyItems():
        strTitle = ""
        if not strId in ['title', 'MaySearch']:
            if strSearchText in varValue.lower():
                if strId == 'MainPage':
                    strLink = '/Rules'
                    strTitle = "List Rules"
                else:
                    strLink = '/Rules?Id=%s' % strId
                    objHelp = SearchOne(objHere, 'E3Help', 'HelpId', strId)
                    if objHelp:
                        strTitle = objHelp.title
                if strTitle:
                    lstResult.append((strTitle, """<li><a href="%s">%s</a></li>\n""" % (strLink, strTitle)))
    return PresentWebTree(lstResult)

def SiteSearch(objHere):
    objStart = GetWebsiteRoot(objHere, 'E3')
    objRequest = objHere.REQUEST
    strSearchText = GetParameter(objRequest, 'SearchText').lower()
    if strSearchText:
        strOfferings = GeneralOfferingsSearch(objHere, strSearchText)
        strWebPages = SearchHomePage(objHere, strSearchText) + SearchWebBranch(objStart, strSearchText)
        strHelp = SearchHelp(objHere, strSearchText)
        strRules = SearchRules(objHere, strSearchText)
#        if IsLoggedIn(objHere):
        strArchive = SearchResults(objHere, objRequest, strSearchText)
        strResult = "<p><em>Searching for: %s</em></p>\n" % strSearchText
        if strWebPages:
            strResult += "<h2>Website pages</h2>\n" + strWebPages

        if strHelp:
            strResult += "<h2>Help pages</h2>\n" + strHelp

        if strRules:
            strResult += "<h2>List rules</h2>\n" + strRules

        if not strWebPages + strHelp + strRules:
            strResult += "<h2>No website pages found</h2>"

        if strOfferings:
            strResult += "<h2>Products and Services</h2>\n" + strOfferings

        if IsFullMember(objHere):
            if strArchive:
                strResult += "<h2>List messages</h2>\n" + strArchive
            else:
                strResult += "<h2>No list messages found</h2>\n"
        else:
            if strArchive:
                strResult += "<h2>Public list messages</h2>\n" + strArchive
            else:
                strResult += "<h2>No public list messages found</h2>\n"

#            strResult += """<h2>List messages</h2>
#    <p>For list members only. Membership is free for the first three months.
#        <a href="/Membership">Join now</a></p>"""

    else:
        strResult = """<p class="ErrorMessage">No text specified, please try again</p>"""
    return strResult

def GetPageTemplate(objHere, strName):
    """Finds <strName>, starting from <objHere> and makes sure that it is processed"""
    objPage = objHere.unrestrictedTraverse(strName)
    return objPage.__call__(client=objHere)

def GetPageContents(objHere, strTemplate = "PageContents"):
    from E3Thread import IsThreadPublic
    """Figures out what to show on the page
        If error screen to show, show it
        Checks whether user has sufficient priviliges, asks to log in if required
        If all of that is okay, find and show PageContents"""

    strErrorScreen = GetErrorScreen(objHere)
    if strErrorScreen:
        return strErrorScreen

    try:
        blnNeedsCurrentMembership = objHere.unrestrictedTraverse('NeedsCurrentMembership')
    except:
        blnNeedsCurrentMembership = False

    try:
        blnNeedsFullMembership = objHere.unrestrictedTraverse('NeedsFullMembership')
    except:
        blnNeedsFullMembership = False

    try:
        blnNeedsMembership = objHere.unrestrictedTraverse('NeedsMembership')
    except:
        blnNeedsMembership = False

    try:
        blnNeedsManager = objHere.unrestrictedTraverse('NeedsManager')
    except:
        blnNeedsManager = False

    try:
        blnCheckPublicMessage = objHere.unrestrictedTraverse('CheckPublicMessage')
    except:
        blnCheckPublicMessage = False

    if blnNeedsCurrentMembership or blnNeedsFullMembership or blnNeedsMembership or blnCheckPublicMessage:
        objMember = GetCurrentMember(objHere)

    if blnNeedsCurrentMembership:
        if not objMember or objMember.MembershipType == 'None':
            return GetPageTemplate(objHere, 'AskCurrentMembership')

    if blnNeedsFullMembership:
        if not objMember:
            return GetPageTemplate(objHere, 'AskMembership')
        if objMember.MembershipType == 'None':
            return GetPageTemplate(objHere, 'AskPayment')

    if blnNeedsMembership:
        if not objMember:
            return GetPageTemplate(objHere, 'AskMembership')

    if blnNeedsManager:
        if not ManagerLoggedIn(objHere):
            return GetPageTemplate(objHere, 'AskManager')

    if blnCheckPublicMessage:
        if not objMember or objMember.MembershipType == 'None':
            if not IsThreadPublic(objHere, objHere.REQUEST):
                if not objMember:
                    return GetPageTemplate(objHere, 'AskMembership')
                else:
                    return """<p>Your membership is expired. Before you can view this message you need to renew your membership on the <a href="/MyECL">MyECL page</a></p>"""


    strResult = ""
    (strErrorMessage, strPlainMessage) = GetMessages(objHere)

    if strErrorMessage:
        strResult = strResult + """<p class="ErrorMessage">%s</p>""" % strErrorMessage

    if strPlainMessage:
        strResult = strResult + """<p class="Message">%s</p>""" % strPlainMessage

    strResult = strResult + GetPageTemplate(objHere, strTemplate)

    # Code to fix UnicodeDecodeError error, as per http://wiki.wxpython.org/index.cgi/UnicodeDecodeError
#    strResult = strResult.decode('latin1')

#    print "Result generated"
#    strResult = "Testing"
#    ShowCharsOver128(strResult)
#    strResult = "Testing"
#    strResult = strResult.replace('_', '')
#    strResult = strResult.encode('utf-8')
#    try:
#        strResult = strResult.encode('utf-8')
#    except:
#        pass
    return strResult

def InsertAbsoluteReferences(strHTML, strTag, strAppend = "http://" + cnECLRoot):
    # Anything which says: href = "..., without http:// in front
    # Plus src = "...., without http:// in front
    # should be replaced with = "http://www.eurocoachlist.com/....." (with or without the / at the end)
    strResult = ""
    strToDo = strHTML
    while strTag in strToDo.lower():
        intPosition = strToDo.lower().find(strTag)
        strResult = strResult + strToDo[:intPosition]
        strToDo = strToDo[intPosition:]
        intPosition = strToDo.find('"') + 1
        strResult = strResult + strToDo[:intPosition]
        strToDo = strToDo[intPosition:]
        intPosition = strToDo.find('"')
        strAddress = strToDo[:intPosition]
#        print "Address found: '%s'" % strAddress
        if not "http:" in strAddress.lower():
            if strAddress[0] <> '/':
                strAddress = "/" + strAddress
            strAddress = strAppend + strAddress
        strToDo = strToDo[intPosition:]
        strResult = strResult + strAddress

    strResult = strResult + strToDo
#    strResult = ToUnicode(strHTML)
    return strResult

#def ToUnicode(strHTML):
#    print "Testing"
#    strResult = strHTML.encode('iso-8859-1', 'replace')
#    strResult = strHTML.encode('iso-8859-1', 'ignore')
#    return strResult

def LoadContainerContents(objHere):
    strUsername = GetUsername(objHere)
    if not strUsername and objHere.id == "ECLv3":
        strResult = objHere.NewHomePageContainerContents.__call__(objHere)
    else:
        strResult = objHere.MainContainerContents.__call__(objHere)
    return strResult

def CompletePage(objHere, blnAbsoluteReference = False):
# Was: <span tal:replace="structure here/MainTemplate"></span>
#    strUsername = GetUsername(objHere)

    strResult = objHere.MainTemplate.__call__(objHere)
#    strResult = ToUnicode(strResult)
#    blnAbsoluteReference = True
    if blnAbsoluteReference:
        strResult = InsertAbsoluteReferences(strResult, "href")
#        strResult = InsertAbsoluteReferences(strResult, "src", "zope_")
#    print strResult[:1000]
    return strResult


def ShowCharsOver128(strString):
    print "Over128:"
    for strChar in strString:
        if ord(strChar) > 127:
            print "%s = char(%s), over 127" % (strChar, ord(strChar))
#    strDummy = strString.decode('latin1')
    fileText = open('/home/zope/Page.txt', 'w')
    fileText.write(strString)
    print strString

def PersonalTools(objHere, blnOnHomePage = False):
    """Shows personal actions
        If logged in, greeting and option to log out
        If not logged in, form to log in or join"""
    strUsername = GetUsername(objHere)
    strURL = FullURL(objHere)
    strURL2 = strURL
    if "?" in strURL:
        strURL2 += "&"
    else:
        strURL2 += "?"
    if strUsername:
        objMember = GetCurrentMember(objHere)
        if objMember.HasConfirmedEmailAddress:
            strToConfirm = ""
        else:
            strToConfirm = """<div class="LeftBoxError"><p><a href="%sAction=ConfirmationEmail">No confirmed email address. Click here to be sent a confirmation request</a></p></div>""" % strURL2
        return """
<div id="LeftBox">
    <img src="/images/BoxTop.gif" width="197" height="12" border="0"/>
    <div id="LeftBoxContents">
        <h1>Welcome</h1>
        <p>Hello %(Name)s</p>
        <ul>
            <li><a href="/MyECL">Your profile, and other information</a></li>
            <li><a href="/MyECL/Events">Your events</a></li>
            <li><a href="/MyECL/Offerings">Your products and services</a></li>
            <li><a href="%(URL)sAction=LogOut">Log out</a></li>
        </ul>
        %(ToConfirm)s
    </div>
    <img src="/images/BoxBottom.gif" width="197" height="12" />
</div>
""" % {'Name': strUsername,
       'URL': strURL2,
       "ToConfirm": strToConfirm}
    elif blnOnHomePage:
        return """
<div id="OrangeLeftBox">
    <img src="/images/OrangeBoxTop.gif" width="197" height="12" border="0"/>
    <div id="LeftBoxContents">
        <h2>Already a member?</h2>
                <form action="%(URL)s" method="post">
            <p>
                <input type="hidden" name="Action" value="LogIn">
                                <input type="text" name="Username" value = "Username" class="txt"/>
                                <input type="password" name="Password" value = "Password" class="txt"/>
                                <br clear="all">
                                <input type="checkbox" name="KeepLoggedIn" value="Yes"> Keep me logged in
                        </p>
            <p class="FormComment">
                <a href="%(URL2)sAction=PasswordReminder">(Forgot your password?)</a>
            </p>
                        <p>
                            <input name="" type="submit" value="Log in" class="btn"/>
                        </p>
                </form>
        </div>
        <img src="/images/OrangeBoxBottom.gif" width="197" height="12" />
</div>
""" % {'Name': strUsername,
                                  'URL': strURL,
                                  'URL2': strURL2}
    else:
        return """
<div id="OrangeLeftBox">
    <img src="/images/OrangeBoxTop.gif" width="197" height="12" border="0"/>
    <div id="LeftBoxContents">
        <h2>Join now</h2>
 	    <p><b>Free</b> 3 months membership</p>
		<form action="/Membership/Welcome" method="post">
            <p>
                <input type="hidden" name="Action" value="JoinNow">
				<input type="text" name="EmailAddress" value = "Email Address" class="txt"/>
		    </p>
			<p>
			    <input name="" type="submit" value="Join" class="btn"/>
			</p>
		</form>
		<h2>Log in</h2>
		<form action="%(URL)s" method="post">
            <p>
                <input type="hidden" name="Action" value="LogIn">
				<input type="text" name="Username" value = "Username" class="txt"/>
				<input type="password" name="Password" value = "Password" class="txt"/>
				<br clear="all">
				<input type="checkbox" name="KeepLoggedIn" value="Yes"> Keep me logged in
			</p>
            <p class="FormComment">
                <a href="%(URL2)sAction=PasswordReminder">(Forgot your password?)</a>
            </p>
			<p>
			    <input name="" type="submit" value="Log in" class="btn"/>
			</p>
		</form>
	</div>
	<img src="/images/OrangeBoxBottom.gif" width="197" height="12" />
</div>
""" % {'Name': strUsername,
                                  'URL': strURL,
                                  'URL2': strURL2}
