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

def getMuaggatt(aSym, ordLst):

    import socket

    funcDict = dict()

    try:

        muaggatQry = \
        """SELECT ma.musym,ma.muname,ma.mustatus,ma.slopegraddcp,ma.slopegradwta,ma.brockdepmin,ma.wtdepannmin,ma.wtdepaprjunmin,ma.flodfreqdcd,ma.flodfreqmax,ma.pondfreqprs,ma.aws025wta,ma.aws050wta,ma.aws0100wta,
        ma.aws0150wta,ma.drclassdcd,ma.drclasswettest,ma.hydgrpdcd,ma.iccdcd,ma.iccdcdpct,ma.niccdcd,ma.niccdcdpct,ma.engdwobdcd,ma.engdwbdcd,ma.engdwbll,ma.engdwbml,ma.engstafdcd,ma.engstafll,ma.engstafml,ma.engsldcd,ma.engsldcp,
        ma.englrsdcd,ma.engcmssdcd,ma.engcmssmp,ma.urbrecptdcd,ma.urbrecptwta,ma.forpehrtdcp,ma.hydclprs,ma.awmmfpwwta,ma.mukey
        FROM legend
        INNER JOIN mapunit ON mapunit.lkey=legend.lkey
        INNER JOIN muaggatt ma ON mapunit.mukey=ma.mukey
        WHERE areasymbol = '""" + aSym + """'"""

        print muaggatQry

        #theURL = "https://sdmdataaccess.nrcs.usda.gov"
        #url = theURL + "/Tabular/SDMTabularService/post.rest"

        url = r'https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest'

        # Create request using JSON, return data as JSON
        request = {}
        request["format"] = "JSON"
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
        print cResponse

        # read query results
        qResults = response.read()

        # Convert the returned JSON string into a Python dictionary.
        qData = json.loads(qResults)

        print qData

        # get rid of objects
        del qResults, response, req


        # if dictionary key "Table" is found
        if "Table" in qData:


            # get its value
            # a list of lists
            resLst = qData["Table"]

         #containers

            #the ordLst is the order of the list returned from SDA.  This allows us to step through each returned list/row
            #and convert to appropriate data type
            ordLst = ['musym', 'muname', 'mustatus', 'slopegraddcp', 'slopegradwta', 'brockdepmin', 'wtdepannmin', 'wtdepaprjunmin', 'flodfreqdcd', 'flodfreqmax', 'pondfreqprs', 'aws025wta', 'aws050wta', 'aws0100wta', 'aws0150wta', 'drclassdcd', 'drclasswettest', 'hydgrpdcd', 'iccdcd', 'iccdcdpct', 'niccdcd', 'niccdcdpct', 'engdwobdcd', 'engdwbdcd', 'engdwbll', 'engdwbml', 'engstafdcd', 'engstafll', 'engstafml', 'engsldcd', 'engsldcp', 'englrsdcd', 'engcmssdcd', 'engcmssmp', 'urbrecptdcd', 'urbrecptwta', 'forpehrtdcp', 'hydclprs', 'awmmfpwwta', 'mukey']
            fltFlds = ['slopegraddcp', 'slopegradwta', 'aws025wta', 'aws050wta', 'aws0100wta', 'aws0150wta', 'urbrecptwta', 'awmmfpwwta']
            strFlds = ['musym', 'muname', 'mustatus', 'flodfreqdcd', 'flodfreqmax', 'pondfreqprs', 'drclassdcd', 'drclasswettest', 'hydgrpdcd', 'iccdcd', 'niccdcd', 'engdwobdcd', 'engdwbdcd', 'engdwbll', 'engdwbml', 'engstafdcd', 'engstafll', 'engstafml', 'engsldcd', 'engsldcp', 'englrsdcd', 'engcmssdcd', 'engcmssmp', 'urbrecptdcd', 'forpehrtdcp', 'hydclprs', 'mukey']
            intFlds = ['brockdepmin', 'wtdepannmin', 'wtdepaprjunmin', 'iccdcdpct', 'niccdcdpct']



            for tblRow in resLst:
                convertedList = list()
                position = 0

                # element corresponds to field
                # for field in the row
                for element in tblRow:

                    # get the field name coresponding to position in ordLst
                    eleName = ordLst[position]

                    if eleName in strFlds:
                            if str(element):
                                element = element
                            else:
                                element = None

                    if eleName in fltFlds:
                        try:
                            element = float(element)
                        except:
                            element = None

                    if eleName in intFlds:
                        try:
                            element = int(element)
                        except:
                            element = None

                    convertedList.append(element)
                    position+=1



                #put the list for each mapunit into a dictionary.  dict keys are mukeys.
                funcDict[convertedList[-1]]= convertedList

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

