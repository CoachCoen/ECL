# encoding: utf-8

from formatter import AbstractFormatter , NullWriter
from htmllib import HTMLParser
import htmllib

from libDatabase import GetDataFolder
from libDatabase import GetDOD
from libString import AddToLines
from libDatabase import SearchMany
from libDatabase import SearchOne
from libDatabase import ReindexOne
from E3Members import GetCurrentMember
from libGeneral import GetParameter
from libDatabase import GetWebsiteRoot
from LocalPaths import cnLocalPathExtensions
from libConstants import cnEuroAmount
from libConstants import cnUSAmount
from libConstants import cnUKAmount
from libConstants import cnEuroBankCosts

class myWriter ( NullWriter ):
    def send_flowing_data( self, str ):
        self . _bodyText . append ( str )
    def __init__ ( self ):
        NullWriter.__init__ ( self )
        self . _bodyText = [ ]
    def _get_bodyText ( self ):
        return " ".join ( self . _bodyText)
    bodyText = property ( _get_bodyText, None, None, "plain text from body" )

class MyHTMLParser(HTMLParser):
    def __init__(self, funFormatter, objHere):
        self.objH1 = None
        self.objH2 = None
        self.objH3 = None
        self.dodHelp = GetDOD(objHere, 'E3Help')

        HTMLParser.__init__(self, funFormatter)

    def CheckExpand(self, strDetails):
        blnCanExpand = False
        strId = ""
        if strDetails[0] == '+':
            blnCanExpand = True
            strDetails = strDetails[1:]
        if strDetails[0] == '{':
            strId = strDetails[1:]
            strId = strId[:strId.find('}')]
            strDetails = strDetails[strDetails.find('}')+1:]
        return (strDetails, blnCanExpand, strId)

    def SplitH1(self, strDetails):
        (strDetails, blnCanExpand, strId) = self.CheckExpand(strDetails)
        lstDetails = strDetails.split(':')
        strTitle = ':'.join(lstDetails[1:])
        strDetails = lstDetails[0]
        if '(' in strDetails:
            (strType, strCategories) = strDetails.split('(')
        else:
            strType = strDetails
            strCategories = 'toprule'
        strCategories = strCategories.replace(')', '')
        return (strType.strip(), strCategories.strip(), strTitle.strip(), blnCanExpand, strId)

    def NewH1(self):
        self.objH2 = None
        self.objH3 = None
        self.objH1 = self.dodHelp.NewObject()
        strDetails = self.save_end()
        (self.objH1.Type, self.objH1.Categories, self.objH1.title, self.objH1.CanExpand, strId) = self.SplitH1(strDetails)
        if strId:
            self.objH1.HelpId = strId
        else:
            self.objH1.HelpId = self.objH1.id

    def NewH2(self):
        if not self.objH1: 
            print "H1 missing: %s" % self.save_end()
            return
        self.objH3 = None
        self.objH2 = self.dodHelp.NewObject(self.objH1)
        (strTitle, blnCanExpand, strId) = self.CheckExpand(self.save_end())
        self.objH2.title = strTitle
        self.objH2.CanExpand = blnCanExpand
        if strId:
            self.objH2.HelpId = strId
        else:
            self.objH2.HelpId = self.objH2.id

    def NewH3(self):
        if not self.objH1:
            print "H1 missing: %s" % self.save_end()
            return
        if not self.objH2:
            print "H2 missing: %s" % self.save_end()
            return
        (strTitle, blnCanExpand, strId) = self.CheckExpand(self.save_end())
        self.objH3 = self.dodHelp.NewObject(self.objH2)
        self.objH3.title = strTitle
        self.objH3.CanExpand = blnCanExpand
        if strId:
            self.objH3.HelpId = strId
        else:
            self.objH3.HelpId = self.objH3.id

    def start_h1(self, attrs):
        self.save_bgn()

    def end_h1(self):
        self.NewH1()

    def start_h2(self, attrs):
        self.save_bgn()

    def end_h2(self):
        self.NewH2()

    def start_h3(self, attrs):
        self.save_bgn()

    def end_h3(self):
        self.NewH3()

    def start_p(self, attrs):
        self.save_bgn()

    def end_p(self):
        if self.objH3:
            self.objH3.Lines = AddToLines(self.objH3.Lines, self.save_end())
        elif self.objH2:
            self.objH2.Lines = AddToLines(self.objH2.Lines, self.save_end())
        elif self.objH1:
            self.objH1.Lines = AddToLines(self.objH1.Lines, self.save_end())
        else:
            print "Missing H1, trying to add line: %s" % self.save_end()

def ReadHelp(objHere):
    fileHelp = open(cnLocalPathExtensions + 'FAQs etc.htm')
    strHelp = fileHelp.read()
    strHelp = strHelp.replace('~UKAmount', str(cnUKAmount))
    strHelp = strHelp.replace('~USAmount', str(cnUSAmount))
    strHelp = strHelp.replace('~EuroAmount', str(cnEuroAmount))
    strHelp = strHelp.replace('~EuroPlusCosts', str(cnEuroAmount + cnEuroBankCosts))
    mywriter = myWriter ( )
    abstractformatter = AbstractFormatter ( mywriter )
    objParser = MyHTMLParser(abstractformatter, objHere)
    objParser.feed(strHelp)
    objParser.close()

def MergeHelp(lstOne, lstTwo):
    if not lstOne:
        return lstTwo

    if not lstTwo:
        return lstOne

    lstResult = lstOne
    for objHelp in lstTwo:
        if not objHelp in lstResult:
            lstResult.append(objHelp)
    return lstResult

def GetCategoryForPage(objHere):
    dictPages = {'Membership': 'membership',
                'About': '', 
                'Help': '', 
                'MyECL': 'settings', 
                'Archive': 'archive'}
    strURL = objHere.absolute_url()
    lstURL = strURL.split('/')
    for strFolder in lstURL:
        if strFolder in dictPages.keys():
            return dictPages[strFolder]
    return ""

def ShowHelpSideBar(objHere):
    strBox = """
			<div id="LeftBox"><img 
				src="/images/BoxTop.gif" width="197" height="12" border="0"/><div 
				id="LeftBoxContents">
            <h2>Help</h2>
                    %s</div><img 
				src="/images/BoxBottom.gif" width="197" height="12" 
			/></div>"""
    strCategory = GetCategoryForPage(objHere)
    if strCategory:
        lstPageHelp = SearchMany(objHere, 'E3Help', 'Categories', strCategory)
    else:
        lstPageHelp = None
    if GetCurrentMember(objHere):
        lstLoginHelp = None
    else:
        lstLoginHelp = SearchMany(objHere, 'E3Help', 'Categories', 'ifloggedout')
    lstHelp = MergeHelp(lstLoginHelp, lstPageHelp)
    if lstHelp:
        strResult = "<ul>\n"
        for objHelp in lstHelp:
            strResult = strResult + objHelp.ShortHelpLine()
        strResult = strResult + "</ul>\n"
        strResult = strBox % strResult
    else:
        strResult = ""
    return strResult

def LinesToHTML(lstLines):
    strResult = ""
    blnUL = False
    blnOL = False
    for strLine in lstLines:
        strPre = ""
        strPost = ""
        if len(strLine.strip()) <= 3:
            strLine = "&nbsp;"
        if strLine[0] == '*':
            if not blnUL:
                strPre = "<ul>\n"
                blnUL = True
        elif blnUL:
            strPost += "</ul>\n"
            blnUL = False
        if strLine[0] == '0':
            if not blnOL:
                strPre = "<ol>\n"
                blnOL = True
        elif blnOL:
            strPost += "</ol>\n"
            blnOL = False
        if strLine[0] in '0*':
            strLine = strLine[1:].strip()
        if blnOL or blnUL:
            strLine = "<li>%s</li>\n" % strLine
        else:
            strLine = "<p>%s</p>\n" % strLine
        strResult += strPre + strPost + strLine
    if blnUL:
        strResult += "</ul>\n"
    if blnOL:
        strResult += "</ol>\n"
    return strResult

def RemoveLinks(strHTML):
    # Remove all <a .... > and all </a>
    strHTML = strHTML.replace('</a>', '')
    while '<a' in strHTML:
        intPosition = strHTML.find('<a')
        strLeft = strHTML[:intPosition]
        strRight = strHTML[intPosition:]
        strRight = strRight[strRight.find('>') + 1:]
        strHTML = strLeft + strRight
    return strHTML

def ShowHelpContents(objHere, objRequest, blnLinks = True):
    strId = GetParameter(objRequest, 'Id')
    if not strId:
        return MainHelpPage(objHere)
    objHelp = SearchOne(objHere, 'E3Help', 'HelpId', strId)
    if not objHelp:
        return MainHelpPage(objHere)
    strBody = LinesToHTML(objHelp.Lines)
    if not blnLinks:
        strBody = RemoveLinks(strBody)
    return "<h2>%s</h2>" % objHelp.title + strBody

def OneHelpTopic(objHere, strKey):
    lstHelp = SearchMany(objHere, 'E3Help', 'Categories', strKey)
    strHowTo = ""
    strFAQ = ""
    for objHelp in lstHelp:
        if objHelp.Type == 'Howto':
            strHowTo = strHowTo + """<li><a href="/Help/ShowOne?Id=%s">How to: %s</a></li>\n""" % (objHelp.HelpId, objHelp.title)
        elif objHelp.Type == 'FAQ':
            strFAQ = strFAQ + """<li><a href="/Help/ShowOne?Id=%s">FAQ: %s</a></li>\n""" % (objHelp.HelpId, objHelp.title)
        else:
            print "Unknown help type: %s for %s" % (objHelp.Type, objHelp.id)
    return strHowTo + strFAQ

def GetHelpCategories():
    return (('membership', 'List membership'),
                ('email addresses', 'Your email address(es)'),
                ('adverts', 'Advertising'),
                ('background', 'Miscellaneous'),
                ('joining', 'Joining the Euro Coach List'),
                ('payment', 'Paying for your membership'),
                ('receiving', 'Receiving list messages'),
                ('sending', 'Sending list messages'),
                ('settings', 'Changing your membership settings'),
                ('digest', 'List digest'),
                ('archive', 'List messages archive'),
                ('rules', 'List rules'), 
                ('website', 'Using the Euro Coach List website'),
                ('profile', 'Your profile, products, services, events and organisations'))

def MainHelpPage(objHere):
    # 3 parts:
#    1. Link to rules page
#    2. For each category
#        - "How to ..." ..Category title - dropdown list
#        - "Frequently asked questions for ... " Category title - dropdown list
    strTemplate = """<h2>List rules</h2>
<p>See the <a href="/Rules">List Rules Page</a> for full information on the rules</p>
%s
<h2>More help</h2>
<p>If you can't find what you are looking for feel free to <a href="/ContactDetails">contact the list owner</a></p>"""

    strHelpList = ""
    lstCategories = GetHelpCategories()
    for (strKey, strTitle) in lstCategories:
        strHelpList += "<h2>%s</h2>\n" % strTitle
        strHelpList += "<ul>%s</ul>\n" % OneHelpTopic(objHere, strKey)
    return strTemplate % strHelpList

def OneHelpDropdown(objHere, strKey, strTitle):
    strResult = """<select name="HelpFor%s">\n""" % strKey
    strResult = strResult + """<option selected>%s</option>\n""" % strTitle
    lstHelp = SearchMany(objHere, 'E3Help', 'Categories', strKey)
    for objHelp in lstHelp:
        strResult = strResult + """<option value="%s">%s</option>\n""" % (objHelp.HelpId, objHelp.title)
    strResult = strResult + "</select>\n"
    return strResult

def HelpDropdownLists(objHere):
    strResult = ""
    lstCategories = GetHelpCategories()
    for (strKey, strTitle) in lstCategories:
        strResult = strResult + OneHelpDropdown(objHere, strKey, strTitle)
    return strResult

def ShowHelpPage(objHere, objRequest):
    strResult = ShowHelpContents(objHere, objRequest)
    strResult = unicode(strResult, 'utf-8', 'replace')
#   strResult = strResult + "<h2>Other help pages</h2>\n" + HelpDropdownLists(objHere)
    return strResult

def ShowOneRule(objRule, intLevel, blnExpanded):
    if blnExpanded:
        strResult = "<h%s>%s</h%s>\n" % (intLevel + 1, objRule.title, intLevel + 1)
    else:
        if intLevel == 3:
            strResult = "<li>%s</li>\n" % objRule.title
        elif intLevel == 2:
            strResult = "<p><b>%s</b></p>\n" % objRule.title
        else:
            strResult = "<p>%s</p>\n" % objRule.title

    if objRule.CanExpand and intLevel > 1:
        strResult = strResult + """<p>(<a href="/Rules?Id=%s">More details</a>)</p>""" % objRule.HelpId
        BuildRules(objRule, objRule.HelpId)
    if blnExpanded:
        strResult = strResult + LinesToHTML(objRule.Lines)
    return strResult

def ShowRuleAndBelow(objStart, intLevel, blnExpanded):
    strResult = ShowOneRule(objStart, intLevel, blnExpanded)
    strSubResult = ""
    for objSubRule in objStart.objectValues('E3Help'):
        strSubResult = strSubResult + ShowRuleAndBelow(objSubRule, intLevel + 1, blnExpanded)
    if intLevel == 2 and strSubResult:
        strSubResult = "<ul>%s</ul>\n" % strSubResult
    strResult = strResult + strSubResult
    return strResult

def StoreRules(objHere, strId, strHTML):
    objRules = GetWebsiteRoot(objHere, 'E3').Rules
    try:
        objRules.manage_addProperty(strId, strHTML, 'string')
    except:
        objRules.manage_changeProperties({strId: strHTML})

def BuildRules(objHere, strId = ""):
    if not strId:
        objTop = SearchOne(objHere, 'E3Help', 'Categories', 'toprule')
        if not objTop:
            print "toprule not found"
        strHTML = ShowRuleAndBelow(objTop, 1, False)
        strId = "MainPage"
    else:
        objTop = SearchOne(objHere, 'E3Help', 'HelpId', strId)
        strHTML = ShowRuleAndBelow(objTop, 1, True)
    StoreRules(objHere, strId, strHTML)
    return "Done"

def ShowRules(objHere, objRequest):
    strId = GetParameter(objRequest, 'Id')
    if not strId:
        strId = 'MainPage'
    try:
        return GetWebsiteRoot(objHere, 'E3').Rules.unrestrictedTraverse(strId)
    except:
        return GetWebsiteRoot(objHere, 'E3').Rules.MainPage

def ImportHelpFile(objHere):
    objHelpFolder = GetDataFolder(objHere, 'E3Help')
    for strId in objHelpFolder.objectIds('E3Help'):
        objHelpFolder.manage_delObjects(strId)
    ReadHelp(objHere)
    ReindexOne(objHere, "E3Help")
    BuildRules(objHere)
