from libDatabase import Catalogue
from libDatabase import SearchMany
from libDatabase import GetDOD
from libString import ToUnicode
import datetime
from DateTime import DateTime
from HtmlSanitizer import Cleaner
import re
from libString import encode_for_xml

def CheckRequiredFields(dictData, lstFields):
    dictResult = {}
    for strField in lstFields:
        if not dictData[strField]:
            dictResult[strField] = ("MissingField", "Missing field")
    return dictResult

def ReportErrors(dictErrors, dictTranslation = None):
    if not dictErrors:
        return ""

    if len(dictErrors.keys()) > 1:
        strIntro = "The following errors were found:"
    else:
        strIntro = "The following error was found:"

    lstErrors = []
    lstMissingFields = []
    for strKey in dictErrors.keys():
        (strCode, strMessage) = dictErrors[strKey]
        if strCode == "MissingField":
            if dictTranslation and dictTranslation.has_key(strKey):
                lstMissingFields.append(dictTranslation[strKey])
            else:
                lstMissingFields.append(strKey)
        else:
            lstErrors.append(strMessage)

    intMissingFields = len(lstMissingFields)
    if intMissingFields:
        if intMissingFields == 1:
            strMessage = "Missing field: "
        elif intMissingFields > 1:
            strMessage = "Missing fields: "
        if dictTranslation:
            strMessage += ", ".join(lstMissingFields)
        lstErrors.append(strMessage)

    strResult = """<div class="GeneralError">
"""
    if len(lstErrors) == 1:
        strResult += "<p>%s %s</p>\n" % (strIntro, lstErrors[0])
    else:
        strResult += """
<p>%s</p>
<ul>
""" % strIntro
        for strError in lstErrors:
            strResult += "<li>%s</li>\n" % strError
        strResult += "</ul>\n"

    strResult +="""
<p>Please correct the form and re-submit</p>
</div>
"""
    return strResult

def BuildLabel(strLabel):
    if strLabel:
        return """<label>%s</label>
""" % strLabel
    return ""

def AddOneOption(objHere, strFieldName, strOption):
    # Check whether it exists yet. If so, quit
    lstOptions = SearchMany(objHere, "E3MultiOption", "FieldName", strFieldName)
    if lstOptions:
        for objOption in lstOptions:
            if objOption.Option.lower() == strOption.lower():
                return
    dodOption = GetDOD(objHere, "E3MultiOption")
    objMultiOption = dodOption.NewObject()
    objMultiOption.title = strFieldName + ": " + strOption
    objMultiOption.FieldName = strFieldName
    objMultiOption.Option = strOption
    Catalogue(objMultiOption)

## MultiOptionBlock
def LoadCheckBoxes(objHere, strGroup, dictData, blnFieldsActive):
#    print "LoadCheckBoxes ", dictData
    lstOptions = []
    objMultiOptions = SearchMany(objHere, "E3MultiOption", "FieldName", strGroup)
    for objMultiOption in objMultiOptions:
        lstOptions.append(objMultiOption.Option)
    lstOptions.sort()
    strResult = ""
    intI = 0
    lstGroupData = []
    if dictData.has_key(strGroup) and dictData[strGroup]:
        lstGroupData = dictData[strGroup]
        if type(lstGroupData) in (type(""), (type(u""))):
            lstGroupData = [lstGroupData, ""]
#        print "Group %s, data: %s" % (strGroup, lstGroupData)
    for strOption in lstOptions:
        strOption = ToUnicode(strOption)
        strChecked = ""
        for strItem in lstGroupData:
            if ToUnicode(strItem) == strOption:
                strChecked = " checked "
        intI += 1
        strId = "MultiOption-%s-%s" % (strGroup, intI)
        strResult += """<div class="LocationOption"><input type="checkbox" value="%(Text)s" name="%(FieldName)s" id="%(Id)s" %(Checked)s %(Disable)s> <label for="%(Id)s">%(Text)s</label></div>&nbsp; \n""" % {'FieldName': strGroup,
        'Id': strId,
        'Checked': strChecked,
        'Disable': ShowDisabled(blnFieldsActive),
        'Text': strOption}
    return strResult

def MultiOptionBlock(strLegend, strExplanation, strGroup, strFieldName = ""):
    dictResult = {}
    dictResult["Type"] = "MultiOptionBlock"
    dictResult["Legend"] = strLegend
    dictResult["Explanation"] = strExplanation
    dictResult["Group"] = strGroup
    if strFieldName:
        dictResult["FieldName"] = strFieldName
    else:
        dictResult["FieldName"] = strGroup
    return dictResult

def BuildMultiOptionBlock(objHere, dictParagraph, dictData, blnFieldsActive):
    strCheckBoxes = LoadCheckBoxes(objHere, dictParagraph["Group"], dictData, blnFieldsActive)
    strResult = """<p><b>%s</b></p>
    <p>%s</p>
    <p>Add a new category <input type="input" class="txt" name="New-%s"></br>
Note: to add more than one category, enter one, click on Save and then enter another</p>
""" % (dictParagraph["Explanation"], strCheckBoxes, dictParagraph["Group"])

    strLegend = dictParagraph["Legend"]
    if strLegend:
        strResult = """<fieldset>
        <legend><b>%s</b></legend>
        %s
    </fieldset>""" % (strLegend, strResult)
    return strResult

## Fieldset
def Fieldset(strLegend, lstConditions, *lstParagraphs):
    dictResult = {}
    dictResult["Type"] = "Fieldset"
    dictResult['Legend'] = strLegend
    if lstConditions:
        dictResult['Conditions'] = lstConditions
    dictResult['Paragraphs'] = lstParagraphs
    return dictResult

## Tabset
def Tabset(*lstTabs):
    dictResult = {}
    dictResult["Type"] = "Tabset"
    dictResult["Tabs"] = lstTabs
    return dictResult

def BuildTabset(objHere, dictTabset, dictData, blnFieldsActive, dictErrors):
    strTabs = u""
    for dictOneTab in dictTabset["Tabs"]:
        strTabs += ToUnicode(BuildOneTab(objHere, dictOneTab, dictData, blnFieldsActive, dictErrors))
    strResult = """<div class="tabber" id="tab1">
    %s
    </div>""" % strTabs
    return strResult

## OneTab
def OneTab(strTitle, *lstElements):
    dictResult = {}
    dictResult["Type"] = "OneTab"
    dictResult["Title"] = strTitle
    dictResult["Elements"] = lstElements
    return dictResult

def BuildOneTab(objHere, dictOneTab, dictData, blnFieldsActive, dictErrors):
    strTitle = dictOneTab["Title"]
    strElements = u""
    for dictElement in dictOneTab["Elements"]:
        if dictElement["Type"] == "MultiOptionBlock":
            strElements += ToUnicode(BuildMultiOptionBlock(objHere, dictElement, dictData, blnFieldsActive))
        elif dictElement["Type"] == "Fieldset":
            strElements += OneFieldset(objHere, dictElement, dictData, blnFieldsActive, dictErrors)
        else:
            strElements += ToUnicode(OneParagraph(dictElement["Elements"], dictData, blnFieldsActive, dictErrors))
    strResult = """<div class="tabbertab" title="%s">

<h2>%s</h2>
%s
</div>""" % (strTitle, strTitle, strElements)
    return strResult

## Paragraph
def Paragraph(*lstElements):
    dictResult = {}
    dictResult['Elements'] = lstElements
    dictResult['Type'] = 'Paragraph'
    return dictResult

## FileControl
def FileControl(strLabel, strName):
    dictResult = {}
    dictResult['Type'] = 'FileControl'
    dictResult['Name'] = strName
    dictResult['Label'] = strLabel
    return dictResult

def BuildFileControl(dictElement, dictData, blnFieldsActive):
    strName = dictElement['Name']
    strLabel = BuildLabel(dictElement['Label'])
    return """%s<input type="file" name="%s" %s>\n""" % (strLabel, strName, ShowDisabled(blnFieldsActive))

## Date control
def DateControl(strLabel, strName, blnComingDates = True, strComments = ""):
    # 3 drop down boxes - date, month, year
    dictResult = {}
    dictResult['Type'] = 'DateControl'
    dictResult['Name'] = strName
    dictResult['Label'] = strLabel
    dictResult['ComingDates'] = blnComingDates
    dictResult['Comments'] = strComments
    return dictResult

def BuildDateControl(dictElement, dictData, blnFieldsActive):
    strName = dictElement['Name']
    blnComingDates = dictElement['ComingDates']
    dtmValue = datetime.date.today()
    dtmToday = dtmValue
    intDate = dtmValue.day
    intMonth = dtmValue.month
    intYear = dtmValue.year
    if dictData:
        if strName + "-month" in dictData.keys():
            intDate = int(dictData[strName + "-date"])
            intMonth = int(dictData[strName + "-month"])
            intYear = int(dictData[strName + "-year"])

#            dtmValue = dictData[strName]
#            try:
#                dtmValue = datetime.date(strValue)
#            except:
#                pass

    lstDates = range(1, 32)
    lstMonths = range(1, 13)
    if blnComingDates:
        intFirstYear = dtmToday.year
    else:
        intFirstYear = 1990
    if intFirstYear > intYear:
        intFirstYear = intYear
    lstYears = range(intFirstYear, dtmToday.year + 10)

    strDateOptions = BuildOptionsForSelectControl(lstDates, intDate, False)
    strMonthOptions = BuildOptionsForSelectControl(lstMonths, intMonth, False)
    strYearOptions = BuildOptionsForSelectControl(lstYears, intYear, False)

    strLabel = BuildLabel(dictElement['Label'])

    strResult = """%(Label)s
<select name="%(Name)s-date" %(Disabled)s>
    %(DateOptions)s
</select> /
<select name="%(Name)s-month" %(Disabled)s>
    %(MonthOptions)s
</select> /
<select name="%(Name)s-year" %(Disabled)s>
    %(YearOptions)s
</select>
%(Comments)s
""" % {'Label': strLabel,
    'Name': strName,
    'Disabled': ShowDisabled(blnFieldsActive),
    'DateOptions': strDateOptions,
    'MonthOptions': strMonthOptions,
    'YearOptions': strYearOptions,
    'Comments': dictElement['Comments']}
    return strResult

## Checkbox
def CheckboxControl(strLabel, strName, strComments = None):
    dictResult = {}
    dictResult['Type'] = 'CheckboxControl'
    dictResult['Name'] = strName
    dictResult['Label'] = strLabel
    if strComments:
        dictResult['Comments'] = strComments
    return dictResult

def BuildCheckboxControl(dictElement, dictData, blnFieldsActive):
    strName = dictElement['Name']
    blnValue = False
    if dictData:
        if strName in dictData.keys():
            blnValue = dictData[strName]

    if blnValue:
        strChecked = " checked"
    else:
        strChecked = ""

    strLabel = BuildLabel(dictElement['Label'])
    return """%s<input type="checkbox" name="%s" %s %s>\n""" % (strLabel, strName, strChecked, ShowDisabled(blnFieldsActive))

## Text control
def TextControl(strLabel, strName, lstConditions = None, strComments = None):
    dictResult = {}
    dictResult['Type'] = 'TextControl'
    dictResult['Label'] = strLabel
    dictResult['Name'] = strName
    if lstConditions:
        dictResult['Conditions'] = lstConditions
    if strComments:
        dictResult['Comments'] = strComments
    return dictResult

def BuildTextControl(dictElement, dictData, blnFieldsActive):
    strLabel = BuildLabel(dictElement['Label'])
    strName = dictElement['Name']
    if dictElement.has_key('Comments'):
        strComments = dictElement['Comments']
    else:
        strComments = ""
    strValue = ""
    if dictData:
        if strName in dictData.keys():
            strValue = dictData[strName]

    return """%s<input type="text" class="profile" name="%s" value="%s" %s>%s\n""" % (strLabel, strName, strValue, ShowDisabled(blnFieldsActive), strComments)

## Password control
def PasswordControl(strLabel, strName, lstConditions = None, strComments = None):
    dictResult = {}
    dictResult['Type'] = 'PasswordControl'
    dictResult['Label'] = strLabel
    dictResult['Name'] = strName
    if lstConditions:
        dictResult['Conditions'] = lstConditions
    if strComments:
        dictResult['Comments'] = strComments
    return dictResult

def BuildPasswordControl(dictElement, dictData, blnFieldsActive):
    strLabel = BuildLabel(dictElement['Label'])
    strName = dictElement['Name']
    if dictElement.has_key('Comments'):
        strComments = dictElement['Comments']
    else:
        strComments = ""
    strValue = ""
    if dictData:
        if strName in dictData.keys():
            strValue = dictData[strName]

    strResult = """%s<input type="password" class="profile" name="%s" value="%s" %s>%s\n""" % (strLabel, strName, strValue, ShowDisabled(blnFieldsActive), strComments)

    return strResult

## Hidden control
def HiddenControl(strName):
    dictResult = {}
    dictResult['Type'] = 'HiddenControl'
    dictResult['Name'] = strName
    return dictResult

def BuildHiddenControl(dictElement, dictData):
    strName = dictElement['Name']
    strValue = ""
    if dictData:
        if strName in dictData.keys():
            strValue = dictData[strName]
    return """<input type="hidden" name="%s" value="%s">""" % (strName, strValue)

## Select
def SelectControl(strLabel, strName, lstOptions, strComments = None, blnWithId = False):
    dictResult = {}
    dictResult['Type'] = 'SelectControl'
    dictResult['Label'] = strLabel
    dictResult['Name'] = strName
    dictResult['Options'] = lstOptions
    dictResult['WithId'] = blnWithId
    if strComments:
        dictResult['Comments'] = strComments
    return dictResult

def SimpleBuildSelectControl(strName, lstOptions, strOptionSelected):
    strOptions = ""
    for strOptionValue in lstOptions:
        if strOptionValue == strOptionSelected:
            strSelected = " selected"
        else:
            strSelected = ""
        strOptions += "<option %s>%s</option>\n" % (strSelected, strOptionValue)
    return """<select name="%s">
%s
</select>""" % (strName, strOptions)

def BuildOptionsForSelectControl(lstOptions, strValue, blnWithId):
    strResult = ""

    if blnWithId:
        for (strOptionValue, strId) in lstOptions:
            if strOptionValue == strValue or strId == strValue:
                strSelected = " selected"
            else:
                strSelected = ""
            strResult += """<option value="%s" %s>%s</option>\n""" % (strId, strSelected, ToUnicode(strOptionValue))
    else:
        for strOptionValue in lstOptions:
            if strOptionValue == strValue:
                strSelected = " selected"
            else:
                strSelected = ""
            strResult += "<option %s>%s</option>\n" % (strSelected, strOptionValue)
    return strResult

def BuildSelectControl(dictElement, dictData, blnFieldsActive):
    strLabel = BuildLabel(dictElement['Label'])
    strName = dictElement['Name']
    if dictElement.has_key("Comments"):
        strComments = dictElement["Comments"]
    else:
        strComments = ""
    strValue = ""
    if dictData:
        if strName in dictData.keys():
            strValue = dictData[strName]

    if len(dictElement['Options']) == 1:
        if dictElement['WithId']:
            strToShow = dictElement['Options'][0][0]
            strValue = dictElement['Options'][0][1]
        else:
            strToShow = dictElement['Options'][0]
            strValue = strToShow
        if strComments:
            strComments = "(%s) " % strComments
        return """%s<input type="hidden" name="%s" value="%s">%s %s""" % (strLabel, strName, strValue, strToShow, strComments)

    strOptions = BuildOptionsForSelectControl(dictElement['Options'], strValue, dictElement['WithId'])

    return """%s<select name="%s" %s>
%s
</select> %s""" % (strLabel, strName, ShowDisabled(blnFieldsActive), strOptions, strComments)

## RichTextArea
def RichTextArea(strLabel, strName, strComments = None, strWidth = "", strHeight = ""):
    dictResult = {}
    dictResult['Type'] = 'RichTextArea'
    dictResult['Label'] = strLabel
    dictResult['Name'] = strName
    if strComments:
        dictResult['Comments'] = strComments
    if strWidth:
        dictResult["Width"] = strWidth
    if strHeight:
        dictResult["Height"] = strHeight
    return dictResult

def BuildRichTextAreaControl(dictElement, dictData, blnFieldsActive):
#    strLabel = BuildLabel(dictElement['Label'])
    strLabel = dictElement["Label"]
    strName = dictElement['Name']
    strValue = ""
    if dictData:
        if strName in dictData.keys():
            strValue = dictData[strName]
    if dictElement.has_key('Comments'):
        strComments = dictElement['Comments']
        strComments = """<br><label>&nbsp;</label>%s""" % strComments
    else:
        strComments = ""

    if dictElement.has_key("Width"):
        strWidth = "rte1.width=%s;" % dictElement["Width"]
    else:
        strWidth = ""

    if dictElement.has_key("Height"):
        strHeight = "rte1.height=%s;" % dictElement["Height"]
    else:
        strHeight = ""

    if not blnFieldsActive:
        strReadOnly = "rte1.readOnly = true"
    else:
        strReadOnly = ""

#    print "0:", strValue
    strValue = ToUnicode(strValue)

#    print "1:", strValue
    strValue = strValue.replace("\n", " \n")
    strValue = re.escape(strValue)
#    print "2:", strValue
#    strValue = strValue.encode('ascii', 'xmlcharrefreplace')
#    print "3:", strValue
    strValue = encode_for_xml(strValue)
#    print "4:", strValue

    return """
<p>%s</p>
<script language="JavaScript" type="text/javascript">

//Usage: initRTE(imagesPath, includesPath, cssFile, genXHTML, encHTML)
initRTE("/images/RTE/", "/js/", "", false);
//-->
</script>
<noscript><p><b>Javascript must be enabled to use this form.</b></p></noscript>

<script language="JavaScript" type="text/javascript">
<!--
//build new richTextEditor
var rte1 = new richTextEditor('%s');
// rte1.html = unescape('');
rte1.html = '%s';

//enable all commands for demo
rte1.cmdFormatBlock = true;
rte1.cmdFontName = true;
rte1.cmdFontSize = true;
rte1.cmdIncreaseFontSize = true;
rte1.cmdDecreaseFontSize = true;

rte1.cmdBold = true;
rte1.cmdItalic = true;
rte1.cmdUnderline = true;
rte1.cmdStrikethrough = true;
rte1.cmdSuperscript = true;
rte1.cmdSubscript = true;

rte1.cmdJustifyLeft = true;
rte1.cmdJustifyCenter = true;
rte1.cmdJustifyRight = true;
rte1.cmdJustifyFull = true;

rte1.cmdInsertHorizontalRule = true;
rte1.cmdInsertOrderedList = true;
rte1.cmdInsertUnorderedList = true;

rte1.cmdOutdent = true;
rte1.cmdIndent = true;
rte1.cmdForeColor = true;
rte1.cmdHiliteColor = true;
rte1.cmdInsertLink = true;
rte1.cmdInsertImage = true;
rte1.cmdInsertSpecialChars = true;
rte1.cmdInsertTable = true;
rte1.cmdSpellcheck = true;

rte1.cmdCut = true;
rte1.cmdCopy = true;
rte1.cmdPaste = true;
rte1.cmdUndo = true;
rte1.cmdRedo = true;
rte1.cmdRemoveFormat = true;
rte1.cmdUnlink = true;

rte1.toggleSrc = false;
%s
%s
%s
rte1.build();
//-->
</script>

%s""" % (strLabel, strName, strValue, strWidth, strHeight, strReadOnly, strComments)
#re.escape(strValue)

## TextArea
def TextArea(strLabel, strName, strComments = None):
    dictResult = {}
    dictResult['Type'] = 'TextArea'
    dictResult['Label'] = strLabel
    dictResult['Name'] = strName
    if strComments:
        dictResult['Comments'] = strComments
    return dictResult

def BuildTextAreaControl(dictElement, dictData, blnFieldsActive):
    strLabel = BuildLabel(dictElement['Label'])
    strName = dictElement['Name']
    strValue = ""
    if dictData:
        if strName in dictData.keys():
            strValue = dictData[strName]
    if dictElement.has_key('Comments'):
        strComments = dictElement['Comments']
        strComments = """<br><label>&nbsp;</label>%s""" % strComments
    else:
        strComments = ""
    return """%s<textarea class="medium" name="%s" %s>%s</textarea> %s""" % (strLabel, strName, ShowDisabled(blnFieldsActive), strValue, strComments)


## RadioButtons
def RadioButtonControl(strLabel, strName, lstOptions, blnLongDescriptions = False, blnUnorderedList = False):
    dictResult = {}
    dictResult['Type'] = 'RadioButtonControl'
    dictResult['Label'] = strLabel
    dictResult['Name'] = strName
    dictResult['Options'] = lstOptions
    dictResult['LongDescriptions'] = blnLongDescriptions
    dictResult["UnorderedList"] = blnUnorderedList
    return dictResult

def ShowDisabled(blnFieldActive):
    if blnFieldActive:
        return ""
    return " disabled "

def BuildRadioButtonControl(dictElement, dictData, blnFieldsActive):
    blnLongDescriptions = dictElement["LongDescriptions"]
    blnUnorderedList = dictElement["UnorderedList"]

    if blnUnorderedList:
        strResult = """<p>%s</p>
<ul class="RadioOptions">
""" % dictElement["Label"]
    else:
        strResult = BuildLabel(dictElement['Label'])

    strName = dictElement['Name']
    strValue = ""
    if dictData:
        if strName in dictData.keys():
            strValue = dictData[strName]


    for varOptionValue in dictElement['Options']:
        if blnLongDescriptions:
            (strOptionValue, strDescription) = varOptionValue
        else:
            strOptionValue = varOptionValue
            strDescription = varOptionValue
        strOptionValue = strOptionValue.replace(" ", "")
        if strValue == strOptionValue:
            strChecked = " checked"
        else:
            strChecked = ""
        strId = strName + strOptionValue

        strOptionHTML = """<label for="%s"><input type="radio"
name="%s" id="%s" value="%s" %s %s/> %s</label>""" % (strId, strName, strId, strOptionValue, strChecked, ShowDisabled(blnFieldsActive), strDescription)
        if blnUnorderedList:
            strResult += "<li>%s</li>\n" % strOptionHTML
        else:
            strResult += "%s\n" % strOptionHTML

    if blnUnorderedList:
        strResult += "</ul>\n"
    return strResult

## Submit control
def SubmitControl(strLabel, strSubAction = None):
    dictResult = {}
    dictResult['Type'] = 'SubmitControl'
    dictResult['Label'] = strLabel
    dictResult['SubAction'] = strSubAction
    return dictResult

def BuildSubmitControl(dictElement):
    return """<input type="submit" name ="SubmitButton" value="%s" class="btn">\n""" % dictElement['Label']

## Pure text
def PureText(strText, lstConditions = None):
    dictResult = {}
    dictResult['Type'] = 'PureText'
    dictResult['Text'] = strText
    if lstConditions:
        dictResult['Conditions'] = lstConditions
    return dictResult

def BuildPureText(dictElement, dictData):
    if dictElement.has_key('Conditions'):
        if not ConditionSatisfied(dictElement['Conditions'], dictData):
            return ""
    return dictElement['Text']

def CheckElementErrors(dictElement, dictErrors):
    if not dictElement.has_key('Name'):
        return ""
    strName = dictElement['Name']
    if dictErrors.has_key(strName):
        return dictErrors[strName][0]
    return ""

def OneElement(dictElement, dictData, blnFieldsActive, dictErrors):
#    print dictElement
#    print
    strType = dictElement['Type']

    if strType == 'PureText':
        strResult = BuildPureText(dictElement, dictData)
    elif strType == 'TextControl':
        strResult = BuildTextControl(dictElement, dictData, blnFieldsActive)
    elif strType == "PasswordControl":
        strResult = BuildPasswordControl(dictElement, dictData, blnFieldsActive)
    elif strType == 'HiddenControl':
        strResult = BuildHiddenControl(dictElement, dictData)
    elif strType == 'SelectControl':
        strResult = BuildSelectControl(dictElement, dictData, blnFieldsActive)
    elif strType == 'TextArea':
        strResult = BuildTextAreaControl(dictElement, dictData, blnFieldsActive)
    elif strType == 'RichTextArea':
        strResult = BuildRichTextAreaControl(dictElement, dictData, blnFieldsActive)
    elif strType == 'SubmitControl':
        strResult = BuildSubmitControl(dictElement)
    elif strType == 'CheckboxControl':
        strResult = BuildCheckboxControl(dictElement, dictData, blnFieldsActive)
    elif strType == 'RadioButtonControl':
        strResult = BuildRadioButtonControl(dictElement, dictData, blnFieldsActive)
    elif strType == 'DateControl':
        strResult = BuildDateControl(dictElement, dictData, blnFieldsActive)
    elif strType == 'FileControl':
        strResult = BuildFileControl(dictElement, dictData, blnFieldsActive)
    else:
        print "Unknown element type: %s" % strType
        strResult = ""

    strError = CheckElementErrors(dictElement, dictErrors)

    return (strResult, strError)

def OneParagraph(varElements, dictData, blnFieldsActive, dictErrors):
    strError = False
    if isinstance(varElements, dict):
        (strContents, strError) = OneElement(varElements, dictData, blnFieldsActive, dictErrors)
#        print "Paragraph = Element"
    else:
        strContents = ""
        for dictElement in varElements:
            (strElement, strElementError) = OneElement(dictElement, dictData, blnFieldsActive, dictErrors)
            strContents += strElement
            if strElementError:
                strError = strElementError
    if strError:
        return """
<p class="%s">
    %s
</p>""" % (strError, strContents)
    else:
        return """
<p>
    %s
</p>""" % strContents

def ConditionSatisfied(lstConditions, dictData):
#    print lstConditions
    for (strField, strComparator, varValue) in lstConditions:
        if dictData.has_key(strField):
            varData = dictData[strField]
        elif strField == 'HasMissingFields':
            varData = ''
        elif strField == 'CanAdvertise':
            varData = False
        else:
            print "Unknown field: %s" % strField
            varData = ""
#        print strField, strComparator, varValue, varData
        if strComparator == '=':
            if varData != varValue:
                return False
        if strComparator == '!=':
            if varData == varValue:
                return False
    return True

def OneFieldset(objHere, dictFieldset, dictData, blnFieldsActive, dictErrors):
    if dictFieldset.has_key('Conditions'):
        if not ConditionSatisfied(dictFieldset['Conditions'], dictData):
            return ""

    strContents = u""
    for dictParagraph in dictFieldset['Paragraphs']:
        if dictParagraph["Type"] == "Paragraph":
            if dictParagraph.has_key('Elements'):
                strContents += ToUnicode(OneParagraph(dictParagraph['Elements'], dictData, blnFieldsActive, dictErrors))
            else:
                strContents += OneParagraph(dictParagraph, dictData, blnFieldsActive, dictErrors)
        elif dictParagraph["Type"] == "MultiOptionBlock":
            strContents += BuildMultiOptionBlock(objHere, dictParagraph, dictData, blnFieldsActive, dictErrors)
        elif dictParagraph["Type"] == "Tabset":
            strContents += BuildTabset(objHere, dictParagraph, dictData, blnFieldsActive, dictErrors)
        else:
            print "Unknown paragraph type: %s" % dictParagraph["Type"]
    return """
<fieldset>
    <legend>%s</legend>
    %s
</fieldset>""" % (dictFieldset['Legend'], strContents)

def CreateForm(objHere, lstFormStructure, dictData = None, strURL = "", dictHiddenFields = None, blnIncludeClosingTag = True, blnFieldsActive = True, dictErrors = {}, strPreceedWith = ""):
    if not strURL:
        strURL = objHere.REQUEST.ACTUAL_URL
    strElements = ""
    for dictFieldset in lstFormStructure:
        strElements += OneFieldset(objHere, dictFieldset, dictData, blnFieldsActive, dictErrors)

    strOnSubmit = ""
    strExtraCode = ""
    if "initRTE" in strElements:
        strOnSubmit = """onsubmit="return submitForm();" """
        strExtraCode = """
<!-- html2xhtml.js written by Jacob Lee <letsgolee@lycos.co.kr> //-->
<script language="JavaScript" type="text/javascript" src="/js/html2xhtml.js"></script>
<script language="JavaScript" type="text/javascript" src="/js/richtext_compressed.js"></script>

<script language="JavaScript" type="text/javascript">
<!--
function submitForm() {
    //make sure hidden and iframe values are in sync for all rtes before submitting form
    updateRTEs();

    return true;
}
//-->
</script>
"""

    strHiddenFields = ""
    if dictHiddenFields:
        for strFieldName in dictHiddenFields.keys():
            strHiddenFields += """<input type="hidden" name="%s" value="%s">\n""" % (strFieldName, dictHiddenFields[strFieldName])

    strResult = """
<script type="text/javascript" src="/js/tabber.js"></script>

<form method="post" action="%s" %s>
%s
%s
%s
%s
""" % (strURL, strOnSubmit, strExtraCode, strPreceedWith, strElements, strHiddenFields)
    if blnIncludeClosingTag:
        strResult += "</form>\n"
    return strResult

def LoadDataFromObject(objObject, lstFields):
    dictResult = {}
    for strField in lstFields:
        if strField == "id":
            dictResult[strField] = objObject.id
        else:
            if objObject.hasProperty(strField):
                strType = objObject.getPropertyType(strField)
                if strType == "date":
                    dtmZopeDate = objObject.getProperty(strField)
                    dictResult[strField + "-year"] = dtmZopeDate.year()
                    dictResult[strField + "-month"] = dtmZopeDate.month()
                    dictResult[strField + "-date"] = dtmZopeDate.day()
                else:
                    dictResult[strField] = objObject.getProperty(strField)
#            if strField == "myTitle":
#                print "LoadDataFromObject, myTitle: %s" % dictResult[strField]
    return dictResult

def GetDataFromForm(objHere, objForm, lstFields):
#    print objForm.keys()
#    print objForm["rte1"]
    dictResult = {}
#    print objForm
    for strField in lstFields:
        if objForm.has_key(strField):
#            if strField == "myTitle":
#                print "myTitle, on the form: %s" % objForm["myTitle"]
            dictResult[strField] = objForm[strField]
        else:
            dictResult[strField] = None
    for strField in objForm.keys():
        if strField[:4] == "New-":
            strValue = objForm[strField]
            if strValue:
                strGroup = strField[4:]
                lstOldValue = dictResult[strGroup]
                if lstOldValue:
                    if isinstance(lstOldValue, str):
                        lstOldValue = [lstOldValue, ]
                    lstNewValue = lstOldValue + [strValue, ]
                else:
                    lstNewValue = [strValue, ]
                dictResult[strGroup] = lstNewValue
                AddOneOption(objHere, strGroup, strValue)
#                print "New multi option: %s in group %s" % (strValue, strGroup)
#                print "Existing value of %s: %s" % (strGroup, dictResult[strGroup])
#                if not strValue in dictResult[strGroup]:
#                    dictResult[strGroup].append(strValue)
#                print "New value of %s: %s" % (strGroup, dictResult[strGroup])
#    print "Data from form: ", dictResult
    return dictResult

def LinesToUnicode(lstLines):
    lstResult = []
    for strLine in lstLines:
        lstResult.append(ToUnicode(strLine))
    return lstResult

def SafeDate(intYear, intMonth, intDate):
    dtmDate = None
    while not dtmDate:
        try:
            dtmDate =  DateTime(intYear, intMonth, intDate)
        except:
            intDate -= 1
    return dtmDate

def CleanHTML(strString):
    if not strString:
        return strString
    if "<" in strString:
        objCleaner = Cleaner()
        return objCleaner(strString)
    return strString

def UpdateObjectFromData(objObject, dictData, lstFields):
#    print dictData
    for strName in lstFields:
        if strName != "id" and objObject.hasProperty(strName):
            if strName in dictData.keys() or strName + "-year" in dictData.keys():
                strType = objObject.getPropertyType(strName)
                if strType == 'string':
                    objObject.manage_changeProperties({strName:CleanHTML(dictData[strName])})
                elif strType == 'ustring':
#                    print "%s set to %s" % (strName, dictData[strName])
#                    print "Or in unicode, set to %s" % unicode(dictData[strName], 'utf-8', 'replace')
#                    objObject.manage_changeProperties({strName:objCleaner(unicode(dictData[strName], 'utf-8', 'replace'))})
                    objObject.manage_changeProperties({strName:unicode(dictData[strName], 'utf-8', 'replace')})
#                    objObject.manage_changeProperties({strName:objCleaner(dictData[strName].decode('ascii', 'replace'))})
                elif strType == 'date':
                    intYear = int(dictData[strName + "-year"])
                    intMonth = int(dictData[strName + "-month"])
                    intDate = int(dictData[strName + "-date"])
                    dtmDate = SafeDate(intYear, intMonth, intDate)

#                    print "New value for %s: %s" % (strName, dtmDate)

                    objObject.manage_changeProperties({strName:dtmDate})
                elif strType == 'boolean':
                    if dictData[strName]:
                        objObject.manage_changeProperties({strName:True})
                    else:
                        objObject.manage_changeProperties({strName:False})
                elif strType == 'text':
                    objObject.manage_changeProperties({strName:dictData[strName]})
                elif strType == 'utext':
#                    print strName
                    strValue = dictData[strName]
                    if not strValue:
                        strValue = ""
                    strValue = unicode(strValue, 'utf-8', 'replace')
                    objObject.manage_changeProperties({strName:strValue})
                elif strType == 'lines':
                    lstLines = dictData[strName]
                    if isinstance(lstLines, str):
                        lstLines = [lstLines, ]
                    objObject.manage_changeProperties({strName: lstLines})
                elif strType == 'ulines':
                    lstLines = dictData[strName]
                    if isinstance(lstLines, str):
                        lstLines = [lstLines, ]
                    if lstLines:
                        lstLines = LinesToUnicode(lstLines)
                    objObject.manage_changeProperties({strName: lstLines})

            elif strType == 'boolean':
                objObject.manage_changeProperties({strName:False})
    Catalogue(objObject)

def MergeData(dictData, dictOtherData):
    for strKey in dictOtherData.keys():
        if not dictData.has_key(strKey):
            dictData[strKey] = dictOtherData[strKey]
    return dictData

def FormProcessing(objData, lstLoadFields, lstForm, blnUpdate, fnValidate = None, lstSaveFields = None, lstFormFields = None, dictOtherData = {}):

    strMessage = ""

    if not lstSaveFields:
        lstSaveFields = lstLoadFields

    if not lstFormFields:
        lstFormFields = lstLoadFields

    # If update button pressed:
    if blnUpdate:

        # Load data from form
        dictData = GetDataFromForm(objData, objData.REQUEST.form, lstFormFields)
        dictData = MergeData(dictData, dictOtherData)

        if fnValidate:
            # Validate
            dictErrors = fnValidate(dictData, objData)
            strMessage = ReportErrors(dictErrors)
        else:
            dictErrors = {}

        # If valid:
        if not dictErrors:

            # Save
            UpdateObjectFromData(objData, dictData, lstSaveFields)
            strMessage = """<p class="InfoMessage">Changes saved</p>\n"""

    # Else:
    else:
        dictData = LoadDataFromObject(objData, lstLoadFields)
        dictData = MergeData(dictData, dictOtherData)
        dictErrors = {}
        # Load data from object

    # Return form
    strResult = strMessage + CreateForm(objData, lstForm, dictData, ".", None, True, True, dictErrors)
    return strResult

def SaveNewFromForm(objHere, strObjectType, lstSaveFields, lstForm, fnValidate = None, lstFormFields = None, dictOtherData = {}, objSaveIn = None, strIdField = None):

    strMessage = ""

    if not lstFormFields:
        lstFormFields = lstSaveFields

    dictData = GetDataFromForm(objHere, objHere.REQUEST.form, lstFormFields)
    dictData = MergeData(dictData, dictOtherData)

    if fnValidate:
        # Validate
        dictErrors = fnValidate(dictData, objHere)
        strMessage = ReportErrors(dictErrors)
        objObject = None
    else:
        dictErrors = {}

        # If valid:
    if not dictErrors:
        dodObject = GetDOD(objHere, strObjectType)
        objObject = dodObject.NewObject(objSaveIn)
            # Save
        UpdateObjectFromData(objObject, dictData, lstSaveFields)
        strMessage = """<p class="InfoMessage">Changes saved</p>\n"""

        if strIdField:
            dictData[strIdField] = objObject.id

    strForm = strMessage + ToUnicode(CreateForm(objHere, lstForm, dictData, ".", None, True, True, dictErrors))

    return (objObject, strForm)

