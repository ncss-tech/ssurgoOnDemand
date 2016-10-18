#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      charles.ferguson
#
# Created:     15/05/2015
# Copyright:   (c) charles.ferguson 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os

pDict = {}
pList = []
with open(r'c:\chad\fields.csv', 'r') as f:
    for line in f:
        line = line.replace('  ', ' ').replace("#", "no. ")[:-1]
        ndx = line.find(",")
        field = line[:ndx]
        prop = line[ndx + 1:]
        pList.append(prop)
        pDict[prop] = field
f.close()

pList.sort()
#print pList
##for k,v in pDict.iteritems():
##    print k, ':::', v

print pDict

