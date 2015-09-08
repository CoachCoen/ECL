# encoding: utf-8
"""Various string functions"""

from email.Header import decode_header
from StringValidator import StringValidator
import datetime
from libDate import MonthName
import re
import string

def encode_for_xml(unicode_data, encoding='ascii'):
    """
    Encode unicode_data for use as XML or HTML, with characters outside
    of the encoding converted to XML numeric character references.
    """
    try:
        return unicode_data.encode(encoding, 'xmlcharrefreplace')
    except ValueError:
        # ValueError is raised if there are unencodable chars in the
        # data and the 'xmlcharrefreplace' error handler is not found.
        # Pre-2.3 Python doesn't support the 'xmlcharrefreplace' error
        # handler, so we'll emulate it.
        return _xmlcharref_encode(unicode_data, encoding)

def _xmlcharref_encode(unicode_data, encoding):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    chars = []
    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            chars.append(char.encode(encoding, 'strict'))
        except UnicodeError:
            chars.append('&#%i;' % ord(char))
    return ''.join(chars)

def GetFirstWord(strString):
    reFirstWord = re.compile(r"\w+")
    lstResult = reFirstWord.findall(strString)
    if lstResult:
        return lstResult[0]
    return ""

def RemoveFirst(strString, strRE):
    reFirstWord = re.compile(strRE)
    return reFirstWord.sub("", strString, 1)

def ExtractParameters(strString):
    # Parameters are between brackets, [], () or {}
    # Must have exactly 1 opening bracket and 1 closing bracket
    # Opening bracket must come before the closing bracket
    # Opening bracket must be of the same type as the closing bracket
    strBrackets = ""
    for intI in range(0, len(strString)):
        strChar = strString[intI]
        if strChar in "[]{}()":
            strBrackets += strChar

#    print strBrackets
    if strBrackets == "[" or strBrackets == "]":
        return ("", strString, "Missing square bracket")
    if not strBrackets in ["()", "[]", "{}"]:
        return ("", strString, "")

    intStart = strString.find(strBrackets[0])
    intEnd = strString.find(strBrackets[1])

    strParameters = strString[intStart + 1: intEnd ].strip()
    strPlain = strString[:intStart].strip() + " " + strString[intEnd + 1:].strip()
    strPlain = strPlain.strip()
    return (strParameters, strPlain, "")

def AllValidDates(intYear, intMonth, intDay, lstToDo):
    dtmNow = datetime.date.today()
    lstResult = []
    if lstToDo:
        intToTry = int(lstToDo[0])
        lstRemainder = lstToDo[1:]
        if not intYear:
            lstResult += AllValidDates(intToTry + 2000, intMonth, intDay, lstRemainder)
        if not intMonth:
            lstResult += AllValidDates(intYear, intToTry, intDay, lstRemainder)
        if not intDay:
            lstResult += AllValidDates(intYear, intMonth, intToTry, lstRemainder)
    else:
        try:
#            print "Trying year, month, day"
            dtmDate = datetime.date(year = intYear, month = intMonth, day = intDay)
            if dtmDate >= dtmNow:
                lstResult.append(dtmDate)
#            else:
#                print "Date before today"
        except:
            pass
#    print "AllValidDates, year, month, day, to do: ", intYear, intMonth, intDay, lstToDo
#    print "Result: ", lstResult
    return lstResult

def ParseDate(strPart):
    """    If valid date and more info, assume all additional info is the location
If valid date and no more info, not correct, bounce back
If no valid date, but some extra info, not correct, bounce back
Is a valid date?
Split into parts, using /, space, -
If not 3 parts, incorrect
If one part a string (instead of just numbers)
If month name, make this the month
Otherwise, incorrect
For any parts not processed
If >= current year, assume it is the year
Else, if > 12 and <= 31, assume it is the day
If both year and day already determined, and <= 12, assume it is the month
If both year and month already determined and <= 31, assume it is the day
If < current day, assume it is the month
If either year, month or day missing, incorrect
If resulting date in the past, incorrect
If resulting date not a valid date (e.g. 31 Feb), incorrect"""
    strPart = strPart.strip()
    if not strPart:
        return None

    lstParts = None
    for strSeparator in " -/":
        lstSplit = strPart.split(strSeparator)
        if len(lstSplit) in [2, 3]:
            lstParts = lstSplit

    if not lstParts:
        return None

    intMonth = 0
    intDay = 0
    intYear = 0

    if len(lstSplit) == 2:
        dtmNow = datetime.date.today()
        intYear = dtmNow.year

    lstToDo = []

#    print "Parse date, parts: ", lstParts

    for strPart in lstParts:
        blnCorrect = False
        if strPart.isdigit():
            intPart = int(strPart)
            if intPart > 31:
                if intPart in range(2008, 2030):
                    if not intYear:
                        intYear = intPart
                        blnCorrect = True
            elif intPart in range(13, 32):
                # Assuming that this program won't be used after 2020
                if not intDay and (intYear or intPart > 20):
                    intDay = intPart
                    blnCorrect = True
            elif intPart in range(1, 32):
                if not intDay and intYear and intMonth :
                    intDay = intPart
                    blnCorrect = True
                elif not intMonth and intYear and intDay:
                    intMonth = intPart
                    blnCorrect = True
                elif not intYear and intMonth and intDay:
                    intYear = intPart + 2000
                    blnCorrect = True
        elif not intMonth:
            strPart = strPart.lower()
            for intI in range(1, 13):
                if strPart == MonthName(intI)[:len(strPart)].lower():
                    intMonth = intI
                    blnCorrect = True
        if not blnCorrect:
            lstToDo.append(strPart)

#    print "Parse date, to do: ", lstToDo
#    print "Year, month, day: ", intYear, intMonth, intDay

    # At this point we may still have one or two parts left to do
    # These should all be numbers between 1 and 12
    for strPart in lstToDo:
        if not strPart.isdigit():
            return None
        intPart = int(strPart)
        if not intPart in range(1, 32):
            return None

    # Now try out all possible combinations
    # Keeping all/any dates which are valid dates and not in the past
    lstDates = AllValidDates(intYear, intMonth, intDay, lstToDo)

    if len(lstDates) == 1:
        return lstDates[0]
    return None

def ParseParameters(strParameters):
    strErrorMessage = ""

    lstParts = strParameters.split(",")
    if len(lstParts) <= 1:
        lstParts = strParameters.split()

    # Process and remove 'hold'
    lstRemainder = []
    blnHold = False
    for strPart in lstParts:
        strPart = strPart.strip()
#        print "Checking parameter: |%s|" % strPart
        if strPart.lower() == "hold":
            blnHold = True
        else:
            lstRemainder.append(strPart)

    # Process and remove date
    lstParts = lstRemainder
    lstRemainder = []
    dtmDate = None
    for strPart in lstParts:
        dtmPartDate = ParseDate(strPart)
        if dtmPartDate:
            if dtmDate:
#                return (error: two dates found)
                pass
            dtmDate = dtmPartDate
        else:
            lstRemainder.append(strPart)

    # Re-join remainder into the location
    strLocation = ", ".join(lstRemainder).strip()

    # If date found, then must have location
    if dtmDate and not strLocation:
        strErrorMessage = "Missing location. Events must have a date and a location"

    # If location found, then must have date
    elif strLocation and not dtmDate:
        strErrorMessage = "Missing or incorrect date. Events must have a date and a location"

#    print "ParseParameters, hold: ", blnHold

    return (strErrorMessage, dtmDate, strLocation, blnHold)

def TestForAdvert(strSubjectHeader):
    # Possible outcomes:
    # 1. Header does not start with adv/ert/isment, so not an advert
    # 2. Header starts with adv/ert/isment, no parameters
    # 3. Header starts with adv/ert/isment, parameters incorrect
    # 4. Header starts with adv/ert/isment, parameters correct

    # Set defaults
#    print "Testing for advert: %s" % strSubjectHeader
    strNewHeader = strSubjectHeader
    dtmDate = None
    strLocation = ""
    blnHold = False
    blnIsAdvert = False
    strErrorMessage = ""

    # Extract the first word
    strFirstWord = GetFirstWord(strSubjectHeader)
#    print "First word: |%s|" % strFirstWord

    # If first word adv/ert/isement, is an advert
    if strFirstWord.lower() in ['adv', 'advert', 'advertisement']:
        blnIsAdvert = True

        # Remove the first word
#        print strNewHeader.find(strFirstWord)
        strNewHeader = strNewHeader[(strNewHeader.find(strFirstWord) + len(strFirstWord)):]
        strNewHeader = strNewHeader.strip()

        # Remove any separator at the start, i.e. [:;~->}])?]
        strNewHeader = RemoveFirst(strNewHeader, r"[:;~\-\]>}.]").strip()

        # Any parameters?
        (strParameters, strPlain, strErrorMessage) = ExtractParameters(strNewHeader)
 #       print "Parameters: |%s|" % strParameters
 #       print "Remainder: |%s|" % strPlain

        if strParameters and not strErrorMessage:
            (strErrorMessage, dtmDate, strLocation, blnHold) = ParseParameters(strParameters)
            strNewHeader = strPlain

    return (blnIsAdvert, strErrorMessage, strNewHeader, dtmDate, strLocation, blnHold)

def TruncateLine(strString, intMaxLength):
    lstWords = strString.split(" ")
    strResult = lstWords[0]
    for strWord in lstWords[1:]:
        if len(strResult + strWord) >= intMaxLength:
            return strResult
        strResult += " " + strWord
    return strResult

def GetMessage(objHere, strMessageId):
    return objHere.unrestrictedTraverse("/Data/E3/StandardMessages/%s" % strMessageId).Body

def ListToText(lstOriginalList):
    if not lstOriginalList:
        return ""
    lstList = []
    for varItem in lstOriginalList:
        if varItem and str(varItem) <> "[]":
            lstList.append(varItem)
    if len(lstList) == 1:
        return ToUnicode(lstList[0])
    elif len(lstList) > 1:
        return ToUnicode(" and ".join((", ".join(lstList[:-1]), lstList[len(lstList)-1])))
    return ""

def ValidEmailAddress(strEmailAddress):
    objValidator = StringValidator(strEmailAddress)
    if objValidator.isEmail():
        return True
    return False

def ToUnicode(strString, blnDetectCharSet = False, strCharSet = ""):
    if not strString:
#        print "ToUnicode, empty string"
        return strString

#    print "ToUnicode, from |%s|" % strString[:20]

    if isinstance(strString, unicode):
#        print "Already unicode, no further encoding done"
        return strString

    if strCharSet:
#        print "Encoding: |%s|" % strCharSet
        try:
            strResult = unicode(strString, strCharSet, "replace")
#            print "ToUnicode, from |%s| using %s" % (strString[:20], strCharSet)
#            print "Result: |%s|" % strResult[:20]
            return strResult
            return strResult
        except:
            pass
#            print "Encoding failed"
        
    if blnDetectCharSet and "charset=" in strString:
        strRemainder = strString[strString.find("charset=") + 8:]
        strCharSet = ""
        intI = 0
        while intI <= len(strRemainder) and strRemainder[intI] in string.ascii_letters + "-" + string.digits:
            strCharSet += strRemainder[intI]
            intI += 1

#        print "Encoding: |%s|" % strCharSet
        try:
            strResult = unicode(strString, strCharSet, "replace")
#            print "ToUnicode, from |%s| using %s" % (strString[:20], strCharSet)
#            print "Result: |%s|" % strResult[:20]
            return strResult
        except:
#            print "Encoding failed"
            pass

#    print "Default encoding: utf-8"

    try:
        strResult = unicode(strString, "utf-8", 'replace')
#        print "ToUnicode, from |%s| using %s" % (strString[:20], "utf-8")
#        print "Result: |%s|" % strResult[:20]
        return strResult
    except:
#        print "Encoding failed, no encoding done"
        return strString
    return strString

def TrimBlank(strString):
    lstString = strString.split("\n")
    lstResult = []
    for strLine in lstString:
        strLine = strLine.strip()
        if strLine:
            lstResult.append(strLine)
    return "\n".join(lstResult)

def AddToLines(tplLines, strLine):
    """Add a line to a tuple of lines
        Typically used for an object property of type 'lines'"""
    lstResult = tplLines + (strLine, )
    return lstResult

def RemoveStrings(strString, lstToRemove):
    """Remove all occurrences of all strings in lstToRemove"""
    strResult = strString
    for strToRemove in lstToRemove:
        strResult = string.replace(strResult, strToRemove, "")
    return strResult

def GetChunk(strString, strStart, strEnd):
    """Returns the string between strStart and strEnd"""
    strResult = strString
    intPosition = strResult.find(strStart)
    if intPosition > 0:
        strResult = strResult[intPosition:]
    else:
        return ""
    intPosition = strResult.find(strEnd)
    if intPosition > 0:
        strResult = strResult[:intPosition + len(strEnd)]
    else:
        return ""
    return strResult

def FirstFind(strSearchIn, lstSearchFor):
    """Looks for the word within lstSearchFor which occurs first within strSearchIn
        returns the location within strSearchIn and the length of the word found"""
    intPosition = len(strSearchIn)
    intLen = 0
    for strSearchFor in lstSearchFor:
        intP = strSearchIn.find(strSearchFor)
        if intP < intPosition:
            intPosition = intP
            intLen = len(strSearchFor)
    return (intPosition, intLen)

def GetChunk2(strString, lstStart, lstEnd):
    """Looks for the first word from lstStart, and from there the first word from lstEnd
        returns the string between them"""
    strResult = strString
    (intPosition, intDummy) = FirstFind(strResult, lstStart)
    if intPosition > 0:
        strResult = strResult[intPosition:]
    else:
        return ""
    (intPosition, intLen) = FirstFind(strResult, lstEnd)
    if intPosition > 0:
        strResult = strResult[:intPosition + intLen]
    else:
        return ""
    return strResult

def StripLeadingSpaces(strString):
    """Removes spaces at the start of each line within strString"""
    cnCrLf = "\n"
    strResult = ""
    for strLine in strString.split(cnCrLf):
        while len(strLine) > 0 and strLine[0] == " ":
            strLine = strLine[1:]
        strResult = strResult + strLine + cnCrLf
    return strResult

def ExtractAddress(strRawAddress):
# Format: "Jilly Shaul" <lifematters@btinternet.com>
    """Extracts email address from, e.g. "Jilly Shaul" <lifematters@btinternet.com>"""
    strName = GetChunk(strRawAddress, '"', '"')
    strEmailAddress = GetChunk(strRawAddress, '<', '>')
    if not strEmailAddress:
        strResult = strRawAddress
        for strChar in '<>"':
            strResult = strResult.replace(strChar, ' ')
        lstResult = strResult.split()
        for strResult in lstResult:
            if "@" in strResult and "." in strResult:
                return (strResult.lower(), "")
    strEmailAddress = strEmailAddress.replace('<', '')
    strEmailAddress = strEmailAddress.replace('>', '')
    return (strEmailAddress.lower(), strName)
# So now I need to store those, and generate a unique key for all of them, so that later people can come and claim them

# Within MyECL there will be a "Claim email address" box, which takes the unique key. After entering the key the system will find all messages for that email address and give it the user's UserId'

def ClearSubjectHeader(strSubject):
    """Returns mailSubject without list name"""
    strResult = strSubject
    for strPrefix in 'UKCoach', 'ec-l', 'eurocoach-list':
        strResult = strResult.replace('[%s]' % strPrefix, '')
    (strResult, strEncoding) = decode_header(strResult)[0]
    return strResult

def RemoveHTMLCodes(strText):
    strResult = ""
    while "<" in strText:
        intPosition = strText.find("<")
        strResult += strText[:intPosition]
        strText = strText[intPosition:]
        strText = strText[strText.find(">") + 1:]
    strResult += strText
    return strResult

def PrepareMessageText(strMessageText, intMaxWords = 500, blnInsertBRs = True):
    try:
        strMessageText = unicode(strMessageText, 'ascii', 'ignore')
    except:
        pass
    lstLines = strMessageText.split('\n')
    strResult = ""
    intWords = 0
    for strLine in lstLines:
        if intWords > intMaxWords:
            return (True, strResult)
        strLine = strLine.strip()
        if strLine:
            if strResult and blnInsertBRs:
                strResult += "<br>\n"
            else:
                strResult += " "
            strResult += strLine
            intWords = intWords + len(strResult.split())

    return (False, strResult)

