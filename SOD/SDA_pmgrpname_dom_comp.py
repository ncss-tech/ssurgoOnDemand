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



def getPMgrp(areaSym, ordLst, dBool):

    import socket

    try:

        funcDict = dict()

        if dBool == "true":
            pmQry = "SELECT \n" \
            " sacatalog.areasymbol AS areasymbol, \n" \
            " mapunit.mukey AS mukey, \n" \
            " mapunit.musym AS musym,\n" \
            " mapunit.muname AS muname,\n" \
            " compname,\n" \
            " comppct_r , \n" \
            " \n" \
            " CASE WHEN pmgroupname LIKE '%Calcareous loess%' THEN 'Eolian Deposits (nonvolcanic)'\n" \
            " WHEN pmgroupname LIKE '%Eolian deposits%' THEN 'Eolian Deposits (nonvolcanic)'\n" \
            " WHEN pmgroupname LIKE '%Eolian sands%' THEN 'Eolian Deposits (nonvolcanic)'\n" \
            " WHEN pmgroupname LIKE '%Loess%' THEN 'Eolian Deposits (nonvolcanic)'\n" \
            " WHEN pmgroupname LIKE '%Noncalcareous loess%' THEN 'Eolian Deposits (nonvolcanic)'\n" \
            " WHEN pmgroupname LIKE '%Ablation till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Basal till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Cryoturbate%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Drift%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Flow till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Glaciofluvial deposits%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Glaciolacustrine deposits%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Glaciomarine deposits%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Lodgment till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Melt-out till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Outwash%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Solifluction deposits%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Subglacial till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Supraglacial meltout till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Supraglacial till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Till%' THEN 'Glacial and Periglacial Deposits'\n" \
            " WHEN pmgroupname LIKE '%Bauxite%' THEN 'In-Place Deposits (nontransported)'\n" \
            " WHEN pmgroupname LIKE '%Grus%' THEN 'In-Place Deposits (nontransported)'\n" \
            " WHEN pmgroupname LIKE '%Residuum%' THEN 'In-Place Deposits (nontransported)'\n" \
            " WHEN pmgroupname LIKE '%Saprolite%' THEN 'In-Place Deposits (nontransported)'\n" \
            " WHEN pmgroupname LIKE '%Colluvium%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Complex landslide deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Creep deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Debris avalanche deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Debris flow deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Debris slide deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Debris spread deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Debris topple deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Earth spread deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Earthflow deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Flow deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Lateral spread deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Mass movement deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Mudflow deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Rock spread deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Rock topple deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Rockfall avalanche deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Rockfall deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Rotational earth slide deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Rotational slide deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Sand flow deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Scree%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Slide deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Talus%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Topple deposits%' THEN 'Mass Movement Deposits'\n" \
            " WHEN pmgroupname LIKE '%Diamicton%' THEN 'Miscellaneous Deposits'\n" \
            " WHEN pmgroupname LIKE '%mixed%' THEN 'Miscellaneous Deposits'\n" \
            " WHEN pmgroupname LIKE '%Coprogenic material%' THEN 'Organic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Grassy organic material%' THEN 'Organic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Herbaceous organic material%' THEN 'Organic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Mossy organic material%' THEN 'Organic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Organic material%' THEN 'Organic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Woody organic material%' THEN 'Organic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Acidic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Andesitic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Ash flow%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Basaltic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Basic volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Cinders%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Lahar deposits%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Pumice%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Pyroclastic flow%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Pyroclastic surge%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Scoria%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Tephra%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%tuff%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%tuff-breccia%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Volcanic ash%' THEN 'Volcanic Deposits (unconsolidated; eolian and mass movement)'\n" \
            " WHEN pmgroupname LIKE '%Alluvium%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Backswamp deposits%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Beach sand%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Diatomaceous earth%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Estuarine deposits%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Fluviomarine deposits%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Greensands%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Lacustrine deposits%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Lagoonal deposits%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Marine deposits%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Marl%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Overbank deposits%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Pedisediment%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Slope alluvium%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Valley side alluvium%' THEN 'Waterlaid (or Transported) Deposits'\n" \
            " WHEN pmgroupname LIKE '%Coal extraction mine spoil%' THEN 'Anthropogenic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Dredge spoils%' THEN 'Anthropogenic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Human-transported material%' THEN 'Anthropogenic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Metal ore extraction mine spoil%' THEN 'Anthropogenic Deposits'\n" \
            " WHEN pmgroupname LIKE '%Mine spoil or earthy fill%' THEN 'Anthropogenic Deposits'\n" \
            " WHEN pmgroupname LIKE '%aa%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%breccia-basic%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%conglomerate%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%dolomite%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%igneous%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%limestone%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%limestone-shale%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%metamorphic%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%quartzite%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%sandstone%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%sedimentary%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%serpentine%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%shale%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%shale-calcareous%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%siltstone%' THEN 'Miscoded - should be pmorigin'\n" \
            " WHEN pmgroupname LIKE '%NULL%' THEN 'NULL' ELSE 'NULL' END AS pmgroupname\n" \
            " \n" \
            " \n" \
            " FROM sacatalog \n" \
            " INNER JOIN legend  ON legend.areasymbol = sacatalog.areasymbol AND sacatalog.areasymbol = '" + areaSym + "'\n" \
            " INNER JOIN mapunit  ON mapunit.lkey = legend.lkey\n" \
            " INNER JOIN component AS c ON c.mukey = mapunit.mukey AND c.cokey =\n" \
            " (SELECT TOP 1 c1.cokey FROM component AS c1 \n" \
            " INNER JOIN mapunit AS mu1 ON c1.mukey=mu1.mukey AND c1.mukey=mapunit.mukey ORDER BY c1.comppct_r DESC, c1.cokey ) \n" \
            " INNER JOIN copmgrp ON copmgrp.cokey=c.cokey\n"

        else:

            pmQry = "SELECT \n" \
            " sacatalog.areasymbol AS areasymbol, \n" \
            " mapunit.mukey AS mukey, \n" \
            " mapunit.musym AS musym,\n" \
            " mapunit.muname AS muname,\n" \
            " compname,\n" \
            " comppct_r,\n" \
            " pmgroupname" \
            " \n" \
            " FROM sacatalog \n" \
            " INNER JOIN legend  ON legend.areasymbol = sacatalog.areasymbol AND sacatalog.areasymbol = '" + areaSym + "'\n" \
            " INNER JOIN mapunit  ON mapunit.lkey = legend.lkey\n" \
            " INNER JOIN component AS c ON c.mukey = mapunit.mukey AND c.cokey =\n" \
            " (SELECT TOP 1 c1.cokey FROM component AS c1 \n" \
            " INNER JOIN mapunit AS mu1 ON c1.mukey=mu1.mukey AND c1.mukey=mapunit.mukey ORDER BY c1.comppct_r DESC, c1.cokey ) \n" \
            " INNER JOIN copmgrp ON copmgrp.cokey=c.cokey"


        #arcpy.AddMessage(pmQry)

        #send the soap request
        sXML = """<?xml version="1.0" encoding="utf-8"?>
                <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                <RunQuery xmlns="http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx">
                  <Query>""" + pmQry + """</Query>
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
dBool = arcpy.GetParameterAsText(2)
WS = arcpy.GetParameterAsText(3)
jLayer = arcpy.GetParameterAsText(4)

#arcpy.AddMessage(nullParam)
srcDir = os.path.dirname(sys.argv[0])

ordLst = ['areasymbol', 'mukey', 'musym', 'muname', 'compname', 'comppct_r', 'pmgroupname']

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
        gP1, gP2, gP3 = getPMgrp(eSSA, ordLst, dBool)

        #if it was successful...
        if gP1:
            if len(gP2) == 0:
                AddMsgAndPrint('No records returned for ' + eSSA, 1)
                failPM.append(eSSA )
                arcpy.SetProgressorPosition()
            else:
                AddMsgAndPrint('Response for parent material table request on ' + eSSA + ' = ' + gP3)
                for k,v in gP2.iteritems():
                    compDict[k] = v
                arcpy.SetProgressorPosition()

        #if it was unsuccessful...
        else:
            #try again
            gP1, gP2, gP3 = getPMgrp(eSSA, ordLst, dBool)

            #if 2nd run was successful
            if gP1:
                if len(gP2) == 0:
                    AddMsgAndPrint('No records returned for ' + eSSA , 1)
                    failPM.append(eSSA )
                    arcpy.SetProgressorPosition()
                else:
                    AddMsgAndPrint('Response for parent material table request on '  + eSSA + ' = ' + gP3 + ' - 2nd attempt')
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
        tblName = "SOD_pmgrpname"

        jTbl = WS + os.sep  + tblName

        #fields list for cursor
        fldLst = ['AREASYMBOL', 'MUKEY', 'int_MUKEY', 'MUSYM', 'MUNAME', 'COMPNAME', 'COMPPCT_R', 'PARENT_MATERIAL']


        #define the template table delivered with the tool
        template_table = srcDir + os.sep + 'templates.gdb' + os.sep + 'pmgrp_template'

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

