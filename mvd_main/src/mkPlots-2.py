#!/usr/bin/env python

import ROOT
from ROOT import *
import sys,re,os
global paves
paves = []

####################################################################################################
def epavetext(text,x,y,x2,y2,size=0.04,hl=1):
    global paves
    p = TPaveText(x,y,x2,y2,"NDC")
    p.SetTextSize(size)
    p.SetTextFont(42)
    p.SetTextAlign(11)
    p.SetTextColor(kBlack)
    p.SetFillStyle(0)
    p.SetBorderSize(0)
    for i,t in enumerate(text): 
        ti = p.AddText(t)
        if i==0: ti.SetTextFont(62)
    p.Draw("same")
    paves += [p]
    return p

####################################################################################################
def epave(text,x,y,pos="left",hl=1,size=0.028):
    global paves
    p = TLatex(x,y,text)
    p.SetNDC()
    p.SetTextSize(size)
    p.SetTextFont(62 if hl==1 else 42)
    p.SetTextAlign(12 if pos=="left" else (32 if pos=="right" else 22))
    p.SetTextColor(kBlack)
    p.Draw("same")
    paves += [p]

####################################################################################################
fout = TFile.Open("plots/performance.root","recreate")

FOLDER = "v1"

colours = [kBlack,kOrange,kBlue,kGreen+1,kRed]
styles = [5,8,6,7,1]
labels = ["qq' system","b-tagging","q/g tagging","soft activity","angular dynamics"]
variables = ["m_{qq'}","|#Delta#eta_{qq'}|","|#Delta#phi_{qq'}|","b-jet_{0} b-tag","b-jet_{1} b-tag","b-jet_{0} QGL","b-jet_{1} QGL","q-jet_{0} QGL","q-jet_{1} QGL","H_{T}^{soft}","N_{2}^{soft}","cos #theta_{qq',b#bar{b}}"]

gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x ../common/styleCMSTDR.C")
gStyle.SetLineScalePS(2.2)
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadRightMargin(0.04)
gStyle.SetPadLeftMargin(0.12)
gStyle.SetPadTopMargin(0.07)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleOffset(1.05,"X")
gStyle.SetTitleOffset(1.10,"Y")
gStyle.SetPalette(1)
gStyle.SetGridColor(17)
TGaxis.SetMaxDigits(4)
gStyle.SetTitleSize(0.05,"XYZ")
gStyle.SetLabelSize(0.04,"XYZ")

for SEL in ["NOM","VBF"]:
    f = [None]*5
    hSB = [None]*5
    hCORS = [None]*5
    hCORB = [None]*5
    for i in range(5):
        f[i] = TFile.Open("%s/BDT-groups1-%d_%s.root"%(FOLDER,i+1,SEL),"read")
        hSB[i] = f[i].Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_rejBvsS")
        hSB[i].SetName("ROC_%s"%(f[i].GetName()[4:13]))
        hCORS[i] = f[i].Get("CorrelationMatrixS")
        hCORB[i] = f[i].Get("CorrelationMatrixB")
    
    fout.cd()
    c = TCanvas("c","c",900,750)
    c.cd()
    h0 = TH1F("h","h;Signal efficiency;Background rejection",hSB[0].GetNbinsX()+10,hSB[0].GetXaxis().GetXmin(),hSB[0].GetXaxis().GetXmax()+10*hSB[0].GetBinWidth(1))
    for i in range(hSB[0].GetNbinsX()):
        h0.SetBinContent(i,hSB[0].GetBinContent(i))
    h0.GetYaxis().SetRangeUser(0,1.05)
    h0.GetXaxis().SetLimits(0,1.05)
    gPad.SetLeftMargin(gStyle.GetPadLeftMargin())
    gPad.SetRightMargin(gStyle.GetPadRightMargin())
    gPad.SetTopMargin(gStyle.GetPadTopMargin())
    gPad.SetBottomMargin(gStyle.GetPadBottomMargin())
    h0.GetXaxis().SetTitleSize(gStyle.GetTitleSize("X"))
    h0.GetYaxis().SetTitleSize(gStyle.GetTitleSize("Y"))
    h0.GetXaxis().SetTitleOffset(gStyle.GetTitleOffset("X"))
    h0.GetYaxis().SetTitleOffset(gStyle.GetTitleOffset("Y"))
    h0.GetXaxis().SetLabelSize(gStyle.GetLabelSize("X"))
    h0.GetYaxis().SetLabelSize(gStyle.GetLabelSize("Y"))
    gPad.Update()
    h0.Draw("axis")
    
    pv = TPaveText(0.50,gStyle.GetPadBottomMargin()+0.05,0.55,0.6,"NDC")
    pv.SetBorderSize(0)
    pv.SetFillStyle(0)
    pv.SetTextSize(0.032)
    pv.SetTextFont(42)
    pv.SetTextAlign(12)
    l = TLegend(0.16,gStyle.GetPadBottomMargin()+0.05,0.45,0.6)
    l.SetBorderSize(0)
    l.SetFillStyle(0)
    l.SetTextSize(0.035)
    l.SetTextFont(62)
    l.SetHeader("Variable group")
    l.SetTextFont(42)
    b = pv.AddText("ROC area")
    b.SetTextFont(62)
    for i,h in enumerate(hSB):
        #h.SetLineColor(i+1)
        h.SetLineColor(colours[i])
        h.SetLineStyle(styles[i])
        h.Draw("same,L")
        I = h.Integral()/h.GetNbinsX()
        a = l.AddEntry(h,labels[i],"L")
        a.SetTextColor(colours[i])
        b = pv.AddText("%.3f"%I)
        b.SetTextColor(colours[i])
    l.SetY2(l.GetY1()+l.GetNRows()*l.GetTextSize()*1.25)
    epave("Set %s selection"%("A" if SEL=="NOM" else "B"),gStyle.GetPadLeftMargin()+0.01,1.-0.5*gStyle.GetPadTopMargin(),"left",1,0.046)
    epave("%.1f fb^{-1} (8 TeV)"%(19.8 if SEL=="NOM" else 18.3),1.-gStyle.GetPadRightMargin()-0.01,1.-0.5*gStyle.GetPadTopMargin(),"right",0,0.046)
    l.Draw()
    pv.Draw()
    gPad.Update()
    pv.SetY2NDC(pv.GetY1NDC()+len(pv.GetListOfLines())*pv.GetTextSize()*1.25*0.35/0.32)
    gPad.Update()
    
    c.SaveAs("plots/ROC_%s.pdf"%SEL)
    c.Write("ROC_%s.pdf"%SEL)
    
    c = TCanvas("c","c",1800,900)
    c.Divide(2,1)
    for h in [hCORS[4],hCORB[4]]:
        h.SetMarkerColor(kBlack)
    c.cd(1)
    gPad.SetGrid(1,1)
    gPad.SetTopMargin(0.14)
    gPad.SetRightMargin(0.13)
    for i in range(1,hCORS[4].GetNbinsX()+1): 
        hCORS[4].GetXaxis().SetBinLabel(i,variables[i-1])
        hCORS[4].GetYaxis().SetBinLabel(i,variables[i-1])
    hCORS[4].GetXaxis().SetLabelSize(0.034)
    hCORS[4].GetYaxis().SetLabelSize(0.034)
    hCORS[4].GetXaxis().SetLabelOffset(0.005)
    hCORS[4].LabelsOption("v","X")
    hCORS[4].Draw("colz,text")
    epavetext(["Correlation matrix (signal)","%s selection"%("Set A" if SEL=="NOM" else "Set B")],0.03,0.88,0.5,0.97)
    epavetext(["Linear correlation coefficients in %"],0.52,0.85,0.99,0.89,0.025,0)
    c.cd(2)
    gPad.SetGrid(1,1)
    gPad.SetTopMargin(0.14)
    gPad.SetRightMargin(0.13)
    for i in range(1,hCORB[4].GetNbinsX()+1): 
        hCORB[4].GetXaxis().SetBinLabel(i,variables[i-1])
        hCORB[4].GetYaxis().SetBinLabel(i,variables[i-1])
    hCORB[4].GetXaxis().SetLabelSize(0.034)
    hCORB[4].GetYaxis().SetLabelSize(0.034)
    hCORB[4].GetXaxis().SetLabelOffset(0.005)
    hCORB[4].LabelsOption("v","X")
    hCORB[4].Draw("colz,text")
    epavetext(["Correlation matrix (background)","%s selection"%("Set A" if SEL=="NOM" else "Set B")],0.03,0.88,0.5,0.97)
    epavetext(["Linear correlation coefficients in %"],0.52,0.85,0.99,0.89,0.025,0)
    c.SaveAs("plots/Correlation_%s.pdf"%SEL)
    c.Write("Correlation_%s.pdf"%SEL)


    for i in range(5):
        f[i].Close()
    
fout.Close()
