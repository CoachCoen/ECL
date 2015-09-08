from libDatabase import GetDataFolder

def ListRecentArticles(objHere):
    objArticles = GetDataFolder(objHere, 'MCIArticle')
    lstArticles = []
    for objArticle in objArticles.objectValues('MCIArticle'):
        lstArticles
    return ""
