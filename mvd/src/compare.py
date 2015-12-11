#!/usr/bin/env python

import ROOT
from ROOT import *
import os,re,sys
sys.path.append('../common')
from array import array
from numpy import zeros
from datetime import datetime, timedelta
now = datetime.now

from toolkit import testimate
global paves
paves = []

##########################################################################
def epavetext(text,x1,y1,x2,y2,size=0.04,hl=1,fill=None):
    global paves
    p = TPaveText(x1,y1,x2,y2,"NDC")
    p.SetTextSize(size)
    p.SetTextFont(42)
    p.SetTextAlign(11)
    p.SetTextColor(kBlack)
    if fill==None:
        p.SetFillStyle(0)
    else:
        p.SetFillStyle(3002)
        p.SetFillColor(fill)
    p.SetBorderSize(0)
    for i,t in enumerate(text): 
        ti = p.AddText(t)
        if i==0: ti.SetTextFont(62)
    p.Draw("same")
    paves += [p]

####################################################################################################

PRINT = 0
MBB = 1

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetLineScalePS(1.8)
gROOT.ProcessLineSync(".x ../common/styleCMSTDR.C")
gStyle.SetPadRightMargin(0.02)
gStyle.SetPadLeftMargin(0.16)
gStyle.SetPadTopMargin(0.02)
gStyle.SetPadBottomMargin(0.12)
gROOT.SetBatch(1)
gStyle.SetTitleSize(0.05,"XY")
gStyle.SetLabelSize(0.04,"XY")
gStyle.SetTitleOffset(1.35,"Y")
gStyle.SetGridColor(17)
gStyle.SetPalette(1)

f1 = "./tmpcern/factory_BCanditate_NOM_BDT_GRAD.weights.xml"
f2 = "./weights/factory_NOM_Alt__BDT_GRAD2.weights.xml"
f3 = "./weights/kostas.NOM.xml"

F1 = TFile.Open("/usb/data2/UAData/2015/flatTree_VBFPowheg125.root","read")
F2 = TFile.Open("/usb/data2/UAData/fromKostas/autumn2013/flatTree_VBFPowheg125.root","read")
F3 = TFile.Open("/usb/data2/UAData/2015/trigger/flatTree_VBFPowheg125.root","read")

f = [f1,f2,f3]
F = [F1,F2,F3]

N = 100000
var0 = zeros(1,'float32')
var1 = zeros(1,'float32')
var2 = zeros(1,'float32')
var3 = zeros(1,'float32')

r1 = TMVA.Reader()
r2 = TMVA.Reader()
r3 = TMVA.Reader()

r1.AddVariable("btagIdx",var0)
r1.AddVariable("etaIdx", var1)
r1.AddVariable("btag",   var2)
r1.AddVariable("eta",    var3)
r1.BookMVA("BDT",f1)

r2.AddVariable("btag",   var2)
r2.AddVariable("eta",    var3)
r2.AddVariable("btagIdx",var0)
r2.AddVariable("etaIdx", var1)
r2.BookMVA("BDT",f2)

r3.AddVariable("btagIdx",var0)
r3.AddVariable("etaIdx", var1)
r3.AddVariable("btag",   var2)
r3.AddVariable("eta",    var3)
r3.BookMVA("BDT",f3)

T1 = F1.Get("Hbb/events")
T2 = F2.Get("Hbb/events")
T3 = F3.Get("Hbb/events")

T = [T1,T2,T3]
r = [r1,r2,r3]

if PRINT:
    for t in T:
        for iev,ev in enumerate(t):
            if iev>N: break
            if iev<N:
                blik1,blik2,blik3 = [[]]*4,[[]]*4,[[]]*4
                for jid in range(4):
                    var0[0],var1[0],var2[0],var3[0] = [ev.btagIdx[jid],ev.etaIdx[jid],ev.jetBtag[jid],ev.jetEta[jid]]
                    blik1[jid] = [r[0].EvaluateMVA("BDT"),jid]
                    blik2[jid] = [r[1].EvaluateMVA("BDT"),jid]
                    blik3[jid] = [r[2].EvaluateMVA("BDT"),jid]
                blikIdx1 = [x[1] for x in sorted(blik1,key=lambda (a,b):(a),reverse=True)]
                blikIdx2 = [x[1] for x in sorted(blik2,key=lambda (a,b):(a),reverse=True)]
                blikIdx3 = [x[1] for x in sorted(blik3,key=lambda (a,b):(a),reverse=True)]
                v = []
                for jid in range(4):
                    v += [TLorentzVector()]
                    v[-1].SetPtEtaPhiM(ev.jetPt[jid],ev.jetEta[jid],ev.jetPhi[jid],ev.jetMass[jid])
                mbb  = ev.mbb[1]
                mbbBLIK = (v[ev.blikNOMIdx[0]]+v[ev.blikNOMIdx[1]]).M()
                mbb1 = (v[blikIdx1[0]]+v[blikIdx1[1]]).M()
                mbb2 = (v[blikIdx2[0]]+v[blikIdx2[1]]).M()
                mbb3 = (v[blikIdx3[0]]+v[blikIdx3[1]]).M()
                if not (blikIdx1==blikIdx2 and blikIdx1==blikIdx3):
                    print "%3d%3d%3d%3d%10.2f%10.2f"%(ev.blikNOMIdx[0],ev.blikNOMIdx[1],ev.blikNOMIdx[2],ev.blikNOMIdx[3],mbb,mbbBLIK)
                    print "%3d%3d%3d%3d%10.2f"%(blikIdx1[0],blikIdx1[1],blikIdx1[2],blikIdx1[3],mbb1)
                    print "%3d%3d%3d%3d%10.2f"%(blikIdx2[0],blikIdx2[1],blikIdx2[2],blikIdx2[3],mbb2)
                    print "%3d%3d%3d%3d%10.2f"%(blikIdx3[0],blikIdx3[1],blikIdx3[2],blikIdx3[3],mbb3)
                    print
    
        print "="*150
        print "="*150

if MBB:
#    hmbb = TH2F("hmbb","hmbb;m_{b#bar{b}} (GeV);b-likelihood m_{b#bar{b}} (GeV)",140,0,700,140,0,700)
#    hmbb1 = TH1F("hmbb1","hmbb1;m_{b#bar{b}} (GeV)",50,0,250)
#    hmbb2 = TH1F("hmbb2","hmbb2;b-likelihood m_{b#bar{b}} (GeV)",50,0,250)
#    T3.Draw("mbb[1]:mbb[0]>>hmbb","triggerResult[0]==1||triggerResult[1]==1")
#    T3.Draw("mbb[0]>>hmbb1","triggerResult[0]==1||triggerResult[1]==1")
#    T3.Draw("mbb[1]>>hmbb2","triggerResult[0]==1||triggerResult[1]==1")
#    c = TCanvas("c","c",1800,900)
#    c.Divide(2,1)
#    c.cd(1)
#    hmbb.GetZaxis().SetRangeUser(1,4000)
#    hmbb.Draw("colz")
#    gPad.SetRightMargin(0.14)
#    gPad.SetLogz(1)
#    c.cd(2)
#    hmbb1.Scale(1./hmbb1.Integral())
#    hmbb2.Scale(1./hmbb2.Integral())
#    hmbb1.GetYaxis().SetRangeUser(0,0.12)
#    hmbb1.SetLineColor(kBlack)
#    hmbb1.SetLineStyle(kDashed)
#    hmbb2.SetLineColor(kGreen+2)
#    hmbb1.Draw()
#    hmbb2.Draw("same")
#    c.SaveAs("plots/compare_mbb-3.pdf")
#    c.Close()

    hmbb = TH2F("hmbb","hmbb;m_{b#bar{b}} (GeV);b-likelihood m_{b#bar{b}} (GeV)",140,0,700,140,0,700)
    hmbbb = TH2F("hmbbb","hmbbb;m_{b#bar{b}} (GeV);b-likelihood m_{b#bar{b}} (GeV)",140,0,700,140,0,700)
    hmbbc = TH2F("hmbbc","hmbbc;m_{b#bar{b}} (GeV);b-likelihood m_{b#bar{b}} (GeV)",140,0,700,140,0,700)
    hmbb1 = TH1F("hmbb1","hmbb1;m_{b#bar{b}} (GeV)",50,0,250)
    hmbb2 = TH1F("hmbb2","hmbb2;b-likelihood m_{b#bar{b}} (GeV)",50,0,250)
    hmbb3 = TH1F("hmbb3","hmbb3;b-likelihood m_{b#bar{b}} (GeV)",50,0,250)
    hmbb4 = TH1F("hmbb4","hmbb4;b-likelihood m_{b#bar{b}} (GeV)",50,0,250)
    nentries = T3.GetEntries()
    tref = now() 
    for iev,ev in enumerate(T3):
        if iev > N: break
        if iev%10000==0: 
            if not iev==0: test,pro = testimate(tref,iev,nentries)
            else: test,pro = [0,0],100
            print "%-8d/%8d (est. %dm %ds, %d%%)"%(iev,nentries,test[0],test[1],pro)
        blik1,blik2,blik3 = [[]]*4,[[]]*4,[[]]*4
        for jid in range(4):
            var0[0],var1[0],var2[0],var3[0] = [ev.btagIdx[jid],ev.etaIdx[jid],ev.jetBtag[jid],ev.jetEta[jid]]
            blik1[jid] = [r1.EvaluateMVA("BDT"),jid]
            blik2[jid] = [r2.EvaluateMVA("BDT"),jid]
            blik3[jid] = [r3.EvaluateMVA("BDT"),jid]
        blikIdx1 = [x[1] for x in sorted(blik1,key=lambda (a,b):(a),reverse=True)]
        blikIdx2 = [x[1] for x in sorted(blik2,key=lambda (a,b):(a),reverse=True)]
        blikIdx3 = [x[1] for x in sorted(blik3,key=lambda (a,b):(a),reverse=True)]
        v = []
        for jid in range(4):
            v += [TLorentzVector()]
            v[-1].SetPtEtaPhiM(ev.jetPt[jid],ev.jetEta[jid],ev.jetPhi[jid],ev.jetMass[jid])
        mbbblik1 = (v[blikIdx1[0]]+v[blikIdx1[1]]).M()
        mbbblik2 = (v[blikIdx2[0]]+v[blikIdx2[1]]).M()
        mbbblik3 = (v[blikIdx3[0]]+v[blikIdx3[1]]).M()
        hmbb.Fill(ev.mbb[1],mbbblik1)
        hmbbb.Fill(ev.mbb[1],mbbblik2)
        hmbbc.Fill(ev.mbb[1],mbbblik3)
        hmbb1.Fill(ev.mbb[1])
        hmbb2.Fill(mbbblik1)
        hmbb3.Fill(mbbblik2)
        hmbb4.Fill(mbbblik3)
    c = TCanvas("c","c",1800,1500)
    c.Divide(2,2)
    c.cd(1)
    hmbb.GetZaxis().SetRangeUser(1,4000)
    hmbb.Draw("colz")
    gPad.SetRightMargin(0.14)
    gPad.SetLogz(1)
    epavetext(["b-likelihood (CERN)"],0.45,0.90,0.80,0.96,0.04,1,kGray-2)
    c.cd(2)
    hmbbb.GetZaxis().SetRangeUser(1,4000)
    hmbbb.Draw("colz")
    gPad.SetRightMargin(0.14)
    gPad.SetLogz(1)
    epavetext(["b-likelihood (me)"],0.45,0.90,0.80,0.96,0.04,1,kGray-2)
    c.cd(3)
    hmbbc.GetZaxis().SetRangeUser(1,4000)
    hmbbc.Draw("colz")
    gPad.SetRightMargin(0.14)
    gPad.SetLogz(1)
    epavetext(["b-likelihood (kostas)"],0.45,0.90,0.80,0.96,0.04,1,kGray-2)
    c.cd(4)
    hmbb1.Scale(1./hmbb1.Integral())
    hmbb2.Scale(1./hmbb2.Integral())
    hmbb3.Scale(1./hmbb3.Integral())
    hmbb4.Scale(1./hmbb4.Integral())
    hmbb1.GetYaxis().SetRangeUser(0.004,0.5)
    hmbb1.SetLineColor(kBlack)
    hmbb1.SetLineStyle(kDashed)
    hmbb2.SetLineColor(kGreen+2)
    hmbb3.SetLineColor(kBlue)
    hmbb4.SetLineColor(kRed)
    hmbb1.Draw()
    hmbb2.Draw("same")
    hmbb3.Draw("same")
    hmbb4.Draw("same")
    gPad.SetLogy(1)
    l = TLegend(0.5,0.7,0.88,0.95)
    l.AddEntry(hmbb1,"CSV b-tag","L")
    l.AddEntry(hmbb2,"b-likelihood (CERN)","L")
    l.AddEntry(hmbb3,"b-likelihood (me)","L")
    l.AddEntry(hmbb4,"b-likelihood (Kostas)","L")
    l.SetBorderSize(0)
    l.SetFillStyle(0)
    l.SetTextSize(0.042)
    l.SetY1(l.GetY2()-l.GetNRows()*0.048)
    l.Draw()
    c.SaveAs("plots/compare_mbb-4.pdf")
    c.Close()

F1.Close()
F2.Close()
F3.Close()
