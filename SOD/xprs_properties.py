#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Charles.Ferguson
#
# Created:     19/07/2016
# Copyright:   (c) Charles.Ferguson 2016
# Licence:     <your licence>

# Electrial Conductivity 1:5 by volume - Rep Value was removed, exists in rslvProp, just remoed from validator
# Exchangeable Sodium Percentage - Rep Value was removed, exists in rslvProp, just remoed from validator
# Ki ditto
# Kr ditto
# Unrubber Fiber % - Rep Value
# Rubbed Fiber % - Rep Value
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

def rslvProps(aProp):
    try:

        #propDict = {'Wind Erodibility Index': 'wei', 'Wind Erodibility Group' : 'weg', 'Drainage Class' : 'drainagecl', 'Hydrologic Group' : 'hydgrp', 'Corrosion of Steel' : 'corsteel', 'Corrosion of Steel' : 'corsteel', 'Taxonomic Class Name' : 'taxclname', 'Taxonomic Suborder' : 'taxsuborder', 'Taxonomic Order' : 'taxorder', 'Taxonomic Temperature Regime' : 'taxtempregime', 't Factor' : 'tfact', 'Cation Exchange Capcity - Rep Value': 'cec7_r', 'CaCO3 Clay - High': 'claysizedcarb_h', 'Coarse Silt - Low': 'siltco_l', 'Total Rock Fragment Volume - Rep Value': 'fragvoltot_r', 'Water Soluble Phosphate - Rep Value': 'ph2osoluble_r', 'Sum of Bases - High': 'sumbases_h', 'Available Water Capacity - Low': 'awc_l', 'Fine Sand - Low': 'sandfine_l', 'Extractable Acidity - High': 'extracid_h', 'CaCO3 Clay - Rep Value': 'claysizedcarb_r', 'pH Oxidized - Rep Value': 'phoxidized_r', 'Oxalate Aluminum - Low': 'aloxalate_l', 'Coarse Sand - Rep Value': 'sandco_r', 'no. 4 sieve - Low': 'sieveno4_l', 'Bulk Density 15 bar H2O - High': 'dbfifteenbar_h', 'Electrical Conductivity - Rep Value': 'ec_r', 'Calcium Carbonate - Low': 'caco3_l', 'Bulk Density 0.33 bar H2O - Low': 'dbthirdbar_l', 'Rock Fragments 3 - 10 cm- Rep Value': 'frag3to10_r', 'Bray 1 Phosphate - High': 'pbray1_h', 'pH Oxidized - Low': 'phoxidized_l', 'Exchangeable Sodium Percentage - Rep Value': 'esp_r', 'Sodium Adsorption Ratio - Rep Value': 'sar_r', 'no. 4 sieve - High': 'sieveno4_h', 'Medium Sand - Low': 'sandmed_l', 'Bulk Density 15 bar H2O - Rep Value': 'dbfifteenbar_r', 'Effective Cation Exchange Capcity - Rep Value': 'ecec_r', 'pH Oxidized - High': 'phoxidized_h', 'Rock Fragments 3 - 10 cm- High': 'frag3to10_h', 'Oxalate Iron - Low': 'feoxalate_l', 'Free Iron - High': 'freeiron_h', 'Total Rock Fragment Volume - High': 'fragvoltot_h', 'Fine Sand - High': 'sandfine_h', 'Total Sand - High': 'sandtotal_h', 'Liquid Limit - Low': 'll_l', 'Organic Matter - Rep Value': 'om_r', 'Coarse Sand - High': 'sandco_h', 'Very Fine Sand - Low': 'sandvf_l', 'Oxalate Iron - Rep Value': 'feoxalate_r', 'Very Coarse Sand - Low': 'sandvc_l', 'Total Silt - Rep Value': 'silttotal_r', 'Liquid Limit - High': 'll_h', 'Saturated Hydraulic Conductivity - High': 'ksat_h', 'no. 40 sieve - Rep Value': 'sieveno40_r', 'Extract Aluminum - High': 'extral_h', 'no. 40 sieve - High': 'sieveno40_h', 'Kr ': 'krfact', 'Coarse Sand - Low': 'sandco_l', 'Sum of Bases - Rep Value': 'sumbases_r', 'Organic Matter - High': 'om_h', 'no. 10 sieve - Rep Value': 'sieveno10_r', 'Total Silt - High': 'silttotal_h', 'Saturated Hydraulic Conductivity - Low': 'ksat_l', 'Calcium Carbonate - Rep Value': 'caco3_r', 'pH .01M CaCl2 - Rep Value': 'ph01mcacl2_r', 'Bulk Density 15 bar H2O - Low': 'dbfifteenbar_l', 'Sodium Adsorption Ratio - Low': 'sar_l', 'Gypsum - High': 'gypsum_h', 'Rubbed Fiber % - Rep Value': 'fiberrubbedpct_r', 'CaCO3 Clay - Low': 'claysizedcarb_l', 'Electrial Conductivity 1:5 by volume - Rep Value': 'ec15_r', 'Satiated H2O - Rep Value': 'wsatiated_r', 'Medium Sand - High': 'sandmed_h', 'Bulk Density oven dry - Rep Value': 'dbovendry_r', 'Plasticity Index - Low': 'pi_l', 'Extractable Acidity - Rep Value': 'extracid_r', 'Oxalate Aluminum - Rep Value': 'aloxalate_r', 'Medium Sand - Rep Value': 'sandmed_r', 'Total Rock Fragment Volume - Low': 'fragvoltot_l', 'pH 1:1 water - Low': 'ph1to1h2o_l', 'no. 10 sieve - Low': 'sieveno10_l', 'Very Coarse Sand - Rep Value': 'sandvc_r', 'Gypsum - Low': 'gypsum_l', 'Plasticity Index - High': 'pi_h', 'Total Phosphate - High': 'ptotal_h', 'Unrubbed Fiber % - Rep Value': 'fiberunrubbedpct_r', 'Bulk Density 0.1 bar H2O - High': 'dbtenthbar_h', 'Cation Exchange Capcity - Low': 'cec7_l', '0.33 bar H2O - Rep Value': 'wthirdbar_r', '0.1 bar H2O - Low': 'wtenthbar_l', 'Bulk Density 0.1 bar H2O - Rep Value': 'dbtenthbar_r', 'no. 40 sieve - Low': 'sieveno40_l', 'Extract Aluminum - Low': 'extral_l', 'Calcium Carbonate - High': 'caco3_h', 'Water Soluble Phosphate - Low': 'ph2osoluble_l', 'Gypsum - Rep Value': 'gypsum_r', '0.33 bar H2O - High': 'wthirdbar_h', 'Bray 1 Phosphate - Low': 'pbray1_l', 'Available Water Capacity - Rep Value': 'awc_r', 'Rubbed Fiber % - High': 'fiberrubbedpct_h', 'Coarse Silt - Rep Value': 'siltco_r', '0.1 bar H2O - High': 'wtenthbar_h', 'Plasticity Index - Rep Value': 'pi_r', 'Extract Aluminum - Rep Value': 'extral_r', 'Fine Sand - Rep Value': 'sandfine_r', 'Fine Silt - Low': 'siltfine_l', 'Bulk Density oven dry - High': 'dbovendry_h', 'Total Clay - High': 'claytotal_h', 'Fine Silt - High': 'siltfine_h', 'Exchangeable Sodium Percentage - High': 'esp_h', 'Total Clay - Low': 'claytotal_l', 'Bulk Density 0.33 bar H2O - High': 'dbthirdbar_h', 'Total Phosphate - Low': 'ptotal_l', 'Cation Exchange Capcity - High': 'cec7_h', '15 bar H2O - Low': 'wfifteenbar_l', 'no. 10 sieve - High': 'sieveno10_h', 'Extractable Acidity - Low': 'extracid_l', 'Electrical Conductivity - High': 'ec_h', 'Oxalate Phosphate - Low': 'poxalate_l', 'Electrial Conductivity 1:5 by volume - High': 'ec15_h', 'Sodium Adsorption Ratio - High': 'sar_h', 'Liquid Limit - Rep Value': 'll_r', '0.33 bar H2O - Low': 'wthirdbar_l', 'Satiated H2O - High': 'wsatiated_h', 'Bulk Density 0.33 bar H2O - Rep Value': 'dbthirdbar_r', '15 bar H2O - Rep Value': 'wfifteenbar_r', '15 bar H2O - High': 'wfifteenbar_h', 'no. 200 sieve - Low': 'sieveno200_l', 'LEP - Low': 'lep_l', 'Satiated H2O - Low': 'wsatiated_l', 'Total Clay - Rep Value': 'claytotal_r', 'Very Fine Sand - High': 'sandvf_h', 'Available Water Capacity - High': 'awc_h', 'Total Phosphate - Rep Value': 'ptotal_r', 'Electrical Conductivity - Low': 'ec_l', 'Oxalate Aluminum - High': 'aloxalate_h', 'Effective Cation Exchange Capcity - High': 'ecec_h', 'Rubbed Fiber % - Low': 'fiberrubbedpct_l', 'Coarse Silt - High': 'siltco_h', 'Bulk Density oven dry - Low': 'dbovendry_l', 'no. 4 sieve - Rep Value': 'sieveno4_r', 'Bray 1 Phosphate - Rep Value': 'pbray1_r', 'no. 200 sieve - High': 'sieveno200_h', '0.1 bar H2O - Rep Value': 'wtenthbar_r', 'Unrubbed Fiber % - Low': 'fiberunrubbedpct_l', 'pH .01M CaCl2 - Low': 'ph01mcacl2_l', 'Saturated Hydraulic Conductivity - Rep Value': 'ksat_r', 'Kw ': 'kwfact', 'Unrubbed Fiber % - High': 'fiberunrubbedpct_h', 'Rock Fragments > 10 cm - High': 'fraggt10_h', 'Kf': 'kffact', 'no. 200 sieve - Rep Value': 'sieveno200_r', 'pH .01M CaCl2 - High': 'ph01mcacl2_h', 'Oxalate Phosphate - Rep Value': 'poxalate_r', 'Rock Fragments 3 - 10 cm- Low': 'frag3to10_l', 'Water Soluble Phosphate - High': 'ph2osoluble_h', 'Very Fine Sand - Rep Value': 'sandvf_r', 'Electrial Conductivity 1:5 by volume - Low': 'ec15_l', 'Total Silt - Low': 'silttotal_l', 'Total Sand - Low': 'sandtotal_l', 'Organic Matter - Low': 'om_l', 'Fine Silt - Rep Value': 'siltfine_r', 'Very Coarse Sand - High': 'sandvc_h', 'Free Iron - Low': 'freeiron_l', 'Rock Fragments > 10 cm - Rep Value': 'fraggt10_r', 'LEP - High': 'lep_h', 'pH 1:1 water - High': 'ph1to1h2o_h', 'Oxalate Phosphate - High': 'poxalate_h', 'Total Sand - Rep Value': 'sandtotal_r', 'Oxalate Iron - High': 'feoxalate_h', 'Rock Fragments > 10 cm - Low': 'fraggt10_l', 'Sum of Bases - Low': 'sumbases_l', 'Free Iron - Rep Value': 'freeiron_r', 'LEP - Rep Value': 'lep_r', 'Effective Cation Exchange Capcity - Low': 'ecec_l', 'pH 1:1 water - Rep Value': 'ph1to1h2o_r', 'Exchangeable Sodium Percentage - Low': 'esp_l', 'Ki ': 'kifact', 'Bulk Density 0.1 bar H2O - Low': 'dbtenthbar_l'}
        propDict = {'0.1 bar H2O - Rep Value' : 'wtenthbar_r', '0.33 bar H2O - Rep Value' : 'wthirdbar_r', '15 bar H2O - Rep Value' : 'wfifteenbar_r', 'Available Water Capacity - Rep Value' : 'awc_r', 'Bray 1 Phosphate - Rep Value' : 'pbray1_r', 'Bulk Density 0.1 bar H2O - Rep Value' : 'dbtenthbar_r', 'Bulk Density 0.33 bar H2O - Rep Value' : 'dbthirdbar_r', 'Bulk Density 15 bar H2O - Rep Value' : 'dbfifteenbar_r', 'Bulk Density oven dry - Rep Value' : 'dbovendry_r', 'CaCO3 Clay - Rep Value' : 'claysizedcarb_r', 'Calcium Carbonate - Rep Value' : 'caco3_r', 'Cation Exchange Capcity - Rep Value' : 'cec7_r', 'Coarse Sand - Rep Value' : 'sandco_r', 'Coarse Silt - Rep Value' : 'siltco_r', 'Corrosion of Steel' : 'corsteel', 'Corrosion of Concrete' : 'corcon', 'Drainage Class' : 'drainagecl', 'Effective Cation Exchange Capcity - Rep Value' : 'ecec_r', 'Electrial Conductivity 1:5 by volume - Rep Value' : 'ec15_r', 'Electrical Conductivity - Rep Value' : 'ec_r', 'Exchangeable Sodium Percentage - Rep Value' : 'esp_r', 'Extract Aluminum - Rep Value' : 'extral_r', 'Extractable Acidity - Rep Value' : 'extracid_r', 'Fine Sand - Rep Value' : 'sandfine_r', 'Fine Silt - Rep Value' : 'siltfine_r', 'Free Iron - Rep Value' : 'freeiron_r', 'Gypsum - Rep Value' : 'gypsum_r', 'Hydrologic Group' : 'hydgrp', 'Kf' : 'kffact', 'Ki ' : 'kifact', 'Kr ' : 'krfact', 'Kw ' : 'kwfact', 'LEP - Rep Value' : 'lep_r', 'Liquid Limit - Rep Value' : 'll_r', 'Medium Sand - Rep Value' : 'sandmed_r', 'Organic Matter - Rep Value' : 'om_r', 'Oxalate Aluminum - Rep Value' : 'aloxalate_r', 'Oxalate Iron - Rep Value' : 'feoxalate_r', 'Oxalate Phosphate - Rep Value' : 'poxalate_r', 'Plasticity Index - Rep Value' : 'pi_r', 'Rock Fragments 3 - 10 cm - Rep Value' : 'frag3to10_r', 'Rock Fragments > 10 cm - Rep Value' : 'fraggt10_r', 'Rubbed Fiber % - Rep Value' : 'fiberrubbedpct_r', 'Satiated H2O - Rep Value' : 'wsatiated_r', 'Saturated Hydraulic Conductivity - Rep Value' : 'ksat_r', 'Sodium Adsorption Ratio - Rep Value' : 'sar_r', 'Sum of Bases - Rep Value' : 'sumbases_r', 'Taxonomic Class Name' : 'taxclname', 'Taxonomic Order' : 'taxorder', 'Taxonomic Suborder' : 'taxsuborder', 'Taxonomic Temperature Regime' : 'taxtempregime', 'Total Clay - Rep Value' : 'claytotal_r', 'Total Phosphate - Rep Value' : 'ptotal_r', 'Total Rock Fragment Volume - Rep Value' : 'fragvoltot_r', 'Total Sand - Rep Value' : 'sandtotal_r', 'Total Silt - Rep Value' : 'silttotal_r', 'Unrubbed Fiber % - Rep Value' : 'fiberunrubbedpct_r', 'Very Coarse Sand - Rep Value' : 'sandvc_r', 'Very Fine Sand - Rep Value' : 'sandvf_r', 'Water Soluble Phosphate - Rep Value' : 'ph2osoluble_r', 'Wind Erodibility Group' : 'weg', 'Wind Erodibility Index' : 'wei', 'no. 10 sieve - Rep Value' : 'sieveno10_r', 'no. 200 sieve - Rep Value' : 'sieveno200_r', 'no. 4 sieve - Rep Value' : 'sieveno4_r', 'no. 40 sieve - Rep Value' : 'sieveno40_r', 'pH .01M CaCl2 - Rep Value' : 'ph01mcacl2_r', 'pH 1:1 water - Rep Value' : 'ph1to1h2o_r', 'pH Oxidized - Rep Value' : 'phoxidized_r', 't Factor' : 'tfact'}
        propVal = propDict.get(aProp)

        return propVal

    except:
        errorMsg()


def geoRequest(aoi):

     try:

        if descWsType == '':
            geoExt = '.shp'
        else:
            geoExt = ''

        sr = arcpy.SpatialReference(4326)
        arcpy.management.CreateFeatureclass(outLoc, "SSURGO_express_properties" + geoExt, "POLYGON", None, None, None, sr)
        arcpy.management.AddField(outLoc + os.sep + "SSURGO_express_properties" + geoExt, "mukey", "TEXT", None, None, "30")

        gQry = """ --   Define a AOI in WGS84
        ~DeclareGeometry(@aoi)~
        select @aoi = geometry::STPolyFromText('polygon(( """ + aoi + """))', 4326)\n

        --   Extract all intersected polygons
        ~DeclareIdGeomTable(@intersectedPolygonGeometries)~
        ~GetClippedMapunits(@aoi,polygon,geo,@intersectedPolygonGeometries)~

        --   Convert geometries to geographies so we can get areas
        ~DeclareIdGeogTable(@intersectedPolygonGeographies)~
        ~GetGeogFromGeomWgs84(@intersectedPolygonGeometries,@intersectedPolygonGeographies)~

        --   Return the polygonal geometries
        select * from @intersectedPolygonGeographies
        where geog.STGeometryType() = 'Polygon'"""

        #uncomment next line to print geoquery
        #arcpy.AddMessage(gQry)

        theURL = "https://sdmdataaccess.nrcs.usda.gov"
        url = theURL + "/Tabular/SDMTabularService/post.rest"

        arcpy.AddMessage('Sending coordinates to Soil Data Access...\n')

        # Create request using JSON, return data as JSON
        request = {}
        request["FORMAT"] = "JSON"
        request["QUERY"] = gQry

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
            resLst = qData["Table"]  # Data as a list of lists. All values come back as string.

##        #msg =  "Geometry Response time = {}\n".format((time.time() - startTime))[:-6]
##        if cStatus == 200:
##            msg = "AOI collected successfully"
##            arcpy.AddMessage(msg + '\n')
##        else:
##            msg = "Error collecting AOI: " + str(cStatus) + "=" + cResponse
##            return False, msg



        rows =  arcpy.da.InsertCursor(outLoc + os.sep + "SSURGO_express_properties" + geoExt, ["SHAPE@WKT", "mukey"])

        keyList = list()

        for e in resLst:

            mukey = e[0]
            geog = e[1]

            if not mukey in keyList:
                keyList.append(mukey)

            value = geog, mukey
            rows.insertRow(value)

        arcpy.AddMessage('\nReceived SSURGO polygon information successfully.\n')

        return True, keyList

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




def tabRequest(aProp):

    #import socket
    arcpy.AddMessage('Fetching data for ' + prop + '...')

    try:

        if aggMethod == "Dominant Component (Category)":
            pQry = "SELECT areasymbol, musym, muname, mu.mukey  AS mukey, " + aProp + " AS " + aProp + "\n"\
            " FROM legend  AS l\n"\
            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey\n\n"\
            " AND mu.mukey IN (" + keys + ")\n"\
            " INNER JOIN component AS c ON c.mukey = mu.mukey\n\n"\
            " AND c.cokey =\n"\
            " (SELECT TOP 1 c1.cokey FROM component AS c1\n"\
            " INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)"
        elif aggMethod == "Weighted Average":
            pQry = "SELECT areasymbol, musym, muname, mukey\n"\
            " INTO #kitchensink\n"\
            " FROM legend  AS lks\n"\
            " INNER JOIN  mapunit AS muks ON muks.lkey = lks.lkey AND muks.mukey IN (" + keys + ")\n"\
            " SELECT mu1.mukey, cokey, comppct_r,"\
            " SUM (comppct_r) over(partition by mu1.mukey ) AS SUM_COMP_PCT\n"\
            " INTO #comp_temp\n"\
            " FROM legend  AS l1\n"\
            " INNER JOIN  mapunit AS mu1 ON mu1.lkey = l1.lkey AND mu1.mukey IN (" + keys + ")\n"\
            " INNER JOIN  component AS c1 ON c1.mukey = mu1.mukey AND majcompflag = 'Yes'\n"\
            " SELECT cokey, SUM_COMP_PCT, CASE WHEN comppct_r = SUM_COMP_PCT THEN 1\n"\
            " ELSE CAST (CAST (comppct_r AS  decimal (5,2)) / CAST (SUM_COMP_PCT AS decimal (5,2)) AS decimal (5,2)) END AS WEIGHTED_COMP_PCT\n"\
            " INTO #comp_temp3\n"\
            " FROM #comp_temp\n"\
            " SELECT\n"\
            " areasymbol, musym, muname, mu.mukey/1  AS MUKEY, c.cokey AS COKEY, ch.chkey/1 AS CHKEY, compname, hzname, hzdept_r, hzdepb_r, CASE WHEN hzdept_r <" + tDep + "  THEN " + tDep + " ELSE hzdept_r END AS hzdept_r_ADJ,\n"\
            " CASE WHEN hzdepb_r > " + bDep + "  THEN " + bDep + " ELSE hzdepb_r END AS hzdepb_r_ADJ,\n"\
            " CAST (CASE WHEN hzdepb_r > " +bDep + "  THEN " +bDep + " ELSE hzdepb_r END - CASE WHEN hzdept_r <" + tDep + " THEN " + tDep + " ELSE hzdept_r END AS decimal (5,2)) AS thickness,\n"\
            " comppct_r,\n"\
            " CAST (SUM (CASE WHEN hzdepb_r > " + bDep + "  THEN " + bDep + " ELSE hzdepb_r END - CASE WHEN hzdept_r <" + tDep + " THEN " + tDep + " ELSE hzdept_r END) over(partition by c.cokey) AS decimal (5,2)) AS sum_thickness,\n"\
            " CAST (ISNULL (" + aProp + ", 0) AS decimal (5,2))AS " + aProp +\
            " INTO #main"\
            " FROM legend  AS l\n"\
            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND mu.mukey IN (" + keys + ")\n"\
            " INNER JOIN  component AS c ON c.mukey = mu.mukey\n"\
            " INNER JOIN chorizon AS ch ON ch.cokey=c.cokey AND hzname NOT LIKE '%O%'AND hzname NOT LIKE '%r%'\n"\
            " AND hzdepb_r >" + tDep + " AND hzdept_r <" + bDep + ""\
            " INNER JOIN chtexturegrp AS cht ON ch.chkey=cht.chkey  WHERE cht.rvindicator = 'yes' AND  ch.hzdept_r IS NOT NULL\n"\
            " AND texture NOT LIKE '%PM%' and texture NOT LIKE '%DOM' and texture NOT LIKE '%MPT%' and texture NOT LIKE '%MUCK' and texture NOT LIKE '%PEAT%' and texture NOT LIKE '%br%' and texture NOT LIKE '%wb%'\n"\
            " ORDER BY areasymbol, musym, muname, mu.mukey, comppct_r DESC, cokey,  hzdept_r, hzdepb_r\n"\
            " SELECT #main.areasymbol, #main.musym, #main.muname, #main.MUKEY,\n"\
            " #main.COKEY, #main.CHKEY, #main.compname, hzname, hzdept_r, hzdepb_r, hzdept_r_ADJ, hzdepb_r_ADJ, thickness, sum_thickness, " + aProp + ", comppct_r, SUM_COMP_PCT, WEIGHTED_COMP_PCT ,\n"\
            " SUM((thickness/sum_thickness ) * " + aProp + " )over(partition by #main.COKEY)AS COMP_WEIGHTED_AVERAGE\n"\
            " INTO #comp_temp2\n"\
            " FROM #main\n"\
            " INNER JOIN #comp_temp3 ON #comp_temp3.cokey=#main.cokey\n"\
            " ORDER BY #main.areasymbol, #main.musym, #main.muname, #main.MUKEY, comppct_r DESC,  #main.COKEY,  hzdept_r, hzdepb_r\n"\
            " SELECT #comp_temp2.MUKEY,#comp_temp2.COKEY, WEIGHTED_COMP_PCT * COMP_WEIGHTED_AVERAGE AS COMP_WEIGHTED_AVERAGE1\n"\
            " INTO #last_step\n"\
            " FROM #comp_temp2\n"\
            " GROUP BY  #comp_temp2.MUKEY,#comp_temp2.COKEY, WEIGHTED_COMP_PCT, COMP_WEIGHTED_AVERAGE\n"\
            " SELECT areasymbol, musym, muname,\n"\
            " #kitchensink.mukey, #last_step.COKEY,\n"\
            " CAST (SUM (COMP_WEIGHTED_AVERAGE1) over(partition by #kitchensink.mukey) as decimal(5,2))AS " + aProp + "\n"\
            " INTO #last_step2"\
            " FROM #last_step\n"\
            " RIGHT OUTER JOIN #kitchensink ON #kitchensink.mukey=#last_step.mukey\n"\
            " GROUP BY #kitchensink.areasymbol, #kitchensink.musym, #kitchensink.muname, #kitchensink.mukey, COMP_WEIGHTED_AVERAGE1, #last_step.COKEY\n"\
            " ORDER BY #kitchensink.areasymbol, #kitchensink.musym, #kitchensink.muname, #kitchensink.mukey\n"\
            " SELECT #last_step2.areasymbol, #last_step2.musym, #last_step2.muname,\n"\
            " #last_step2.mukey, #last_step2." + aProp + "\n"\
            " FROM #last_step2\n"\
            " LEFT OUTER JOIN #last_step ON #last_step.mukey=#last_step2.mukey\n"\
            " GROUP BY #last_step2.areasymbol, #last_step2.musym, #last_step2.muname, #last_step2.mukey, #last_step2." + aProp + "\n"\
            " ORDER BY #last_step2.areasymbol, #last_step2.musym, #last_step2.muname, #last_step2.mukey, #last_step2."+ aProp
        elif aggMethod == "Min\Max":
            pQry = "SELECT areasymbol, musym, muname, mu.mukey  AS mukey,\n"\
            " (SELECT TOP 1 " + mmC + " (chm1." + aProp + ") FROM  component AS cm1\n"\
            " INNER JOIN chorizon AS chm1 ON cm1.cokey = chm1.cokey AND cm1.cokey = c.cokey\n"\
            " AND CASE WHEN chm1.hzname LIKE  '%O%' AND hzdept_r <10 THEN 2\n"\
            " WHEN chm1.hzname LIKE  '%r%' THEN 2\n"\
            " WHEN chm1.hzname LIKE  '%'  THEN  1 ELSE 1 END = 1\n"\
            " ) AS " + aProp + "\n"+\
            " FROM legend  AS l\n"\
            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND mu.mukey IN (" + keys + ")\n"\
            " INNER JOIN  component AS c ON c.mukey = mu.mukey  AND c.cokey =\n"\
            " (SELECT TOP 1 c1.cokey FROM component AS c1\n"\
            " INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)\n"
        elif aggMethod == "Dominant Component (Numeric)":
            pQry = "SELECT areasymbol, musym, muname, mukey\n"\
            " INTO #kitchensink\n"\
            " FROM legend  AS lks\n"\
            " INNER JOIN  mapunit AS muks ON muks.lkey = lks.lkey AND muks.mukey IN (" + keys + ")\n"\
            " SELECT mu1.mukey, cokey, comppct_r,\n"\
            " SUM (comppct_r) over(partition by mu1.mukey ) AS SUM_COMP_PCT\n"\
            " INTO #comp_temp\n"\
            " FROM legend  AS l1\n"\
            " INNER JOIN  mapunit AS mu1 ON mu1.lkey = l1.lkey AND mu1.mukey IN (" + keys + ")\n"\
            " INNER JOIN  component AS c1 ON c1.mukey = mu1.mukey AND majcompflag = 'Yes'\n"\
            " AND c1.cokey =\n"\
            " (SELECT TOP 1 c2.cokey FROM component AS c2\n"\
            " INNER JOIN mapunit AS mm1 ON c2.mukey=mm1.mukey AND c2.mukey=mu1.mukey ORDER BY c2.comppct_r DESC, c2.cokey)\n"\
            " SELECT cokey, SUM_COMP_PCT, CASE WHEN comppct_r = SUM_COMP_PCT THEN 1\n"\
            " ELSE CAST (CAST (comppct_r AS  decimal (5,2)) / CAST (SUM_COMP_PCT AS decimal (5,2)) AS decimal (5,2)) END AS WEIGHTED_COMP_PCT\n"\
            " INTO #comp_temp3\n"\
            " FROM #comp_temp\n"\
            " SELECT areasymbol, musym, muname, mu.mukey/1  AS MUKEY, c.cokey AS COKEY, ch.chkey/1 AS CHKEY, compname, hzname, hzdept_r, hzdepb_r, CASE WHEN hzdept_r < " + tDep + " THEN " + tDep + " ELSE hzdept_r END AS hzdept_r_ADJ,"\
            " CASE WHEN hzdepb_r > " + bDep + "  THEN " + bDep + " ELSE hzdepb_r END AS hzdepb_r_ADJ,\n"\
            " CAST (CASE WHEN hzdepb_r > " + bDep + "  THEN " + bDep + " ELSE hzdepb_r END - CASE WHEN hzdept_r <" + tDep + " THEN " + tDep + " ELSE hzdept_r END AS decimal (5,2)) AS thickness,\n"\
            " comppct_r,\n"\
            " CAST (SUM (CASE WHEN hzdepb_r > " + bDep + "  THEN " + bDep + " ELSE hzdepb_r END - CASE WHEN hzdept_r <" + tDep + " THEN " + tDep + " ELSE hzdept_r END) over(partition by c.cokey) AS decimal (5,2)) AS sum_thickness,\n"\
            " CAST (ISNULL (" + aProp + " , 0) AS decimal (5,2))AS " + aProp + " \n"\
            " INTO #main\n"\
            " FROM legend  AS l\n"\
            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND mu.mukey IN (" + keys + ")\n"\
            " INNER JOIN  component AS c ON c.mukey = mu.mukey\n"\
            " INNER JOIN chorizon AS ch ON ch.cokey=c.cokey AND hzname NOT LIKE '%O%'AND hzname NOT LIKE '%r%'\n"\
            " AND hzdepb_r >" + tDep + " AND hzdept_r <" + bDep + "\n"\
            " INNER JOIN chtexturegrp AS cht ON ch.chkey=cht.chkey  WHERE cht.rvindicator = 'yes' AND  ch.hzdept_r IS NOT NULL\n"\
            " AND\n"\
            " texture NOT LIKE '%PM%' and texture NOT LIKE '%DOM' and texture NOT LIKE '%MPT%' and texture NOT LIKE '%MUCK' and texture NOT LIKE '%PEAT%' and texture NOT LIKE '%br%' and texture NOT LIKE '%wb%'\n"\
            " ORDER BY areasymbol, musym, muname, mu.mukey, comppct_r DESC, cokey,  hzdept_r, hzdepb_r\n"\
            " SELECT #main.areasymbol, #main.musym, #main.muname, #main.MUKEY,\n"\
            " #main.COKEY, #main.CHKEY, #main.compname, hzname, hzdept_r, hzdepb_r, hzdept_r_ADJ, hzdepb_r_ADJ, thickness, sum_thickness, " + aProp + " , comppct_r, SUM_COMP_PCT, WEIGHTED_COMP_PCT ,\n"\
            " SUM((thickness/sum_thickness ) * " + aProp + "  )over(partition by #main.COKEY)AS COMP_WEIGHTED_AVERAGE\n"\
            " INTO #comp_temp2\n"\
            " FROM #main\n"\
            " INNER JOIN #comp_temp3 ON #comp_temp3.cokey=#main.cokey\n"\
            " ORDER BY #main.areasymbol, #main.musym, #main.muname, #main.MUKEY, comppct_r DESC,  #main.COKEY,  hzdept_r, hzdepb_r\n"\
            " SELECT #comp_temp2.MUKEY,#comp_temp2.COKEY, WEIGHTED_COMP_PCT * COMP_WEIGHTED_AVERAGE AS COMP_WEIGHTED_AVERAGE1\n"\
            " INTO #last_step\n"\
            " FROM #comp_temp2\n"\
            " GROUP BY  #comp_temp2.MUKEY,#comp_temp2.COKEY, WEIGHTED_COMP_PCT, COMP_WEIGHTED_AVERAGE\n"\
            " SELECT areasymbol, musym, muname,\n"\
            " #kitchensink.mukey, #last_step.COKEY,\n"\
            " CAST (SUM (COMP_WEIGHTED_AVERAGE1) over(partition by #kitchensink.mukey) as decimal(5,2))AS " + aProp + "\n"\
            " INTO #last_step2\n"\
            " FROM #last_step\n"\
            " RIGHT OUTER JOIN #kitchensink ON #kitchensink.mukey=#last_step.mukey\n"\
            " GROUP BY #kitchensink.areasymbol, #kitchensink.musym, #kitchensink.muname, #kitchensink.mukey, COMP_WEIGHTED_AVERAGE1, #last_step.COKEY\n"\
            " ORDER BY #kitchensink.areasymbol, #kitchensink.musym, #kitchensink.muname, #kitchensink.mukey\n"\
            " SELECT #last_step2.areasymbol, #last_step2.musym, #last_step2.muname,\n"\
            " #last_step2.mukey, #last_step2." + aProp + "\n"\
            " FROM #last_step2\n"\
            " LEFT OUTER JOIN #last_step ON #last_step.mukey=#last_step2.mukey\n"\
            " GROUP BY #last_step2.areasymbol, #last_step2.musym, #last_step2.muname, #last_step2.mukey, #last_step2." + aProp + "\n"\
            " ORDER BY #last_step2.areasymbol, #last_step2.musym, #last_step2.muname, #last_step2.mukey, #last_step2." + aProp
        elif aggMethod == "Dominant Condition":
            pQry = "SELECT areasymbol, musym, muname, mu.mukey/1  AS mukey,\n"\
            " (SELECT TOP 1 " + aProp + "\n"\
            " FROM mapunit\n"\
            " INNER JOIN component ON component.mukey=mapunit.mukey\n"\
            " AND mapunit.mukey = mu.mukey\n"\
            " GROUP BY " + aProp + ", comppct_r ORDER BY SUM(comppct_r) over(partition by " + aProp + ") DESC) AS " + aProp + "\n"\
            " FROM legend  AS l\n"\
            " INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND  mu.mukey IN (" + keys + ")\n"\
            " INNER JOIN  component AS c ON c.mukey = mu.mukey\n"\
            " AND c.cokey =\n"\
            " (SELECT TOP 1 c1.cokey FROM component AS c1\n"\
            " INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)\n"\
            " GROUP BY areasymbol, musym, muname, mu.mukey, c.cokey,  compname, comppct_r\n"\
            " ORDER BY areasymbol, musym, muname, mu.mukey, comppct_r DESC, c.cokey\n"\

        #uncomment next line to print interp query to console
        #arcpy.AddMessage(pQry.replace("&gt;", ">").replace("&lt;", "<"))

        theURL = "https://sdmdataaccess.nrcs.usda.gov"
        url = theURL + "/Tabular/SDMTabularService/post.rest"

        # Create request using JSON, return data as JSON
        request = {}
        request["FORMAT"] = "JSON"
        request["QUERY"] = pQry

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

        container = dict()


        # if dictionary key "Table" is found
        if "Table" in qData:

            # get its value
            resLst = qData["Table"]  # Data as a list of lists. All values come back as string.

##        #msg =  "Geometry Response time = {}\n".format((time.time() - startTime))[:-6]
##        if cStatus == 200:
##            msg = "AOI collected successfully"
##            arcpy.AddMessage(msg + '\n')
##        else:
##            msg = "Error collecting AOI: " + str(cStatus) + "=" + cResponse
##            return False, msg

            for e in resLst:

                areasymbol = e[0]
                musym = e[1]
                muname = e[2]
                mukey = e[3]
                theProp = e[4]

                try:
                    rating = float(theProp)
                except:
                    if str(theProp):
                        rating = theProp
                else:
                    rating = theProp
##        #msg =  "Collected {} data ({} seconds)".format(interp, (time.time() - startTime)[:-6])
##        msg = "Request for {} = {}".format(aProp, cResponse)
##        arcpy.AddMessage(msg)
##        # Convert XML to tree format


                container[mukey] = areasymbol,musym, muname, mukey, rating

##        for k,v in container.iteritems():
##            arcpy.AddMessage(v)

        return True, container


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


def soloTbl(sdaTab):

    #arcpy.AddMessage('Running solotable')
    import collections

    srtDict = collections.OrderedDict(sorted(sdaTab.items()))

    srcDir = os.path.dirname(sys.argv[0])

    aggMethod == aggMethod.replace(" ", "_")

    #descWsType = arcpy.Describe(outLoc).workspaceFactoryProgID

    template = os.path.dirname(sys.argv[0]) + os.sep + 'templates.gdb' + os.sep + 'prop_template_table_base_1'


    #if descWsType == '':
    if tblExt == ".dbf":
        if not arcpy.Exists(os.path.join(path, name + tblExt)):
            arcpy.management.CreateTable(path, name + tblExt, template)
    if tblExt == '':
        if not arcpy.Exists(os.path.join(path, name + tblExt)):
            arcpy.management.CreateTable(path, name + tblExt, template)

    #fields for cursor to look for
    fldLst = ['areasymbol', 'musym', 'muname', 'mukey', propVal]


    #if the property returns string values
    if propVal in strFldLst:

        #get max length for field definition
        n = 0
        for eDef in srtDict:
            theDef = srtDict.get(eDef)[4]
            #WEG can't be numeric bc of class 4l
            #all other values are numeric/float and don't have a len()
            #so cast to string
            theDef = str(theDef)

            if theDef == None:
                theDef = 'None'
            if len(theDef) > n:
                n = len(theDef)


        arcpy.management.AddField(os.path.join(path, name + tblExt), propVal, "TEXT", "#", "#", str(n))
        desc = arcpy.Describe(os.path.join(path, name + tblExt))
        curFields = [(x.name).encode() for x in desc.fields]
        if not 'muname' in curFields:

            cursor = arcpy.da.InsertCursor(tblName + tblExt, fldLst)

            for entry in srtDict:
                row = srtDict.get(entry)
                cursor.insertRow(row)

            del cursor, row, srtDict, n

        else:

            with arcpy.da.UpdateCursor(tblName + tblExt, ["mukey", propVal]) as cursor:
                for row in cursor:
                    updateVal = srtDict.get(row[0])[4]
                    row[1] = updateVal
                    cursor.updateRow(row)



    #if the property doesn't return text
    else:
        arcpy.management.AddField(os.path.join(path, name + tblExt), propVal, "FLOAT")
        fldCnt = arcpy.Describe(os.path.join(path, name + tblExt)).fields
        if len(fldCnt) < 7:
            #arcpy.AddMessage('runnining insert cursor')

            cursor = arcpy.da.InsertCursor(tblName + tblExt, fldLst)

            for entry in srtDict:
                row = srtDict.get(entry)

                cursor.insertRow(row)

            del cursor, row, srtDict

        else:
            #arcpy.AddMessage('runnining update cursor')
            with arcpy.da.UpdateCursor(tblName + tblExt, ["mukey", propVal]) as cursor:
                for row in cursor:
                    updateVal = srtDict.get(row[0])[4]
##                    if updateVal is None:
##                        updateVal = -1
                    row[1] = updateVal
                    cursor.updateRow(row)



def mkTbl(sdaTab):

    import collections

    srtDict = collections.OrderedDict(sorted(sdaTab.items()))

    srcDir = os.path.dirname(sys.argv[0])

    aggMethod == aggMethod.replace(" ", "_")

    #descWsType = arcpy.Describe(outLoc).workspaceFactoryProgID

    template = os.path.dirname(sys.argv[0]) + os.sep + 'templates.gdb' + os.sep + 'prop_template_table_base_1'


    #if descWsType == '':
    if tblExt == ".dbf":
        arcpy.management.CreateTable(path, name + tblExt, template)
    if tblExt == '':
        arcpy.management.CreateTable(path, name + tblExt, template)

    #fields for cursor to look for
    fldLst = ['areasymbol', 'musym', 'muname', 'mukey', propVal]


    #if the property returns string values
    if propVal in strFldLst:

        #get max length for field definition
        n = 0
        for eDef in srtDict:
            theDef = srtDict.get(eDef)[4]
            #WEG can't be numeric bc of class 4l
            #all other values are numeric/float and don't have a len()
            #so cast to string
            theDef = str(theDef)

            if theDef == None:
                theDef = 'None'
            if len(theDef) > n:
                n = len(theDef)


        arcpy.management.AddField(os.path.join(path, name + tblExt), propVal, "TEXT", "#", "#", str(n))
        cursor = arcpy.da.InsertCursor(tblName + tblExt, fldLst)

        for entry in srtDict:
            row = srtDict.get(entry)
            #arcpy.AddMessage(row)
            cursor.insertRow(row)

        del cursor, row, srtDict, n

    #if the property doesn't return text
    else:
        arcpy.management.AddField(os.path.join(path, name + tblExt), propVal, "FLOAT")

        cursor = arcpy.da.InsertCursor(tblName + tblExt, fldLst)

        for entry in srtDict:
            row = srtDict.get(entry)
            cursor.insertRow(row)

        del cursor, row, srtDict




def mkGeo():

    #arcpy.env.addOutputsToMap = True

    inFeats = outLoc + os.sep + "SSURGO_express_properties" + geoExt
    #outFeats = outLoc + os.sep + "SSURGO_express_prop_polys_" + name[19:] + geoExt

    arcpy.management.CopyFeatures(inFeats, outFeats)


    flds = ['areasymbol', 'musym', 'muname', propVal]
    arcpy.management.JoinField(outFeats, "mukey", path + os.sep + name + tblExt, "mukey", flds)


def sym(inLyr):

    if geoExt == '.shp':
        lyrLoc = outLoc
    else:
        lyrLoc = os.path.dirname(outLoc)


    outLyr = lyrLoc + os.sep + "SSURGO_express_properties_" + name[19:] + ".lyr"

    lyr = arcpy.mapping.Layer(inLyr)

    arcpy.management.AddJoin(lyr, "mukey", path + os.sep + name + tblExt, "mukey", None)

    srcSymLyr = arcpy.mapping.Layer(os.path.dirname(sys.argv[0]) + os.sep + 'unq_val.lyr')


    #add the layer to arcmap
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = mxd.activeDataFrame
    arcpy.mapping.AddLayer(df, lyr)
    #lyr = arcpy.mapping.Layer(outFeats)



    #search string of the property that was run
    srcStr =  os.path.basename(lyr.name)

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

            l.name = name[19:]

            valFld = name + tblExt + '.'+ propVal
            if valFld in [x.name for x in arcpy.Describe(l).fields]:

                arcpy.mapping.UpdateLayer(df, l, srcSymLyr, True)

                values = list()
                with arcpy.da.SearchCursor(l.name, valFld) as rows:
                    for row in rows:
                        #arcpy.AddMessage(row[0])

                        #if it's a number
                        if not propVal in strFldLst:
                            try:
                                aVal = round(row[0], 3)
                            except:
                                aVal = -1

                        #if it's a string
                        else:
                            if row[0] is None:
                                aVal = 'Not Rated'
                            else:
                                aVal = row[0]

                        #arcpy.AddMessage('aVal is: ' + str(aVal))
                        if not aVal in values:
                            values.append(aVal)
                values.sort()

                l.symbology.valueField = valFld
                l.symbology.addAllValues()
                l.symbology.classValues = values
                l.symbology.classDescriptions = values
                #l.symbology.showOtherValues = False


                arcpy.RefreshActiveView()
                arcpy.RefreshTOC()

                del values

                l.saveACopy(outLyr)



#===============================================================================


import sys, os, time, urllib2, json, traceback, socket, arcpy
from urllib2 import HTTPError, URLError

arcpy.env.overwriteOutput = True
arcpy.AddMessage('\n\n')

featSet = arcpy.GetParameterAsText(0)
#arcpy.AddMessage(featSet + '\n\n')


aggMethod = arcpy.GetParameterAsText(1)
#paramProps = arcpy.GetParameterAsText(2)
tDep = arcpy.GetParameterAsText(3)
bDep = arcpy.GetParameterAsText(4)
mmC = arcpy.GetParameterAsText(5)
outLoc = arcpy.GetParameterAsText(6)
bAll = arcpy.GetParameterAsText(7)
bSingle = arcpy.GetParameterAsText(8)

propParam = '"' + arcpy.GetParameterAsText(2) + '"'
propParam = propParam.replace("'", "")
propParam = propParam[1:-1]
propLst = propParam.split(";")

#these properties return text
strFldLst = ['weg', 'taxclname', 'taxorder', 'taxsuborder', 'taxtempregime', 'corsteel', 'drainagecl', 'hydgrp', 'corcon']

if aggMethod == 'Dominant Component (Category)':
    aggMod = '_dom_comp_cat'
elif aggMethod == 'Dominant Component (Numeric)':
    aggMod = '_dom_comp_num'
elif aggMethod == 'Dominant Condition':
    aggMod ='_dom_cond'
elif aggMethod == 'Weighted Average':
    aggMod = '_wtd_avg'
elif aggMethod == 'Min\Max':
    aggMod = '_min_max'
else:
    raise ForceExit('unable to determine aggregation method')


desc = arcpy.Describe(featSet).spatialReference.datumName
#arcpy.AddMessage(desc)

descWsType = arcpy.Describe(outLoc).workspaceFactoryProgID

if descWsType == '':
    geoExt = '.shp'
    tblExt = '.dbf'
else:
    geoExt = ''
    tblExt = ''


# get the corrdinates from the parameter and make them into a poly
# first point is also the last
coorStr = ''
with arcpy.da.SearchCursor(featSet, "SHAPE@XY") as rows:
    for row in rows:
        coorStr = coorStr + (str(row[0][0]) + " " + str(row[0][1]) + ",")


cIdx = coorStr.find(",")
endPoint = coorStr[:cIdx]
coorStr = coorStr + endPoint

if coorStr == '':
    raise ForceExit('Fatal. No AOI created')

arcpy.SetProgressor("step", "Collecting AOI info", 0, len(propLst) + 1, 1)

geoResponse, geoVal = geoRequest(coorStr)

if geoResponse:
    arcpy.SetProgressorPosition()
    keys = ",".join(geoVal)

    for prop in propLst:
        arcpy.SetProgressorLabel('Collecting ' + prop + '...')
        #arcpy.AddMessage(prop)
        propVal = rslvProps(prop).strip()

        root = "SSURGO_express_tbl_"

        if bSingle == 'true':
            propHldr = 'multiprops'
        else:
            propHldr = propVal

        if aggMethod == "Weighted Average":
            tblName =  root + propHldr + aggMod + "_" + tDep + "_" + bDep
        elif aggMethod == "Dominant Component (Category)":
            tblName =  root + propHldr + "_" + aggMod
        elif aggMethod == "Min\Max":
            tblName =  root + propHldr + "_" + aggMod + "_" + mmC.upper()
        elif aggMethod == "Dominant Component (Numeric)":
            tblName =  root + propHldr + "_" + aggMod + "_" + tDep + "_" + bDep
        elif aggMethod == "Dominant Condition":
            tblName =  root + propHldr + "_" + aggMod

        #tblName = "SSURGO_express_tbl" + propVal + aggMethod + tDep + "_" + bDep
        tblName = arcpy.ValidateTableName (tblName)
        tblName = tblName.replace("___", "_")
        tblName = tblName.replace("__", "_")
        tblName = outLoc + os.sep + tblName

        path = os.path.dirname(tblName)
        name = os.path.basename(tblName)

        sdaResponse, sdaItem = tabRequest(propVal)

        if sdaResponse:

            outFeats = os.path.join(outLoc, "SSURGO_express_properties" + geoExt)

            if bSingle == 'false' or bSingle == '#':
                mkTbl(sdaItem)
                sym(outFeats)

            elif bAll == "true":
                mkTbl(sdaItem)
                #mkGeo()
                sym(outFeats)

            elif bSingle == 'true':
                soloTbl(sdaItem)

            else:
                mkTbl(sdaItem)
                sym(outFeats)


            arcpy.SetProgressorPosition()


        else:
            arcpy.AddMessage(sdaItem)


    if bSingle == "true":
        descFlds = [(x.name).encode() for x in arcpy.Describe(path + os.sep + name + tblExt).fields]
        descFlds.remove("MUKEY")
        arcpy.management.JoinField(outLoc + os.sep + "SSURGO_express_properties" + geoExt, "mukey", path + os.sep + name + tblExt, "mukey", descFlds)
        outFeats = os.path.join(outLoc, "SSURGO_express_properties" + geoExt)
        #arcpy.AddMessage(outFeats)
        sym(outFeats)

else:
    arcpy.AddError('Fatal.\n' + geoVal)

arcpy.AddMessage('\n\n')







