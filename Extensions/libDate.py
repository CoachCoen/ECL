# encoding: utf-8

"""Various date-related functions"""

import datetime

def MonthName(intMonth):
    """Returns the full name of the month"""
    return {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 
                    7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}[intMonth]

def ShortMonthName(intMonth):
    """Returns the short name of the month"""
    return {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                    7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}[intMonth]

def GetLastDate(intYear, intMonth):
    """Returns the last date of intYear/intMonth - e.g. 28, 29, 30 or 31"""
    for intDate in range(31, 27, -1):
        try:
            dtmDummy = datetime.date(year = intYear, month = intMonth, day = intDate)
            return intDate
        except:
            pass
    return 0

def MonthToNumber(strMonth):
    """Takes a short month name, e.g. Jan, and returns the number of the month (1-12)"""
    lstMonthList = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    for intI in range(0, 12):
        if lstMonthList[intI].lower() == strMonth.lower():
            return intI + 1
    return 0
    
def GuessAtYMD(strItem, strYMDFound):
    try:
        intItem = int(strItem)
    except:
        intItem = 0
    if intItem:
        if intItem > 31:
            if 'Y' in strYMDFound:
                return ('', 0)
            else:
                return ('Y', intItem)
        elif intItem > 12:
            if 'D' in strYMDFound:
                return ('', 0)
            else:
                return ('D', intItem)
        else:
            if 'Y' in strYMDFound and 'D' in strYMDFound and not 'M' in strYMDFound:
                return ('M', intItem)
            elif 'Y' in strYMDFound and 'M' in strYMDFound and not 'D' in strYMDFound:
                return ('D', intItem)
    else:
        intMonth = MonthToNumber(strItem)
        if intMonth:
            if 'M' in strYMDFound:
                return ('', 0)
            else:
                return ('M', intMonth)
    return ('', 0)

def SplitDate(strDate):
    for strSeparator in [' ', '/', '-']:
        lstResult = strDate.split(strSeparator)
        if len(lstResult) == 3:
            return lstResult
    return None

def DateFromString(strDate):
    lstDate = SplitDate(strDate)
    if not lstDate:
        return

    strYMDFound = ''
    for intJ in range(0, 3):
        for intI in range(0, 3):
            (strYMD, intValue) = GuessAtYMD(lstDate[intI], strYMDFound)
            if strYMD == 'Y':
                intYear = intValue
                strYMDFound += 'Y'
            elif strYMD == 'M':
                intMonth = intValue
                strYMDFound += 'M'
            elif strYMD == 'D':
                intDay = intValue
                strYMDFound += 'D'

    if len(strYMDFound) == 3:
        return datetime.date(year = intYear, month = intMonth, day = intDay)

    return None


