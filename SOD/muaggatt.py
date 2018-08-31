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
#
#Updated to https 2017/02/23
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
def CreateNewTable(newTable, columnNames, columnInfo):
    # Create new table. Start with in-memory and then export to geodatabase table
    #
    # ColumnNames and columnInfo come from the Attribute query JSON string
    # MUKEY would normally be included in the list, but it should already exist in the output featureclass
    #
    try:
        # Dictionary: SQL Server to FGDB
        dType = dict()

        dType["int"] = "long"
        dType["smallint"] = "short"
        dType["bit"] = "short"
        dType["varbinary"] = "blob"
        dType["nvarchar"] = "text"
        dType["varchar"] = "text"
        dType["char"] = "text"
        dType["datetime"] = "date"
        dType["datetime2"] = "date"
        dType["smalldatetime"] = "date"
        dType["decimal"] = "double"
        dType["numeric"] = "double"
        dType["float"] = "double"

        # numeric type conversion depends upon the precision and scale
        dType["numeric"] = "float"  # 4 bytes
        dType["real"] = "double"  # 8 bytes

        # Iterate through list of field names and add them to the output table
        i = 0

        # ColumnInfo contains:
        # ColumnOrdinal, ColumnSize, NumericPrecision, NumericScale, ProviderType, IsLong, ProviderSpecificDataType, DataTypeName
        # PrintMsg(" \nFieldName, Length, Precision, Scale, Type", 1)

        joinFields = list()
        outputTbl = os.path.join("IN_MEMORY", os.path.basename(newTable))
        arcpy.CreateTable_management(os.path.dirname(outputTbl), os.path.basename(outputTbl))

        for i, fldName in enumerate(columnNames):
            vals = columnInfo[i].split(",")
            length = int(vals[1].split("=")[1])
            precision = int(vals[2].split("=")[1])
            scale = int(vals[3].split("=")[1])
            dataType = dType[vals[4].lower().split("=")[1]]

            if fldName.lower().endswith("key"):
                # Per SSURGO standards, key fields should be string. They come from Soil Data Access as long integer.
                dataType = 'text'
                length = 30

            arcpy.AddField_management(outputTbl, fldName, dataType, precision, scale, length)

        return outputTbl

    except:
        errorMsg()
    return False


def getMuaggatt(aSym):

    import socket
    from urllib2 import HTTPError, URLError
    # funcDict = dict()

    try:

        muaggatQry = \
        """SELECT ma.musym,ma.muname,ma.mustatus,ma.slopegraddcp,ma.slopegradwta,ma.brockdepmin,ma.wtdepannmin,ma.wtdepaprjunmin,ma.flodfreqdcd,ma.flodfreqmax,ma.pondfreqprs,ma.aws025wta,ma.aws050wta,ma.aws0100wta,
        ma.aws0150wta,ma.drclassdcd,ma.drclasswettest,ma.hydgrpdcd,ma.iccdcd,ma.iccdcdpct,ma.niccdcd,ma.niccdcdpct,ma.engdwobdcd,ma.engdwbdcd,ma.engdwbll,ma.engdwbml,ma.engstafdcd,ma.engstafll,ma.engstafml,ma.engsldcd,ma.engsldcp,
        ma.englrsdcd,ma.engcmssdcd,ma.engcmssmp,ma.urbrecptdcd,ma.urbrecptwta,ma.forpehrtdcp,ma.hydclprs,ma.awmmfpwwta,ma.mukey
        FROM legend
        INNER JOIN mapunit ON mapunit.lkey=legend.lkey
        INNER JOIN muaggatt ma ON mapunit.mukey=ma.mukey
        WHERE areasymbol IN (""" + aSym + """)"""

        #theURL = "https://sdmdataaccess.nrcs.usda.gov"
        #url = theURL + "/Tabular/SDMTabularService/post.rest"

        url = r'https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest'

        # Create request using JSON, return data as JSON
        request = {}
        request["format"] = "JSON+COLUMNNAME+METADATA"
        request["query"] = muaggatQry

        #json.dumps = serialize obj (request dictionary) to a JSON formatted str
        data = json.dumps(request)

        # Send request to SDA Tabular service using urllib2 library
        # because we are passing the "data" argument, this is a POST request, not a GET
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)

        code = response.getcode()
        cResponse = bhrh.responses.get(code)
        cResponse = "{}; {}".format(cResponse[0], cResponse[1])

        # read query results
        qResults = response.read()

        # Convert the returned JSON string into a Python dictionary.
        qData = json.loads(qResults)

        # get rid of objects
        del qResults, response, req

        # if dictionary key "Table" is found
        if "Table" in qData:

            return True, qData, cResponse

        else:
            cResponse = "muaggat failed for " + state
            return False, None, cResponse

    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, None, Msg

    except socket.error as e:
        state + " = " + str(e)
        return False, None, Msg

    except HTTPError as e:
        Msg = state +  " = " + str(e)
        return False, None, Msg

    except URLError as e:
        state + " = " + str(e)
        return False, None, Msg

    except:
        errorMsg()
        Msg = 'Unhandled error collecting muaggat for ' + aSym
        return False, None, Msg

#===============================================================================

import arcpy, sys, os, traceback, time, httplib, urllib2, json
from BaseHTTPServer import BaseHTTPRequestHandler as bhrh
#import xml.etree.cElementTree as ET

arcpy.env.overwriteOutput = True

PrintMsg('\n \n')

areaParam = arcpy.GetParameterAsText(1)
WS = arcpy.GetParameterAsText(2)
jLayer = arcpy.GetParameterAsText(3)

#arcpy.AddMessage(nullParam)
srcDir = os.path.dirname(sys.argv[0])

tblName = 'SOD_muaggat'

try:
    areaList = areaParam.split(";")
    states = list(set([s[:2] for s in areaList]))
    states.sort()

    failMuaggatt = list()

    jobCnt = len(states)

    n=0
    arcpy.SetProgressor('step', 'Starting MUAGGATT Tool...', 0, jobCnt, 1)

    # for eSSA in areaList:
    for state in states:
        p = [x for x in areaList if x[:2] == state]
        theReq = ",".join(map("'{0}'".format, p))

        n += 1

        arcpy.SetProgressorLabel('Collecting muaggatt table for: ' + state + " (" + str(n) + ' of ' + str(jobCnt) + ')')

        agLogic, agData, agMsg = getMuaggatt(theReq)

        #if it was successful...
        if agLogic:
            if len(agData) == 0:
                PrintMsg('No records returned for ' + state, 1)
                failMuaggatt.append(state)
                
            else:
                PrintMsg('Response for muaggatt request on ' + state + ' = ' + agMsg)
                agRes = agData["Table"]

            if not arcpy.Exists(WS + os.sep + tblName):

                columnNames = agRes.pop(0)
                columnInfo = agRes.pop(0)

                newTable = CreateNewTable(tblName, columnNames, columnInfo)

                with arcpy.da.InsertCursor(newTable, columnNames) as cursor:
                    for row in agRes:
                        cursor.insertRow(row)

                # convert from in-memory to table on disk
                arcpy.conversion.TableToTable(newTable, WS, tblName)


            else:
                columnNames = agRes.pop(0)
                columnInfo = agRes.pop(0)

                with arcpy.da.InsertCursor(WS + os.sep + tblName, columnNames) as cursor:
                    for row in agRes:
                        cursor.insertRow(row)

        #if it was unsuccessful...
        else:
            #try again
            agLogic, agData, agMsg = getMuaggatt(theReq)

            #if 2nd run was successful
            if agLogic:
                if len(agData) == 0:
                    PrintMsg('No records returned for ' + eSSA , 1)
                    failMuaggatt.append(state)

                else:
                    PrintMsg('Response for muaggatt table request on'  + state + ' = ' + agMsg + ' - 2nd attempt')
                    agRes = agData["Table"]

                if not arcpy.Exists(WS + os.sep + tblName):

                    columnNames = agRes.pop(0)
                    columnInfo = agRes.pop(0)

                    newTable = CreateNewTable(tblName, columnNames, columnInfo)

                    with arcpy.da.InsertCursor(newTable, columnNames) as cursor:
                        for row in agRes:
                            cursor.insertRow(row)

                    # convert from in-memory to table on disk
                    arcpy.conversion.TableToTable(newTable, WS, tblName)

                else:
                    columnNames = agRes.pop(0)
                    columnInfo = agRes.pop(0)

                    with arcpy.da.InsertCursor(WS + os.sep + tblName, columnNames) as cursor:
                        for row in agRes:
                            cursor.insertRow(row)


            #if 2nd run was unsuccesful that's' it
            else:
                PrintMsg(agMsg)
                failMuaggatt.append(state)

        arcpy.SetProgressorPosition()

    if jLayer != "":

        jTbl = WS + os.sep + tblName

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

