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


def getHyd(areaSym):

    import socket
    from urllib2 import HTTPError, URLError

    try:

        hydQry = \
        """SELECT
        AREASYMBOL,
        MUSYM,
        MUNAME,
        mu.mukey/1  AS MUKEY,
        (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey) AS comp_count,
        (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey
        AND majcompflag = 'Yes') AS count_maj_comp,
        (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey
        AND hydricrating = 'Yes' ) AS all_hydric,
        (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey
        AND majcompflag = 'Yes' AND hydricrating = 'Yes') AS maj_hydric,
        (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey
        AND majcompflag = 'Yes' AND hydricrating != 'Yes') AS maj_not_hydric,
         (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey
        AND majcompflag != 'Yes' AND hydricrating  = 'Yes' ) AS hydric_inclusions,
        (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey
        AND hydricrating  != 'Yes') AS all_not_hydric,
         (SELECT TOP 1 COUNT_BIG(*)
        FROM mapunit
        INNER JOIN component ON component.mukey=mapunit.mukey AND mapunit.mukey = mu.mukey
        AND hydricrating  IS NULL ) AS hydric_null
        INTO #main_query
        FROM legend  AS l
        INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND  l.areasymbol IN ("""+ areaSym + """)


        SELECT  AREASYMBOL, MUKEY, MUSYM, MUNAME,
        CASE WHEN comp_count = all_not_hydric + hydric_null THEN  'Nonhydric'
        WHEN comp_count = all_hydric  THEN 'Hydric'
        WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 'Predominantly Hydric'
        WHEN hydric_inclusions &gt;= 0.5 AND  maj_hydric &lt; 0.5 THEN  'Predominantly Nonhydric'
        WHEN maj_not_hydric &gt;= 0.5  AND  maj_hydric &gt;= 0.5 THEN 'Partially Hydric' ELSE 'Error' END AS HYDRIC_RATING
        FROM #main_query"""

        #print hydQry.replace("&gt;", ">").replace("&lt;", "<")
        hydQry = hydQry.replace("&gt;", ">").replace("&lt;", "<")

        #theURL = "https://sdmdataaccess.nrcs.usda.gov"
        #url = theURL + "/Tabular/SDMTabularService/post.rest"
        url = r'https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest'

        # Create request using JSON, return data as JSON
        request = {}
        request["format"] = "JSON+COLUMNNAME+METADATA"
        request["query"] = hydQry

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
            cResponse = 'OK'

            return True, qData, cResponse

        else:
            cResponse = 'Failed'
            return False, None, cResponse

    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, None, Msg

    except socket.error as e:
        Msg = state + " = " + str(e)
        return False, None, Msg

    except HTTPError as e:
        Msg = state + " = " + str(e)
        return False, None, Msg

    except URLError as e:
        Msg = state + " = " + str(e)
        return False, None, Msg

    except:
        errorMsg()
        Msg = 'Unknown error collecting interpreations for ' + eSSA
        return False, Msg, None

#===============================================================================

import arcpy, sys, os, traceback, time, httplib, urllib2, json
from BaseHTTPServer import BaseHTTPRequestHandler as bhrh

arcpy.env.overwriteOutput = True


AddMsgAndPrint('\n \n')

areaParam = arcpy.GetParameterAsText(1)
WS = arcpy.GetParameterAsText(2)
jLayer = arcpy.GetParameterAsText(3)

#arcpy.AddMessage(nullParam)
srcDir = os.path.dirname(sys.argv[0])

try:
    areaList = areaParam.split(";")
    states = list(set([s[:2] for s in areaList]))
    states.sort()

    failHyd = list()

    jobCnt = len(states)

    n=0
    
    arcpy.SetProgressor('step', 'Starting Parent Material Group Name Tool...', 0, jobCnt, 1)

    tblName = "SOD_hydricrating"
    

    # for eSSA in areaList:
    for state in states:
        p = [x for x in areaList if x[:2] == state]
        theReq = ",".join(map("'{0}'".format, p))

        n+=1

        arcpy.SetProgressorLabel('Collecting parent material table for: ' + state + " (" + str(n) + ' of ' + str(jobCnt) + ')')

        #send the request
        hydLogic, hydData, hydMsg = getHyd(theReq)

        #if it was successful...
        if hydLogic:
            if len(hydData) == 0:
                AddMsgAndPrint('No records returned for ' + state, 1)
                failHyd.append(state)
                arcpy.SetProgressorPosition()
            else:
                AddMsgAndPrint('Response for hydric summary request on ' + state + ' = ' + hydMsg)
                hydRes = hydData["Table"]

                if not arcpy.Exists(WS + os.sep + tblName):

                    columnNames = hydRes.pop(0)
                    columnInfo = hydRes.pop(0)

                    newTable = CreateNewTable(tblName, columnNames, columnInfo)

                    with arcpy.da.InsertCursor(newTable, columnNames) as cursor:
                        for row in hydRes:
                            cursor.insertRow(row)

                    # convert from in-memory to table on disk
                    arcpy.conversion.TableToTable(newTable, WS, tblName)

                    arcpy.SetProgressorPosition()

                else:
                    columnNames = hydRes.pop(0)
                    columnInfo = hydRes.pop(0)

                    with arcpy.da.InsertCursor(WS + os.sep + tblName, columnNames) as cursor:
                        for row in hydRes:
                            cursor.insertRow(row)

                    arcpy.SetProgressorPosition()

        #if it was unsuccessful...
        else:
            #try again
            hydLogic, hydData, hydMsg = getHyd(theReq)

            #if 2nd run was successful
            if hydLogic:
                if len(hydData) == 0:
                    AddMsgAndPrint('No records returned for ' + state , 1)
                    failHyd.append(state)
                    arcpy.SetProgressorPosition()
                else:
                    AddMsgAndPrint('Response for hydric summary request on '  + state + ' = ' + hydMsg + ' - 2nd attempt')
                    hydRes = hydData["Table"]

                    if not arcpy.Exists(WS + os.sep + tblName):

                        columnNames = hydRes.pop(0)
                        columnInfo = hydRes.pop(0)

                        newTable = CreateNewTable(tblName, columnNames, columnInfo)

                        with arcpy.da.InsertCursor(newTable, columnNames) as cursor:
                            for row in hydRes:
                                cursor.insertRow(row)

                        # convert from in-memory to table on disk
                        arcpy.conversion.TableToTable(newTable, WS, tblName)

                        arcpy.SetProgressorPosition()

                    else:
                        columnNames = hydRes.pop(0)
                        columnInfo = hydRes.pop(0)

                        with arcpy.da.InsertCursor(WS + os.sep + tblName, columnNames) as cursor:
                            for row in hydRes:
                                cursor.insertRow(row)

                        arcpy.SetProgressorPosition()

            #if 2nd run was unsuccesful that's' it
            else:
                AddMsgAndPrint('Response for hydric summary request on '  + state + ' = ' + hydMsg + ' - 2nd attempt')
                failHyd.append(state)
                arcpy.SetProgressorPosition()

    arcpy.AddMessage('\n')
##########################################################################################################

    if jLayer != "":

        try:
            mxd = arcpy.mapping.MapDocument("CURRENT")
            df = mxd.activeDataFrame
            objLyr = arcpy.mapping.ListLayers(mxd, jLayer, df)
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
                    arcpy.mapping.RemoveLayer(df, refLyr)
                    arcpy.MakeRasterLayer_management(path, bName)
                    arcpy.management.AddJoin(bName, "MUKEY", os.path.join(WS,tblName), "MUKEY")
                    AddMsgAndPrint('\n \nAdded join to ' + jLayer)
                elif dType == 'FEATURELAYER':
                    arcpy.mapping.RemoveLayer(df, refLyr)
                    arcpy.MakeFeatureLayer_management(path, bName)
                    arcpy.management.AddJoin(bName, "MUKEY", os.path.join(WS,tblName), "MUKEY")
                    AddMsgAndPrint('\n \nAdded join to ' + jLayer)
            else:
                arcpy.management.AddJoin(jLayer, "MUKEY", os.path.join(WS,tblName), "MUKEY")
                AddMsgAndPrint('\n \nAdded join to ' + jLayer)

        except:
            errorMsg()
            AddMsgAndPrint('\n \nUnable to make join to ' + jLayer)


    if len(failHyd) > 0:
        AddMsgAndPrint('\n \nThe following interpretations either failed or collected no records:', 1)
        for f in failHyd:
            AddMsgAndPrint(f)


    AddMsgAndPrint('\n \n')

except:
    errorMsg()

