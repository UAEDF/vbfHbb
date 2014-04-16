#!/usr/bin/env python

import ROOT
from ROOT import *
import sys,os,re

tc1 = TChain("Hbb/events")
tc1.Add("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_JetMonB.root")
tc1.Add("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_JetMonC.root")
tc1.Add("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_JetMonD.root")

f1 = TFile("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_QCD100.root")
f2 = TFile("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_QCD250.root")
f3 = TFile("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_QCD500.root")
f4 = TFile("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_QCD1000.root")
w1 = 4.837581
w2 = 98.051000
w3 = 3631.531688
w4 = 67862.073529

lumi = 18300.

VBFcut = TCut("dEtaqq[2]>3.5 && dEtaTrig>3.5 && mqq[2]>700 && mjjTrig>700 && ptAve>80 && jetPt[3]>30")
VBFtrg = TCut("triggerResult[9]")
VBFref = TCut("triggerResult[15]")

binx = {3.5,3.8,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,10.}
h = TH1F("hnumdat","hnumdat",)

numdat = tc1.Draw("dEtaqq[2]",VBFcut + TCut("runNo>194270") + VBFtrg + VBFref)
dendat = tc1.Draw("dEtaqq[2]",VBFcut + TCut("runNo>194270")          + VBFref)

numqcd = tc1.Draw("dEtaqq[2]",VBFcut + VBFtrg + VBFref)
denqcd = tc1.Draw("dEtaqq[2]",VBFcut +        + VBFref)
