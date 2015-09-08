import string

def GoToProcessing(objRequest, objHere):
    # www.MentorCoaches.com/GoTo/Book005a
    # Extract name part
    # If built up like "Book<no><letter>" then
    #   Get the review with that number
    #   Get the Amazon details
    #       .co.uk for Book...a
    #       .com for Book...b
    #   Create the forwarding URL
    # Otherwise
    #   Forward to home page
    # And get the browser to forward to the URL
    strQueryString = string.lower(objRequest['QUERY_STRING'])
    # Remove anything up to www.MentorCoaches.com/GoTo:

    strHome = "http://www.MentorCoaches.com/"

    if len(strQueryString) <> 8:
        return(strHome)
    if strQueryString[:4] == "book":
        strBookNumber = strQueryString[4:7]
        strLinkType = strQueryString[7:]
        if not strLinkType in ['a', 'b']:
            return(strHome)
        for strChar in strBookNumber:
            if not strChar in '0123456789':
                return(strHome)
        intBookNumber = string.atoi(strBookNumber)
        objBook = objHere.SearchOne(objHere, 'Books', 'id', intBookNumber)
        if objBook:
            return objBook.GetAmazonLink()
        for objBookReview in objBookReviews.objectValues():
            if objBookReview.ReviewNumber == intBookNumber:
                return AmazonLink(objBookReview, strLinkType)
    return strHome
        
