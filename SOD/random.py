#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Charles.Ferguson
#
# Created:     18/04/2016
# Copyright:   (c) Charles.Ferguson 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, random, arcpy

feats = r'D:\Chad\GIS\NRCS\V\MLRA\mlra_v42.shp'

oidFld = arcpy.Describe(feats).oidFieldName
oidLst = list()

with arcpy.da.SearchCursor(feats, oidFld) as rows:
    for row in rows:
       oidLst.append(row[0])

rLst = random.sample(oidLst, 50)

print rLst

arcpy


def main():
    pass

if __name__ == '__main__':
    main()
