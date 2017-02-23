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



def getHyd(areaSym):

    import socket

    funcDict = dict()

    try:
        #fldLst = ['AREASYMBOL', 'MUKEY', 'int_MUKEY', 'MUSYM', 'MUNAME', 'HYDRIC_RATING']

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
        INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND  l.areasymbol LIKE '"""+ areaSym + """'


        SELECT  AREASYMBOL, MUKEY, MUSYM, MUNAME,
        CASE WHEN comp_count = all_not_hydric + hydric_null THEN  'Nonhydric'
        WHEN comp_count = all_hydric  THEN 'Hydric'
        WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 'Predominantly Hydric'
        WHEN hydric_inclusions &gt;= 0.5 AND  maj_hydric &lt; 0.5 THEN  'Predominantly Nonhydric'
        WHEN maj_not_hydric &gt;= 0.5  AND  maj_hydric &gt;= 0.5 THEN 'Partially Hydric' ELSE 'Error' END AS HYDRIC_RATING
        FROM #main_query"""

        #print hydQry.replace("&gt;", ">").replace("&lt;", "<")
        hydQry = hydQry.replace("&gt;", ">").replace("&lt;", "<")

        theURL = "https://sdmdataaccess.nrcs.usda.gov"
        url = theURL + "/Tabular/SDMTabularService/post.rest"

        # Create request using JSON, return data as JSON
        request = {}
        request["FORMAT"] = "JSON"
        request["QUERY"] = hydQry

        #json.dumps = serialize obj (request dictionary) to a JSON formatted str
        data = json.dumps(request)

        # Send request to SDA Tabular service using urllib2 library
        # because we are passing the "data" argument, this is a POST request, not a GET
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)

        code = response.getcode()
        cResponse = bhrh.responses.get(code)
        cResponse = "{}; {}".format(cResponse[0], cResponse[1])
        print cResponse

        # read query results
        qResults = response.read()

        # Convert the returned JSON string into a Python dictionary.
        qData = json.loads(qResults)

        #print qData

        # get rid of objects
        del qResults, response, req


        # if dictionary key "Table" is found
        if "Table" in qData:


            # get its value
            # a list of lists
            resLst = qData["Table"]

            for res in resLst:
                #insert integer copy of mukey into list at position 3
                res.insert(2, int(res[1]))


                #put the list for each mapunit into a dictionary.  dict keys are mukeys.
                funcDict[res[1]] = res

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

import arcpy, sys, os, traceback, time, httplib, urllib2, json
from BaseHTTPServer import BaseHTTPRequestHandler as bhrh

arcpy.env.overwriteOutput = True


AddMsgAndPrint('\n \n')

areaParam = arcpy.GetParameterAsText(1)
WS = arcpy.GetParameterAsText(2)
jLayer = arcpy.GetParameterAsText(3)

#arcpy.AddMessage(nullParam)
srcDir = os.path.dirname(sys.argv[0])

#ordLst = ['AREASYMBOL', 'MUKEY', 'MUSYM', 'MUNAME', 'HYDRIC_RATING']

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
        gP1, gP2, gP3 = getHyd(eSSA)

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
            gP1, gP2, gP3 = getHyd(eSSA)

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

