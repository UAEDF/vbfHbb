#!/usr/bin/env python

import ROOT
from ROOT import *


f = TFile.Open("rootfiles/vbfHbb_BDTcorrelations.root","update")

c = TCanvas("c","c")
keys = f.GetListOfKeys()
for k in keys:
	h = f.Get(k)
	h.Draw()
	f	h.Draw()
	f	h.Draw()
	f...

f.Close()
