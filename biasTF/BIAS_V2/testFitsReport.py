#!/usr/bin/env python

import os,sys,re

fopen = open("TestFit.log","r")

alts = ["expPow","tanh","modG","sine1","brn4","brn5","brn6"]
cats = ["CAT0","CAT1","CAT2","CAT3","CAT4","CAT5","CAT6"]
dxs = [0.1,0.2,0.5,1,2,2.5,5]
count = 0
cat = ""

found = {}

for line in fopen.read().split('\n'):

	if 'Current category' in line: 
		if count > 0:
			here = {'func':func,'nbins':nbins,'npars':npars,'dX':dX,'chi2red':chi2red,'chi2prob':chi2prob}
			found[(cat,func,dX)] = here

		cat = "CAT%d"%(int(re.search('Current category: ([0-9]*).*',line).group(1)))
		
		funcs = ""
		nbins = ""
		npars = ""
		dX = ""
		chi2red = ""
		chi2prob = ""

	if 'ERROR CALC' in line:
		func = re.search('.*] ([A-Za-z0-9]*)  .*',line).group(1).strip()
		if 'NBINS' in line: 
			nbins = re.search('.*NBINS.*: ([0-9.]*).*',line).group(1).strip()
		if 'NPARS' in line: 
			npars = re.search('.*NPARS.*: ([0-9.]*).*',line).group(1).strip()
		if re.search('.*](.*)  (.*)  .*:.*',line): 
			dX = float(re.search('.*](.*)  (.*)  .*:.*',line).group(2).strip())
		if 'CHI2 / NDOF' in line:
			chi2red = re.search('.*CHI2.*: *([0-9.]*).*',line).group(1).strip()
		if 'Probability chi' in line:
			chi2prob = re.search('.*Probability.*: *([0-9.]*).*',line).group(1).strip()
		count += 1

fopen.close()
here = {'func':func,'nbins':nbins,'npars':npars,'dX':dX,'chi2red':chi2red,'chi2prob':chi2prob}
found[(cat,func,dX)] = here

print "%5s %5s |"%("dX","CAT"),
for a in alts: print "%17s |"%a,
print
print "%11s |"%"",
for a in alts: print "%8s %8s |"%('X2red','X2prob'),
print
prevd = ""
for d in dxs:
	if not d == prevd: print "-"*(6+6+1+1+len(alts)*20)
	for c in cats:
		print "%5s %5s |"%(d,c),
		for a in alts:
			if (c,a,d) in found: print "%8.2f"%float(found[(c,a,d)]['chi2red']),
			if (c,a,d) in found: print "%s%8.2f%s |"%("\033[0;31m" if (float(found[(c,a,d)]['chi2prob'])<1e-5 or float(found[(c,a,d)]['chi2prob'])>(1-1e-5)) else "\033[m",float(found[(c,a,d)]['chi2prob']),"\033[m"),
			else: print "%17s |"%"-",
		print
	prevd = d
