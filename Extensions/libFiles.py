# encoding: utf-8

"""Functions for reading files"""

import urllib

def ReadFileLines(strName):
    """Reads lines from <strName> and return them as a list"""
    lstFile = open(strName)
    lstResult = lstFile.readlines()
    lstFile.close()
    return lstResult

def ReadFile(strName):
    """Reads whole file and returns content as a single string"""
    lstFile = open(strName)
    strResult = lstFile.read()
    lstFile.close()
    return strResult

def LoadPage(strURL):
    """Loads webpage and returns contents as a single string"""
    try:
        objRead = urllib.urlopen(strURL)
        strPage = objRead.read() + ""
    except:
        return ""
    return strPage

