#!/usr/bin/env python

import ROOT
from ROOT import *

typ  = ["S+B","S+B","S+B","S+B","B","B","B","B"]
size = [0.1,0.5,1,2.5,0.1,0.5,1,2.5]
chi2 = [7566.4,1601.7,830.5,309.3,7571.9,1611.5,842.5,322.0]
ndof = [8297,1577,737,233,8298,1578,738,234]
bins = [8400,1680,840,336,8400,1680,840,336]
npar = [103,103,103,103,102,102,102,102]
npar = [19,19,19,19,18,18,18,18]

npar = [103,103,103,103,102,102,102,102]
ndof = [8381,1661,821,317,8382,1662,822,318]

for i in range(8):
	print "%8d"%bins[i],
	print "%8d"%npar[i],
	print "%8d"%ndof[i],
	print "%8.2f"%chi2[i],
	print "%8.2f"%(chi2[i]/float(ndof[i])),
	print "%8.9f"%(TMath.Prob(chi2[i],ndof[i]))



