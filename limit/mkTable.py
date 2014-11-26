#!/usr/bin/env python

import sys,os,re


fin = open("input.txt","r+")
lines = []
numbers = []
nblock = 0
masses = []
table = {}
for l in fin.read().split('\n'):
	if l=="": continue
	if "None" in l: continue
	lines += [l]
	if 'ex' in l: numbers += [[float(x) for x in re.search('x\[.\]=([0-9\.+\-]*), y\[.\]=([0-9\.+\-]*), exl\[.\]=([0-9\.+\-]*), exh\[.\]=([0-9\.+\-]*), eyl\[.\]=([0-9\.+\-]*), eyh\[.\]=([0-9\.+\-]*)',l).groups()]]
	else: numbers += [[float(x) for x in re.search('x\[.\]=([0-9\.+\-]*), y\[.\]=([0-9\.+\-]*)',l).groups()]]
	if not numbers[-1][0] in masses: masses += [numbers[-1][0]]
	else: 
		masses = [numbers[-1][0]]
		nblock += 1
	if nblock==0:
		table[(numbers[-1][0],"expected")] = [round(numbers[-1][1] + pow(-1,i+1)*x,6) for i,x in enumerate(numbers[-1][4:])]
	elif nblock==1:
		table[(numbers[-1][0],"expected")] = [round(numbers[-1][1] + pow(-1,i+1)*x,6) for i,x in enumerate(numbers[-1][4:])]+table[(numbers[-1][0],"expected")]
	elif nblock==2:
		table[(numbers[-1][0],"expected")] = [numbers[-1][1]]+table[(numbers[-1][0],"expected")]
	elif nblock==3:
		table[(numbers[-1][0],"observed")] = numbers[-1][1]
	elif nblock==4:
		table[(numbers[-1][0],"injected")] = numbers[-1][1]

fin.close()

#for k,v in sorted(table.iteritems()):
#	print k,v

ncols = 6
masses = [115,120,125,130,135]
positions = [0,3,1,2,4]
fout = open("tables.txt","w+")
fout.write('\\begin{tabular}{|*{%d}{c|}}\\hline\n'%ncols)
for n in ["observed","injected"]:
	fout.write('%15s &'%n)
	for i,mass in enumerate(masses):
		fout.write('%15.4f %s'%(table[(mass,n)],"&" if i<4 else "\\\\ \\hline"))
	fout.write('\n')
for ni,n in enumerate(["expected","expected -95\%","expected -68\%","expected +68\%","expected +95\%"]):
	fout.write('%15s &'%n)
	for i,mass in enumerate(masses):
		fout.write('%15.4f %s'%(table[(mass,"expected")][positions[ni]],"&" if i<4 else "\\\\ \\hline"))
	fout.write('\n')
fout.write('\\end{tabular}\n\n')

fout.close()
