# encoding: utf-8

"""Functions for taking HTML code apart"""

import sgmllib
from libString import StripLeadingSpaces
from libString import ToUnicode

def GetAttribute(strPage, strTag):
    """Extracts the value of <strTag> from <strPage> webpage """
    strChunk = GeneralBookFunctions.GetChunk(strPage, "<" + strTag, "/%s>" % strTag)

    if not strChunk:
        return ""
    intPosition = strChunk.find('>')
    strChunk = strChunk[intPosition + 1:]
    intPosition =strChunk.find('<')
    strChunk = strChunk[:intPosition]
    strChunk = string.strip(strChunk)
    print "Attribute %s = %s" % (strTag, strChunk)
    return strChunk

def GetMultipleAttributes(strPage, strTag):
    """Extracts all values for <strTag> from <strPage> webpage"""
    strRemain = strPage
    strStart = "<" + strTag
    strEnd = "/%s>" % strTag
    lstResult = []
    intPosition = strRemain.find(strStart)
    while intPosition >= 0:
        strRemain = strRemain[intPosition:]
        intPosition = strRemain.find(">")
        strRemain = strRemain[intPosition + 1:]
        intPosition = strRemain.find(strEnd)
        if intPosition >= 0:
            strChunk = strRemain[:intPosition]
            strRemain = strRemain[intPosition:]
            intPosition = strChunk.find("<")
            strChunk = strChunk[:intPosition]
            strChunk = string.strip(strChunk)
            if strChunk:
                lstResult.append(strChunk)
            intPosition = strRemain.find(strStart)
    print "Attribute %s = %s" % (strTag, lstResult)
    return lstResult

class Stripper(sgmllib.SGMLParser):
    def __init__(self):
	   sgmllib.SGMLParser.__init__(self)

    def strip(self, some_html, blnInsertBrs = False):
        self.InsertBrs = blnInsertBrs
        self.theString = ""
        self.feed(some_html)
        self.close()
        return StripLeadingSpaces(self.theString)

    def do_br(self, attributes):
        if self.theString:
            self.theString += "\n"

    def end_p(self, attributes):
        if self.theString:
            self.theString += "\n"

    def handle_data(self, data):
        self.theString = (self.theString + " " + data).strip()

def HTMLToText(strText, blnInsertBrs = False):
    """Uses smgllib and class Stripper to turn HTML into plain text"""
    objStripper = Stripper()
    try:
        strResult =  objStripper.strip(strText, blnInsertBrs)
    except:
        strText = ToUnicode(strText)
        strResult = objStripper.strip(strText, blnInsertBrs)
    return strResult

