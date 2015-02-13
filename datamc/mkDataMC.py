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
        Lsamples[n]['g'] = jsoninfo['groups'][samples[n]['tag'].replace('_sNOM','').replace('_sVBF','')]    # group
        Lsamples[n]['s'] = jsonsamp[n]['scale']                     # scale
        Lsamples[n]['i'] = samples[n]                               # info
    return jsoninfo, jsonvars, jsonsamp, Lsamples

def closeSamples(Lsamples):
    for s in Lsamples:
        s['f'].Close()

####################################################################################################
def hists(s,v,c):
    h = {}
    for sn,si in s.iteritems():
        for vn,vi in v.iteritems():
            for cn in c:
                st = si['i']['tag']
                vt = vn
                ct = cn
                ht = "h_s%s_v%s_c%s"%(st,vt,ct)
                binsize = (float(v['xmax'])-float(v['xmin']))/float(v['nbins_x'])
                h[ht] = TH1F(ht,ht+";%s;%s"%(v['title_x'],"Events / (%.2g)"%binsize),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
    return h
    
####################################################################################################
def datamc():
    mp = parser()
    opts,fout,samples,variables = main.main(mp,False,True,True)

    ROOTsetup()

    ji, jv, js, Lsamples = loadSamples(opts,samples)

    can = TCanvas("c","c",900,750)
    can.cd()

    for s in opts.selection:
        for t in opts.trigger:
            # cuts
            cut,cutlabel = write_cuts(s,t,reftrig=["None"],sample=Lsamples[Lsamples.keys()[0]]['i']['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
            cut1,cut2 = cut.split(' * ')[0][1:],cut.split(' * ')[1][:-1]
            #if opts.debug: l3("Cut %s: \n\t\t%s%s%s: \n\t\t%s"%("None",blue,cutlabel.split(' * ')[0][1:],plain,cut.split(' * ')[0][1:]))
            for sn,si in Lsamples.iteritems():
                st = si['i']['tag']
                sg = si['g']
                print st, sg
                ca,cal = write_cuts(s,t,reftrig=["None"],sample=st,jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
                ca1,ca2 = ca.split(' * ')[0][1:],ca.split(' * ')[1][:-1]
                for Ev in si['t']:
                    print Ev.jetPt[0]
                    print TCut(cut1).Eval()
    
    can.Close()

           
####################################################################################################
if __name__=='__main__':
    datamc()

