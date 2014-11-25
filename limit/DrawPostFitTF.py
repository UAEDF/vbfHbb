#!/usr/bin/env python

import ROOT
from ROOT import *
import os,sys,re
from optparse import OptionParser

mp = OptionParser()
opts,args = mp.parse_args()

f1 = TFile.Open("combine/mlfit%s.mH%s.root"%(args[0],args[1]))

fit_s = f1.Get("fit_s")
iter = fit_s.floatParsFinal().createIterator()
a = iter.Next()
while a:
	if not "trans" in a.GetName(): 
		a = iter.Next()
		continue
	print "%-30s %9.3e +- %9.3e" % (a.GetName(), a.getValV(), a.getError())
	CAT = re.search(".*CAT([0-9]*)",a.GetName()).group(1)
	PAR = re.search(".*p([0-9]*).*",a.GetName()).group(1)
	print CAT, PAR
	a = iter.Next()

print
iter = fit_s.floatParsInit().createIterator()
a = iter.Next()
while a:
	if not "trans" in a.GetName(): 
		a = iter.Next()
		continue
	print "%-30s %9.3e" % (a.GetName(), a.getValV())
	a = iter.Next()

f1.Close()
