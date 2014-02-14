#!/usr/bin/env python
import sys
tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from optparse import OptionParser

def listdir(ikey0,level,info):
	print ' '*level*2 + '++ ' + ikey0.GetName(),
	if not info:
		choice = raw_input(" rm ([n]/y/s(kip))? ",)
		if choice == "y":
			print "REMOVED."
			ikey0.Delete()
			return 0
		if choice == "s":
			print "SKIPPED."
			return 0
	else: print
	if ikey0.IsFolder():
		gDirectory.cd(ikey0.GetName())
		for ikey in gDirectory.GetListOfKeys():	
			listdir(ikey,level+1,info)
		gDirectory.cd('../')
		print

def clean(opts,args):
	f = TFile(args[0],"read" if opts.info else "update")
	f.cd()
	for ikey in gDirectory.GetListOfKeys(): 
		listdir(ikey,1,opts.info)
		print
	if not opts.info:
		f.Write()

if __name__=='__main__':
	mp = OptionParser()
	mp.add_option('-i','--info',help='Print only, no actions.',action='store_true',default=False)
	opts,args = mp.parse_args()

	clean(opts,args)
	
	
