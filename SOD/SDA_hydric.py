#-------------------------------------------------------------------------------
#
#Chad Ferguson
#USDA-NRCS
#Soil Survey Division
#Mid-Atlantic and Caribbean Area Regional Office
#Raleigh, NC
#
# Created:     31/03/2015
#
#This tool grabs interprtations from Soil Data Access and aggregates based on user specified method.
#It is designed to be used as a BATCH tool
#Soil Data Access SQL code is from Jason Nemecek
#SOAP request code is from Steve Peaslee's SSURGO Download Tool - Downlaod By Map's validation class
#
#
#
#
#
#-------------------------------------------------------------------------------

class ForceExit(Exception):
    pass

def AddMsgAndPrint(msg, severity=0):
    # prints message to screen if run as a python script
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
                #arcpy.AddMessage("    ")
                arcpy.AddError(string)

    except:
        pass


def errorMsg():
    try:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        theMsg = tbinfo + " \n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        AddMsgAndPrint(theMsg, 2)

    except:
        AddMsgAndPrint("Unhandled error in errorMsg method", 2)
        pass



def getHyd(areaSym, ordLst):

    import socket

    funcDict = dict()

    try:
        hydQry = \
        "  SELECT \n" \
        "  AREASYMBOL, \n" \
        "  MUSYM, \n" \
        "  MUNAME,\n" \
        "  mu.mukey/1  AS MUKEY,\n" \
        "  (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey) AS comp_count,\n" \
        "  (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey\n" \
        "  AND majcompflag = 'Yes') AS count_maj_comp,\n" \
        "  (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey\n" \
        "  AND hydricrating = 'Yes' ) AS all_hydric,\n" \
        "  (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey\n" \
        "  AND majcompflag = 'Yes' AND hydricrating = 'Yes') AS maj_hydric,\n" \
        "  (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey\n" \
        "  AND majcompflag = 'Yes' AND hydricrating != 'Yes') AS maj_not_hydric,\n" \
        "   (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey\n" \
        "  AND majcompflag != 'Yes' AND hydricrating  = 'Yes' ) AS hydric_inclusions,\n" \
        "  (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey\n" \
        "  AND hydricrating  != 'Yes') AS all_not_hydric, \n" \
        "   (SELECT TOP 1 COUNT_BIG(*)\n" \
        "  FROM mapunit\n" \
        "  INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey\n" \
        "  AND hydricrating  IS NULL ) AS hydric_null \n" \
        "  INTO #main_query\n" \
        "  FROM legend  AS l\n" \
        "  INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND  l.areasymbol LIKE '" + areaSym + "'\n" \
        "  \n" \
        "  \n" \
        " SELECT  AREASYMBOL, MUSYM, MUNAME, MUKEY,\n" \
        " CASE WHEN comp_count = all_not_hydric + hydric_null THEN  'Nonhydric' \n" \
        " WHEN comp_count = all_hydric  THEN 'Hydric' \n" \
        " WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 'Predominantly Hydric' \n" \
        " WHEN hydric_inclusions &gt;= 0.5 AND  maj_hydric &lt; 0.5 THEN  'Predominantly Nonhydric' \n" \
        " WHEN maj_not_hydric &gt;= 0.5  AND  maj_hydric &gt;= 0.5 THEN 'Partially Hydric' ELSE 'Error' END AS HYDRIC_RATING\n" \
        " FROM #main_query\n"

        #arcpy.AddMessage(hydQry.replace("&gt;", ">").replace("&lt;", "<"))


        #send the soap request
        sXML = """<?xml version="1.0" encoding="utf-8"?>
                <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                <RunQuery xmlns="http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx">
                  <Query>""" + hydQry + """</Query>
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

        #AddMsgAndPrint(str(cStatus) + ": " + cResponse)

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
                if str(eRes):
                    eRes = eRes
                else:
                    eRes = None


                hldrLst.append(eRes)

            #get interger mukey into the list
            hldrLst.insert(2, int(hldrLst[1]))
            #arcpy.AddMessage(hldrLst)

            #put the list for each mapunit into a dictionary.  dict keys are mukeys.
            funcDict[hldrLst[1]]= hldrLst

        return True, funcDict, cResponse



    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, Msg, None

    except socket.error as e:
        Msg = 'Socket error: ' + str(e)
        return False, Msg, None

    except:
        errorMsg()
        Msg = 'Unknown error collecting interpreations for ' + eSSA
        return False, Msg, None

#===============================================================================

import arcpy, sys, os, traceback, time, httplib
import xml.etree.cElementTree as ET

arcpy.env.overwriteOutput = True


AddMsgAndPrint('\n \n')

areaParam = arcpy.GetParameterAsText(1)
WS = arcpy.GetParameterAsText(2)
jLayer = arcpy.GetParameterAsText(3)

#arcpy.AddMessage(nullParam)
srcDir = os.path.dirname(sys.argv[0])

ordLst = ['AREASYMBOL', 'MUKEY', 'MUSYM', 'MUNAME', 'HYDRIC_RATING']

try:
    areaList = areaParam.split(";")

    failPM = list()

    jobCnt = len(areaList)

    n=0
    arcpy.SetProgressor('step', 'Starting Parent Material Group Name Tool...', 0, jobCnt, 1)

    compDict = dict()

    for eSSA in areaList:
        n = n + 1
        arcpy.SetProgressorLabel('Collecting parent material table for: ' + eSSA + " (" + str(n) + ' of ' + str(jobCnt) + ')')

        #send the request
        #True, funcDict, cResponse
        gP1, gP2, gP3 = getHyd(eSSA, ordLst)

        #if it was successful...
        if gP1:
            if len(gP2) == 0:
                AddMsgAndPrint('No records returned for ' + eSSA, 1)
                failPM.append(eSSA )
                arcpy.SetProgressorPosition()
            else:
                AddMsgAndPrint('Response for hydric summary request on ' + eSSA + ' = ' + gP3)
                for k,v in gP2.iteritems():
                    compDict[k] = v
                arcpy.SetProgressorPosition()

        #if it was unsuccessful...
        else:
            #try again
            gP1, gP2, gP3 = getHyd(eSSA, ordLst)

            #if 2nd run was successful
            if gP1:
                if len(gP2) == 0:
                    AddMsgAndPrint('No records returned for ' + eSSA , 1)
                    failPM.append(eSSA )
                    arcpy.SetProgressorPosition()
                else:
                    AddMsgAndPrint('Response for hydric summary request on '  + eSSA + ' = ' + gP3 + ' - 2nd attempt')
                    for k,v in gP2.iteritems():
                        compDict[k] = v
                    arcpy.SetProgressorPosition()

            #if 2nd run was unsuccesful that's' it
            else:
                AddMsgAndPrint(gP3)
                failPM.append(eSSA)
                arcpy.SetProgressorPosition()

    arcpy.AddMessage('\n')
##########################################################################################################
    if len(compDict) > 0:
        #create the geodatabase output tables
        tblName = "SOD_hydricrating"

        jTbl = WS + os.sep  + tblName

        #fields list for cursor
        fldLst = ['AREASYMBOL', 'MUKEY', 'int_MUKEY', 'MUSYM', 'MUNAME', 'HYDRIC_RATING']


        #define the template table delivered with the tool
        template_table = srcDir + os.sep + 'templates.gdb' + os.sep + 'hydric_template'


        arcpy.management.CreateTable(WS, tblName, template_table)


        #populate the table
        cursor = arcpy.da.InsertCursor(jTbl, fldLst)

        for value in compDict:

            row = compDict.get(value)
            cursor.insertRow(row)

        del cursor
        del compDict

    else:
        arcpy.AddMessage(r'No data to build parent material table\n')

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
                AddMsgAndPrint('\n \nReloading ' + jLayer + ' due to existing join')
                if dType == 'RASTERLAYER':
                    arcpy.mapping.RemoveLayer(dfs, refLyr)
                    arcpy.MakeRasterLayer_management(path, bName)
                    arcpy.management.AddJoin(bName, "MUKEY", jTbl, "MUKEY")
                    AddMsgAndPrint('\n \nAdded join to ' + jLayer)
                elif dType == 'FEATURELAYER':
                    arcpy.mapping.RemoveLayer(dfs, refLyr)
                    arcpy.MakeFeatureLayer_management(path, bName)
                    arcpy.management.AddJoin(bName, "MUKEY", jTbl, "MUKEY")
                    AddMsgAndPrint('\n \nAdded join to ' + jLayer)
            else:
                arcpy.management.AddJoin(jLayer, "MUKEY", jTbl, "MUKEY")
                AddMsgAndPrint('\n \nAdded join to ' + jLayer)

        except:
            AddMsgAndPrint('\n \nUnable to make join to ' + jLayer)


    if len(failPM) > 0:
        AddMsgAndPrint('\n \nThe following interpretations either failed or collected no records:', 1)
        for f in failPM:
            AddMsgAndPrint(f)


    AddMsgAndPrint('\n \n')

except:
    errorMsg()

