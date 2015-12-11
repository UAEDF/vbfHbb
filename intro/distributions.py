#!/usr/bin/env python

import os,sys,re,json,datetime
from glob import glob
from array import array
from optparse import OptionParser,OptionGroup

basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+"/../common/")

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from main import main 

col = ["\033[m"] + ["\033[%d;%dm"%(x,y) for (x,y) in [(0,z) for z in range(31,37)]+[(1,z) for z in range(31,37)]]

def parser(mp=None):
	if not mp: mp = OptionParser()
#	mp.add_option('','',help=col[5]+''+col[0],default='',type='',dest='')
#
#	mg1 = OptionGroup(mp,'GroupTitle')
#	mg1.add_option('','',help=col[5]+''+col[0],default='',type='',dest='')
#	mp.add_option_group(mg1)
#
	return mp

def thismain():
# Load main
    mp = parser()
    opts,fout,samples,variables = main(mp,False,True,True)
    localvariables = dict([(x,y) for (x,y) in variables.iteritems() if x in opts.variable])
# Samples and variables
    l1("Selected samples:")
    for s in samples: l2(s)
    l1("Selected variables:")
    for v in localvariables: l2(v)
# Sample loading
    fopen = {}
    for ks,vs in samples.iteritems():
        fopen[ks] = {}
        fopen[ks]['TFile'] = TFile.Open(vs['fname'],'read')
        fopen[ks]['TTree'] = fopen[ks]['TFile'].Get("Hbb/events")
        fopen[ks]['Scale'] = float(vs['scale'])
        fopen[ks]['TTree'].SetWeight(1./fopen[ks]['Scale'])
# Variable loop
    for kv,vv in localvariables.iteritems():
        hs = []
        for f in fopen:
            t = f['TTree']
            ht = "h_%s_%s"%(t.GetName(),kv)
            h = TH1F(ht,ht+";%s;%s"%(vv['titlex'],vv['titley']),vv['nbinsx'],vv['xmin'],vv['xmax'])
            t.Draw("%s>>%s"%(vv['var'],h.GetName()))
            hs += [h]
        ct = "c_%s"%(kv)
        c = TCanvas(ct,ct,900,750)
        hs[0].Draw("A")
        for h in hs: h.Draw("same")
        makeDirs("plots")
        c.SaveAs("plots/%s.pdf"%(c.GetName()))
        c.Close()
# Clean
    for f in fopen:
        f['TFile'].Close()
        fout.Close()

if __name__=='__main__':
	thismain()
