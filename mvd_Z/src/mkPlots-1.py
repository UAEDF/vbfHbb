#!/usr/bin/env python

import ROOT
from ROOT import *
import sys,re,os

gROOT.SetBatch(1)

f1 = TFile.Open("BDT-5905_NOM.root","read")
f2 = TFile.Open("BDT-108010_NOM.root","read")
f3 = TFile.Open("BDT-255025_NOM.root","read")
f4 = TFile.Open("BDT-333333_NOM.root","read")
f5 = TFile.Open("BDT-100100100_NOM.root","read")

h1S = f1.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_S")
h1S.SetName("h1S")
h2S = f2.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_S")
h2S.SetName("h2S")
h3S = f3.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_S")
h3S.SetName("h3S")
h4S = f4.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_S")
h4S.SetName("h4S")
h5S = f5.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_S")
h5S.SetName("h5S")
h1B = f1.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_B")
h1B.SetName("h1B")
h2B = f2.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_B")
h2B.SetName("h2B")
h3B = f3.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_B")
h3B.SetName("h3B")
h4B = f4.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_B")
h4B.SetName("h4B")
h5B = f5.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_B")
h5B.SetName("h5B")
h1V = f1.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_rejBvsS")
h1V.SetName("h1V")
h2V = f2.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_rejBvsS")
h2V.SetName("h2V")
h3V = f3.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_rejBvsS")
h3V.SetName("h3V")
h4V = f4.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_rejBvsS")
h4V.SetName("h4V")
h5V = f5.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_rejBvsS")
h5V.SetName("h5V")

h1CS = f1.Get("CorrelationMatrixS")
h1CS.SetName("h1CS")
h2CS = f2.Get("CorrelationMatrixS")
h2CS.SetName("h2CS")
h3CS = f3.Get("CorrelationMatrixS")
h3CS.SetName("h3CS")
h4CS = f4.Get("CorrelationMatrixS")
h4CS.SetName("h4CS")
h5CS = f5.Get("CorrelationMatrixS")
h5CS.SetName("h5CS")
h1CB = f1.Get("CorrelationMatrixB")
h1CB.SetName("h1CB")
h2CB = f2.Get("CorrelationMatrixB")
h2CB.SetName("h2CB")
h3CB = f3.Get("CorrelationMatrixB")
h3CB.SetName("h3CB")
h4CB = f4.Get("CorrelationMatrixB")
h4CB.SetName("h4CB")
h5CB = f5.Get("CorrelationMatrixB")
h5CB.SetName("h5CB")

H = [h1S,h1B,h1CS,h1CB,h1V,h2S,h2B,h2CS,h2CB,h2V,h3S,h3B,h3CS,h3CB,h3V,h4S,h4B,h4CS,h4CB,h4V,h5S,h5B,h5CS,h5CB,h5V]

c = TCanvas("c","c",3600,3750)
c.Divide(5,5)
for i,h in enumerate(H):
    c.cd(i+1)
    h.Draw("" if not "C" in h.GetName() else "text,colz")
    gPad.SetGrid(1,1)

c.SaveAs("plots/performance.pdf")

H = [h1V,h2V,h3V,h4V,h5V]
c.Clear()
for i,h in enumerate(H):
    h.SetLineColor(i+1)
    h.Draw("" if i==0 else "same")
gPad.SetGrid(1,1)
tl1 = TLine(0.72,0.0,0.72,1.0)
tl1.SetNDC(0)
tl1.Draw("same")
tl2 = TLine(0.74,0.0,0.74,1.0)
tl2.SetNDC(0)
tl2.Draw("same")
tl3 = TLine(0.76,0.0,0.76,1.0)
tl3.SetNDC(0)
tl3.Draw("same")
tl4 = TLine(0.78,0.0,0.78,1.0)
tl4.SetNDC(0)
tl4.Draw("same")
c.SaveAs("plots/performance-2.pdf")

f1.Close()
f2.Close()
f3.Close()
f4.Close()



