#!/usr/bin/env python

import os,sys,re
from glob import glob

import ROOT
from ROOT import *

name="B80*/output/combine"

globlist = glob("%s/higgsCombine*MaxLikelihoodFit*"%name)

systlist = {re.search(".*mH([0-9]{3}).",x).group(1):TFile(x,"read") for x in globlist if not "NoSyst" in x}
nosystlist = {re.search(".*mH([0-9]{3}).",x).group(1):TFile(x,"read") for x in globlist if "NoSyst" in x}

systtree = {k:v.Get("limit") for (k,v) in systlist.iteritems()}
nosysttree = {k:v.Get("limit") for (k,v) in nosystlist.iteritems()}

systval = {k:[None,None,None,None,None] for (k,v) in systtree.iteritems()}
nosystval = {k:[None,None,None,None,None] for (k,v) in nosysttree.iteritems()}

for k,v in systtree.iteritems():
	for iEv,Ev in enumerate(v):
		if iEv>2: 
			systval[k][3] = systval[k][1] - systval[k][0]
			systval[k][4] = systval[k][2] - systval[k][0]
			break
		systval[k][iEv] = Ev.limit

for k,v in nosysttree.iteritems():
	for iEv,Ev in enumerate(v):
		if iEv>2: 
			nosystval[k][3] = nosystval[k][1] - nosystval[k][0]
			nosystval[k][4] = nosystval[k][2] - nosystval[k][0]
			break
		nosystval[k][iEv] = Ev.limit

val = {}
for k in systval.iterkeys():
	val[k] = {} 
	val[k]["mu"] = systval[k][0]
	val[k]["syst-"] = -sqrt(abs(pow(systval[k][3],2)-pow(nosystval[k][3],2)))
	val[k]["syst+"] = sqrt(abs(pow(systval[k][4],2)-pow(nosystval[k][4],2)))
	val[k]["stat-"] = nosystval[k][3]
	val[k]["stat+"] = nosystval[k][4]
	val[k]["comb-"] = -sqrt(pow(val[k]["stat-"],2)+pow(val[k]["syst-"],2))
	val[k]["comb+"] = sqrt(pow(val[k]["stat+"],2)+pow(val[k]["syst+"],2))

print
print "%6s | %8s | %17s | %17s | %17s"%("mH","mu","stat","syst","combined")
print "-"*77
for k,v in sorted(val.iteritems()):
	print "%6d | %8.2f | %+8.2f %+8.2f | %+8.2f %+8.2f | %+8.2f %+8.2f"%(int(k),v["mu"],v["stat+"],v["stat-"],v["syst+"],v["syst-"],v["comb+"],v["comb-"])  
