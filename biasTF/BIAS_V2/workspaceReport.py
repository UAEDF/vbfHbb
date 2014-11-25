#!/usr/bin/env python
import ROOT
from ROOT import *
from optparse import OptionParser
import os,re

mp = OptionParser()
opts,args = mp.parse_args()

NBRN=7

import os, sys

print "%52s | %40s | %40s |"%("filename","varname","formula")
print "-"*(55+43+43)
for fname in args:
	fnameShort = os.path.split(fname)[1]
	save = os.dup( sys.stdout.fileno() )
	newout = file( 'test.stdouterr', 'w' )
	os.dup2( newout.fileno(), sys.stdout.fileno() )
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	w.Print()
	os.dup2( save, sys.stdout.fileno() )
	newout.close()

	newout = file( 'test.stdouterr', 'r' )
	for line in newout.read().split('\n'):
		if 'Generic' in line: 
			v = re.search('.*::(.*)\[.*',line).group(1)
			o = w.obj(v)
			print "%52s | %40s | %60s |"%(fnameShort,v,o.GetTitle())
		if 'ProdPdf' in line and 'qcd_model' in line:
			v = re.search('.*::(.*)\[.*',line).group(1)
			o = w.obj(v)
			print "%52s | %40s | %60s |"%(fnameShort,v,o.getComponents().contentsString().replace(v,'').replace(',','*')[1:])
	newout.close()
	fopen.Close()
	print "-"*(55+43+63)
	os.remove("test.stdouterr")

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print

symbols = {0:'\033[0;42;38m V \033[m', 1:'\033[0;41;38m C \033[m'}

print "\033[1;31mParameters VARIABLE or CONSTANT (BERNSTEIN)\033[m"
print "%52s | %10s |"%("filename","key"),
for i in range(NBRN): print "%3s |"%("bN%d"%i),
for i in range(NBRN): print "%3s |"%("bP%d"%i),
print
print "-"*(55+13+6*NBRN+6*NBRN)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = ''.join(keys1)
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	for i in range(NBRN):
		a = w.obj("%s%d_selNOM_CAT0"%("b" if 'Fit' in fname or 'brn' in fname else "p",i))
		if a: print "%3s |"%symbols[a.isConstant()],
		else: print "%3s |"%"- ",
	for i in range(NBRN):
		a = w.obj("%s%d_selVBF_CAT4"%("b" if 'Fit' in fname or 'brn' in fname  else "p",i))
		if a: print "%3s |"%symbols[a.isConstant()],
		else: print "%3s |"%"- ",
	print	

print
print "\033[1;31mParameters VARIABLE or CONSTANT (TRANSFER)\033[m"
print "%52s | %10s |"%("filename","key"),
for j in [1,2,3]:
	for i in range(4): print "%3s |"%("N%d-%d"%(j,i)),
for j in [5,6]:
	for i in range(4): print "%3s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+13+7*4*3+7*4*2)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	key = re.search('.*Fit([A-Za-z0-9\-]*).*',fname).group(1) if re.search('.*Fit([A-Za-z0-9\-]*).*',fname) else ""
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	key = key.replace('FixedPOL','POL')
	keyhere = key
	for j in [1,2,3]:
		if '-' in key: keyhere = key.split('-')[0]
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%keyhere if not keyhere=="" else "",i,j))
			if a: print " %4s |"%symbols[a.isConstant()],
			else: print "%4s |"%"- ",
	for j in [5,6]:
		if '-' in key: keyhere = key.split('-')[1]
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%keyhere if not keyhere=="" else "",i,j))
			if a: print " %4s |"%symbols[a.isConstant()],
			else: print "%4s |"%"- ",
	print

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter values (BERNSTEIN)\033[m"
print "%52s | %10s |"%("filename","key"),
for i in range(NBRN): print "%6s |"%("bN%d"%i),
for i in range(NBRN): print "%6s |"%("bP%d"%i),
print
print "-"*(55+13+9*NBRN+9*NBRN)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = ''.join(keys1)
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	for i in range(NBRN):
		a = w.obj("%s%d_selNOM_CAT0"%("b" if 'Fit' in fname or "brn" in fname else "p",i))
		if a: print "%6.3g |"%a.getVal(),
		else: print "%6s |"%"- ",
	for i in range(NBRN):
		a = w.obj("%s%d_selVBF_CAT4"%("b" if 'Fit' in fname or "brn" in fname else "p",i))
		if a: print "%6.3g |"%a.getVal(),
		else: print "%6s |"%"- ",
	print	

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter errors (BERNSTEIN)\033[m"
print "%52s | %10s |"%("filename","key"),
for i in range(NBRN): print "%6s |"%("bN%d"%i),
for i in range(NBRN): print "%6s |"%("bP%d"%i),
print
print "-"*(55+13+9*NBRN+9*NBRN)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = ''.join(keys1)
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	for i in range(NBRN):
		a = w.obj("%s%d_selNOM_CAT0"%("b" if 'Fit' in fname or "brn" in fname else "p",i))
		if a: print "%6.3g |"%a.getError(),
		else: print "%6s |"%"- ",
	for i in range(NBRN):
		a = w.obj("%s%d_selVBF_CAT4"%("b" if 'Fit' in fname or "brn" in fname else "p",i))
		if a: print "%6.3g |"%a.getError(),
		else: print "%6s |"%"- ",
	print	

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter values (TRANSFER)\033[m"
print "%52s | %10s |"%("filename","key"),
for j in [1,2,3]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+13+12*4*3)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	key = re.search('.*Fit([A-Za-z0-9\-]*).*',fname).group(1) if re.search('.*Fit([A-Za-z0-9\-]*).*',fname) else ""
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	key = key.replace('FixedPOL','POL')
	keyhere = key
	for j in [1,2,3]:
		if '-' in key: keyhere = key.split('-')[0]
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%keyhere if not keyhere=="" else "",i,j))
			if a: print "%9.3g |"%a.getVal(),
			else: print "%9s |"%"- ",
	print

print
print "%52s | %10s |"%("filename","key"),
for j in [5,6]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+13+12*4*2)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	key = re.search('.*Fit([A-Za-z0-9\-]*).*',fname).group(1) if re.search('.*Fit([A-Za-z0-9\-]*).*',fname) else ""
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	key = key.replace('FixedPOL','POL')
	keyhere = key
	for j in [5,6]:
		if '-' in key: keyhere = key.split('-')[1]
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%keyhere if not keyhere=="" else "",i,j))
			if a: print "%9.3g |"%a.getVal(),
			else: print "%9s |"%"- ",
	print	

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter errors (TRANSFER)\033[m"
print "%52s | %10s |"%("filename","key"),
for j in [1,2,3]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+13+12*4*3)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	key = re.search('.*Fit([A-Za-z0-9\-]*).*',fname).group(1) if re.search('.*Fit([A-Za-z0-9\-]*).*',fname) else ""
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	key = key.replace('FixedPOL','POL')
	keyhere = key
	for j in [1,2,3]:
		if '-' in key: keyhere = key.split('-')[0]
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%keyhere if not keyhere=="" else "",i,j))
			if a: print "%9.3g |"%a.getError(),
			else: print "%9s |"%"- ",
	print	

print
print "%52s | %10s |"%("filename","key"),
for j in [5,6]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+13+12*4*2)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	key = re.search('.*Fit([A-Za-z0-9\-]*).*',fname).group(1) if re.search('.*Fit([A-Za-z0-9\-]*).*',fname) else ""
	print "%52s |"%os.path.split(fname)[1],
	print "%10s |"%key,
	key = key.replace('FixedPOL','POL')
	keyhere = key
	for j in [5,6]:
		if '-' in key: keyhere = key.split('-')[1]
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%keyhere if not keyhere=="" else "",i,j))
			if a: print "%9.3g |"%a.getError(),
			else: print "%9s |"%"- ",
	print	

