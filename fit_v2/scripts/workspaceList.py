#!/usr/bin/env python

import os,sys,re,json,datetime,random,string
from glob import glob
from array import array
from optparse import OptionParser,OptionGroup
import warnings
warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='.*class stack<RooAbsArg\*,deque<RooAbsArg\*> >' )

basepath=os.path.split(os.path.abspath(__file__))[0]+"/../../"
sys.path.append(basepath+"common/")

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *

colours = ["\033[m"] + ["\033[%d;%dm"%(x,y) for (x,y) in [(0,z) for z in range(31,37)]+[(1,z) for z in range(31,37)]]

####################################################################################################
def parser(mp=None):
	if not mp: mp = OptionParser()
#
	mp.add_option('-v','--verbosity',help=colours[5]+'Verbosity.'+colours[0],default=0,action='count')
	mp.add_option('-q','--quiet',help=colours[5]+'Quiet.'+colours[0],default=True,action='store_false')
#
	mg1 = OptionGroup(mp,'Workspace list setup')
	mg1.add_option('--dummy',type='str')
	mp.add_option_group(mg1)
#
	return mp

####################################################################################################
def getParList(f,w):
	save = os.dup(sys.stdout.fileno())
	ftmp = 'tmp_%s.std'%(''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6)))
	newout = file(ftmp,'w')
	os.dup2(newout.fileno(),sys.stdout.fileno())
	w.Print()
	os.dup2(save,sys.stdout.fileno())
	newout.close()
	newout = file(ftmp,'r')
	
	inlines = []
	for line in newout.read().split('\n'):
		if line=="": continue
		inlines += [line]
	
	headers = ['variables','p.d.f.s','functions','datasets']
	lines = {}
	fillheader = None
	for iline,line in enumerate(inlines):
		headerchange = False
		linepre,linepost = inlines[max(0,iline-1)],inlines[min(iline+1,len(inlines)-1)]
		for h in headers:
			if h in line and "---" in linepost: 
				lines[h] = []
				fillheader = h
				headerchange = True
		if headerchange: continue
		if "---" in line: continue
		if fillheader: 
			lines[fillheader] += [line]
	newout.close()
	os.remove(ftmp)

	tmpvariables = (''.join(lines['variables'][0][1:-1])).split(',')
	lines['variables'] = {}
	for l in tmpvariables:
		lines['variables'][l] = {'name':l,'value':"%.6f"%w.var(l).getValV(),'error':"%.6f"%w.var(l).getError(),'type':'variable'}
	tmpdatasets = lines['datasets']
	lines['datasets'] = {}
	for l in tmpdatasets:
		typ,nam,var = re.search('(.*)::(.*)\((.*)\)',l).groups()[0:3]
		lines['datasets'][nam] = {'type':typ,'name':nam,'variable':var}
	tmpfunctions = lines['functions']
	lines['functions'] = {}
	for l in tmpfunctions:
		typ,nam,act,frm = re.search('(.*)::(.*)\[ actualVars=\((.*)\) formula="(.*)" \].*',l).groups()
		lines['functions'][nam] = {'type':typ,'name':nam,'function':frm,'parameters':act}
	tmppdfs = lines['p.d.f.s']
	lines['p.d.f.s'] = {}
	for l in tmppdfs:
		typ,nam,oth = re.search('(.*)::(.*)\[ (.*) \]',l).groups()
		if 'actualVar' in oth: 
			act,frm = re.search('actualVars=\((.*)\) formula="(.*)"',oth).groups()
			lines['p.d.f.s'][nam] = {'type':typ,'name':nam,'functions':frm,'parameters':act}
		elif 'coef' in oth:
			x,cf = re.search('x=(.*) coefList=\((.*)\)',oth).groups()
			lines['p.d.f.s'][nam] = {'type':typ,'name':nam,'variable':x,'coefficients':cf}
		elif 'mean=' in oth and 'sigma=' in oth:
			x,m,s = re.search('x=(.*) mean=(.*) sigma=(.*)',oth).groups()
			lines['p.d.f.s'][nam] = {'type':typ,'name':nam,'variable':x,'mean':m,'sigma':s}
		elif '=' in oth:
			lines['p.d.f.s'][nam] = {'type':typ,'name':nam}
			for part in oth.split(' '):
				x,y = re.search('(.*)=(.*)',part).groups()
				lines['p.d.f.s'][nam][x] = y
		elif '*' in oth:
			lines['p.d.f.s'][nam] = {'type':typ,'name':nam,'product':oth}
		else:
			lines['p.d.f.s'][nam] = {'type':typ,'name':nam,'other':oth}

	for k,v in lines.iteritems():
		for k1,v1 in sorted(v.iteritems(),key=lambda (x,y):(x)):
			print "\033[1;35m%-28s\033[m"%k1,
			for k2,v2 in sorted(v1.iteritems(),key=lambda (x,y):(not 'name' in x,not 'type' in x)):
				if 'name' in k2: continue 
				elif 'type' in k2: print "| \033[0;35m%-6s\033[m %15s"%(k2,v2),
				elif 'value' in k2: print "| \033[0;35m%-6s\033[m %15s"%(k2,v2),
				elif 'error' in k2: print "| \033[0;35m%-6s\033[m %15s"%(k2,v2),
				elif 'mean' in k2: print "| \033[0;35m%-6s\033[m %15s"%(k2,v2),
				elif 'sigma' in k2: print "| \033[0;35m%-6s\033[m %15s"%(k2,v2),
				elif 'variable' in k2: print "| \033[0;35m%-6s\033[m %15s"%("var",v2),
				elif 'parameters' in k2: print "| \033[0;35m%-6s\033[m %50s"%("pars",v2),
				elif 'function' in k2: print "| \033[0;35m%-6s\033[m %27s"%("fun",v2),
				elif 'coefficients' in k2: print "| \033[0;35m%-6s\033[m %100s"%("coef",v2),
				elif 'product' in k2: print "| \033[0;35m%-6s\033[m %100s"%("prod",v2),
				else: print "| \033[0;35m%-6s\033[m %15s"%(k2,v2),
			print " |"

   ##newout = file( 'test.stdouterr', 'r' )
   ##for line in newout.read().split('\n'):
   ##   if 'Generic' in line:
   ##      v = re.search('.*::(.*)\[.*',line).group(1)
   ##      o = w.obj(v)
   ##      print "%52s | %40s | %60s |"%(fnameShort,v,o.GetTitle())
   ##   if 'ProdPdf' in line and 'qcd_model' in line:
   ##      v = re.search('.*::(.*)\[.*',line).group(1)
   ##      o = w.obj(v)
   ##      print "%52s | %40s | %60s |"%(fnameShort,v,o.getComponents().contentsString().replace(v,'').replace(',','*')[1:])
   ##newout.close()

####################################################################################################
def workspaceList():
	mp = parser()
	opts,args = mp.parse_args()

	f = TFile(args[0],'read')
	w = f.Get("w")
	getParList(f,w)

####################################################################################################
if __name__=='__main__':
	workspaceList()
