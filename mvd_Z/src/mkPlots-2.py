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

FOLDER = "."

colours = [kRed,kBlack,kOrange-2,kBlue,kGreen+3,kRed]
styles = [1,5,8,6,7,1]
labels = ["qq' system","b-tagging","q/g tagging","soft activity","angular dynamics"]
variables = ["|#Delta#eta_{qq'}|","|#eta_{b#bar{b}}|","b-jet_{1} b-tag","b-jet_{0} QGL","b-jet_{1} QGL","q-jet_{0} QGL","q-jet_{1} QGL"]

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

for SEL in ["Z"]:
    N = 1
    f = [None]*N
    hSB = [None]*N
    hCORS = [None]*N
    hCORB = [None]*N
    hBDTS = [None]*N
    hBDTB = [None]*N
    hBDTST = [None]*N
    hBDTBT = [None]*N
    f[0] = TFile.Open("%s/BDT_%s.root"%(FOLDER,SEL),"read")
    hSB[0] = f[0].Get("Method_Fisher/Fisher/MVA_Fisher_rejBvsS")
    hCORS[0] = f[0].Get("CorrelationMatrixS")
    hCORB[0] = f[0].Get("CorrelationMatrixB")
    hBDTS[0] = f[0].Get("Method_Fisher/Fisher/MVA_Fisher_S")
    hBDTB[0] = f[0].Get("Method_Fisher/Fisher/MVA_Fisher_B")
    hBDTST[0] = f[0].Get("Method_Fisher/Fisher/MVA_Fisher_Train_S")
    hBDTBT[0] = f[0].Get("Method_Fisher/Fisher/MVA_Fisher_Train_B")
    
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
    
    pv = TPaveText(0.15,gStyle.GetPadBottomMargin()+0.05,0.25,0.6,"NDC")
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
    for i,h in enumerate(hSB):
        #h.SetLineColor(i+1)
        h.SetLineColor(colours[i])
        h.SetLineStyle(styles[i])
        h.SetLineWidth(2)
        h.Draw("same,L")
        I = h.Integral()/h.GetNbinsX()
#        a = l.AddEntry(h,labels[i],"L")
#        a.SetTextColor(colours[i])
        b = pv.AddText("ROC area: %.3f"%I)
#        b.SetTextColor(colours[i])
        b.SetTextFont(62)
    l.SetY2(l.GetY1()+l.GetNRows()*l.GetTextSize()*1.25)
    epave("%s selection"%("Set A" if SEL=="NOM" else ("Set B" if SEL=="VBF" else "Z")),gStyle.GetPadLeftMargin()+0.01,1.-0.5*gStyle.GetPadTopMargin(),"left",1,0.046)
    epave("%.1f fb^{-1} (8 TeV)"%(19.8 if (SEL=="NOM" or SEL=="Z") else 18.3),1.-gStyle.GetPadRightMargin()-0.01,1.-0.5*gStyle.GetPadTopMargin(),"right",0,0.046)
    #l.Draw()
    pv.Draw()
    gPad.Update()
    pv.SetY2NDC(pv.GetY1NDC()+len(pv.GetListOfLines())*pv.GetTextSize()*1.25*0.35/0.32)
    gPad.Update()
    
    c.SaveAs("plots/ROC_%s.pdf"%SEL)
    c.Write("ROC_%s.pdf"%SEL)
    
    c = TCanvas("c","c",1800,900)
    c.Divide(2,1)
    n = 0
    for h in [hCORS[n],hCORB[n]]:
        h.SetMarkerColor(kBlack)
    c.cd(1)
    gPad.SetGrid(1,1)
    gPad.SetTopMargin(0.14)
    gPad.SetRightMargin(0.13)
    for i in range(1,hCORS[n].GetNbinsX()+1): 
        hCORS[n].GetXaxis().SetBinLabel(i,variables[i-1])
        hCORS[n].GetYaxis().SetBinLabel(i,variables[i-1])
    hCORS[n].GetXaxis().SetLabelSize(0.034)
    hCORS[n].GetYaxis().SetLabelSize(0.034)
    hCORS[n].GetXaxis().SetLabelOffset(0.005)
    hCORS[n].LabelsOption("v","X")
    hCORS[n].Draw("colz,text")
    epavetext(["Correlation matrix (signal)","%s selection"%("Set A" if SEL=="NOM" else "Set B")],0.03,0.88,0.5,0.97)
    epavetext(["Linear correlation coefficients in %"],0.52,0.85,0.99,0.89,0.025,0)
    c.cd(2)
    gPad.SetGrid(1,1)
    gPad.SetTopMargin(0.14)
    gPad.SetRightMargin(0.13)
    for i in range(1,hCORB[n].GetNbinsX()+1): 
        hCORB[n].GetXaxis().SetBinLabel(i,variables[i-1])
        hCORB[n].GetYaxis().SetBinLabel(i,variables[i-1])
    hCORB[n].GetXaxis().SetLabelSize(0.034)
    hCORB[n].GetYaxis().SetLabelSize(0.034)
    hCORB[n].GetXaxis().SetLabelOffset(0.005)
    hCORB[n].LabelsOption("v","X")
    hCORB[n].Draw("colz,text")
    epavetext(["Correlation matrix (background)","%s selection"%("Set A" if SEL=="NOM" else "Set B")],0.03,0.88,0.5,0.97)
    epavetext(["Linear correlation coefficients in %"],0.52,0.85,0.99,0.89,0.025,0)
    c.SaveAs("plots/Correlation_%s.pdf"%SEL)
    c.Write("Correlation_%s.pdf"%SEL)

    c = TCanvas("c","c",900,700)
    c.cd(0)
    gStyle.SetStripDecimals(kFALSE)
    gPad.SetTopMargin(0.065)
    gPad.SetRightMargin(0.03)
    gPad.SetGrid(1,1)
#    hBDTST[n].GetXaxis().SetLimits(-1.0,1.0)
    hBDTST[n].SetFillColor(kBlue-9)
    hBDTST[n].SetLineColor(kBlue)
    hBDTST[n].SetFillStyle(1001)
    hBDTBT[n].SetFillColor(kRed)
    hBDTBT[n].SetLineColor(kRed)
    hBDTBT[n].SetFillStyle(3004)
    hBDTS[n].SetLineColor(kBlue)
    hBDTS[n].SetMarkerColor(kBlue)
    hBDTS[n].SetMarkerStyle(20)
    hBDTS[n].SetFillStyle(0)
    hBDTB[n].SetLineColor(kRed)
    hBDTB[n].SetMarkerColor(kRed)
    hBDTB[n].SetMarkerStyle(20)
    hBDTB[n].SetFillStyle(0)

    hBDTST[n].GetXaxis().SetTitle("BDT output")
    hBDTST[n].GetYaxis().SetTitle("A.U.")
    hBDTST[n].GetXaxis().SetLabelSize(0.04)
    hBDTST[n].GetYaxis().SetLabelSize(0.04)
    hBDTST[n].GetXaxis().SetTitleSize(0.05)
    hBDTST[n].GetYaxis().SetTitleSize(0.05)
    hBDTST[n].GetXaxis().SetLabelOffset(0.005)
    hBDTST[n].GetXaxis().SetTitleOffset(1.04)
    hBDTST[n].GetYaxis().SetTitleOffset(1.05)
    hBDTST[n].Draw("hist")
    hBDTBT[n].Draw("hist,same")
    hBDTS[n].Draw("p,same")
    hBDTB[n].Draw("p,same")
    
    gPad.Update()

    l = TLegend(0.15,0.7,0.49,1.-0.02-gPad.GetTopMargin())
    l.SetBorderSize(0)
    l.SetFillStyle(0)
    l.SetTextSize(0.04)
    l.SetTextFont(42)
    l.AddEntry(hBDTST[n],"Signal (train)","F")
    l.AddEntry(hBDTS[n],"Signal (test)","PL")
    l.AddEntry(hBDTBT[n],"Background (train)","F")
    l.AddEntry(hBDTB[n],"Background (test)","PL")
    l.SetY1(l.GetY2() - l.GetNRows()*l.GetTextSize()*1.2)
    l.Draw()

    epave("%s selection"%("Set A" if SEL=="NOM" else ("Set B" if SEL=="VBF" else "Z")),gPad.GetLeftMargin()+0.01,1.-0.5*gPad.GetTopMargin(),"left",1,0.045)
    c.SaveAs("plots/Training_%s.pdf"%SEL)
    c.Write("Training_%s.pdf"%SEL)

    for i in range(len(hSB)):
        f[i].Close()
    
fout.Close()
