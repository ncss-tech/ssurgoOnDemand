import sys, os, arcpy

from arcpy import env

env.OverwriteOutput=True

tbls = [u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_wei_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_weg_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_drainagecl_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_hydgrp_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_corcon_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_corsteel_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_taxclname_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_taxsuborder_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_taxorder_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_taxtempregime_dom_cond', u'D:\\Chad\\GIS\\scratch.gdb\\SSURGO_express_tbl_tfact_dom_cond']

source = os.path.dirname(tbls[0]) + os.sep + "SSURGO_express_multiprop"

arcpy.conversion.TableToTable(tbls[0], os.path.dirname(tbls[0]), "SSURGO_express_multiprop")

sfs = [f.name for f in arcpy.Describe(source).fields]
#fldName, dataType, precision, scale, length
for tbl in tbls[1:]:
    for fld in arcpy.Describe(tbl).fields:
        if fld.name not in sfs:
            #mpgs = (fld.name, fld.type, fld.precision, fld.scale, fld.length)
            arcpy.management.AddField(source, fld.name, fld.type, fld.precision, fld.scale, fld.length)

            tblDict = dict()

            with arcpy.da.SearchCursor(tbl, ["mukey", fld.name]) as rows:
                for row in rows:
                    tblDict[row[0]] = row[1]

            with arcpy.da.UpdateCursor(source, ["mukey", fld.name]) as rows:
                for row in rows:
                    val = tblDict.get(row[0])
                    row[1] = val
                    rows.updateRow(row)
