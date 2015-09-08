import cgi

import MailFunctions
reload(MailFunctions)

import GeneralFunctions
reload(GeneralFunctions)

from StringValidator import StringValidator

def SendNewMaterials():
    # Run immediately after uploading the new materials (to avoid people receiving it twice)
    # Send new materials
    # Mark new materials as sent
    pass

def FancyPrint(strString):
    strResult = ""
    for strChar in strString:
        if ord(strChar) >= 32:
            strResult = strResult + strChar
        else:
            strResult = strResult + " %s "%(ord(strChar))
    print strResult

def ClassListToString(lstClassList):
    return ", ".join(lstClassList)

def AddEnrolmentLog(objDatabase, strParticipantName, strEmailAddress, lstClassList):
    strSQL = "INSERT INTO EnrolmentLog (ParticipantName, EmailAddress, ClassIdList) VALUES ('%s', '%s', '%s')" % (
        strParticipantName, strEmailAddress, ClassListToString(lstClassList))
    ExecuteSQL(objDatabase, strSQL)

def UpdateParticipantName(objDatabase, strParticipantName, intParticipantId):
    if strParticipantName != "":
        strSQL = "UPDATE Participant SET ParticipantName = '%s' WHERE ParticipantId = %s" % (strParticipantName, intParticipantId)
        ExecuteSQL(objDatabase, strSQL)

def SaveParticipantDetails(objDatabase, strParticipantName, strEmailAddress):
    strSQL = "SELECT ParticipantId FROM Participant WHERE EmailAddress = '%s'" % (strEmailAddress.lower())
    objResult = ExecuteSQL(objDatabase, strSQL)
    if len(objResult.getresult()) > 0:
        intParticipantId = objResult.getresult()[0][0]
        UpdateParticipantName(objDatabase, strParticipantName, intParticipantId)
        return intParticipantId
    
    strNewSQL = "INSERT INTO Participant(ParticipantName, EmailAddress) VALUES ('%s', '%s')" % (strParticipantName, strEmailAddress.lower())
    ExecuteSQL(objDatabase, strNewSQL)
    
    objResult = ExecuteSQL(objDatabase, strSQL)
    intParticipantId = objResult.getresult()[0][0]
    return intParticipantId

def IsEnrolled(objDatabase, intParticipantId, strClassId):
    strSQL = "SELECT EnrolmentId FROM Enrolment WHERE ParticipantId = %s AND ClassId = '%s'" % (intParticipantId, strClassId)
    objResult = ExecuteSQL(objDatabase, strSQL)
    if len(objResult.getresult()) > 0:
        return(1, objResult.getresult()[0][0])
    else:
        return(0, 0)

def SaveEnrolment(objDatabase, intParticipantId, strClassId):
    strSQL = "INSERT INTO Enrolment(ParticipantId, ClassId) VALUES (%s, '%s')" % (intParticipantId, strClassId)
    ExecuteSQL(objDatabase, strSQL)
    
    (blnDummy, intEnrolmentId) = IsEnrolled(objDatabase, intParticipantId, strClassId)
    return intEnrolmentId

def GetFullClassDetails(objMasterclass):
    strClassTitle = objMasterclass.ClassTitle

    lstPresenters = []
    for objPresenter in objMasterclass.objectValues():
        lstPresenters.append(objPresenter.PresenterName)
    strPresenters = ", ".join(lstPresenters)

    strClassWhen = objMasterclass.ClassDate.strftime('%a %d %B %Y')
    if objMasterclass.ClassTime:
        strClassWhen = strClassWhen + "<br> at " + objMasterclass.ClassTime
    else:
        strClassWhen = strClassWhen + "<br> at 6pm UK time, 19:00 Central European Time or 1pm Eastern Standard Time"

    strBridgeNumber = objMasterclass.BridgeNumber
    strBridgePin = objMasterclass.BridgePin
    strBackupNumber = objMasterclass.BackupBridgeNumber
    strBackupPin = objMasterclass.BackupBridgePin
    return (strClassTitle, strClassWhen, strPresenters, 
            strBridgeNumber, strBridgePin, 
            strBackupNumber, strBackupPin)

def CreateInstructions(objMasterclass, objHere):
    (strClassTitle, strClassWhen, strDummy, 
        strBridgeNumber, strBridgePin, 
        strBackupNumber, strBackupPin) = GetFullClassDetails(objMasterclass)

    dictClassDetails = {'ClassTitle': strClassTitle,
            'ClassWhen': GeneralFunctions.HTMLToText(strClassWhen),
            'BridgeNumber': strBridgeNumber,
            'BridgePin': strBridgePin,
            'BackupNumber': strBackupNumber,
            'BackupPin': strBackupPin}
    
    strSubject = "Masterclass Instructions - %s" % strClassTitle
    strTextMessage = objHere.restrictedTraverse("/MCI/Templates/MasterclassInstructionsText").data + ""
    strHTMLMessage = objHere.restrictedTraverse("/MCI/Templates/MasterclassInstructionsHTML").data + ""
    
    strTextMessage = strTextMessage % dictClassDetails
    strHTMLMessage = strHTMLMessage % dictClassDetails
            
    return(strSubject, strTextMessage, strHTMLMessage)

def SendInstructions(objMasterclass, objHere, strEmailAddress):
    (strSubject, strTextMessage, strHTMLMessage) = CreateInstructions(objMasterclass, objHere)
    MailFunctions.SendPrettyEmail(strEmailAddress, strHTMLMessage, strSubject, objHere, strTextMessage)

def SendWelcomeAndInstructions(objMasterclass, objHere, strEmailAddress):    
    (strSubject, strTextMessage, strHTMLMessage) = CreateWelcomeMessageAndInstructions(objMasterclass, objHere)
    MailFunctions.SendPrettyEmail(strEmailAddress, strHTMLMessage, strSubject, objHere, strTextMessage)

def SendTrialInstructions(objMasterclass, objHere):
    strEmailAddress = "coen@coachcoen.com"
    SendInstructions(objMasterclass, objHere, strEmailAddress)
    SendWelcomeAndInstructions(objMasterclass, objHere, strEmailAddress)

def CreateWelcomeMessageAndInstructions(objMasterclass, objHere):
    (strClassTitle, strClassWhen, strPresenters, 
        strBridgeNumber, strBridgePin, 
        strBackupNumber, strBackupPin) = GetFullClassDetails(objMasterclass)

    dictClassDetails = {'ClassTitle': strClassTitle,
            'Presenters': strPresenters,
            'ClassWhen': GeneralFunctions.HTMLToText(strClassWhen),
            'BridgeNumber': strBridgeNumber,
            'BridgePin': strBridgePin,
            'BackupNumber': strBackupNumber,
            'BackupPin': strBackupPin}

    strSubject = "Masterclass Welcome and Instructions - %s" % strClassTitle
    strTextMessage = objHere.restrictedTraverse("/MCI/Templates/MasterclassWelcomeAndInstructionsText").data + ""
    strHTMLMessage = objHere.restrictedTraverse("/MCI/Templates/MasterclassWelcomeAndInstructionsHTML").data + ""
    
    strTextMessage = strTextMessage % dictClassDetails
    strHTMLMessage = strHTMLMessage % dictClassDetails
            
    return(strSubject, strTextMessage, strHTMLMessage)
    
def CreateWelcomeMessage(objMasterclass):
    lstPresenters = []
    for objPresenter in objMasterclass.objectValues():
        lstPresenters.append(objPresenter.PresenterName)
    strPresenters = ", ".join(lstPresenters)

    strClassWhen = objMasterclass.ClassDate.strftime('%a %d %B %Y')
    if objMasterclass.ClassTime:
        strClassWhen = strClassWhen + "<br> at " + objMasterclass.ClassTime
    else:
        strClassWhen = strClassWhen + "<br> at 6pm UK time, 19:00 Central European Time or 1pm Eastern Standard Time"

    strResult = """Welcome,<br><br>
You are now enrolled on the <span class=3D"Quote">%s</span> Masterclass with %s, <br>which will be held %s<br><br>

You will be sent full instructions, including the phone number to call, in due course<br><br>

Our Masterclasses are held by telephone, using a US-based telebridge. Many countries now have services providing cheap calls to the US, like <a href=3D"http://www.OneTel.co.uk">OneTel</a> and <a href=3D"http://www.1899.com">1899</a> in the UK. Check with your local coaching contacts for the services available in your country""" % (objMasterclass.ClassTitle, strPresenters, strClassWhen)

    strSubject = "Masterclass Enrolment - %s" % objMasterclass.ClassTitle

    return (strResult, strSubject)
    
def SendWelcomeMessage(objMasterclass, objHere, strEmailAddress):
    (strMessage, strSubject) = CreateWelcomeMessage(objMasterclass)
    MailFunctions.SendPrettyEmail(strEmailAddress, strMessage, strSubject, objHere)
    
def SendInitialMessage(objDatabase, intEnrolmentId, strClassId, objHere, strEmailAddress):
    objMasterclass = objHere.restrictedTraverse("/MCI/Masterclasses/" + strClassId)
    if objMasterclass.InstructionsReadyToSend:
        SendWelcomeAndInstructions(objMasterclass, objHere, strEmailAddress)
        strSQL = "UPDATE Enrolment SET InstructionsSent = TRUE WHERE EnrolmentId = %s" % intEnrolmentId
        ExecuteSQL(objDatabase, strSQL)
    else:
        SendWelcomeMessage(objMasterclass, objHere, strEmailAddress)
        
def SendAvailableMaterials(objDatabase, intEnrolmentId, objHere):
    # If materials available
        # Send materials
        # Note on database: materials sent
    pass

def ExecuteSQL(objDatabase, strSQL):
    try:
        objResult = objDatabase.query(strSQL)
        return objResult
    except:
        FancyPrint(strSQL)
        raise

def GetClassList(objRequest):
    lstClassList = []
    for strKey in objRequest.form.keys():
        if strKey[:7] == "EnrolOn":
            lstClassList.append(strKey[8:])
    return lstClassList

def ProcessMasterClassSignUp(objRequest, objHere):
    strResult = ""
    objDatabase = pg.connect(dbname = 'mci')

    strParticipantName = cgi.escape(objRequest.form["ParticipantName"])
    strEmailAddress = objRequest.form["EmailAddress"]

    if objRequest.form['EmailAddress'] == "":
        return "No email address entered.<br>Use the 'Back' button to return to the previous screen. Please enter a valid email address and try again."

    objValidator = StringValidator(objRequest.form['EmailAddress'])
    if not objValidator.isEmail():
        return "Invalid email address entered.<br>Use the 'Back' button to return to the previous screen. Please correct your email address and try again."

    lstClassList = GetClassList(objRequest)
    
    AddEnrolmentLog(objDatabase, strParticipantName, strEmailAddress, lstClassList)
    
    intParticipantId = SaveParticipantDetails(objDatabase, strParticipantName, strEmailAddress)

    for strClassId in lstClassList:
        (blnAlreadyEnrolled, intDummy) = IsEnrolled(objDatabase, intParticipantId, strClassId)
        objClass = objHere.restrictedTraverse("/MCI/Masterclasses/" + strClassId)
        strTitle = objClass.ClassTitle
        strDate = objClass.ClassDate.strftime('%a %d %B %Y')
        if blnAlreadyEnrolled:
            strResult = strResult + "You were already enrolled for %s, %s<br>" % (strTitle, strDate)
            (blnDummy, intEnrolmentId) = IsEnrolled(objDatabase, intParticipantId, strClassId)
        else:
            intEnrolmentId = SaveEnrolment(objDatabase, intParticipantId, strClassId)
            strResult = strResult + "You are now enrolled for %s, %s<br>" % (strTitle, strDate)

        SendInitialMessage(objDatabase, intEnrolmentId, strClassId, objHere, strEmailAddress)
        SendAvailableMaterials(objDatabase, intEnrolmentId, objHere)

        if objClass.InstructionsReadyToSend:
            strResult = strResult + "To join the Masterclass, please call the following US number:<br>%s, and enter pin number %s<br>" % (objClass.BridgeNumber, objClass.BridgePin)
            strResult = strResult + "Full instructions, including the phone number, have been sent to %s<br>" % strEmailAddress
        else:
            strResult = strResult + "A welcome message has been sent to %s. Instructions will be sent as soon as possible<br>" % strEmailAddress
        strResult = strResult + "<br>"
    if len(lstClassList) > 1:
        strPlural = "s"
    else:
        strPlural = ""
    strResult = strResult + """If you do not receive the email%s it may be because of overzealous anti-spam software. For any questions please go to the <a href="/ContactUs.html" class="MenuItem">contact details page</a>""" % strPlural

    # If phone details available:
    #   Show phone details
    # Else:
    #   Message: details will be sent out later

    # State the message has been sent out to (email address)
    # if it doesn't arrive, then it may be due to an overzealous spam filter

    return strResult
        
def SendMissingInstructions(objMasterclass, objHere):
    objDatabase = pg.connect(dbname = 'mci')
    strClassId = objMasterclass.id + ""
    strSQL = """SELECT Participant.EmailAddress, Enrolment.EnrolmentId 
                FROM Enrolment, Participant
                WHERE Enrolment.ParticipantId = Participant.ParticipantId
                AND NOT Enrolment.InstructionsSent
                AND Enrolment.ClassId = '%s'""" % strClassId
    objResult = ExecuteSQL(objDatabase, strSQL)
    for objRow in objResult.getresult():
        strEmailAddress = objRow[0]
        intEnrolmentId = objRow[1]
        SendInstructions(objMasterclass, objHere, strEmailAddress)
        strSQL2 = "UPDATE Enrolment SET InstructionsSent = TRUE WHERE EnrolmentId = %s" % intEnrolmentId
        ExecuteSQL(objDatabase, strSQL2)
