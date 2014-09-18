#!/usr/bin/env python

import ROOT
from ROOT import *


f0 = TFile.Open("rootfiles/TransferFunction_0.00_0.70_0.84.root")
f1 = TFile.Open("rootfiles/vbfHbb_transferFunctions_kostas.root")
f2 = TFile.Open("rootfiles/vbfHbb_transferFunctions_sara.root")

h0 = f0.Get("fitRatio_selNOM_CAT3;1")
h1 = f1.Get("fitRatio_selNOM_CAT3;1")
h2 = f2.Get("fitRatio_selNOM_CAT3;1")

h4 = f0.Get("fitRatio_selVBF_CAT2;1")
h5 = f1.Get("fitRatio_selVBF_CAT6;1")
h6 = f2.Get("fitRatio_selVBF_CAT6;1")

h0.SetLineColor(kRed)
h1.SetLineColor(kBlue)
h2.SetLineColor(kGreen)

h4.SetLineColor(kRed)
h5.SetLineColor(kBlue)
h6.SetLineColor(kGreen)

c = TCanvas("c","c",1200,600)
c.Divide(2,1)

c.cd(1)
h0.SetTitle("NOM_CAT3")
h0.Draw()
h1.Draw("same")
h2.Draw("same")

c.cd(2)
h4.SetTitle("VBF_CAT6")
h4.Draw()
h5.Draw("same")
h6.Draw("same")

c.cd(1)
leg = TLegend(0.6,0.6,0.9,0.9)
leg.AddEntry(h0,"Kostas","L")
leg.AddEntry(h1,"Intermed","L")
leg.AddEntry(h2,"Sara","L")
leg.Draw()

c.SaveAs("/home/salderwe/Desktop/compare.pdf")
