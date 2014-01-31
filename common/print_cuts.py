#!/usr/bin/env python

import sys,os,json,array
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath)

from toolkit import *
from write_cuts import *
from weightFactory import *

import main
from optparse import OptionParser,OptionGroup

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from copy import deepcopy as dc
from array import array


####################################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mg1 = OptionGroup(mp,cyan+"print_cuts settings"+plain)
	mg1.add_option('--regex',help='Filter cuts with regex',default=[],type='str',action='callback',callback=optsplit)
	mg1.add_option('--regexveto',help='Filter cuts with regex veto',default=[],type='str',action='callback',callback=optsplit)
	mp.add_option_group(mg1)
	return mp

####################################################################################################

def print_cuts(opts):
	jsoncuts = json.loads(filecontent(opts.jsoncuts))
	for c,ccut in sorted(jsoncuts['sel'].iteritems(),key=lambda (k,v):k):
		if opts.regex:
			if any([re.match(r,c) for r in opts.regex]): continue
		if opts.regexveto: 
			if any([re.match(v,c) for v in opts.regexveto]): continue
		print blue+c+plain+': '+str(ccut).replace('u\'','\'')

########################################
if __name__=='__main__':
	mp = parser(main.parser())
	opts,args = mp.parse_args()

	print_cuts(opts)



# RUN EXAMPLE:
# ./../common/dependencyFactory.py -I ../common/vbfHbb_info.json -S ../common/vbfHbb_samples_SA_2012Paper.json -V ../common/vbfHbb_variables_2012Paper.json -C ../common/vbfHbb_cuts.json --nosample JetMon -t 'NOMMC' -p 'NOMold'
# ./../common/dependencyFactory.py -D ../common/vbfHbb_KK_defaultOpts.json --nosample JetMon -t 'NOMMC' -p 'NOMold' --weight "19000.,XSEC;LUMI;PU"
