#!/usr/bin/env python

import sys,re,os
import ROOT
from ROOT import *
from optparse import OptionParser

mp = OptionParser()
opts,args = mp.parse_args()

inf = TFile.Open("combine/higgsCombine_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2.ChannelCompatibilityCheck.mH%d.root"%int(args[0]))
fit_alternate = inf.Get("fit_alternate")

prefix = "_ChannelCompatibilityCheck_r_"

nChann = 0
iter = fit_alternate.floatParsFinal().createIterator()
a = iter.Next()

while a:
	if prefix==a.GetName()[0:len(prefix)]: nChann += 1
	a = iter.Next()

iter = fit_alternate.floatParsFinal().createIterator()
a = iter.Next()
iChann = 0
print

while a:
	if prefix==a.GetName()[0:len(prefix)]:
		channel = a.GetName()
		channel.replace(prefix,"")
		print "CAT%d %.3f +- (%+.3f/%+.3f)"%(iChann,a.getVal(),a.getAsymErrorLo(),a.getAsymErrorHi())
		iChann += 1
	a = iter.Next()

print
inf.Close()
