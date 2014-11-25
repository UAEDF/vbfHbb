#!/usr/bin/env python
import ROOT
from ROOT import *
from optparse import OptionParser
import os,sys

mp = OptionParser()
opts,args = mp.parse_args()

print "\033[1;31mYIELD VALUES\033[m"
print "%52s | %8s |"%("filename","tag"),
for i in range(4): print "%12s |"%("yN%d"%i),
for i in range(3): print "%12s |"%("yP%d"%i),
print
print "-"*(55+11+15*7)

tags = ['data','QCD','ZJets','Top']

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	for j,k in enumerate(tags):
		print "%52s |"%os.path.split(fname)[1],
		print "%8s |"%k,
		for i in range(4):
			a = w.obj("yield_%s_CAT%d"%(k,i))
			if a: print "%12.1f |"%(a.getVal()),
			else: print "%12s |"%"- ",
		for i in range(3):
			a = w.obj("yield_%s_CAT%d"%(k,i+4))
			if a: print "%12.1f |"%(a.getVal()),
			else: 
				b = w.obj("yield_%s_CAT%d%d"%(k,i+4,i+5))
				if b: print "%12.1f |"%(b.getVal()),
				else: print "%12s |"%"- ",
		print	

