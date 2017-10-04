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



def getIntrps(interp, areaSym, aggMethod):

    import socket
    from urllib2 import HTTPError, URLError

    try:
##        if interp.find("<") <> -1:
##            interp = interp.replace("<", '&lt;')
##            #Msg = 'Illegal Character found in ' + interp +' name.  Skipping for ' + areaSym
##            #return False, Msg, None
##        elif interp.find(">") <> -1:
##            interp = interp.replace("<", '&gt;')
##            #Msg = 'Illegal Character found in ' + interp +' name.  Skipping for ' + areaSym
##            #return False, Msg, None

        #arcpy.AddMessage(interp)
        #Not suited changed to Very Poorly Suited to align better with dominant condition and dominant component for wtd_avg
        if aggMethod == "Dominant Component":
            #SDA Query
            interpQry = """SELECT areasymbol, musym, muname, mu.mukey  AS MUKEY,
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
                INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND l.areasymbol LIKE '""" + areaSym + """'
                INNER JOIN  component AS c ON c.mukey = mu.mukey  AND c.cokey = (SELECT TOP 1 c1.cokey FROM component AS c1
                INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)"""
##            interpQry ="SELECT areasymbol, musym, muname, mu.mukey  AS MUKEY,(SELECT interphr FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE "+interp+") as rating, (SELECT interphrc FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE "+interp+") as class\n"\
##            " FROM legend  AS l\n"\
##            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND l.areasymbol LIKE '" + areaSym + "'\n"+\
##            " INNER JOIN  component AS c ON c.mukey = mu.mukey  AND c.cokey = (SELECT TOP 1 c1.cokey FROM component AS c1\n"\
##            " INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)\n"
        elif aggMethod == "Dominant Condition":
            interpQry = """SELECT areasymbol, musym, muname, mu.mukey/1  AS MUKEY,
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
            INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND l.areasymbol LIKE '""" + areaSym + """'
            INNER JOIN  component AS c ON c.mukey = mu.mukey AND c.cokey =
            (SELECT TOP 1 c1.cokey FROM component AS c1
            INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)
            ORDER BY areasymbol, musym, muname, mu.mukey"""

##            "SELECT areasymbol, musym, muname, mu.mukey/1  AS MUKEY,\n"\
##            " (SELECT TOP 1 ROUND (AVG(interphr) over(partition by interphrc),2)\n"\
##            " FROM mapunit\n"\
##            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
##            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " +interp+ " GROUP BY interphrc, interphr\n"\
##            " ORDER BY SUM (comppct_r) DESC)as rating,\n"\
##            " (SELECT TOP 1 interphrc\n"\
##            " FROM mapunit\n"\
##            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
##            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " +interp+ "\n"+\
##            " GROUP BY interphrc, comppct_r ORDER BY SUM(comppct_r) over(partition by interphrc) DESC) as class\n"\
##            " FROM legend  AS l\n"\
##            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND l.areasymbol LIKE '" +areaSym+ "'\n"+\
##            " INNER JOIN  component AS c ON c.mukey = mu.mukey AND c.cokey =\n"\
##            " (SELECT TOP 1 c1.cokey FROM component AS c1\n"\
##            " INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)\n"\
##            " ORDER BY areasymbol, musym, muname, mu.mukey\n"
        elif aggMethod == "Weighted Average":
            interpQry = """SELECT areasymbol, musym, muname, mu.mukey/1  AS MUKEY,
                (SELECT TOP 1 CASE WHEN ruledesign = 1 THEN 'limitation'
                WHEN ruledesign = 2 THEN 'suitability' END
                FROM mapunit
                INNER JOIN component ON component.mukey=mapunit.mukey
                INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE """ + interp+"""
                GROUP BY mapunit.mukey, ruledesign) as design,
                ROUND ((SELECT SUM (interphr * comppct_r)
                FROM mapunit
                INNER JOIN component ON component.mukey=mapunit.mukey
                INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE """ + interp+"""
                GROUP BY mapunit.mukey),2) as rating,
                ROUND ((SELECT SUM (comppct_r)
                FROM mapunit
                INNER JOIN component ON component.mukey=mapunit.mukey
                INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE """ + interp+"""
                AND (interphr) IS NOT NULL GROUP BY mapunit.mukey),2) as sum_com,
                (SELECT DISTINCT SUBSTRING(  (  SELECT ( '; ' + interphrc)
                FROM mapunit
                INNER JOIN component ON component.mukey=mapunit.mukey AND compkind != 'miscellaneous area'
                INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey

                AND ruledepth != 0 AND interphrc NOT LIKE 'Not%' AND mrulename LIKE """ + interp + """GROUP BY interphrc
                ORDER BY interphrc
                FOR XML PATH('') ), 3, 1000) )as reason

                INTO #main
                FROM legend  AS l
                INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND l.areasymbol LIKE '""" + areaSym + """'
                INNER JOIN  component AS c ON c.mukey = mu.mukey
                GROUP BY  areasymbol, musym, muname, mu.mukey

                SELECT areasymbol, musym, muname, MUKEY, ISNULL (ROUND ((rating/sum_com),2), 99) AS rating,
                CASE WHEN rating IS NULL THEN 'Not Rated'
                WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2) < = 0 THEN 'Not suited'
                WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  > 0.001 and  ROUND ((rating/sum_com),2)  <=0.333 THEN 'Poorly suited'
                WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  > 0.334 and  ROUND ((rating/sum_com),2)  <=0.666  THEN 'Moderately suited'
                WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  > 0.667 and  ROUND ((rating/sum_com),2)  <=0.999  THEN 'Moderately well suited'
                WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)   = 1  THEN 'Well suited'

                WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2) < = 0 THEN 'Not limited '
                WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  > 0.001 and  ROUND ((rating/sum_com),2)  <=0.333 THEN 'Slightly limited '
                WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  > 0.334 and  ROUND ((rating/sum_com),2)  <=0.666  THEN 'Somewhat limited '
                WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  > 0.667 and  ROUND ((rating/sum_com),2)  <=0.999  THEN 'Moderately limited '
                WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  = 1 THEN 'Very limited' END AS class, reason
                FROM #main
                DROP TABLE #main"""
##            "SELECT\n"\
##            " areasymbol, musym, muname, mu.mukey/1  AS MUKEY,\n"\
##            " (SELECT TOP 1 CASE WHEN ruledesign = 1 THEN 'limitation'\n"\
##            " WHEN ruledesign = 2 THEN 'suitability' END\n"\
##            " FROM mapunit\n"\
##            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
##            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " + interp+"\n"+\
##            " GROUP BY mapunit.mukey, ruledesign) as design,\n"\
##            " ROUND ((SELECT SUM (interphr * comppct_r)\n"\
##            " FROM mapunit\n"\
##            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
##            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " +interp+"\n"+\
##            " GROUP BY mapunit.mukey),2) as rating,\n"\
##            " ROUND ((SELECT SUM (comppct_r)\n"\
##            " FROM mapunit\n"\
##            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
##            " INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE " +interp+"\n"+\
##            " AND (interphr) IS NOT NULL GROUP BY mapunit.mukey),2) as sum_com\n"\
##            " INTO #main\n"\
##            " FROM legend  AS l\n"\
##            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND l.areasymbol LIKE '" +areaSym+ "'\n"\
##            " INNER JOIN  component AS c ON c.mukey = mu.mukey\n"\
##            " GROUP BY  areasymbol, musym, muname, mu.mukey\n"\
##            " SELECT areasymbol, musym, muname, MUKEY, ISNULL (ROUND ((rating/sum_com),2), 99) AS rating,\n"\
##            " CASE WHEN rating IS NULL THEN 'Not Rated'\n"\
##            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2) &lt; = 0 THEN 'Very Poorly Suited'\n"\
##            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  &gt; 0.001 and  ROUND ((rating/sum_com),2)  &lt;=0.333 THEN 'Poorly suited'\n"\
##            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  &gt; 0.334 and  ROUND ((rating/sum_com),2)  &lt;=0.666  THEN 'Moderately suited'\n"\
##            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)  &gt; 0.667 and  ROUND ((rating/sum_com),2)  &lt;=0.999  THEN 'Moderately well suited'\n"\
##            " WHEN design = 'suitability' AND  ROUND ((rating/sum_com),2)   = 1  THEN 'Well suited'\n"\
##            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2) &lt; = 0 THEN 'Not limited'\n"\
##            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  &gt; 0.001 and  ROUND ((rating/sum_com),2)  &lt;=0.333 THEN 'Slightly limited'\n"\
##            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  &gt; 0.334 and  ROUND ((rating/sum_com),2)  &lt;=0.666  THEN 'Somewhat limited'\n"\
##            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  &gt; 0.667 and  ROUND ((rating/sum_com),2)  &lt;=0.999  THEN 'Moderately limited'\n"\
##            " WHEN design = 'limitation' AND  ROUND ((rating/sum_com),2)  = 1 THEN 'Very limited' END AS class\n"\
##            " FROM #main"


        #arcpy.AddMessage(interpQry.replace("&gt;", ">").replace("&lt;", "<"))
        #arcpy.AddMessage(interpQry)
        # Send XML query to SDM Access service

        funcDict = dict()

        theURL = "https://sdmdataaccess.nrcs.usda.gov"
        url = theURL + "/Tabular/SDMTabularService/post.rest"

        # Create request using JSON, return data as JSON
        request = {}
        request["format"] = "JSON"
        request["query"] = interpQry

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

        # Once data section (key='Table') is found in result...
        valList = []

        # if dictionary key "Table" is found
        if "Table" in qData:
            cResponse = 'OK'

            #grab the records
            resLst = qData["Table"]

            for e in resLst:

                areasymbol = e[0]
                musym = e[1]
                muname = e[2]
                mukey = e[3]
                rating = e[4]
                class_name = e[5]
                reason = e[6]

                try:
                    rating = float(rating)
                except:
                    rating = None

                try:

                    parser = HTMLParser()
                    reason = parser.unescape(reason)

                except:
                    reason = reason


                #collect the results
                funcDict[mukey] = mukey, int(mukey), areasymbol, musym, muname, rating, class_name, reason

        return True, funcDict, cResponse



    except socket.timeout as e:
        Msg = 'Soil Data Access timeout error'
        return False, Msg, None

    except socket.error as e:
        Msg = 'Socket error: ' + str(e)
        return False, Msg, None

    except HTTPError as e:
        Msg = 'HTTP Error: ' + str(e)
        return False, Msg, None

    except URLError as e:
        Msg = 'URL Error: ' + str(e)
        return False, Msg, None

    except:
        errorMsg()
        Msg = 'Unknown error collecting interpreations for ' + eSSA
        return False, Msg, None

#===============================================================================

import arcpy, sys, os, traceback, time, urllib2, json
from HTMLParser import HTMLParser


arcpy.env.overwriteOutput = True


AddMsgAndPrint('\n \n')

areaParam = arcpy.GetParameterAsText(1)
aggMethod = arcpy.GetParameterAsText(3)
interpParam = arcpy.GetParameterAsText(4)
WS = arcpy.GetParameterAsText(5)
jLayer = arcpy.GetParameterAsText(6)
srcDir = os.path.dirname(sys.argv[0])

if aggMethod == 'Dominant Component':
    aggMod = '_dom_comp'
elif aggMethod == 'Dominant Condition':
    aggMod ='_dom_cond'
elif aggMethod == 'Weighted Average':
    aggMod = '_wtd_avg'
else:
    raise ForceExit('unable to determine aggregation method')
#AddMsgAndPrint(aggMethod)

try:

    areaList = areaParam.split(";")
    interpLst = interpParam.split(";")


    failInterps = list()

    jobCnt = len(areaList)*len(interpLst)

    n=0
    arcpy.SetProgressor('step', 'Starting Soil Data Access Dominant Component Tool...', 0, jobCnt, 1)

    #loop through the lists
    for interp in interpLst:
        compDict = dict()
        if interp.find("{:}") <> -1:
            interp = interp.replace("{:}", ";")

        for eSSA in areaList:
            n = n + 1
            arcpy.SetProgressorLabel('Collecting ' + interp + ' for: ' + eSSA + " (" + str(n) + ' of ' + str(jobCnt)+ ')')

            #send the request
            gI1, gI2, gI3 = getIntrps(interp, eSSA, aggMethod)

            #if it was successful...
            if gI1:
                if len(gI2) == 0:
                    AddMsgAndPrint('Response for ' + interp + ' on ' + eSSA + ' = ' + gI3)
                    AddMsgAndPrint('No records returned for ' + eSSA + ': ' + interp, 1)
                    failInterps.append(eSSA + ":" + interp)
                else:
                    AddMsgAndPrint('Response for ' + interp + ' on ' + eSSA + ' = ' + gI3)
                    for k,v in gI2.iteritems():
                            compDict[k] = v
                    arcpy.SetProgressorPosition()

            #if it was unsuccessful...
            else:
                #try again
                #AddMsgAndPrint('Failed first attempt running ' + interp + ' for ' + eSSA + '. Resubmitting request.', 1)
                gI1, gI2, gI3 = getIntrps(interp, eSSA, aggMethod)

                #if 2nd run was successful
                if gI1:
                    if len(gI2) == 0:
                        AddMsgAndPrint('No records returned for ' + eSSA + ': ' + interp, 1)
                        failInterps.append(eSSA + ":" + interp)
                    else:
                        AddMsgAndPrint('Response for ' + interp + ' on ' + eSSA + ' = ' + gI3 + ' - 2nd attempt')
                        for k,v in gI2.iteritems():
                            compDict[k] = v
                        arcpy.SetProgressorPosition()

                #if 2nd run was unsuccesful that's' it
                else:
                    AddMsgAndPrint(gI2)
                    failInterps.append(eSSA + ":" + interp)
                    arcpy.SetProgressorPosition()

        if len(compDict) > 0:
            #create the geodatabase output tables
            #clean up the interp rule name to use as output table name
            outTbl = arcpy.ValidateTableName(interp)
            outTbl = outTbl.replace("__", "_")
            tblName =  'tbl_' + outTbl + aggMod
            jTbl = WS + os.sep + 'tbl_' + outTbl + aggMod

            #fields list for cursor
            fldLst = ['MUKEY', 'int_MUKEY', 'areasymbol', 'musym', 'muname', 'rating', 'class', 'reason']

            #define the template table delivered with the tool
            template_table = srcDir + os.sep + 'templates.gdb' + os.sep + 'template_table'
            arcpy.management.CreateTable(WS, tblName, template_table)

            #populate the table
            cursor = arcpy.da.InsertCursor(jTbl, fldLst)

            for value in compDict:
                row = compDict.get(value)
                cursor.insertRow(row)

            del cursor
            del compDict

        else:
            AddMsgAndPrint('\n \nNo data returned for ' + interp)


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


    if len(failInterps) > 0:
        AddMsgAndPrint('\n \nThe following interpretations either failed or collected no records:', 1)
        for f in failInterps:
            AddMsgAndPrint(f)


    AddMsgAndPrint('\n \n')

except:
    errorMsg()

