#!/usr/bin/env python

import ROOT
from ROOT import *

import os,sys,re

def partonIdx(event,i):
    idxs = [[x,event.partonMatchDR[x]] for x in range(len(event.partonMatchIdx)) if (event.partonMatchIdx[x]==i and event.partonMatchDR[x]<0.3)]
    if not len(idxs)>0: return None
    else: return idxs[0][0]

f = TFile.Open("flatTree_VBFPowheg125.root","read")
t = f.Get("Hbb/events")

TRUE = ROOT.std.vector('bool')()
TRUE.push_back(1)
TRUE0 = TRUE[0]

hsig_btag = TH1F("hsig_btag",";CSV b-tag value;N / (0.1)",110,-10,1)
hsig_btagRank = TH1F("hsig_btagRank",";CSV b-tag value;N / (1.0)",4,0,4)
hsig_eta = TH1F("hsig_eta",";#eta;N / (0.1)",100,-5,5)
hsig_etaRank = TH1F("hsig_etaRank",";#eta rank;N / (1.0)",4,0,4)

hbkg_btag = TH1F("hbkg_btag",";CSV b-tag value;N / (0.1)",110,-10,1)
hbkg_btagRank = TH1F("hbkg_btagRank",";CSV b-tag value;N / (1.0)",4,0,4)
hbkg_eta = TH1F("hbkg_eta",";#eta;N / (0.1)",100,-5,5)
hbkg_etaRank = TH1F("hbkg_etaRank",";#eta rank;N / (1.0)",4,0,4)

nentries = t.GetEntries()
for ievent,event in enumerate(t):
    if ievent%5000 == 0: print "%-8d/%8d"%(ievent,nentries)
    if ievent>500000: break
#    if event.jetBtag[event.b1[0]]>0.244 and event.jetBtag[event.b2[0]]>0.244 and event.jetPt[3]>40.0 and event.jetPt[2]>50.0 and event.jetPt[1]>70.0 and event.jetPt[0]>80.0 and event.dEtaqq[1]>2.5 and event.mqq[1]>250:
    if event.triggerResult[0]==TRUE0 or event.triggerResult[1]==TRUE0:
        for jid in range(4):
            pid = partonIdx(event,jid)
            if pid==None: break
            id = event.partonId[pid]
            btag = event.jetBtag[jid]
            eta = event.jetEta[jid]
            btagRank = list(event.btagIdx).index(jid)
            etaRank = list(event.etaIdx).index(jid)
            if abs(id)==5:
                hsig_btag.Fill(btag)
                hsig_btagRank.Fill(btagRank)
                hsig_eta.Fill(eta)
                hsig_etaRank.Fill(etaRank)
            else:
                hbkg_btag.Fill(btag)
                hbkg_btagRank.Fill(btagRank)
                hbkg_eta.Fill(eta)
                hbkg_etaRank.Fill(etaRank)

for h in [hsig_btag,hsig_btagRank,hsig_eta,hsig_etaRank]:
    h.SetFillStyle(1001)
    h.SetFillColor(kBlue-2)
    h.SetLineColor(kBlue)
for h in [hbkg_btag,hbkg_btagRank,hbkg_eta,hbkg_etaRank]:
    h.SetFillStyle(3004)
    h.SetFillColor(kRed)
    h.SetLineColor(kRed)

fsave = TFile("blikelihood.root","recreate")
for h in [hsig_btag,hsig_btagRank,hsig_eta,hsig_etaRank]:
    h.Write()
for h in [hbkg_btag,hbkg_btagRank,hbkg_eta,hbkg_etaRank]:
    h.Write()

hsig_btag.Scale(1./hsig_btag.Integral()) 
hsig_btagRank.Scale(1./hsig_btagRank.Integral())
hsig_eta.Scale(1./hsig_eta.Integral()) 
hsig_etaRank.Scale(1./hsig_etaRank.Integral()) 

hbkg_btag.Scale(1./hbkg_btag.Integral()) 
hbkg_btagRank.Scale(1./hbkg_btagRank.Integral())
hbkg_eta.Scale(1./hbkg_eta.Integral()) 
hbkg_etaRank.Scale(1./hbkg_etaRank.Integral()) 

c = TCanvas("c","c",900,750)
c.Divide(2,2)
c.cd(1)
hsig_btag.Draw()
hbkg_btag.Draw("same")
c.cd(2)
hsig_btagRank.Draw()
hbkg_btagRank.Draw("same")
c.cd(3)
hsig_eta.Draw()
hbkg_eta.Draw("same")
c.cd(4)
hsig_etaRank.Draw()
hbkg_etaRank.Draw("same")

c.SaveAs("blikelihood.pdf")


f.Close()
fsave.Close()
