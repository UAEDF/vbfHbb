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

colours = ["\033[0;31m","\033[0;32m","\033[0;33m","\033[0;34m","\033[0;35m","\033[0;36m","\033[m"]

def listdir(ikey0,level,maxdepth):
	print ' '*level*2 + '++ ' + colours[level] + ikey0.GetName() + "\033[m"
	if ikey0.IsFolder():
		gDirectory.cd(ikey0.GetName())
		for ikey in sorted(gDirectory.GetListOfKeys()):	
			if level<maxdepth: listdir(ikey,level+1,maxdepth)
		gDirectory.cd('../')
	#	print

def list(opts,args):
	f = TFile(args[0],"read")
	f.cd()
	for ikey in gDirectory.GetListOfKeys(): 
		listdir(ikey,1,opts.depth)
		print

if __name__=='__main__':
	mp = OptionParser()
#	mp.add_option('-i','--info',help='Print only, no actions.',action='store_true',default=False)
	mp.add_option('-d','--depth',help='Maximum depth to print.',type='int',default=2)
	opts,args = mp.parse_args()

	list(opts,args)
	
	
