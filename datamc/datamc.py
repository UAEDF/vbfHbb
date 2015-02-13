#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

from optparse import OptionParser

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from write_cuts import *
import main

# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mg1 = OptionGroup(mp,cyan+"DataMc settings"+plain)

	mp.add_option_group(mg1)
	return mp

####################################################################################################
def ROOTsetup():
    gROOT.SetBatch(1)
    gROOT.ProcessLineSync(".x ../common/styleCMSTDR.C")
    gStyle.SetPadLeftMargin(0.15)
    gStyle.SetPadRightMargin(0.25)
    gStyle.SetPadTopMargin(0.06)
    gStyle.SetPadBottomMargin(0.135)
    gStyle.SetTitleOffset(1.01,"X")
    gStyle.SetTitleOffset(1.15,"Y")
    gStyle.SetTitleSize(0.050,"XY")
    gStyle.SetLabelSize(0.045,"XY")
    
####################################################################################################
def group(h):
    if "QCD" in h.GetName(): return "QCD"
    elif "ZJets" in h.GetName(): return "ZJets"
    elif "WJets" in h.GetName(): return "WJets"
    elif "TTJets" in h.GetName(): return "TTJets"
    elif "singleT" in h.GetName(): return "singleTop"
    else: return "Other"

####################################################################################################
def loadSamples(opts,samples):
    toLoad = []
    for s in samples.keys():
        if any(x in s for x in opts.sample) and not any(x in s for x in opts.nosample):
            toLoad += [s]
    Lsamples = {}
    jsoninfo = json.loads(filecontent(opts.jsoninfo))
    jsonvars = json.loads(filecontent(opts.jsonvars))['variables']
    jsonsamp = json.loads(filecontent(opts.jsonsamp))['files']
    for n in toLoad:
        Lsamples[n] = {}
        Lsamples[n]['f'] = TFile.Open(opts.globalpath+"/"+n,"read") # file
        Lsamples[n]['t'] = Lsamples[n]['f'].Get("Hbb/events")       # tree
        Lsamples[n]['s'] = jsonsamp[n]['scale']                     # scale
        Lsamples[n]['i'] = samples[n]                               # info
    return jsoninfo, jsonvars, jsonsamp, Lsamples

def closeSamples(Lsamples):
    for s in Lsamples:
        s['f'].Close()

####################################################################################################
def hists(v,s):
    h = {}
    for sn,si in s.iteritems():
        st = si['i']['tag']
        hn = "h_s%s_v%s"%(st,v['var'])
        binsize = (float(v['xmax'])-float(v['xmin']))/float(v['nbins_x'])
        h[sn] = TH1F(hn,hn+";%s;%s"%(v['title_x'],"Events / (%.2g)"%binsize),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
    return h
    
####################################################################################################
def datamc():
    mp = parser()
    opts,fout,samples,variables = main.main(mp,False,True,True)

    ROOTsetup()

    ji, jv, js, Lsamples = loadSamples(opts,samples)

    can = TCanvas("c","c",900,750)
    can.cd()

    for v in opts.variable:
        vi = variables[v]
        h = hists(vi,Lsamples)
        for sn,si in Lsamples.iteritems():
            ti = si['t']
            hi = h[sn]
            hi.SetLineColor(si['i']['colour'])
            hi.SetLineWidth(2)
            if not ("125" in hi.GetName() or "Data" in hi.GetName()): 
                hi.SetFillColor(si['i']['colour'])
                hi.SetLineColor(kBlack)
                hi.SetLineWidth(1)
            if "Data" in hi.GetName(): 
                hi.SetMarkerStyle(20)
                hi.SetMarkerSize(1.3)
            ti.Draw("%s>>%s"%(vi['root'],hi.GetName()),"%.8f"%(19821.*1./float(si['i']['scale']) if not "Data" in hi.GetName() else 1.0))
        p1 = TPad("p1","p1",0.0,0.0,1.0,1.0)
        p2 = TPad("p2","p2",0.0,0.0,1.0,1.0)
        p1.SetBottomMargin(0.3)
        p2.SetTopMargin(0.71)
        p1.Draw()
        p2.Draw()
        p2.SetFillStyle(-1)
        can.Update()
        st = None        
        rat = None
        toDraw = []
        hSorted = sorted(h.itervalues(),key=lambda v:("QCD" in v.GetName(),"ZJets" in v.GetName(),"TTJets" in v.GetName(),"singleT" in v.GetName(),"WJets" in v.GetName(),v.Integral()))
        gSorted = [group(x) for x in hSorted]
        for i,hi in enumerate(sorted(h.itervalues(),key=lambda v:("QCD" in v.GetName(),"ZJets" in v.GetName(),"TTJets" in v.GetName(),"singleT" in v.GetName(),"WJets" in v.GetName(),v.Integral()))):
            if i==0: 
                st = THStack("hs","hs;%s;%s"%(hi.GetXaxis().GetTitle(),hi.GetYaxis().GetTitle()))
                rat = hi.Clone("rat")
            if not ("125" in hi.GetName() or "Data" in hi.GetName()):
                print gSorted[i]
                if i+1<len(gSorted) and gSorted[i+1]==gSorted[i]: hi.SetLineColor(hi.GetFillColor())
                st.Add(hi)
                print hi.GetName(), hi.Integral()
            else:
                if "125" in hi.GetName(): hi.Scale(10.)
                toDraw += [hi]
        p1.cd()
        gPad.SetLogy(1)
        st.Draw()
        st.GetXaxis().SetLabelSize(0)
        st.GetXaxis().SetTitleSize(0)
        gPad.Update()
        for hi in toDraw: hi.Draw("same" if not "Data" in hi.GetName() else "Psame")
        p2.cd()
        rat.Draw()
        can.SaveAs("test.pdf")
           
####################################################################################################
if __name__=='__main__':
    datamc()

