#!/usr/bin/env python

import ROOT
from ROOT import *

f = TFile.Open("test.root","recreate")
t = TTree("events","events")
runinfo = TObjString("selection")
t.GetUserInfo().Add(runinfo)

t.GetUserInfo().Print()
f.Write()
f.Close()
