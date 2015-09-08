# encoding: utf-8

from libDatabase import GetDataFolder

"""Various functions"""

def AffiliateSalesTracking(strProductCode, strMemberId, intCost):
    return """
<script id="pap_x2s6df8d" src="http://www.eurocoachlist.com/affiliate/scripts/salejs.php" type="text/javascript">
</script>
<script type="text/javascript">
var sale = PostAffTracker.createSale();
sale.setTotalCost('%s');
sale.setProductID('%s');
sale.setData1('%s');
PostAffTracker.register();
</script>""" % (intCost, strProductCode, strMemberId)

def CombineLists(lst1, lst2):
    if lst1 and len(lst1):
        if lst2 and len(lst2):
            return lst1 + lst2
        return lst1
    return lst2

def GetNextCartId(objHere):
    objData = GetDataFolder(objHere, 'E3Data')
    intNextCartId = objData.LatestCartId + 1
    objData.LatestCartId = intNextCartId
    return intNextCartId

def ExtractFromQueryString(strQueryString, strName):
    lstItems = strQueryString.split('&')
    for strItem in lstItems:
        lstParts = strItem.split('=')
        if len(lstParts) == 2:
            if lstParts[0].lower() == strName.lower():
                return lstParts[1]

def GetParameter(objRequest, strName):
    """If <strName> is either in the query string or in the calling form, return it's contents
    else return blank"""
    try:
        if objRequest.has_key(strName):
            return objRequest[strName].strip()
    except:
        pass

    try:
        if not objRequest.has_property('REQUEST'):
            return ""
    except:
        pass

    try:
        objRequest = objRequest.REQUEST
    except:
        pass

    strQueryString = objRequest['QUERY_STRING']
    strResult = ExtractFromQueryString(strQueryString, strName)
    if strResult:
        return strResult

    if objRequest.has_key(strName):
        return objRequest[strName].strip()

    if objRequest.has_key('form'):
        if objRequest.form.has_key(strName):
            return objRequest.form[strName].strip()
    return ""
