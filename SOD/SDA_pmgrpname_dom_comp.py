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
#This tool grabs soil parent material group names from Soil Data Access .
#It is designed to be used as a BATCH tool
#Soil Data Access SQL code is from Jason Nemecek
#SOAP request code is from Steve Peaslee's SSURGO Download Tool - Downlaod By Map's validation class
#
#SOAP request deprecated on SDA.  Updated to POST 2017/02/22
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


def getPMgrp(areaSym, dBool):

    import socket
    from BaseHTTPServer import BaseHTTPRequestHandler as bhrh
    from urllib2 import HTTPError, URLError

    try:

        if dBool == "true":
            pmQry = \
            """SELECT
             sacatalog.areasymbol AS areasymbol,
             mapunit.mukey AS mukey,
             mapunit.musym AS musym,
             mapunit.muname AS muname,
             compname,
             comppct_r ,

             CASE WHEN pmgroupname LIKE '%Calcareous loess%' THEN 'Eolian Deposits (nonvolcanic)'
             WHEN pmgroupname LIKE '%Eolian deposits%' THEN 'Eolian Deposits (nonvolcanic)'
             WHEN pmgroupname LIKE '%Eolian sands%' THEN 'Eolian Deposits (nonvolcanic)'
             WHEN pmgroupname LIKE '%Loess%' THEN 'Eolian Deposits (nonvolcanic)'
             WHEN pmgroupname LIKE '%Noncalcareous loess%' THEN 'Eolian Deposits (nonvolcanic)'
             WHEN pmgroupname LIKE '%Ablation till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Basal till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Cryoturbate%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Drift%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Flow till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Glaciofluvial deposits%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Glaciolacustrine deposits%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Glaciomarine deposits%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Lodgment till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Melt-out till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Outwash%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Solifluction deposits%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Subglacial till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Supraglacial meltout till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Supraglacial till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Till%' THEN 'Glacial and Periglacial Deposits'
             WHEN pmgroupname LIKE '%Bauxite%' THEN 'In-Place Deposits (nontransported)'
             WHEN pmgroupname LIKE '%Grus%' THEN 'In-Place Deposits (nontransported)'
             WHEN pmgroupname LIKE '%Residuum%' THEN 'In-Place Deposits (nontransported)'
             WHEN pmgroupname LIKE '%Saprolite%' THEN 'In-Place Deposits (nontransported)'
             WHEN pmgroupname LIKE '%Colluvium%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Complex landslide deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Creep deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Debris avalanche deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Debris flow deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Debris slide deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Debris spread deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Debris topple deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Earth spread deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Earthflow deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Flow deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Lateral spread deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Mass movement deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Mudflow deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Rock spread deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Rock topple deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Rockfall avalanche deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Rockfall deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Rotational earth slide deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Rotational slide deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Sand flow deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Scree%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Slide deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Talus%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Topple deposits%' THEN 'Mass Movement Deposits'
             WHEN pmgroupname LIKE '%Diamicton%' THEN 'Miscellaneous Deposits'
             WHEN pmgroupname LIKE '%mixed%' THEN 'Miscellaneous Deposits'
             WHEN pmgroupname LIKE '%Coprogenic material%' THEN 'Organic Deposits'
             WHEN pmgroupname LIKE '%Grassy organic material%' THEN 'Organic Deposits'
             WHEN pmgroupname LIKE '%Herbaceous organic material%' THEN 'Organic Deposits'
             WHEN pmgroupname LIKE '%Mossy organic material%' THEN 'Organic Deposits'
             WHEN pmgroupname LIKE '%Organic material%' THEN 'Organic Deposits'
             WHEN pmgroupname LIKE '%Woody organic material%' THEN 'Organic Deposits'
             WHEN pmgroupname LIKE '%Acidic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Andesitic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Ash flow%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Basaltic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Basic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Cinders%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Lahar deposits%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Pumice%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Pyroclastic flow%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Pyroclastic surge%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Scoria%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Tephra%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%tuff%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%tuff-breccia%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'
             WHEN pmgroupname LIKE '%Alluvium%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Backswamp deposits%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Beach sand%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Diatomaceous earth%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Estuarine deposits%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Fluviomarine deposits%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Greensands%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Lacustrine deposits%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Lagoonal deposits%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Marine deposits%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Marl%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Overbank deposits%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Pedisediment%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Slope alluvium%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Valley side alluvium%' THEN 'Waterlaid (or Transported) Deposits'
             WHEN pmgroupname LIKE '%Coal extraction mine spoil%' THEN 'Anthropogenic Deposits'
             WHEN pmgroupname LIKE '%Dredge spoils%' THEN 'Anthropogenic Deposits'
             WHEN pmgroupname LIKE '%Human-transported material%' THEN 'Anthropogenic Deposits'
             WHEN pmgroupname LIKE '%Metal ore extraction mine spoil%' THEN 'Anthropogenic Deposits'
             WHEN pmgroupname LIKE '%Mine spoil or earthy fill%' THEN 'Anthropogenic Deposits'
             WHEN pmgroupname LIKE '%aa%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%breccia-basic%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%conglomerate%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%dolomite%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%igneous%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%limestone%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%limestone-shale%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%metamorphic%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%quartzite%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%sandstone%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%sedimentary%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%serpentine%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%shale%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%shale-calcareous%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%siltstone%' THEN 'Miscoded - should be pmorigin'
             WHEN pmgroupname LIKE '%NULL%' THEN 'NULL' ELSE 'NULL' END AS pmgroupname


             FROM sacatalog
             INNER JOIN legend  ON legend.areasymbol = sacatalog.areasymbol AND sacatalog.areasymbol = '""" + areaSym + """'
             INNER JOIN mapunit  ON mapunit.lkey = legend.lkey
             INNER JOIN component AS c ON c.mukey = mapunit.mukey AND c.cokey =
             (SELECT TOP 1 c1.cokey FROM component AS c1
             INNER JOIN mapunit AS mu1 ON c1.mukey=mu1.mukey AND c1.mukey=mapunit.mukey ORDER BY c1.comppct_r DESC, c1.cokey )
             INNER JOIN copmgrp ON copmgrp.cokey=c.cokey"""

        else:

            pmQry = """SELECT
             sacatalog.areasymbol AS areasymbol,
             mapunit.mukey AS mukey,
             mapunit.musym AS musym,
             mapunit.muname AS muname,
             compname,
             comppct_r,
             pmgroupname

             FROM sacatalog
             INNER JOIN legend  ON legend.areasymbol = sacatalog.areasymbol AND sacatalog.areasymbol = '""" + areaSym + """'
             INNER JOIN mapunit  ON mapunit.lkey = legend.lkey
             INNER JOIN component AS c ON c.mukey = mapunit.mukey AND c.cokey =
             (SELECT TOP 1 c1.cokey FROM component AS c1
             INNER JOIN mapunit AS mu1 ON c1.mukey=mu1.mukey AND c1.mukey=mapunit.mukey ORDER BY c1.comppct_r DESC, c1.cokey )
             INNER JOIN copmgrp ON copmgrp.cokey=c.cokey"""


        #arcpy.AddMessage(pmQry)
        #theURL = "https://sdmdataaccess.nrcs.usda.gov"
        #url = theURL + "/Tabular/SDMTabularService/post.rest"
        url = r'https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest'

        # Create request using JSON, return data as JSON
        request = {}
        request["format"] = "JSON+COLUMNNAME+METADATA"
        request["query"] = pmQry

        #json.dumps = serialize obj (request dictionary) to a JSON formatted str
        data = json.dumps(request)

        # Send request to SDA Tabular service using urllib2 library
        # because we are passing the "data" argument, this is a POST request, not a GET
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)

        #get http response code and decode
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
        Msg = 'Socket error: ' + str(e)
        return False, None, Msg

    except HTTPError as e:
        Msg = 'HTTP Error: ' + str(e)
        return False, None, Msg

    except URLError as e:
        Msg = 'URL Error: ' + str(e)
        return False, None, Msg

    except:
        errorMsg()
        Msg = 'Unknown error collecting interpreations for ' + eSSA
        return False, None, Msg

#===============================================================================

import arcpy, sys, os, traceback, time, httplib, urllib2, json
#import xml.etree.cElementTree as ET

arcpy.env.overwriteOutput = True


AddMsgAndPrint('\n \n')

areaParam = arcpy.GetParameterAsText(1)
dBool = arcpy.GetParameterAsText(2)
WS = arcpy.GetParameterAsText(3)
jLayer = arcpy.GetParameterAsText(4)

#arcpy.AddMessage(nullParam)
srcDir = os.path.dirname(sys.argv[0])

tblName = "SOD_pmgrpname"

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
        pmLogic, pmData, pmMsg = getPMgrp(eSSA, dBool)

        #if it was successful...
        if pmLogic:
            if len(pmData) == 0:
                AddMsgAndPrint('No records returned for ' + eSSA, 1)
                failPM.append(eSSA )
                arcpy.SetProgressorPosition()
            else:
                AddMsgAndPrint('Response for parent material table request on ' + eSSA + ' = ' + pmMsg)
                pmRes = pmData["Table"]

                if not arcpy.Exists(WS + os.sep + tblName):

                    columnNames = pmRes.pop(0)
                    columnInfo = pmRes.pop(0)

                    newTable = CreateNewTable(tblName, columnNames, columnInfo)

                    with arcpy.da.InsertCursor(newTable, columnNames) as cursor:
                        for row in pmRes:
                            cursor.insertRow(row)

                    # convert from in-memory to table on disk
                    arcpy.conversion.TableToTable(newTable, WS, tblName)

                    arcpy.SetProgressorPosition()

                else:
                    columnNames = pmRes.pop(0)
                    columnInfo = pmRes.pop(0)

                    with arcpy.da.InsertCursor(WS + os.sep + tblName, columnNames) as cursor:
                        for row in pmRes:
                            cursor.insertRow(row)

                    arcpy.SetProgressorPosition()

        #if it was unsuccessful...
        else:
            #try again
            pmLogic, pmData, pmMsg = getPMgrp(eSSA, ordLst, dBool)

            #if 2nd run was successful
            if pmLogic:
                if len(pmData) == 0:
                    AddMsgAndPrint('No records returned for ' + eSSA , 1)
                    failPM.append(eSSA )
                    arcpy.SetProgressorPosition()
                else:
                    AddMsgAndPrint('Response for parent material table request on '  + eSSA + ' = ' + pmMsg + ' - 2nd attempt')
                    pmRes = pmData["Table"]

                    if not arcpy.Exists(WS + os.sep + tblName):

                        columnNames = pmRes.pop(0)
                        columnInfo = pmRes.pop(0)

                        newTable = CreateNewTable(tblName, columnNames, columnInfo)

                        with arcpy.da.InsertCursor(newTable, columnNames) as cursor:
                            for row in pmRes:
                                cursor.insertRow(row)

                        # convert from in-memory to table on disk
                        arcpy.conversion.TableToTable(newTable, WS, tblName)

                        arcpy.SetProgressorPosition()

                    else:
                        columnNames = pmRes.pop(0)
                        columnInfo = pmRes.pop(0)

                        with arcpy.da.InsertCursor(WS + os.sep + tblName, columnNames) as cursor:
                            for row in pmRes:
                                cursor.insertRow(row)

                        arcpy.SetProgressorPosition()

            #if 2nd run was unsuccesful that's' it
            else:
                AddMsgAndPrint('Response for parent material table request on '  + eSSA + ' = ' + pmMsg + ' - 2nd attempt')
                failPM.append(eSSA)
                arcpy.SetProgressorPosition()

    arcpy.AddMessage('\n')
##########################################################################################################

    jTbl = WS + os.sep  + tblName

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

