#!/usr/bin/env python
import ROOT
from ROOT import *

f = TFile.Open("/usb/data2/UAData/fromKostas/autumn2013/flatTree_VBFPowheg125.root","read")
t = f.Get("Hbb/events")

for i,ev in enumerate(t):
    print "pt", list(ev.jetPt)
    print "btag", list(ev.jetBtag)
    print "btagIdx", list(ev.btagIdx)
    print "eta", list(ev.jetEta)
    print "etaIdx", list(ev.etaIdx)
    print
    if i==5: break

