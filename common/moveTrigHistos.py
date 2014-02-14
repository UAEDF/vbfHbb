#!/usr/bin/env python

from optparse import OptionParser
import os,sys

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

def parser():
	mp = OptionParser()
	mp.add_option('--get',help='Read TriggerNames and TriggerPass from this file.',dest='get')
	mp.add_option('--put',help='Write TriggerNames and TriggerPass to this file.',dest='put')
	return mp

def main():
	mp = parser()
	opts,args = mp.parse_args()

	if not os.path.exists(opts.get): sys.exit('Input file doesn\'t exist!')
	#if not opts.new and not os.path.exists(opts.put): sys.exit('Output file doesn\'t exists!')
	if not os.path.exists(opts.put): print 'Output file doesn\'t exist, will be created.' 

	fin = TFile.Open(opts.get)
	t1 = fin.FindObjectAny('TriggerNames;1')
	if not t1: sys.exit('TriggerNames;1 not found!')
	t2 = fin.FindObjectAny('TriggerPass;1')
	if not t2: sys.exit('TriggerPass;1 not found!')
	
	if os.path.exists(opts.put): fout = TFile(opts.put,'update')
	else: 
		fout = TFile(opts.put,'recreate')
		fout.mkdir('Hbb')
	fout.cd('Hbb')
	if fout.FindObjectAny('TriggerNames;1'): sys.exit('TriggerNames;1 already exists!')
	if fout.FindObjectAny('TriggerPass;1'): sys.exit('TriggerPass;1 already exists!')
	t1.Write()
	t2.Write()
	print
	print "New file content: %s"%opts.put
	fout.ls()
	fout.Close()
	fin.Close()

if __name__=='__main__':
	main()

