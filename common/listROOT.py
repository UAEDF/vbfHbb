#!/usr/bin/env python
import sys
sys.path.append('/home/salderwe/svncontrolled/2013/vbfHbb/turnons/include/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from optparse import OptionParser

def listdir(ikey0,level):
	print ' '*level*2 + '++ ' + ikey0.GetName()
	if ikey0.IsFolder():
		gDirectory.cd(ikey0.GetName())
		for ikey in gDirectory.GetListOfKeys():	
			listdir(ikey,level+1)
		gDirectory.cd('../')
		print

def list(opts,args):
	f = TFile(args[0],"read")
	f.cd()
	for ikey in gDirectory.GetListOfKeys(): 
		listdir(ikey,1)
		print

if __name__=='__main__':
	mp = OptionParser()
#	mp.add_option('-i','--info',help='Print only, no actions.',action='store_true',default=False)
	opts,args = mp.parse_args()

	list(opts,args)
	
	
