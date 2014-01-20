#!/usr/bin/env python

from ROOT import *
import ROOT
import sys

def shrink(fname,cuts):
	fold = TFile.Open(fname)
	told = fold.Get("Hbb/events")
	told.SetBranchStatus("*",0)
	variables = ['ht','dEtaqq','dPhibb','mqq','mbbReg','jetBtag','jetPt','mjjMax','jetElf','jetMuf','b1','b2','triggerResult','puWt']
	for v in variables: told.SetBranchStatus(v,1)
	
	fnew = TFile(fname[:-5]+"_shrunk.root","recreate")
	fnew.mkdir("Hbb")
	gDirectory.cd("Hbb")
	tnew = TTree("events","events")
	tnew = told.CopyTree(cuts)
	tnew.Print()
	fnew.Write(fname[:-5]+'_shrunk.root',TH1.kOverwrite)

if __name__=='__main__':
	print sys.argv
	shrink(sys.argv[1],sys.argv[2])
