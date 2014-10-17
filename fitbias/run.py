#!/usr/bin/env python

import os,sys,re,shutil,glob

if not os.system('[ "`root-config --version`" == "5.34/03" ]') == 0: sys.exit('Wrong ROOT version. Stopping.')

XBOUNDS = [80,200]
#FOLDER=("limit_BRN%d+%d_dX%.1f_%d-%d_CAT%d-%d%s"%(BRNORDER[0],BRNORDER[1],dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],"_CATmerge56" if MERGE=="true" else "")).replace(".","p")

RUN = [True]

#print "\033[1;31mWorking in %s\033[m"%FOLDER

if RUN[0]==True:
	rootcmd = "./testQCDmodels.C'(%.2f,%.2f,%d,\"%s\")'"%(XBOUNDS[0],XBOUNDS[1],4,"data_shapes_workspace_BRN5+4_POL1_BIDP.root")
	fullcmd = "root -b %s -q"%rootcmd
	print '\t',fullcmd
	os.system(fullcmd)
	print

