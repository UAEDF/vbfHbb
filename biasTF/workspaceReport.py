#!/usr/bin/env python
import ROOT
from ROOT import *
from optparse import OptionParser
import os

mp = OptionParser()
opts,args = mp.parse_args()


symbols = {0:'\033[0;42;38m V \033[m', 1:'\033[0;41;38m C \033[m'}

print "\033[1;31mParameters VARIABLE or CONSTANT (BERNSTEIN)\033[m"
print "%52s | %8s |"%("filename","key"),
for i in range(6): print "%3s |"%("bN%d"%i),
for i in range(5): print "%3s |"%("bP%d"%i),
print
print "-"*(55+11+6*6+6*5)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = ''.join(keys1)
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for i in range(6):
		a = w.obj("b%d_selNOM_CAT0"%i)
		if a: print "%3s |"%symbols[a.isConstant()],
		else: print "%3s |"%"- ",
	for i in range(5):
		a = w.obj("b%d_selVBF_CAT4"%i)
		if a: print "%3s |"%symbols[a.isConstant()],
		else: print "%3s |"%"- ",
	print	

print
print "\033[1;31mParameters VARIABLE or CONSTANT (TRANSFER)\033[m"
print "%52s | %8s |"%("filename","key"),
for j in [1,2,3]:
	for i in range(4): print "%3s |"%("N%d-%d"%(j,i)),
for j in [5,6]:
	for i in range(4): print "%3s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+11+7*4*3+7*4*2)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = ''.join(keys1)
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for j in [1,2,3]:
		for i in range(4):
			key = keys1[0]
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%key if not key=="" else "",i,j))
			if a: print " %4s |"%symbols[a.isConstant()],
			else: print "%4s |"%"- ",
	for j in [5,6]:
		for i in range(4):
			key = keys1[1]
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%key if not key=="" else "",i,j))
			if a: print " %4s |"%symbols[a.isConstant()],
			else: print "%4s |"%"- ",
	print

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter values (BERNSTEIN)\033[m"
print "%52s | %8s |"%("filename","key"),
for i in range(6): print "%6s |"%("bN%d"%i),
for i in range(5): print "%6s |"%("bP%d"%i),
print
print "-"*(55+11+9*6+9*5)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = ''.join(keys1)
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for i in range(6):
		a = w.obj("b%d_selNOM_CAT0"%i)
		if a: print "%6.3g |"%a.getVal(),
		else: print "%6.3g |"%"- ",
	for i in range(5):
		a = w.obj("b%d_selVBF_CAT4"%i)
		if a: print "%6.3g |"%a.getVal(),
		else: print "%6.3g |"%"- ",
	print	

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter errors (BERNSTEIN)\033[m"
print "%52s | %8s |"%("filename","key"),
for i in range(6): print "%6s |"%("bN%d"%i),
for i in range(5): print "%6s |"%("bP%d"%i),
print
print "-"*(55+11+9*6+9*5)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = ''.join(keys1)
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for i in range(6):
		a = w.obj("b%d_selNOM_CAT0"%i)
		if a: print "%6.3g |"%a.getError(),
		else: print "%6.3g |"%"- ",
	for i in range(5):
		a = w.obj("b%d_selVBF_CAT4"%i)
		if a: print "%6.3g |"%a.getError(),
		else: print "%6.3g |"%"- ",
	print	

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter values (TRANSFER)\033[m"
print "%52s | %8s |"%("filename","key"),
for j in [1,2,3]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+11+12*4*3)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = keys1[0] 
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for j in [1,2,3]:
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%key if not key=="" else "",i,j))
			if a: print "%9.3g |"%a.getVal(),
			else: print "%9s |"%"- ",
	print

print
print "%52s | %8s |"%("filename","key"),
for j in [5,6]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+11+12*4*2)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = keys1[1] 
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for j in [5,6]:
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%key if not key=="" else "",i,j))
			if a: print "%9.3g |"%a.getVal(),
			else: print "%9s |"%"- ",
	print	

print
print "\033[0;35m","#"*150,"\033[m"
print "\033[0;35m","#"*150,"\033[m"
print "\033[1;31mParameter errors (TRANSFER)\033[m"
print "%52s | %8s |"%("filename","key"),
for j in [1,2,3]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+11+12*4*3)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = keys1[0] 
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for j in [1,2,3]:
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%key if not key=="" else "",i,j))
			if a: print "%9.3g |"%a.getError(),
			else: print "%9s |"%"- ",
	print	

print
print "%52s | %8s |"%("filename","key"),
for j in [5,6]:
	for i in range(4): print "%9s |"%("N%d-%d"%(j,i)),
print
print "-"*(55+11+12*4*2)

for fname in args:
	fopen = TFile(fname,"read")
	w = fopen.Get("w")
	keys0 = [x for x in os.path.split(fname)[1].replace('.root','').split("_")]
	keys1 = keys0[keys0.index([x for x in keys0 if 'BRN' in x][0])+1:]
	key = keys1[1] 
	print "%52s |"%os.path.split(fname)[1],
	print "%8s |"%key,
	for j in [5,6]:
		for i in range(4):
			a = w.obj("trans%s_p%d_CAT%d"%("_%s"%key if not key=="" else "",i,j))
			if a: print "%9.3g |"%a.getError(),
			else: print "%9s |"%"- ",
	print	

