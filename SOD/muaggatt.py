#-------------------------------------------------------------------------------
#
#Chad Ferguson
#USDA-NRCS
#Soil Survey Division
#Mid-Atlantic and Caribbean Area Regional Office
#Raleigh, NC
#
# Created:     19/02/2016
#
#This tool generates a muaggatt table from Soil Data Access on an soil survey area basis.
#It is designed to be used as a BATCH tool
#
#headers of the SOAP request code are from Steve Peaslee's
#SSURGO Download Tool - Downlaod By Map's validation class
#
#
#
#
#
#-------------------------------------------------------------------------------

class ForceExit(Exception):
    pass

def PrintMsg(msg, severity=0):
    # Adds tool message to the geoprocessor
    #
    #Split the message on \n first, so that if it's multiple lines, a GPMessage will be added for each line
    try:
        for string in msg.split('\n'):
            #Add a geoprocessing message (in case this is run as a tool)
            if severity == 0:
                arcpy.AddMessage(string)

            elif severity == 1:
                arcpy.AddWarning(string)

            elif severity == 2:
                arcpy.AddError(" \n" + string)

    except:
        pass



def errorMsg():
    try:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        theMsg = tbinfo + " \n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        PrintMsg(theMsg, 2)

    except:
        PrintMsg("Unhandled error in errorMsg method", 2)
        pass

def getMuaggatt(aSym, ordLst):

    try:

        #containers
        fltFlds = ['slopegraddcp', 'slopegradwta', 'aws025wta', 'aws050wta', 'aws0100wta', 'aws0150wta', 'urbrecptwta', 'awmmfpwwta']
        strFlds = ['musym', 'muname', 'mustatus', 'flodfreqdcd', 'flodfreqmax', 'pondfreqprs', 'drclassdcd', 'drclasswettest', 'hydgrpdcd', 'iccdcd', 'niccdcd', 'engdwobdcd', 'engdwbdcd', 'engdwbll', 'engdwbml', 'engstafdcd', 'engstafll', 'engstafml', 'engsldcd', 'engsldcp', 'englrsdcd', 'engcmssdcd', 'engcmssmp', 'urbrecptdcd', 'forpehrtdcp', 'hydclprs', 'mukey']
        intFlds = ['brockdepmin', 'wtdepannmin', 'wtdepaprjunmin', 'iccdcdpct', 'niccdcdpct']

        funcDict = dict()

        #muaggatt Query
        muaggattQry = "SELECT ma.musym,ma.muname,ma.mustatus,ma.slopegraddcp,ma.slopegradwta,ma.brockdepmin,ma.wtdepannmin,ma.wtdepaprjunmin,ma.flodfreqdcd,ma.flodfreqmax,ma.pondfreqprs,ma.aws025wta,ma.aws050wta,ma.aws0100wta,\n"\
        " ma.aws0150wta,ma.drclassdcd,ma.drclasswettest,ma.hydgrpdcd,ma.iccdcd,ma.iccdcdpct,ma.niccdcd,ma.niccdcdpct,ma.engdwobdcd,ma.engdwbdcd,ma.engdwbll,ma.engdwbml,ma.engstafdcd,ma.engstafll,ma.engstafml,ma.engsldcd,ma.engsldcp,\n"\
        " ma.englrsdcd,ma.engcmssdcd,ma.engcmssmp,ma.urbrecptdcd,ma.urbrecptwta,ma.forpehrtdcp,ma.hydclprs,ma.awmmfpwwta,ma.mukey"\
        " FROM legend\n"\
        " INNER JOIN mapunit ON mapunit.lkey=legend.lkey\n"\
        " INNER JOIN muaggatt ma ON mapunit.mukey=ma.mukey\n"\
        " WHERE areasymbol = '" + aSym + "'"

        #print muaggattQry

        #send the soap request
        sXML = """<?xml version="1.0" encoding="utf-8"?>
                <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                <RunQuery xmlns="http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx">
                  <Query>""" + muaggattQry + """</Query>
                </RunQuery>
                </soap12:Body>
                </soap12:Envelope>"""

        dHeaders = dict()
        dHeaders["Host"      ] = "sdmdataaccess.nrcs.usda.gov"
        #dHeaders["User-Agent"] = "NuSOAP/0.7.3 (1.114)"
        #dHeaders["Content-Type"] = "application/soap+xml; charset=utf-8"
        dHeaders["Content-Type"] = "text/xml; charset=utf-8"
        dHeaders["SOAPAction"] = "http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx/RunQuery"
        dHeaders["Content-Length"] = len(sXML)
        sURL = "SDMDataAccess.nrcs.usda.gov"

        # Create SDM connection to service using HTTP
        conn = httplib.HTTPConnection(sURL, 80)

        # Send request in XML-Soap
        conn.request("POST", "/Tabular/SDMTabularService.asmx", sXML, dHeaders)

        # Get back XML response
        response = conn.getresponse()

        cStatus = response.status
        cResponse = response.reason

        #PrintMsg(str(cStatus) + ": " + cResponse)

        xmlString = response.read()

        # Close connection to SDM
        conn.close()

        # Convert XML to tree format
        root = ET.fromstring(xmlString)


        for child in root.iter('Table'):

            #create a list to accumulate values for each mapunit
            hldrLst = list()

            #loop thru the ordered list and get corresponding value from xml
            #and add it to list
            for eFld in ordLst:
                eRes = child.find(eFld).text

                #test and  convert values to appropriate data type
                #convert to None type if no value returned
                if eFld in strFlds:
                    if str(eRes):
                        eRes = eRes
                    else:
                        eRes = None

                if eFld in fltFlds:
                    try:
                        eRes = float(eRes)
                    except:
                        eRes = None

                if eFld in intFlds:
                    try:
                        eRes = int(eRes)
                    except:
                        eRes = None

                hldrLst.append(eRes)

            #put the list for each mapunit into a dictionary.  dict keys are mukeys.
            funcDict[hldrLst[-1]]= hldrLst

        return True, funcDict, cResponse



    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, Msg, None

    except socket.error as e:
        Msg = 'Socket error: ' + str(e)
        return False, Msg, None

    except:
        errorMsg()
        Msg = 'Unknown error collecting muaggatt table for ' + eSSA
        return False, Msg, None

#===============================================================================

import arcpy, sys, os, traceback, time, httplib
import xml.etree.cElementTree as ET

arcpy.env.overwriteOutput = True


PrintMsg('\n \n')

areaParam = arcpy.GetParameterAsText(1)
WS = arcpy.GetParameterAsText(2)
jLayer = arcpy.GetParameterAsText(3)

#arcpy.AddMessage(nullParam)
srcDir = os.path.dirname(sys.argv[0])

ordLst = ['musym', 'muname', 'mustatus', 'slopegraddcp', 'slopegradwta', 'brockdepmin', 'wtdepannmin', 'wtdepaprjunmin', 'flodfreqdcd', 'flodfreqmax', 'pondfreqprs', 'aws025wta', 'aws050wta', 'aws0100wta', 'aws0150wta', 'drclassdcd', 'drclasswettest', 'hydgrpdcd', 'iccdcd', 'iccdcdpct', 'niccdcd', 'niccdcdpct', 'engdwobdcd', 'engdwbdcd', 'engdwbll', 'engdwbml', 'engstafdcd', 'engstafll', 'engstafml', 'engsldcd', 'engsldcp', 'englrsdcd', 'engcmssdcd', 'engcmssmp', 'urbrecptdcd', 'urbrecptwta', 'forpehrtdcp', 'hydclprs', 'awmmfpwwta', 'mukey']

try:
    areaList = areaParam.split(";")


    failMuaggatt = list()

    jobCnt = len(areaList)

    n=0
    arcpy.SetProgressor('step', 'Starting MUAGGATT Tool...', 0, jobCnt, 1)

    compDict = dict()

    for eSSA in areaList:
        n = n + 1
        arcpy.SetProgressorLabel('Collecting muaggatt table for: ' + eSSA + " (" + str(n) + ' of ' + str(jobCnt) + ')')

        #send the request
        #True, funcDict, cResponse
        gP1, gP2, gP3 = getMuaggatt(eSSA, ordLst)

        #if it was successful...
        if gP1:
            if len(gP2) == 0:
                PrintMsg('No records returned for ' + eSSA, 1)
                failMuaggatt.append(eSSA )
                arcpy.SetProgressorPosition()
            else:
                PrintMsg('Response for muaggatt request on ' + eSSA + ' = ' + gP3)
                for k,v in gP2.iteritems():
                    compDict[k] = v
                arcpy.SetProgressorPosition()

        #if it was unsuccessful...
        else:
            #try again
            gP1, gP2, gP3 = getMuaggatt(eSSA, ordLst)

            #if 2nd run was successful
            if gP1:
                if len(gP2) == 0:
                    PrintMsg('No records returned for ' + eSSA , 1)
                    failMuaggatt.append(eSSA )
                    arcpy.SetProgressorPosition()
                else:
                    PrintMsg('Response for muaggatt table request on'  + eSSA + ' = ' + gP3 + ' - 2nd attempt')
                    for k,v in gP2.iteritems():
                        compDict[k] = v
                    arcpy.SetProgressorPosition()

            #if 2nd run was unsuccesful that's' it
            else:
                PrintMsg(gP3)
                failMuaggatt.append(eSSA)
                arcpy.SetProgressorPosition()

    arcpy.AddMessage('\n')
##########################################################################################################
    if len(compDict) > 0:
        #create the geodatabase output tables
        tblName = "SOD_muaggatt"

        jTbl = WS + os.sep  + tblName

        #fields list for cursor
        fldLst = ordLst

        #define the template table delivered with the tool
        template_table = srcDir + os.sep + 'templates.gdb' + os.sep + 'muaggatt_template'

        arcpy.management.CreateTable(WS, tblName, template_table)

        #populate the table
        cursor = arcpy.da.InsertCursor(jTbl, fldLst)

        for value in compDict:

            row = compDict.get(value)
            cursor.insertRow(row)

        del cursor
        del compDict

    else:
        arcpy.AddMessage(r'No data to build muaggatt table for ' + eSSA + '\n')


    if jLayer != "":

        try:
            mxd = arcpy.mapping.MapDocument("CURRENT")
            dfs = arcpy.mapping.ListDataFrames(mxd, "*")[0]

            objLyr = arcpy.mapping.ListLayers(mxd, jLayer, dfs)
            refLyr = objLyr[0]
            desc = arcpy.Describe(jLayer)
            dType = desc.dataType.upper()
            path = desc.catalogPath
            bName = desc.baseName

            flds = [x.name for x in desc.fields]
            if not "MUKEY" in flds:
                arcpy.env.addOutputsToMap = True
                PrintMsg('\n \nReloading ' + jLayer + ' due to existing join')
                if dType == 'RASTERLAYER':
                    arcpy.mapping.RemoveLayer(dfs, refLyr)
                    arcpy.MakeRasterLayer_management(path, bName)
                    arcpy.management.AddJoin(bName, "MUKEY", jTbl, "MUKEY")
                    PrintMsg('\n \nAdded join to ' + jLayer)
                elif dType == 'FEATURELAYER':
                    arcpy.mapping.RemoveLayer(dfs, refLyr)
                    arcpy.MakeFeatureLayer_management(path, bName)
                    arcpy.management.AddJoin(bName, "MUKEY", jTbl, "MUKEY")
                    PrintMsg('\n \nAdded join to ' + jLayer)
            else:
                arcpy.management.AddJoin(jLayer, "MUKEY", jTbl, "MUKEY")
                PrintMsg('\n \nAdded join to ' + jLayer)

        except:
            PrintMsg('\n \nUnable to make join to ' + jLayer)


    if len(failMuaggatt) > 0:
        PrintMsg('\n \nThe following muaggatt requests either failed or collected no records:', 1)
        for f in failMuaggatt:
            PrintMsg(f)


    PrintMsg('\n \n')

except:
    errorMsg()

