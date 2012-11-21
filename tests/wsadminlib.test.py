"""
    This file contains unit tests for wsadminlib.py
    Includes testcases for both:
        - single-server (aka base) envirnnmants, and
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

    propName = "proptestname"
    propValue = "proptestvalue" + getSopTimestamp()
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
    sop(m,"Exit success. gfg=" + repr(cfg))

def testND():
    """Runs all testcases for a clustered environment."""
    m = "testND:"
    enableDebugMessages()
    sop(m,"Entry.")

    cfg = {}
    # TBD

    sop(m,"Exit success. gfg=" + repr(cfg))


