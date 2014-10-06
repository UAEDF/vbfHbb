#!/usr/bin/env python

import os,sys,re,shutil,glob

BRNORDER=[5,4]
dX=0.1
XBOUNDS=[80,200]
XBOUNDSTR=[80,200,80,200]
USETRANSFER="true"

TRINFO=[\
[1,"pol1","_POL1",1,"pol1","_POL1"],\
[2,"pol2","_POL2",2,"pol2","_POL2"],\
[3,"pol3","_POL3",3,"pol3","_POL3"],\
[1,"pol1","_ALT1",1,"pol1","_ALT1"],\
[2,"pol2","_ALT2",2,"pol2","_ALT2"],\
[3,"pol3","_ALT3",3,"pol3","_ALT3"],\
[2,"expo","_ALT4",2,"expo","_ALT4"]\
]

#[1,"pol1","_ALT0",2,"pol2","_ALT0"],\
#[1,"pol1","",2,"pol2",""],\
#[-1,"-1","_ALT4",-1,"-1","_ALT4"],\
#[2,"pow((x-[0]),[1])*exp([2]*x)","_ALT5",2,"pow((x-[0]),[1])*exp([2]*x)","_ALT5"],\
#[2,"[0]*(1.-x)*(1.-x)+[1]*2.*x*(1-x)+[2]*x*x","_ALT6",2,"[0]*(1.-x)*(1.-x)+[1]*2.*x*(1-x)+[2]*x*x","_ALT6"],\
CATBOUNDS=[0,6]
FOLDER=("limit_BRN%d+%d_dX%.1f_%d-%d_CAT%d-%d"%(BRNORDER[0],BRNORDER[1],dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1])).replace(".","p")
DATACARD=0

RUN = [False,False,False,False,True,True]
FRESHCOPY=False

print "\033[1;31mWorking in %s\033[m"%FOLDER

if RUN[0]==True:
	for TR in TRINFO:
		rootcmd = "./src/TransferFunctions.C'(%d,%d,%d,\"%s\",\"%s\",%d,%d,%d,\"%s\",\"%s\",\"%s\")'"%(XBOUNDSTR[0],XBOUNDSTR[1],TR[0],TR[1],TR[2],XBOUNDSTR[2],XBOUNDSTR[3],TR[3],TR[4],TR[5],FOLDER)
		fullcmd = "root -b %s -q"%rootcmd
		print '\t',fullcmd
		os.system(fullcmd)
		print

if RUN[1]==True:
	rootcmd = "./src/CreateBkgTemplates.C'(%d,%d,\"%s\")'"%(XBOUNDS[0],XBOUNDS[1],FOLDER)
	fullcmd = "root -b %s -q"%rootcmd
	print '\t',fullcmd
	os.system(fullcmd)
	print

if RUN[2]==True:
	rootcmd = "./src/CreateSigTemplates.C'(%.2f,%d,%d,\"%s\")'"%(dX,XBOUNDS[0],XBOUNDS[1],FOLDER)
	fullcmd = "root -b %s -q"%rootcmd
	print '\t',fullcmd
	os.system(fullcmd)
	print

if RUN[3]==True:
	for TR in TRINFO:
		rootcmd = "./src/CreateDataTemplates.C'(%.2f,%d,%d,%d,%d,\"%s\",%s,\"%s\",\"%s\",\"%s\",\"%s\")'"%(dX,XBOUNDS[0],XBOUNDS[1],BRNORDER[0],BRNORDER[1],FOLDER,USETRANSFER,TR[1],TR[2],TR[4],TR[5])
		fullcmd = "root -b %s -q"%rootcmd
		print '\t',fullcmd
		os.system(fullcmd)
		print

if RUN[4]==True:
	rootcmd = "./src/CreateDatacards.C'(%d,%d,%d,%d,%d,%d,\"%s\",\"%s\")'"%(CATBOUNDS[0],CATBOUNDS[1],BRNORDER[0],BRNORDER[1],TRINFO[DATACARD][0],TRINFO[DATACARD][3],FOLDER,TRINFO[DATACARD][2])
	fullcmd = "root -b %s -q"%rootcmd
	print '\t',fullcmd
	os.system(fullcmd)
	print

##
#OTHERCARDS
if RUN[5]==True:
	CATBOUNDS=[0,3]
	FOLDEROLD=FOLDER
	FOLDER=("limit_BRN%d+%d_dX%.1f_%d-%d_CAT%d-%d"%(BRNORDER[0],BRNORDER[1],dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1])).replace(".","p")
	if FRESHCOPY==True:
		shutil.copytree(FOLDEROLD,FOLDER)
		for f in glob.glob(FOLDER+"/output/datacards/*"): os.remove(f)
	rootcmd = "./src/CreateDatacards.C'(%d,%d,%d,%d,%d,%d,\"%s\",\"%s\")'"%(CATBOUNDS[0],CATBOUNDS[1],BRNORDER[0],BRNORDER[1],TRINFO[DATACARD][0],TRINFO[DATACARD][3],FOLDER,TRINFO[DATACARD][2])
	fullcmd = "root -b %s -q"%rootcmd
	print '\t',fullcmd
	os.system(fullcmd)
	print
	
	
	CATBOUNDS=[4,6]
	FOLDEROLD=FOLDER
	FOLDER=("limit_BRN%d+%d_dX%.1f_%d-%d_CAT%d-%d"%(BRNORDER[0],BRNORDER[1],dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1])).replace(".","p")
	if FRESHCOPY==True:
		shutil.copytree(FOLDEROLD,FOLDER)
		for f in glob.glob(FOLDER+"/output/datacards/*"): os.remove(f)
	rootcmd = "./src/CreateDatacards.C'(%d,%d,%d,%d,%d,%d,\"%s\",\"%s\")'"%(CATBOUNDS[0],CATBOUNDS[1],BRNORDER[0],BRNORDER[1],TRINFO[DATACARD][0],TRINFO[DATACARD][3],FOLDER,TRINFO[DATACARD][2])
	fullcmd = "root -b %s -q"%rootcmd
	print '\t',fullcmd
	os.system(fullcmd)
	print
