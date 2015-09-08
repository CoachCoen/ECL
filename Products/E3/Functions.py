import datetime
from DateTime import DateTime

def ShowFullDetails(objObject):
    strResult = ""
    for strName in objObject.__dict__:
        strResult = strResult + "%s: %s\n" % (strName, eval('objObject.%s' % strName))
    return strResult

def GenericAddForm(strType, dictFields):
    strFields = ''
    for strFieldName in dictFields.keys():
        strFields = strFields + """<b>%s:</b> <input type="text" name="%s" /><br />""" % (strFieldName, dictFields[strFieldName])

    strResult = """<html>
    <head>
        <title>New %s</title>
    </head>
    <body>
        <form action="addProduct">
            <b>ID:</b> <input type="text" name="id" /><br />
            %s
            <input type="submit">
        </form>
    </body>
</html>""" % (strType, strFields)
    return strResult

def ToZopeDateTime(objHere, dtmDate):
    return DateTime(dtmDate.strftime("%A %d %B %Y"))

def ToZopeDatePlusTime(objHere, dtmDate):
    return DateTime(dtmDate.strftime("%A %d %B %Y %H:%M"))

def FromZopeDateTime(dtmDateTime):
    return datetime.date(year = dtmDateTime.year(), month = dtmDateTime.month(), day = dtmDateTime.day())

def FromZopeDatePlusTime(dtmDateTime):
    return datetime.datetime(year = dtmDateTime.year(), month = dtmDateTime.month(), day = dtmDateTime.day(), hour = dtmDateTime.hour(), minute = dtmDateTime.minute())
