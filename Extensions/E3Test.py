from libDatabase import GetDataFolder 
import random
import time

def GenerateTestData3p1(objContext):

    # Set 'Private' property to True/False at random
    objArchive = GetDataFolder(objContext, 'E3Messages')
    for objYear in objArchive.objectValues('Folder'):
        for objMonth in objYear.objectValues('Folder'):
            for objMessage in objMonth.objectValues('Folder'):
                objMessage.Private = random.choice((True, False))

def ParallelTest(objHere):
    print "Start of parallel test"
    intId = random.randint(1, 1000)
    objData = objHere.unrestrictedTraverse('/Data/ZEOTest')
    for intI in range(0, 10):
#        print "Get value"
        intValue = objData.ParallelTest + 1
#        print "Got value"
        objData.ParallelTest = intValue
        print "Process %s, Step %s, Value: %s" % (intId, intI, intValue)
        time.sleep(2)
    objData2 = objHere.unrestrictedTraverse('/Data/Test')
    print "Nearly done, upgrading /Data/Test from %s to %s" % (objData2.ParallelTest, objData2.ParallelTest + 1)
    objData2.ParallelTest = objData2.ParallelTest + 1


def ParallelTest2(objHere):
    print "Start of parallel test"
    intId = random.randint(1, 1000)
    objData = objHere.unrestrictedTraverse('/Data/ZEOTest')
    for intI in range(0, 10):
#        print "Get value"
        intValue = objData.ParallelTest2 + 1
#        print "Got value"
        objData.ParallelTest2 = intValue
        print "Process %s, Step %s, Value: %s" % (intId, intI, intValue)
        time.sleep(2)

def ParallelRead(objHere):
    print "Reading parallel test"
    objData = objHere.unrestrictedTraverse('/Data/ZEOTest')
    for intI in range(0, 10):
        intValue = objData.ParallelTest
        print "Reading, Step %s, Value: %s" % (intI, intValue)
        time.sleep(2)
