# encoding: utf-8

from libDatabase import GetDataFolder
from libConstants import cnListNameECL
from libDatabase import SearchOne

""" Keep track of:
- Direct list members
- Text digest members
- MIME digest members
- No mail members

(these 4 lists combined are all the posting addresses)

Update when
- Too many bounces (how does this currently work in MailBoxer?)
- ListMembership changes
- Member expires
- Payment made
- Member joins
- Import
- Free period added
- Email address confirmed

So, something like:
objMember.SetMembershipType(Full/None)
objMember.SetListMembership(EmailAddress, MembershipType)
objEmailAddress.ConfirmAddress()

and, just to be sure:
RegenerateMailingLists (done after import?)
VerifyMailingLists (daily process, to make sure that all works fine)
"""

def GetList(objHere, strListName):
    return GetDataFolder(objHere, 'E3List').unrestrictedTraverse(strListName)

def GetMailingLists(objHere):
    lstDirectListMembers = []
    lstTextDigestMembers = []
    lstMIMEDigestMembers = []
    lstNoMailMembers = []
    objMembers = GetDataFolder(objHere, 'E3Member')
    for objBatch in objMembers.objectValues('Folder'):
        for objMember in objBatch.objectValues('E3Member'):
            if objMember.MembershipType == 'Full':
                for objListMembership in objMember.objectValues('E3ListMembership'):
                    strEmailAddress = objListMembership.EmailAddress
                    strDeliveryMode = objListMembership.GetDeliveryMode()
                    if objMember.EmailAddressConfirmed(strEmailAddress):
                        if strDeliveryMode == 'NoMail' or objMember.NoMail:
                            lstNoMailMembers.append(strEmailAddress)
                        elif strDeliveryMode == 'Direct':
                            lstDirectListMembers.append(strEmailAddress)
                        elif strDeliveryMode == 'TextDigest':
                            lstTextDigestMembers.append(strEmailAddress)
                        elif strDeliveryMode == 'MIMEDigest':
                            lstMIMEDigestMembers.append(strEmailAddress)
    return (lstDirectListMembers, lstTextDigestMembers, lstMIMEDigestMembers, lstNoMailMembers)

def UpdateMailingLists(objHere):
    objList = GetList(objHere, cnListNameECL)
    objList.Update(True)
    ReportPostingAddresses(objHere)

def ReportOnePostingAddress(objHere, strEmailAddress):
    objEmailAddress = SearchOne(objHere, 'E3EmailAddress', 'EmailAddress', strEmailAddress)
    strLine = strEmailAddress
    if objEmailAddress.Bouncing:
        strLine += ", bouncing"
    objMember = objEmailAddress.unrestrictedTraverse('..')
    if objMember.NoMail:
        strLine += ", member on nomail"
    if objMember.MembershipType == 'None':
        strLine += ", none membership"
    strDeliveryMode = objEmailAddress.DeliveryMode()
    strLine += ", " + strDeliveryMode
    print strLine
    
def ReportOneList(objHere, strDeliveryMode, lstEmailAddresses):
    intCount = 0
    print strDeliveryMode
    for strEmailAddress in lstEmailAddresses:
        ReportOnePostingAddress(objHere, strEmailAddress)
        intCount += 1
    print
    return intCount

def ReportPostingAddresses(objHere):
    intCount = 0
    objList = GetList(objHere, cnListNameECL)
    intCount += ReportOneList(objHere, 'Direct', objList.GetMailBoxerMembers('Direct'))
    intCount += ReportOneList(objHere, 'TextDigest', objList.GetMailBoxerMembers('TextDigest'))
    intCount += ReportOneList(objHere, 'MIMEDigest', objList.GetMailBoxerMembers('MIMEDigest'))
    intCount += ReportOneList(objHere, 'NoMail', objList.GetMailBoxerMembers('NoMail'))
    print "Done: %s" % intCount
    print "-" * 30
