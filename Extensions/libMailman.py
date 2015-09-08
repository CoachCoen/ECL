# encoding: utf-8

"""Mailman functions"""

import os
import string

from Mailman import Utils
from Mailman import MailList
from Mailman import Errors
from Mailman.UserDesc import UserDesc
from Mailman.Logging.Syslog import syslog

import libConstants
reload(libConstants)

# Following code adapted from Mailman source code
# at mailman-2.1.4/Mailman/Cgi/subscribe.py process_form function
def SubscribeToMailingList(strEmailAddress, strListName, blnDigestMode):
    """Subscribe a new member to the list"""

    blnResult = 1
    intError = 0

    try:
        objList = MailList.MailList(strListName, lock = 1)
    except Errors.MMUnknownListError:
        (blnResult, intError) = (0, libConstants.ErrorUnknownList)

    if blnResult:
        # Who was doing the subscribing?
        varRemote = os.environ.get('REMOTE_HOST',
                                os.environ.get('REMOTE_ADDR',
                                               'unidentified origin'))
    
        # Was an attempt made to subscribe the list to itself?
        if string.upper(strEmailAddress) == string.upper(objList.GetListEmail()):
            syslog('mischief', 'Attempt to self subscribe %s: %s', strEmailAddress, varRemote)
            
            (blnResult, intError) = (0, libConstants.ErrorSubscribingTheListAddress)

    if blnResult:
        strPassword = Utils.MakeRandomPassword()
        
        try:
            objUserDescription = UserDesc(strEmailAddress, "", strPassword, blnDigestMode, 'en')
            objList.AddMember(objUserDescription, varRemote)
            
        except Errors.MembershipIsBanned:
            (blnResult, intError) = (0, libConstants.ErrorMemberIsBanned)
        except Errors.MMBadEmailError:
            (blnResult, intError) = (0, libConstants.ErrorIncorrectEmailAddress)
        except Errors.MMHostileAddress:
            (blnResult, intError) = (0, libConstants.ErrorHostileAddress)
        except Errors.MMSubscribeNeedsConfirmation:
            # This is what we're expecting, so ignore
            pass
        except Errors.MMNeedApproval, x:
            (blnResult, intError) = (0, libConstants.ErrorNeedApproval)
        except Errors.MMAlreadyAMember:
            (blnResult, intError) = (0, libConstants.ErrorAlreadySubscribed)
        
    # Finish off with something like:
    try:
        objList.Save()
        objList.Unlock()
        del objList
    except:
        pass
        
    return (blnResult, intError)
    
def UnsubscribeFromList(strEmailAddress, strListName = 'eurocoach-list'):
    pass

def SubscribeToList(strEmailAddress, strDeliveryMode, strListName = 'eurocoach-list'):
    pass

def SetDeliveryMode(strEmailAddress, strDeliveryMode, strListName = 'eurocoach-list'):
    pass

def BatchUnsubscribeFromList(lstEmailAddresses,  strListName = 'eurocoach-list'):
    pass

def BatchSubscribeToList(lstDetails, strListName = 'eurocoach-list'):
    for (strEmailAddress, strDeliveryMode) in lstDetails:
        pass

def BatchSetDeliveryMode(lstDetails, strListName = 'eurocoach-list'):
    for (strEmailAddress, strDeliveryMode) in lstDetails:
        pass
