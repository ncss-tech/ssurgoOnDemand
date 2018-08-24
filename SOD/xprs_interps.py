#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Charles.Ferguson
#
# Created:     19/07/2016
# Copyright:   (c) Charles.Ferguson 2016
# Licence:     <your licence>

# 2017/10/04 JSON FORMAT to format and QUERY to query
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


def geoRequest(aoi):

    try:

        sr = arcpy.SpatialReference(4326)
        arcpy.management.CreateFeatureclass(outLoc, "SSURGO_express_interpretations", "POLYGON", None, None, None, sr)
        arcpy.management.AddField(outLoc + os.sep + "SSURGO_express_interpretations", "mukey", "TEXT", None, None, "30")

        gQry = """~DeclareGeometry(@aoi)~
        select @aoi = geometry::STPolyFromText('POLYGON (( """ + aoi + """))', 4326)\n

        -- Extract all intersected polygons
        ~DeclareIdGeomTable(@intersectedPolygonGeometries)~
        ~GetClippedMapunits(@aoi,polygon,geo,@intersectedPolygonGeometries)~

        -- Return WKT for the polygonal geometries
        select * from @intersectedPolygonGeometries
        where geom.STGeometryType() = 'Polygon'"""

        #uncomment next line to print geoquery
        #arcpy.AddMessage(gQry)

        arcpy.AddMessage('Sending coordinates to Soil Data Access...\n')
        theURL = "https://sdmdataaccess.nrcs.usda.gov"
        url = theURL + "/Tabular/SDMTabularService/post.rest"

        # Create request using JSON, return data as JSON
        request = {}
        request["format"] = "JSON"
        request["query"] = gQry

        #json.dumps = serialize obj (request dictionary) to a JSON formatted str
        data = json.dumps(request)

        # Send request to SDA Tabular service using urllib2 library
        # because we are passing the "data" argument, this is a POST request, not a GET
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)

        # read query results
        qResults = response.read()

        # Convert the returned JSON string into a Python dictionary.
        qData = json.loads(qResults)

        # get rid of objects
        del qResults, response, req


        funcDict = dict()

        # if dictionary key "Table" is found
        if "Table" in qData:

            # get its value
            resLst = qData["Table"]  # Data as a list of lists. All values come back as string

            rows =  arcpy.da.InsertCursor(outLoc + os.sep + "SSURGO_express_interpretations", ["SHAPE@WKT", "mukey"])

            keyList = list()

            for e in resLst:

                mukey = e[0]
                geog = e[1]

                if not mukey in keyList:
                    keyList.append(mukey)

                value = geog, mukey
                rows.insertRow(value)

            arcpy.AddMessage('\nReceived SSURGO polygons information successfully.\n')

            return True, keyList

        else:
            Msg = 'Unable to translate feature set into valid geometry'
            return False, Msg

    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, Msg

    except socket.error as e:
        Msg = 'Socket error: ' + str(e)
        return False, Msg

    except HTTPError as e:
        Msg = 'HTTP Error' + str(e)
        return False, Msg

    except URLError as e:
        Msg = 'URL Error' + str(e)
        return False, Msg

    except:
        errorMsg()
        Msg = 'Unknown error collecting geometries'
        return False, Msg


def tabRequest(interp):

    #import socket

    try:

        if interp.find("{:}") <> -1:
            interp = interp.replace("{:}", ";")
##        elif interp.find("<") <> -1:
##            interp = interp.replace("<", '&lt;')
##        elif interp.find(">") <> -1:
##            interp = interp.replace(">", '&gt;')

        if aggMethod == "Dominant Component":
            #SDA Query
            iQry = """SELECT areasymbol, musym, muname, mu.mukey  AS MUKEY,
                (SELECT interphr FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE """ + interp + """) as rating,
                (SELECT interphrc FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE """ + interp + """) as class,
                (SELECT DISTINCT SUBSTRING(  (  SELECT ( '; ' + interphrc)
                FROM mapunit
                INNER JOIN component ON component.mukey=mapunit.mukey AND compkind != 'miscellaneous area' AND component.cokey=c.cokey
                INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey

                AND ruledepth != 0 AND interphrc NOT LIKE 'Not%' AND mrulename LIKE """ + interp + """ GROUP BY interphrc, interphr
                ORDER BY interphr DESC, interphrc
                FOR XML PATH('') ), 3, 1000) )as reason
                FROM legend  AS l
                INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND  mu.mukey IN (""" + keys + """)
                INNER JOIN  component AS c ON c.mukey = mu.mukey  AND c.cokey = (SELECT TOP 1 c1.cokey FROM component AS c1
                INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)"""

        elif aggMethod == "Dominant Condition":
            iQry = """SELECT areasymbol, musym, muname, mu.mukey/1  AS MUKEY,
            (SELECT TOP 1 ROUND (AVG(interphr) over(partition by interphrc),2)
            FROM mapunit
            INNER JOIN component ON component.mukey=mapunit.mukey
            INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE """ + interp + """ GROUP BY interphrc, interphr
            ORDER BY SUM (comppct_r) DESC)as rating,
            (SELECT TOP 1 interphrc
            FROM mapunit
            INNER JOIN component ON component.mukey=mapunit.mukey
            INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE """ + interp + """
            GROUP BY interphrc, comppct_r ORDER BY SUM(comppct_r) over(partition by interphrc) DESC) as class,

            (SELECT DISTINCT SUBSTRING(  (  SELECT ( '; ' + interphrc)
            FROM mapunit
            INNER JOIN component ON component.mukey=mapunit.mukey AND compkind != 'miscellaneous area' AND component.cokey=c.cokey
            INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey

            AND ruledepth != 0 AND interphrc NOT LIKE 'Not%' AND mrulename LIKE """ + interp + """ GROUP BY interphrc, interphr
            ORDER BY interphr DESC, interphrc
            FOR XML PATH('') ), 3, 1000) )as reason


            FROM legend  AS l
            INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND mu.mukey IN (""" + keys + """)
            INNER JOIN  component AS c ON c.mukey = mu.mukey AND c.cokey =
            (SELECT TOP 1 c1.cokey FROM component AS c1
            INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)
            ORDER BY areasymbol, musym, muname, mu.mukey"""
##
        elif aggMethod == "Weighted Average":
            iQry = "SELECT\n"\
            " areasymbol, musym, muname, mu.mukey/1  AS MUKEY,\n"\
            " (SELECT TOP 1 CASE WHEN ruledesign = 1 THEN 'limitation'\n"\
            " WHEN ruledesign = 2 THEN 'suitability' END\n"\
            " FROM mapunit\n"\
            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " + interp+"\n"\
            " GROUP BY mapunit.mukey, ruledesign) as design,\n"\
            " ROUND ((SELECT SUM (interphr * comppct_r)\n"\
            " FROM mapunit\n"\
            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " + interp+"\n"\
            " GROUP BY mapunit.mukey),2) as rating,\n"\
            " ROUND ((SELECT SUM (comppct_r)\n"\
            " FROM mapunit\n"\
            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " + interp+"\n"\
            " AND (interphr) IS NOT NULL GROUP BY mapunit.mukey),2) as sum_com,\n"\
            " (SELECT DISTINCT SUBSTRING(  (  SELECT ( '; ' + interphrc)\n"\
            " FROM mapunit\n"\
            " INNER JOIN component ON component.mukey=mapunit.mukey AND compkind != 'miscellaneous area'\n"\
            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey\n"\
            " \n"\
            " AND ruledepth != 0 AND interphrc NOT LIKE 'Not%' AND mrulename LIKE " + interp + "GROUP BY interphrc\n"\
            " ORDER BY interphrc\n"\
            " FOR XML PATH('') ), 3, 1000) )as reason\n"\
            " \n"\
            " \n"\
            " INTO #main\n"\
            " FROM legend  AS l\n"\
            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND mu.mukey IN (" + keys + ")\n"\
            " INNER JOIN  component AS c ON c.mukey = mu.mukey\n"\
            " GROUP BY  areasymbol, musym, muname, mu.mukey\n"\
            " \n"\
            " SELECT areasymbol, musym, muname, MUKEY, ISNULL (ROUND ((rating/sum_com),2), 99) AS rating,\n"\
            " CASE WHEN rating IS NULL THEN 'Not Rated'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2) < = 0 THEN 'Not suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  > 0.001 and  ROUND ((rating/sum_com),2)  <=0.333 THEN 'Poorly suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  > 0.334 and  ROUND ((rating/sum_com),2)  <=0.666  THEN 'Moderately suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  > 0.667 and  ROUND ((rating/sum_com),2)  <=0.999  THEN 'Moderately well suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)   = 1  THEN 'Well suited'\n"\
            " \n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2) < = 0 THEN 'Not limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  > 0.001 and  ROUND ((rating/sum_com),2)  <=0.333 THEN 'Slightly limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  > 0.334 and  ROUND ((rating/sum_com),2)  <=0.666  THEN 'Somewhat limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  > 0.667 and  ROUND ((rating/sum_com),2)  <=0.999  THEN 'Moderately limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  = 1 THEN 'Very limited' END AS class, reason\n"\
            " FROM #main\n"\
            " DROP TABLE #main\n"

        # uncomment next line to print interp query to console
        #arcpy.AddMessage(iQry.replace("&gt;", ">").replace("&lt;", "<"))
        #arcpy.AddMessage(iQry)

        theURL = "https://sdmdataaccess.nrcs.usda.gov"
        url = theURL + "/Tabular/SDMTabularService/post.rest"

        # Create request using JSON, return data as JSON
        request = {}
        request["format"] = "JSON+COLUMNNAME+METADATA"
        request["query"] = iQry

        #json.dumps = serialize obj (request dictionary) to a JSON formatted str
        data = json.dumps(request)

        # Send request to SDA Tabular service using urllib2 library
        # because we are passing the "data" argument, this is a POST request, not a GET
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)

        # read query results
        qResults = response.read()

        # Convert the returned JSON string into a Python dictionary.
        qData = json.loads(qResults)

        # get rid of objects
        del qResults, response, req

        # if dictionary key "Table" is found
        if "Table" in qData:
            return True, qData

        else:
            Msg = 'Unable to collect interpretation informations for ' + interp
            return False, Msg


    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, Msg

    except socket.error as e:
        Msg = 'Socket error: ' + str(e)
        return False, Msg

    except HTTPError as e:
        Msg = 'HTTP Error: ' + str(e)
        return False, Msg

    except URLError as e:
        Msg = 'URL Error: ' + str(e)
        return False, Msg

    except:
        errorMsg()
        Msg = 'Unknown error collecting interpreations for ' + interp
        return False, Msg


def mkLyr():

    inFeats = outLoc + os.sep + "SSURGO_express_interpretations"
    featsLyr = arcpy.mapping.Layer(inFeats)
    lyrLoc = os.path.dirname(outLoc)

    outLyr = lyrLoc + os.sep + "SSURGO_express_interpretations_" + tblName[19:] + ".lyr"

    arcpy.management.AddJoin(featsLyr, "mukey", outLoc + os.sep + tblName, "mukey", None)
    # arcpy.management.SaveToLayerFile(featsLyr, outLyr, None, None )

    srcSymLyr = arcpy.mapping.Layer(os.path.dirname(sys.argv[0]) + os.sep + 'unq_val.lyr')

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = mxd.activeDataFrame
    arcpy.mapping.AddLayer(df, featsLyr)
    #outLyr.name = name

    #search string of the property that was run
    srcStr =  os.path.basename(featsLyr.name)

    #need to strip .shp to find layer in TOC if necessary
    if srcStr.endswith('.lyr'):
        srcStr = srcStr[:-4]

    #set the symbology...

    # must have arcpy list layers
    #a simple declaration to the layer didn't work
    #lyr = arcpy.mapping.Layer(outFeats)
    #refreshing Arc didn't work
    lyrs = arcpy.mapping.ListLayers(mxd, "*", df)
    for l in lyrs:
        if l.name == srcStr:

            l.name = tblName[19:]

            valFld = tblName + '.rating'
            # arcpy.AddMessage(l.name)
            if valFld in [x.name for x in arcpy.Describe(l).fields]:
                arcpy.mapping.UpdateLayer(df, l, srcSymLyr, True)

                values = list()
                with arcpy.da.SearchCursor(l.name, valFld) as rows:

                    for row in rows:

                        #test to see if rating has a value
                        if not row[0] == None:

                            try:
                                aVal = round(row[0], 3)
                            except:
                                aVal = aVal

                            if not aVal in values:
                                values.append(aVal)

                values.sort()

                l.symbology.valueField =  valFld
                l.symbology.addAllValues()
                l.symbology.classValues = values
                l.symbology.classDescriptions = values
                l.symbology.ShowOtherValues = False

                del values

                l.saveACopy(outLyr)

    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()

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
#===============================================================================


import sys, os, time, traceback, socket, urllib2, collections, arcpy, json
from HTMLParser import HTMLParser
from urllib2 import HTTPError, URLError

arcpy.env.overwriteOutput = True
arcpy.AddMessage('\n\n')

featSet = arcpy.GetParameterAsText(0)
aggMethod = arcpy.GetParameterAsText(1)
paramInterps = arcpy.GetParameterAsText(2)
outLoc = arcpy.GetParameterAsText(3)
bAll = arcpy.GetParameterAsText(4)

coorStr = ''
with arcpy.da.SearchCursor(featSet, "SHAPE@XY") as rows:
    for row in rows:
        coorStr = coorStr + (str(row[0][0]) + " " + str(row[0][1]) + ",")

#find the first coordinate
cIdx = coorStr.find(",")
endPoint = coorStr[:cIdx]

#the first point is also last to close
coorStr = coorStr + endPoint

if coorStr == '':
    raise ForceExit('Fatal. No AOI created')

try:
    
    geoResponse, geoVal = geoRequest(coorStr)

    if geoResponse:

        usrInterps = paramInterps.split(";")
        keys = ",".join(geoVal)

        arcpy.SetProgressor("step", None, 0, len(usrInterps), 1)

        for interp in usrInterps:
    
            tblName = "SSURGO_express_tbl" + interp + aggMethod
            tblName = arcpy.ValidateTableName (tblName)
            tblName = tblName.replace("___", "_")
            tblName = tblName.replace("__", "_")

            # path = os.path.dirname(tblName)
            # name = os.path.basename(tblName)

            intrpLogic, intrpData = tabRequest(interp)
    
            if intrpLogic:

                intrpRes = intrpData["Table"]

                if not arcpy.Exists(outLoc + os.sep + tblName):

                    columnNames = intrpRes.pop(0)
                    columnInfo = intrpRes.pop(0)

                    newTable = CreateNewTable(tblName, columnNames, columnInfo)

                    with arcpy.da.InsertCursor(newTable, columnNames) as cursor:
                        for row in intrpRes:
                            cursor.insertRow(row)

                    # convert from in-memory to table on disk
                    arcpy.conversion.TableToTable(newTable, outLoc, tblName)

                else:
                    columnNames = intrpRes.pop(0)
                    columnInfo = intrpRes.pop(0)

                    with arcpy.da.InsertCursor(outLoc + os.sep + tblName, columnNames) as cursor:
                        for row in intrpRes:
                            cursor.insertRow(row)

                if bAll == "true":
                    #mkGeo()
                    mkLyr()
            else:
                arcpy.AddMessage(intrpData)

            arcpy.SetProgressorPosition()
    else:
        arcpy.AddError('Fatal.\n' + geoVal)

except:
    errorMsg()

arcpy.AddMessage('\n\n')









