#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Charles.Ferguson
#
# Created:     19/07/2016
# Copyright:   (c) Charles.Ferguson 2016
# Licence:     <your licence>
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

        gQry = " --   Define a AOI in WGS84 \n"\
        " ~DeclareGeometry(@aoi)~ \n"\
        " select @aoi = geometry::STPolyFromText('polygon(( " + aoi + "))', 4326)\n"\
        " \n"\
        " --   Extract all intersected polygons \n"\
        " ~DeclareIdGeomTable(@intersectedPolygonGeometries)~ \n"\
        " ~GetClippedMapunits(@aoi,polygon,geo,@intersectedPolygonGeometries)~ \n"\
        " \n"\
        " \n"\
        " --   Convert geometries to geographies so we can get areas \n"\
        " ~DeclareIdGeogTable(@intersectedPolygonGeographies)~ \n"\
        " ~GetGeogFromGeomWgs84(@intersectedPolygonGeometries,@intersectedPolygonGeographies)~ \n"\
        " \n"\
        " --   Return the polygonal geometries \n"\
        " select * from @intersectedPolygonGeographies \n"\
        " where geog.STGeometryType() = 'Polygon'\n"\
        " \n"\

        #uncomment next line to print geoquery
        #arcpy.AddMessage(gQry)

        # Send XML query to SDM Access service
        sXML = """<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
        <soap12:Body>
        <RunQuery xmlns="http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx">
          <Query>""" + gQry + """</Query>
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

        startTime = time.time()

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

        #msg =  "Geometry Response time = {}\n".format((time.time() - startTime))[:-6]
        if cStatus == 200:
            msg = "AOI collected successfully"
            arcpy.AddMessage(msg + '\n')
        else:
            msg = "Error collecting AOI: " + str(cStatus) + "=" + cResponse
            return False, msg

        # Convert XML to tree format
        root = ET.fromstring(xmlString)

        # Iterate through XML tree, finding required elements...


        funcDict = dict()

        #grab the records

        if descWsType == '':
            geoExt = '.shp'
        else:
            geoExt = ''

        sr = arcpy.SpatialReference(4326)
        arcpy.management.CreateFeatureclass(outLoc, "SSURGO_express_polys" + geoExt, "POLYGON", None, None, None, sr)
        arcpy.management.AddField(outLoc + os.sep + "SSURGO_express_polys" + geoExt, "mukey", "TEXT", None, None, "30")

        rows =  arcpy.da.InsertCursor(outLoc + os.sep + "SSURGO_express_polys" + geoExt, ["SHAPE@WKT", "mukey"])

        keyList = list()

        for child in root.iter('Table'):
            mukey = child.find('id').text
            geog = child.find('geog').text

            if not mukey in keyList:
                keyList.append(mukey)

            value = geog, mukey
            rows.insertRow(value)

        return True, keyList

    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, Msg

    except socket.error as e:
        Msg = 'Socket error: ' + str(e)
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
        elif interp.find("<") <> -1:
            interp = interp.replace("<", '&lt;')
        elif interp.find(">") <> -1:
            interp = interp.replace(">", '&gt;')

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


##            "SELECT areasymbol, musym, muname, mu.mukey  AS MUKEY,(SELECT interphr FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE "+ interp +") as rating, (SELECT interphrc FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE "+interp+") as class\n"\
##            " FROM legend  AS l\n"\
##            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND mu.mukey IN (" + keys + ")\n"\
##            " INNER JOIN  component AS c ON c.mukey = mu.mukey  AND c.cokey = (SELECT TOP 1 c1.cokey FROM component AS c1\n"\
##            " INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)\n"
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
##            iQry = "SELECT areasymbol, musym, muname, mu.mukey/1  AS MUKEY,\n"\
##            " (SELECT TOP 1 ROUND (AVG(interphr) over(partition by interphrc),2)\n"\
##            " FROM mapunit\n"\
##            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
##            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " +interp+ " GROUP BY interphrc, interphr\n"\
##            " ORDER BY SUM (comppct_r) DESC)as rating,\n"\
##            " (SELECT TOP 1 interphrc\n"\
##            " FROM mapunit\n"\
##            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
##            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " +interp+ "\n"\
##            " GROUP BY interphrc, comppct_r ORDER BY SUM(comppct_r) over(partition by interphrc) DESC) as class\n"\
##            " FROM legend  AS l\n"\
##            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND mu.mukey IN (" + keys + ")\n"\
##            " INNER JOIN  component AS c ON c.mukey = mu.mukey AND c.cokey =\n"\
##            " (SELECT TOP 1 c1.cokey FROM component AS c1\n"\
##            " INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)\n"\
##            " ORDER BY areasymbol, musym, muname, mu.mukey\n"
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
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2) &lt; = 0 THEN 'Not suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  &gt; 0.001 and  ROUND ((rating/sum_com),2)  &lt;=0.333 THEN 'Poorly suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  &gt; 0.334 and  ROUND ((rating/sum_com),2)  &lt;=0.666  THEN 'Moderately suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  &gt; 0.667 and  ROUND ((rating/sum_com),2)  &lt;=0.999  THEN 'Moderately well suited'\n"\
            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)   = 1  THEN 'Well suited'\n"\
            " \n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2) &lt; = 0 THEN 'Not limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  &gt; 0.001 and  ROUND ((rating/sum_com),2)  &lt;=0.333 THEN 'Slightly limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  &gt; 0.334 and  ROUND ((rating/sum_com),2)  &lt;=0.666  THEN 'Somewhat limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  &gt; 0.667 and  ROUND ((rating/sum_com),2)  &lt;=0.999  THEN 'Moderately limited '\n"\
            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  = 1 THEN 'Very limited' END AS class, reason\n"\
            " FROM #main\n"\
            " DROP TABLE #main\n"

        # uncomment next line to print interp query to console
        #arcpy.AddMessage(iQry.replace("&gt;", ">").replace("&lt;", "<"))

        # Send XML query to SDM Access service
        sXML = """<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
        <soap12:Body>
        <RunQuery xmlns="http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx">
          <Query>""" + iQry + """</Query>
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

        startTime = time.time()

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

        #msg =  "Collected {} data ({} seconds)".format(interp, (time.time() - startTime)[:-6])
        msg = "Request for {} = {}".format(interp, cResponse)
        arcpy.AddMessage(msg)
        # Convert XML to tree format

        container = dict()

        root = ET.fromstring(xmlString)

        for child in root.iter('Table'):

            areasymbol = child.find('areasymbol').text

            musym = child.find('musym').text

            muname = child.find('muname').text

            mukey = child.find('MUKEY').text

            rating = child.find('rating').text

            try:
                rating = float(rating)
                #rating = round(float(rating), 3)

            except:
                rating = -1

            clss = child.find('class').text
            if clss == None:
                clss = ''

            reason = child.find('reason').text
            if reason == None:
                reason = ''

            try:

                parser = HTMLParser()
                reason = parser.unescape(reason)

            except:
                reason = reason

            container[mukey] = areasymbol,musym, muname, mukey, rating, clss, reason


        return True, container


    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, Msg

    except socket.error as e:
        Msg = 'Socket error: ' + str(e)
        return False, Msg

    except:
        errorMsg()
        Msg = 'Unknown error collecting interpreations for ' + interp
        return False, Msg


def mkTbl(sdaTab):

    import collections

    srtDict = collections.OrderedDict(sorted(sdaTab.items()))

    srcDir = os.path.dirname(sys.argv[0])

    aggMethod == aggMethod.replace(" ", "_")

    descWsType = arcpy.Describe(outLoc).workspaceFactoryProgID

    template = os.path.dirname(sys.argv[0]) + os.sep + 'templates.gdb' + os.sep + 'xprs_interp_template'


    if descWsType == '':
        tblExt = ".dbf"
        arcpy.management.CreateTable(path, name + tblExt, template)
    else:
        tblExt = ''
        arcpy.management.CreateTable(path, name + tblExt, template)

    flds = ['areasymbol', 'musym', 'muname', 'mukey', 'rating', 'class', 'reason']

    cursor = arcpy.da.InsertCursor(tblName + tblExt, flds)

    for entry in srtDict:
        row = srtDict.get(entry)
        #arcpy.AddMessage(row)
        cursor.insertRow(row)

    del cursor, srtDict



def mkGeo():

    #arcpy.env.addOutputsToMap = True

    if descWsType == '':
        geoExt = '.shp'
        tblExt = '.dbf'
    else:
        geoExt = ''
        tblExt = ''

    inFeats = outLoc + os.sep + "SSURGO_express_polys" + geoExt
    outFeats = outLoc + os.sep + "SSURGO_express_polys_" + name[19:] + geoExt

    arcpy.management.CopyFeatures(inFeats, outFeats)

    flds = ["areasymbol", "musym", "muname", "rating", "class", "reason"]
    arcpy.management.JoinField(outFeats, "mukey", path + os.sep + name + tblExt, "mukey", flds)

    srcSymLyr = arcpy.mapping.Layer(os.path.dirname(sys.argv[0]) + os.sep + 'unq_val.lyr')


    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = mxd.activeDataFrame
    lyr = arcpy.mapping.Layer(outFeats)
    arcpy.mapping.AddLayer(df, lyr)

##    arcpy.RefreshActiveView()
##    arcpy.RefreshTOC()

    #search string of the property that was run
    srcStr =  os.path.basename(outFeats)

    #need to strip .shp to find layer in TOC if necessary
    if srcStr.endswith('.shp'):
        srcStr = srcStr[:-4]

    #set the symbology...

    # must have arcpy list layers
    #a simple declaration to the layer didn't work
    #lyr = arcpy.mapping.Layer(outFeats)
    #refreshing Arc didn't work
    lyrs = arcpy.mapping.ListLayers(mxd, "*", df)
    for l in lyrs:
        if l.name == srcStr:

            arcpy.mapping.UpdateLayer(df, l, srcSymLyr, True)

            values = list()
            with arcpy.da.SearchCursor(l, "rating") as rows:
                for row in rows:
                    #aVal = row[0]
                    aVal = round(row[0], 3)

                    if not aVal in values:
                        values.append(aVal)
            values.sort()

            l.symbology.valueField = 'rating'
            l.symbology.addAllValues()
            l.symbology.classValues = values
            l.symbology.classDescriptions = values
            l.symbology.ShowOtherValues = False

            arcpy.RefreshActiveView()
            arcpy.RefreshTOC()

            del values

def mkLyr():

    if descWsType == '':
        geoExt = '.shp'
        tblExt = '.dbf'

    else:
        geoExt = ''
        tblExt = ''



    inFeats = outLoc + os.sep + "SSURGO_express_polys" + geoExt
    featsLyr = arcpy.mapping.Layer(inFeats)
    if geoExt == '.shp':
        lyrLoc = outLoc
    else:
        lyrLoc = os.path.dirname(outLoc)


    outLyr = lyrLoc + os.sep + "SSURGO_express_polys_" + name[19:] + ".lyr"

    arcpy.management.AddJoin(featsLyr, "mukey", path + os.sep + name + tblExt, "mukey", None)
##    arcpy.management.SaveToLayerFile(featsLyr, outLyr, None, None )

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
            valFld = name + tblExt + '.rating'
            #arcpy.AddMessage(l.name)
            if valFld in [x.name for x in arcpy.Describe(l).fields]:
                arcpy.mapping.UpdateLayer(df, l, srcSymLyr, True)


                values = list()
                with arcpy.da.SearchCursor(l.name, valFld) as rows:
                    for row in rows:
                        #aVal = row[0]
                        aVal = round(row[0], 3)

                        if not aVal in values:
                            values.append(aVal)
                values.sort()



                l.symbology.valueField =  valFld
                l.symbology.addAllValues()
                l.symbology.classValues = values
                l.symbology.classDescriptions = values
                l.symbology.ShowOtherValues = False

                arcpy.RefreshActiveView()
                arcpy.RefreshTOC()

                del values

                l.saveACopy(outLyr)







#===============================================================================


import sys, os, time, traceback, socket, urllib, httplib, collections, arcpy
import xml.etree.cElementTree as ET
from HTMLParser import HTMLParser


arcpy.env.overwriteOutput = True
arcpy.AddMessage('\n\n')

featSet = arcpy.GetParameterAsText(0)
aggMethod = arcpy.GetParameterAsText(1)
paramInterps = arcpy.GetParameterAsText(2)
outLoc = arcpy.GetParameterAsText(3)
bAll = arcpy.GetParameterAsText(4)


desc = arcpy.Describe(featSet).spatialReference.datumName
#arcpy.AddMessage(desc)

descWsType = arcpy.Describe(outLoc).workspaceFactoryProgID

##info = arcpy.Describe(featSet.spatialReference)
##sr = info.factoryCode
##arcpy.AddMessage(type(featSet))


coorStr = ''
with arcpy.da.SearchCursor(featSet, "SHAPE@XY") as rows:
    for row in rows:
        coorStr = coorStr + (str(row[0][0]) + " " + str(row[0][1]) + ",")

cIdx = coorStr.find(",")
endPoint = coorStr[:cIdx]
coorStr = coorStr + endPoint

if coorStr == '':
    raise ForceExit('Fatal. No AOI created')


geoResponse, geoVal = geoRequest(coorStr)

if geoResponse:

    usrInterps = paramInterps.split(";")
    keys = ",".join(geoVal)

    for interp in usrInterps:

        tblName = "SSURGO_express_tbl" + interp + aggMethod
        tblName = arcpy.ValidateTableName (tblName)
        tblName = tblName.replace("___", "_")
        tblName = tblName.replace("__", "_")
        tblName = outLoc + os.sep + tblName

        path = os.path.dirname(tblName)
        name = os.path.basename(tblName)


        sdaResponse, sdaItem = tabRequest(interp)

        if sdaResponse:
            #arcpy.AddMessage('\n\nGenerating Table for ' + interp + '\n\n')
            mkTbl(sdaItem)
            #mkLyr()

            if bAll == "true":
                #mkGeo()
                mkLyr()
        else:
            arcpy.AddMessage(sdaItem)

else:
    arcpy.AddError('Fatal.\n' + geoVal)



arcpy.AddMessage('\n\n')







