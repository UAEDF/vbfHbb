#!/usr/bin/env python

import ROOT
from ROOT import *

import os,sys,re


basedir="/usb/data2/UAData/2015/"
basedir="/data/UAdata/"
N0 = -1#2000

fsave = TFile.Open("puReweight_SetB.root","recreate")

fd1 = TFile.Open("%s/flatTree_MultiJetA.root"%basedir,"read")
fd2 = TFile.Open("%s/flatTree_BJetPlusXB.root"%basedir,"read")
fd3 = TFile.Open("%s/flatTree_BJetPlusXC.root"%basedir,"read")
fd4 = TFile.Open("%s/flatTree_BJetPlusXD.root"%basedir,"read")
fq1 = TFile.Open("%s/flatTree_QCD100.root"%basedir,"read")
fq2 = TFile.Open("%s/flatTree_QCD250.root"%basedir,"read")
fq3 = TFile.Open("%s/flatTree_QCD500.root"%basedir,"read")
fq4 = TFile.Open("%s/flatTree_QCD1000.root"%basedir,"read")

td1 = fd1.Get("Hbb/events")
td2 = fd2.Get("Hbb/events")
td3 = fd3.Get("Hbb/events")
td4 = fd4.Get("Hbb/events")
tq1 = fq1.Get("Hbb/events")
tq2 = fq2.Get("Hbb/events")
tq3 = fq3.Get("Hbb/events")
tq4 = fq4.Get("Hbb/events")
hqp1 = fq1.Get("Hbb/pileup")
hqp2 = fq2.Get("Hbb/pileup")
hqp3 = fq3.Get("Hbb/pileup")
hqp4 = fq4.Get("Hbb/pileup")
tq1.SetWeight(18300./4.837581)
tq2.SetWeight(18300./98.05)
tq3.SetWeight(18300./3631.531688)
tq4.SetWeight(18300./28167.827502)

TRUE = ROOT.std.vector('bool')()
TRUE.push_back(1)
TRUE0 = TRUE[0]

ts = [td1,td2,td3,td4,tq1,tq2,tq3,tq4]
for t in ts:
    t.SetBranchStatus("*",0)
    for v in ["jetPt","mqq","dEtaqq","mjjTrig","dEtaTrig","rho","jetBtag","b1","b2","triggerResult","puWt","nvtx","npu"]:
        t.SetBranchStatus(v,1)

h1 = {}
h2 = {}
h3 = {}
h4 = {}
h5 = {}
h6 = {}
bins = {"rho":35,"nvtx":40,"npu":50,"jetPt[0]":120}
ymax = {"rho":35,"nvtx":40,"npu":50,"jetPt[0]":600}
for var in ["rho","npu","nvtx","jetPt[0]"]:
    h1[var] = TH1F("%sd"%var,"%s"%var,bins[var],0,bins[var])
    h2[var] = TH1F("%sq"%var,"%s"%var,bins[var],0,bins[var])
    h3[var] = TH1F("%sqcorr"%var,"%s"%var,bins[var],0,bins[var])
    h4[var] = TH1F("%sd2"%var,"%s"%var,bins[var],0,bins[var])
    h5[var] = TH1F("%sq2"%var,"%s"%var,bins[var],0,bins[var])
    h6[var] = TH1F("%sqcorr2"%var,"%s"%var,bins[var],0,bins[var])

td = [td1,td2,td3,td4]
for t in td:
    N = t.GetEntries()
    if N0>0: nn = float(N0)/float(N)
    else: nn = 1.
    for i,iev in enumerate(t):
        t.GetEntry(i)
        if N0>0 and i>N0: break
        if i%10000==0: print "%-10d/%10d"%(i,N)
        if iev.jetBtag[iev.b1[0]]>0.679 and iev.jetBtag[iev.b2[0]]>0.244 and iev.jetPt[3] > 30.0 and 0.5*(iev.jetPt[0]+iev.jetPt[1])>80.0 and iev.mqq[2]>700.0 and iev.mjjTrig>700.0 and iev.dEtaqq[2]>3.5 and iev.dEtaTrig>3.5:
            if iev.triggerResult[8]==TRUE0 or iev.triggerResult[9]==TRUE0 or iev.triggerResult[10]==TRUE0:
                for var in ["rho","npu","nvtx","jetPt[0]"]:
                    h4[var].Fill(eval("iev.%s"%var),nn)
                if iev.triggerResult[9]==TRUE0:
                    for var in ["rho","npu","nvtx","jetPt[0]"]:
                        h1[var].Fill(eval("iev.%s"%var),nn)

tq = [tq1,tq2,tq3,tq4]
hq = [hqp1,hqp2,hqp3,hqp4]
for ti,t in enumerate(tq):
    N = t.GetEntries()
    if N0>0: nn = t.GetWeight()*float(N0)/float(N)
    else: nn = t.GetWeight()
    for i,iev in enumerate(t):
        if N0>0 and i>N0: break
        if i%10000==0: print "%-10d/%10d"%(i,N)
        if iev.jetBtag[iev.b1[0]]>0.679 and iev.jetBtag[iev.b2[0]]>0.244 and iev.jetPt[3] > 30.0 and 0.5*(iev.jetPt[0]+iev.jetPt[1])>80.0 and iev.mqq[2]>700.0 and iev.mjjTrig>700.0 and iev.dEtaqq[2]>3.5 and iev.dEtaTrig>3.5:
            if iev.triggerResult[8]==TRUE0 or iev.triggerResult[9]==TRUE0 or iev.triggerResult[10]==TRUE0:
                for var in ["rho","npu","nvtx","jetPt[0]"]:
                    h5[var].Fill(eval("iev.%s"%var),nn)
                    h6[var].Fill(eval("iev.%s"%var),iev.puWt[0]*nn)
                if iev.triggerResult[9]==TRUE0:
                    for var in ["rho","npu","nvtx","jetPt[0]"]:
                        h2[var].Fill(eval("iev.%s"%var),nn)
                        h3[var].Fill(eval("iev.%s"%var),iev.puWt[3]*nn)

fsave.cd()
for var in ["rho","npu","nvtx","jetPt[0]"]:
    h1[var].Write()
    h2[var].Write()
    h3[var].Write()
    h4[var].Write()
    h5[var].Write()
    h6[var].Write()

fd1.Close()
fd2.Close()
fd3.Close()
fd4.Close()
fq1.Close()
fq2.Close()
fq3.Close()
fq4.Close()
fsave.Close()
