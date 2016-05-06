"""
    This file contains unit tests for wsadminlib.py
    Includes testcases for both:
        - single-server (aka base) environments, and
        - clustered (aka ND) environments.

    Please add testcases when you add or fix methods in wsadminlib.py
    Please run these tests before delivering changes to github.

    Execution requires these files in the local directory:
        wsadminlib.test.py  (this file)
        wsadminlib.py       (the file under test)
        hitcount0.ear       (a sample app)

    Invocation example:
        Note: Specify the hostname of either your single server or your Deployment Manager.

        /opt/WAS70/profiles/v7default#  bin/wsadmin.sh -lang jython -host mywas.mycompany.com -port 8879
        wsadmin> execfile('wsadminlib.py')
        wsadmin> execfile('wsadminlib.test.py')
        wsadmin> testBase() 
"""    
import os

def errbrk(m,message):
    """Reports an error and stops testing."""
    sop(m,"ERROR: " + message)
    sys.exit(1)

#-----------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------
def testAndGetNamesBase(cfg):
    """Gets names for the cell, node, server, etc in a single-server environment.
       Stores the values in provided dictionary cfg."""
    m = "testAndGetNamesBase:"
    sop(m,"Entry.")

    # Verify we are running on a single-server.
    env = whatEnv()
    if 'base' != env:
        errbrk(m,"Environment is not 'base'. env=" + env)
    sop(m,"env=" + env)

    # Get cell name.
    cellName = getCellName()
    if 2 > len(cellName):
        errbrk(m,"Cell name is unreasonably small.  cellName=" + cellName)
    sop(m,"cellName=" + cellName)

    # Get node name.
    nodeNameList = getNodeNameList()
    if 1 != len(nodeNameList):
        errbrk(m,"Node name list does not contain exactly one name. nodeNameList=" + nodeNameList)
    nodeName = nodeNameList[0]
    if 2 > len(nodeName):
        errbrk(m,"Node name is unreasonably small.  nodeName=" + nodeName)
    sop(m,"nodeName=" + nodeName)

    # Get server name.
    serverNameList = listAllAppServers()
    if 1 != len(serverNameList):
        errbrk(m,"Server name list does not contain exactly one name. serverNameList=" + serverNameList)
    nodeServerName = serverNameList[0]
    if nodeName != nodeServerName[0]:
        errbrk(m,"Node names to not match. nodeServerName=" + repr(nodeServerName) + " nodeServerName[0]=" + nodeServerName[0])
    serverName = nodeServerName[1]
    if 2 > len(serverName):
        errbrk(m,"Server name is unreasonably small. serverName=" + serverName)
    sop(m,"serverName=" + serverName)

    # Get server ID.
    serverID = getServerByNodeAndName(nodeName,serverName)

    # Verify the server ID string contains recognizable values.
    if not serverID.startswith(serverName):
        errbrk(m,"Server ID does not start with server name. serverID=" + serverID + " serverName=" + serverName)
    if -1 == serverID.find(cellName):
        errbrk(m,"Server ID does not contain the cell name. serverID=" + serverID + " cellName=" + cellName)
    if -1 == serverID.find(nodeName):
        errbrk(m,"Server ID does not contain the node name. serverID=" + serverID + " nodeName=" + nodeName)
    if -1 == serverID.find(serverName):
        errbrk(m,"Server ID does not contain the server name. serverID=" + serverID + " serverName=" + serverName)
    sop(m,"serverID=" + serverID)

    # Save the names for use by other testcases.
    cfg["cellName"] = cellName
    cfg["nodeName"] = nodeName
    cfg["serverName"] = serverName
    cfg["serverID"] = serverID

    sop(m,"Exit success.")

#-----------------------------------------------------------------------
# Logging and tracing.
#-----------------------------------------------------------------------
def testLogTrace(cfg):
    """Sets the traditional log trace spec."""
    m = "testLogTrace:"
    sop(m,"Entry.")

    serverTraceSpec = "*=info:com.ibm.ws.webcontainer.*=all"
    setServerTrace( cfg["nodeName"], cfg["serverName"], serverTraceSpec )

    sop(m,"Exit success.")


#-----------------------------------------------------------------------
# Save
#-----------------------------------------------------------------------
def testSave(cfg):
    """Saves the changes which have been made to the configuration thus far."""
    m = "testSave:"
    sop(m,"Entry.")

    save()

    sop(m,"Exit.")

#-----------------------------------------------------------------------
# Applications
#-----------------------------------------------------------------------
def testApps(cfg):
    """Deletes all apps, installs one test app."""
    m = "testApps:"
    sop(m,"Entry.")

    sop(m,"Before testing: appList=" + repr(listApplications()))

    # Delete all apps before starting.
    deleteAllApplications()

    # Verify no apps are installed.
    appList = listApplications()
    if 0 != len(appList):
        errbrk(m,"Application list is not empty after deleting all apps. appList=" + repr(appList))
    sop(m,"Deleted all apps. appList=" + repr(appList))

    # Define the test app and where it will be installed.
    appName = "hitcount0"
    appFileName = appName + ".ear"
    serverDict = { "nodename": cfg["nodeName"], "servername": cfg["serverName"] }
    serverList = [ serverDict ]
    clusterList = []
    options = [ '-MapWebModToVH', [ ['hitcount0_web', 'hitcount0.war,WEB-INF/web.xml', 'default_host']]]

    # Verify the test app exists.
    if not os.path.exists(appFileName):
        errbrk(m,"Test application " + appFileName + " does not exist.")
    
    # Install the test app.
    installApplication(appFileName, serverList, clusterList, options)

    # Verify 1 app is installed.
    appList = listApplications()
    if 1 != len(appList):
        errbrk(m,"Application list does not have 1 app after installing test app. appList=" + repr(appList))
    sop(m,"One app is installed. appList=" + repr(appList))
    if appName != appList[0]:
        errbrk(m,"Application " + appName + " was not installed.")

    sop(m,"Exit success.")

#-----------------------------------------------------------------------
# SIP
#-----------------------------------------------------------------------
def testSIPCustomProps(cfg):
    """Sets and gets a custom property on the SIP container."""
    m = "testSIPCustomProps:"
    sop(m,"Entry.")

    propName = "sipproptestname"
    propValue = "sipproptestvalue" + getSopTimestamp()
    nodeName = cfg["nodeName"]
    serverName = cfg["serverName"]

    # Write    
    setSipContainerCustomProperty(nodeName, serverName, propName, propValue)
    sop(m,"Set prop. nodeName=" + nodeName + " serverName=" + serverName + " propName=" + propName + " propValue=" + propValue)

    # Read
    newPropValue = getSipContainerCustomProperty(nodeName, serverName, propName)
    sop(m,"Read prop. newPropValue=" + newPropValue)

    # Compare
    if propValue == newPropValue:
        sop(m,"Exit success")
    else:
        errbrk(m,"Prop values are not the same. propValue=" + propValue + " newPropValue=" + newPropValue)

#-----------------------------------------------------------------------
# ORB
#-----------------------------------------------------------------------
def testORBProps(cfg):
    """Sets and gets props in the ORB."""
    m = "testORBProps:"
    sop(m,"Entry.")

    propName = "orbproptestname"
    propValue = "orbproptestvalue" + getSopTimestamp()
    nodeName = cfg["nodeName"]
    serverName = cfg["serverName"]

    # Query ID
    orbID = getOrbId( nodeName, serverName )
    sop(m,"orbID=" + orbID)

    # Write    
    setOrbCustomProperty(nodeName, serverName, propName, propValue)
    sop(m,"Set prop. nodeName=" + nodeName + " serverName=" + serverName + " propName=" + propName + " propValue=" + propValue)

    # Read
    newPropValue = getOrbCustomProperty(nodeName, serverName, propName)
    sop(m,"Read prop. newPropValue=%s" % ( repr(newPropValue) ))

    # Compare
    if not propValue == newPropValue:
        errbrk(m,"Prop values are not the same. propValue=" + propValue + " newPropValue=%s" % ( repr(newPropValue) ))

    # Delete
    deleteOrbCustomProperty(nodeName, serverName, propName)

    # Read again
    newPropValue = getOrbCustomProperty(nodeName, serverName, propName)
    sop(m,"Read prop again. newPropValue=%s" % ( repr(newPropValue) ))

    # Verify
    if not None == newPropValue:
        errbrk(m,"Deleted prop value is not None. newPropValue=%s" % ( repr(newPropValue) ))

    sop(m,"Exit. Success.")

#-----------------------------------------------------------------------
# Web Container
#-----------------------------------------------------------------------
def testWebContainerProps(cfg):
    """Tests the setting of Web Container Properties."""
    m = "testWebContainerProps:"
    sop(m,"Entry.")

    propName1 = "wsadminlib.test.foo"
    propName2 = "wsadminlib.test.bar"
    nodeName = cfg["nodeName"]
    serverName = cfg["serverName"]

    wc = getWebcontainer(nodeName, serverName)
    beforeLen = len(_splitlist(AdminConfig.showAttribute(wc, 'properties')))

    setWebContainerCustomProperty(nodeName, serverName, propName1, "abc123")
    setWebContainerCustomProperty(nodeName, serverName, propName2, "abc456")
    setWebContainerCustomProperty(nodeName, serverName, propName1, "abc123")
    setWebContainerCustomProperty(nodeName, serverName, propName2, "abc456")

    afterLen = len(_splitlist(AdminConfig.showAttribute(wc, 'properties')))

    if afterLen > beforeLen + 2:
        errbrk(m,"Web container prop name not replaced correctly. beforeLen=%s afterLen=%s" % ( repr(beforeLen), repr(afterLen) ))

    sop(m,"Exit. Success.")

#-----------------------------------------------------------------------
# WebSphere Variables
#-----------------------------------------------------------------------
def testWebSphereVariables(cfg):
    """Sets and gets WebSphere Variables."""
    m = "testWebSphereVariables:"
    sop(m,"Entry.")

    setWebSphereVariable("WSADMINLIB_TEST_VARIABLE", "myTestContent", cfg["nodeName"])

    testString = "Test[${WSADMINLIB_TEST_VARIABLE}]String"
    targetString = "Test[myTestContent]String"
    replacedString = expandWebSphereVariables(testString, cfg["nodeName"])

    if targetString != replacedString:
        errbrk(m,"String was not replaced as expected. replacedString=%s" % ( repr(replacedString) ))

    removeWebSphereVariable("WSADMINLIB_TEST_VARIABLE", cfg["nodeName"])

    sop(m,"Exit. Success.")

#-----------------------------------------------------------------------
# Virtual Host
#-----------------------------------------------------------------------
def testVirtualHost(cfg):
    """Creates Virtual Host and tests various functions."""
    m = "testVirtualHost:"
    sop(m,"Entry.")

    testVirtualHost = 'wsadminlibtest_host'

    createVirtualHost(testVirtualHost)

    vh = getVirtualHostByName(testVirtualHost)
    if vh == None:
        errbrk(m,"Created virtual host could not be retrieved.")

    # Load Microsoft MIME Types not included with WAS V6.0 by default
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'docm', 'application/vnd.ms-word.document.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'dotm', 'application/vnd.ms-word.template.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'dotx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.template')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'ppam', 'application/vnd.ms-powerpoint.addin.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'ppsm', 'application/vnd.ms-powerpoint.slideshow.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'ppsx', 'application/vnd.openxmlformats-officedocument.presentationml.slideshow')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'pptm', 'application/vnd.ms-powerpoint.presentation.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'sldx', 'application/vnd.openxmlformats-officedocument.presentationml.slide')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'xlsb', 'application/vnd.ms-excel.sheet.binary.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'xlsm', 'application/vnd.ms-excel.sheet.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'xltm', 'application/vnd.ms-excel.template.macroEnabled.12')
    setVirtualHostMimeTypeForExtension(testVirtualHost, 'xps', 'application/vnd.ms-xpsdocument')

    deleteVirtualHost(testVirtualHost)

    sop(m,"Exit. Success.")

#-----------------------------------------------------------------------
# Classloaders
#-----------------------------------------------------------------------
def testClassloaders(cfg):
    """Test classloader functions."""
    m = "testClassloaders:"
    sop(m,"Entry.")

    deleteAllClassloaders(cfg["nodeName"], cfg["serverName"])

    sop(m,"Exit. Success.")

#-----------------------------------------------------------------------
# Clusters
#-----------------------------------------------------------------------
def testClusters(cfg):
    """Test cluster functions."""
    m = "testClusters:"
    sop(m,"Entry.")

    exceptionMessage = ""

    try:
        retval = getServerIDsForClusters('NonExistantClusterName')
    except:
        ( exceptionMessage, parms, tback ) = sys.exc_info()

    if exceptionMessage != "getServerIDsForClusters only accepts a list as input":
        sop(m,"getServerIDsForClusters returned %s" % ( repr( retval ) ))
        errbrk(m,"getServerIDsForClusters did not raise expected exception message")

    sop(m,"Exit. Success.")


#-----------------------------------------------------------------------
# getObjectByNodeServerAndName()
#-----------------------------------------------------------------------
def testGetObjectByNodeServerAndName(cfg):
    """Tests the getObjectByNodeServerAndName() function."""
    m = "testGetObjectByNodeServerAndName:"
    sop(m,"Entry.")

    nodeName = cfg["nodeName"]

    serverName1  = 'wsadminlibsrv1'
    serverName11 = 'wsadminlibsrv11'

    serverId1  = createServer(nodeName, serverName1)
    serverId11 = createServer(nodeName, serverName11)

    # These two calls should succeed
    tp1  = getObjectByNodeServerAndName( nodeName, serverName1, 'ThreadPool', 'WebContainer')
    tp11 = getObjectByNodeServerAndName( nodeName, serverName11, 'ThreadPool', 'WebContainer')
    # ...and the config id for the threadPool objects should not be equal
    if tp1 == tp11:
        errbrk(m, "config id for the threadPool objects should not be equal. tp1=" + tp1 + " tp11: " + tp11)

    exceptionMessage1 = ""
    exceptionMessage11 = ""
    # "nil" will be in retval(1|11) if it threw an exception
    retval1 = "nil"
    retval11 = "nil"

    try:
        retval1 = getObjectByNodeServerAndName( nodeName, serverName1, 'Property', 'requestTimeout')
    except:
        ( exceptionMessage1, parms, tback ) = sys.exc_info()

    try:
        retval11 = getObjectByNodeServerAndName( nodeName, serverName11, 'Property', 'requestTimeout')
    except:
        ( exceptionMessage11, parms, tback ) = sys.exc_info()

    if (exceptionMessage1 != "FOUND more than one Property with name requestTimeout" or
            exceptionMessage11 != "FOUND more than one Property with name requestTimeout"):
        sop(m,"getObjectByNodeServerAndName returned %s/%s" % ( repr( retval1 ), repr ( retval11 ) ))
        errbrk(m,"getObjectByNodeServerAndName did not raise expected exception message")

    deleteServerByNodeAndName(nodeName, serverName1)
    deleteServerByNodeAndName(nodeName, serverName11)

    sop(m,"Exit. Success.")


#-----------------------------------------------------------------------
# Full suites.
#-----------------------------------------------------------------------
def testBase():
    """Runs all testcases for a single server."""
    m = "testBase:"
    enableDebugMessages()
    sop(m,"Entry.")

    cfg = {}
    testAndGetNamesBase(cfg)
    testLogTrace(cfg)
    testSave(cfg)
    testApps(cfg)
    testSIPCustomProps(cfg)
    testORBProps(cfg)
    testWebContainerProps(cfg)
    testWebSphereVariables(cfg)
    testVirtualHost(cfg)
    testClassloaders(cfg)
    testClusters(cfg)
    testGetObjectByNodeServerAndName(cfg)
    sop(m,"Exit success. cfg=" + repr(cfg))

def testND():
    """Runs all testcases for a clustered environment."""
    m = "testND:"
    enableDebugMessages()
    sop(m,"Entry.")

    cfg = {}
    # TBD

    sop(m,"Exit success. cfg=" + repr(cfg))


