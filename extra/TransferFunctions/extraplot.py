#!/usr/bin/env python

import ROOT
from ROOT import *

import sys,re,os
sys.path.append("../../common/")

from toolkit import *
from math import *

gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
gStyle.SetOptStat(0)
gStyle.SetOptFit(0)
gStyle.SetOptTitle(0)
gStyle.SetPadLeftMargin(0.14)
gStyle.SetPadRightMargin(0.03)
gStyle.SetPadTopMargin(0.07)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleSize(0.05,"XY")
gStyle.SetLabelSize(0.04,"XY")
gStyle.SetStripDecimals(kFALSE)


f = TFile.Open("rootfiles/vbfHbb_transferFunctions.root","read")

hdat1 = f.Get("hRat_selNOM_CAT1_Data")
hdat2 = f.Get("hRat_selVBF_CAT5_Data")
hqcd1 = f.Get("hRat_selNOM_CAT1_QCD")
hqcd2 = f.Get("hRat_selVBF_CAT5_QCD")

hdat1.SetMarkerStyle(25)
hdat1.SetMarkerColor(kBlue+1)
hdat1.SetMarkerSize(1.3)
hdat2.SetMarkerStyle(25)
hdat2.SetMarkerColor(kBlue+1)
hdat2.SetMarkerSize(1.3)

hqcd1.SetLineColor(kBlack)
hqcd1.SetMarkerColor(kBlack)
hqcd1.SetMarkerSize(0.0)
hqcd2.SetLineColor(kBlack)
hqcd2.SetMarkerColor(kBlack)
hqcd2.SetMarkerSize(0.0)

hdat1.GetYaxis().SetRangeUser(0.65,1.35)
hdat2.GetYaxis().SetRangeUser(0.65,1.35)
hdat1.GetYaxis().SetNdivisions(507)
hdat2.GetYaxis().SetNdivisions(507)
hdat1.GetFunction("fitRatio_selNOM_CAT1_Data").SetBit(TF1.kNotDraw)
hdat2.GetFunction("fitRatio_selVBF_CAT5_Data").SetBit(TF1.kNotDraw)
hqcd1.GetFunction("fitRatio_selNOM_CAT1_QCD").SetBit(TF1.kNotDraw)
hqcd2.GetFunction("fitRatio_selVBF_CAT5_QCD").SetBit(TF1.kNotDraw)

hdat1.GetXaxis().SetTitle("m_{bb} (GeV)")
hdat2.GetXaxis().SetTitle("m_{bb} (GeV)")
hdat1.GetYaxis().SetTitle("CAT0 / CAT1+2+3")
hdat2.GetYaxis().SetTitle("CAT4 / CAT5+6")

leg = TLegend(0.50,0.5,0.93,1.-gStyle.GetPadTopMargin()-0.02)
leg.SetTextSize(0.045)
leg.SetTextFont(42)
leg.SetTextColor(kBlack)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.SetY1(leg.GetY2()-2*leg.GetTextSize()*1.25)

tl = TLine(80,1.0,220,1.0)
tl.SetLineColor(kGray+1)
tl.SetLineWidth(1)
tl.SetLineStyle(kDashed)

c = TCanvas("c","c",1800,750)
c.Divide(2,1)
c.cd(1)
hdat1.Draw("P")
hqcd1.Draw("Psame")
epave("Set A selection",gPad.GetLeftMargin()+0.01,1.-0.5*gPad.GetTopMargin(),"left",1,0.048)
epave("19.8 fb^{-1} (8 TeV)",1.-gPad.GetRightMargin()-0.01,1.-0.5*gPad.GetTopMargin(),"right",0,0.048)
leg.AddEntry(hdat1,"Data","LP")
leg.AddEntry(hqcd1,"QCD (H_{T} > 500 GeV)","LP")
leg.Draw()
tl.Draw("same")
c.cd(2)
hdat2.Draw("P")
hqcd2.Draw("Psame")
epave("Set B selection",gPad.GetLeftMargin()+0.01,1.-0.5*gPad.GetTopMargin(),"left",1,0.048)
epave("18.3 fb^{-1} (8 TeV)",1.-gPad.GetRightMargin()-0.01,1.-0.5*gPad.GetTopMargin(),"right",0,0.048)
leg.Clear()
leg.AddEntry(hdat2,"Data","LP")
leg.AddEntry(hqcd2,"QCD (H_{T} > 500 GeV)","LP")
leg.Draw()
tl.Draw("same")

c.SaveAs("tmp.pdf")

f.Close()
f.Close()
