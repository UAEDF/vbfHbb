#!/usr/bin/env python

import sys,os,re

def latexTable():
	rawtable = []
	table = {}
	input = "start"
	print "raw table? "
	while not input=="":
		input = raw_input()
		rawtable += [input]

	massCounter = 0
	for line in rawtable: 
		if "===" in line: continue
		if "Creating datacard" in line:
			massCounter = int(re.search('m([0-9]{3})',line).group(1))
			table[massCounter] = {}
		if "cat#" in line: 
			catCounter = int(re.search('cat#([0-9]{1})',line).group(1))
			table[massCounter][catCounter] = {}
			fields = line.split()
			table[massCounter][catCounter]['data'] = fields[1].strip(',')
			table[massCounter][catCounter]['VBF']  = fields[2].strip(',')
			table[massCounter][catCounter]['GF']   = fields[3].strip(',')
			table[massCounter][catCounter]['Top']  = fields[4].strip(',')
			table[massCounter][catCounter]['Z']    = fields[5].strip(',')
			table[massCounter][catCounter]['S/B']  = fields[8].strip(',')


	for mass in sorted(table.keys()):
		print "MASS: %d"%mass
		print "-"*9
		#header
		print "%13s |"%"sample",
		for cat in table[mass].keys():
			print "%13s |"%cat,
		print
		print "-"*(16*(len(table[mass].keys())+1))
		
		# content
		for sample in sorted(table[mass][0].keys(),key=lambda x:['data','VBF','GF','Top','Z','S/B'].index(x)):
			if sample=='S/B': print "-"*(16*(len(table[mass].keys())+1))
			print "%13s |"%sample,
			for cat in table[mass].keys():
				print "%13s |"%table[mass][cat][sample],
			print
		print

	print
	print "\\begin{table}\n\t\\begin{tabular}{|r|%s}\\hline"%("r|"*(len(table[115][0].keys())+1))
	for mass in sorted(table.keys()):
		print "\t\t\\multicolumn{%d}{|l|}{MASS: %d}"%(len(table[115][0].keys())+2,mass),
		print "\\\\ \\hline"
		#header
		print "\t\t%13s &"%"sample",
		for cat in table[mass].keys():
			print "%13s %s"%(cat,"&" if not cat==table[mass].keys()[-1] else "\\\\ "),
		print "\\hline"
		
		# content
		for sample in sorted(table[mass][0].keys(),key=lambda x:['data','VBF','GF','Top','Z','S/B'].index(x)):
			if sample=='S/B': print "\\hline"
			print "\t\t%13s &"%sample,
			for cat in table[mass].keys():
				print "%13s %s"%(table[mass][cat][sample],"&" if not cat==table[mass].keys()[-1] else "\\\\ "),
			if not (sample=='S/B' or sample=='Z'): print
			elif sample=='S/B': 
				if mass==table.keys()[-1]: print "\\hline"
				else: print "\\hline\\hline"

	print "\t\end{tabular}\n\end{table}"

if __name__=='__main__':
	latexTable()
