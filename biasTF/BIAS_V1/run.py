#!/usr/bin/env python

import os,sys,re,shutil,glob

if not os.system('[ "`root-config --version`" == "5.34/03" ]') == 0: sys.exit('Wrong ROOT version. Stopping.')

dX=0.1
XBOUNDS=[80,200]
XBOUNDSTR=[80,200,80,200]
USETRANSFER="false"

TRINFO=[\
[1,"pol1","_POL1",1,"pol1","_POL1"],\
[2,"pol2","_POL2",2,"pol2","_POL2"],\
[3,"pol3","_POL3",3,"pol3","_POL3"],\
[1,"pol1","_ALT1",1,"pol1","_ALT1"],\
[2,"pol2","_ALT2",2,"pol2","_ALT2"],\
[3,"pol3","_ALT3",3,"pol3","_ALT3"],\
[2,"expo","_ALT4",2,"expo","_ALT4"],\
]
#TRINFO=[\
#[1,"pol1","_POL1",-1,"-1","_BIDP"]\
#]
#TRINFO=[\
#[1,"pol1","_POL1",1,"pol1","_POL1"],\
#[2,"pol2","_POL2",2,"pol2","_POL2"],\
#]
TRINFO=[\
[-1,"-1","_BIDP",-1,"-1","_BIDP"]\
]

BRNORDERS=[[5,4]]
BRNALTS=[\
["","","",""],\
]

#["","","",""],\
#["","","expPow","_expPow"],\
#["","","tanh","_tanh"],\
#["","","modG","_modG"],\
#["","","sine1","_sine1"],\
#["","","brn4","_brn4"],\
#["","","brn5","_brn5"],\
#["","","brn6","_brn6"],\
#["","","brn7","_brn7"],\
#]

#[1,"pol1","_ALT0",2,"pol2","_ALT0"],\
#[1,"pol1","",2,"pol2",""],\
#[-1,"-1","_ALT4",-1,"-1","_ALT4"],\
#[2,"pow((x-[0]),[1])*exp([2]*x)","_ALT5",2,"pow((x-[0]),[1])*exp([2]*x)","_ALT5"],\
#[2,"[0]*(1.-x)*(1.-x)+[1]*2.*x*(1-x)+[2]*x*x","_ALT6",2,"[0]*(1.-x)*(1.-x)+[1]*2.*x*(1-x)+[2]*x*x","_ALT6"],\
CATBOUNDS=[0,6] # [0,3] # [4,6]
CATVETOS=["","4,5,6","0,1,2,3","1,2,3,4,5,6","0,2,3,4,5,6","0,1,3,4,5,6","0,1,2,4,5,6","0,1,2,3,5,6","0,1,2,3,4,6","0,1,2,3,4,5"] #,"2,3","1,3","1,2"] #["","6","5"] #["","2,3","1,3","1,2"] # ["5,6","4,6","4,5"] #string of vetos, comma separated.
MERGE="false"
FREETF=-1

for BRNORDER in BRNORDERS:
	PREFIX="BRNforAll_"
	FOLDER=("%slimit_BRN%d+%d_dX%.1f_%d-%d_CAT%d-%d%s"%(PREFIX,BRNORDER[0],BRNORDER[1],dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],"_CATmerge56" if MERGE=="true" else "")).replace(".","p")
	DATACARDS=[0] 
	
	#RUN = [False,False,False,False,False,False,False]
	RUN = [False,False,False,False,True,False,False]
	RUN = [False]*4 + [True]*1 + [False]*2
	FRESHCOPY=False
	
	print "\033[0;43m%100s\n%100s\n\033[1;31;43mWorking in %-100s\n\033[0;43m%100s\n%100s\033[m"%(" "," ",FOLDER," "," ")
	
	if RUN[0]==True:
		for TR in TRINFO:
			rootcmd = "./src/TransferFunctions.C'(%d,%d,%d,%d,%d,\"%s\",\"%s\",%d,%d,%d,\"%s\",\"%s\",\"%s\",%s)'"%(XBOUNDSTR[0],XBOUNDSTR[1],CATBOUNDS[0],CATBOUNDS[1],TR[0],TR[1],TR[2],XBOUNDSTR[2],XBOUNDSTR[3],TR[3],TR[4],TR[5],FOLDER,MERGE)
			fullcmd = "root -b %s -q"%rootcmd
			print '\t',fullcmd
			os.system(fullcmd)
			print
	
	if RUN[1]==True:
		rootcmd = "./src/CreateBkgTemplates.C'(%d,%d,\"%s\",%s)'"%(XBOUNDS[0],XBOUNDS[1],FOLDER,MERGE)
		fullcmd = "root -b %s -q"%rootcmd
		print '\t',fullcmd
		os.system(fullcmd)
		print
	
	if RUN[2]==True:
		rootcmd = "./src/CreateSigTemplates.C'(%.2f,%d,%d,\"%s\",%s)'"%(dX,XBOUNDS[0],XBOUNDS[1],FOLDER,MERGE)
		fullcmd = "root -b %s -q"%rootcmd
		print '\t',fullcmd
		os.system(fullcmd)
		print
	
	if RUN[3]==True:
		for TR in TRINFO:
			for BR in BRNALTS:
				rootcmd = "./src/CreateDataTemplates.C'(%.2f,%d,%d,%d,%d,%d,%d,\"%s\",%s,\"%s\",\"%s\",\"%s\",\"%s\",%s,\"%s\",\"%s\",\"%s\",\"%s\")'"%(dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],BRNORDER[0],BRNORDER[1],FOLDER,USETRANSFER,TR[1],TR[2],TR[4],TR[5],MERGE,BR[0],BR[1],BR[2],BR[3])
				fullcmd = "root -b %s -q"%rootcmd
				print '\t',fullcmd
				os.system(fullcmd)
				print
		
	for DATACARD in DATACARDS:
		for CATVETO in CATVETOS:
			if RUN[4]==True:
				for BR in BRNALTS:
					trhere = TRINFO[DATACARD][2] if TRINFO[DATACARD][2]==TRINFO[DATACARD][5] else TRINFO[DATACARD][2]+TRINFO[DATACARD][5]
					brhere = BR[1] if (BR[1]==BR[3]) else BR[1]+BR[3]
					rootcmd = "./src/CreateDatacards.C'(%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",\"%s\",%s,%d)'"%(CATBOUNDS[0],CATBOUNDS[1],BRNORDER[0],BRNORDER[1],TRINFO[DATACARD][0],TRINFO[DATACARD][3],FOLDER,trhere,brhere,CATVETO,MERGE,FREETF)
					fullcmd = "root -b %s -q"%rootcmd
					print '\t',fullcmd
					os.system(fullcmd)
					print
			
	##
	#OTHERCARDS
			if RUN[5]==True and not MERGE=="true":
				CATBOUNDS=[0,3]
				FOLDEROLD=FOLDER
				FOLDER=("%slimit_BRN%d+%d_dX%.1f_%d-%d_CAT%d-%d%s"%(PREFIX,BRNORDER[0],BRNORDER[1],dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],"_CATmerge56" if MERGE=="true" else "")).replace(".","p")
				if FRESHCOPY==True:
					shutil.copytree(FOLDEROLD,FOLDER)
					for f in glob.glob(FOLDER+"/output/datacards/*"): os.remove(f)
				else: 
					for f in glob.glob(FOLDEROLD+"/output/data*.root"): shutil.copy(f,FOLDER+'/'+os.path.split(f)[1])
				rootcmd = "./src/CreateDatacards.C'(%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",%s,%d)'"%(CATBOUNDS[0],CATBOUNDS[1],BRNORDER[0],BRNORDER[1],TRINFO[DATACARD][0],TRINFO[DATACARD][3],FOLDER,TRINFO[DATACARD][2]+("" if TRINFO[DATACARD][2]==TRINFO[DATACARD][5] else TRINFO[DATACARD][5]),CATVETO,MERGE,FREETF)
				fullcmd = "root -b %s -q"%rootcmd
				print '\t',fullcmd
				os.system(fullcmd)
				print
				
			if RUN[6]==True:
				CATBOUNDS=[4,6]
				FOLDEROLD=FOLDER
				FOLDER=("%slimit_BRN%d+%d_dX%.1f_%d-%d_CAT%d-%d%s"%(PREFIX,BRNORDER[0],BRNORDER[1],dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],"_CATmerge56" if MERGE=="true" else "")).replace(".","p")
				if FRESHCOPY==True:
					shutil.copytree(FOLDEROLD,FOLDER)
					for f in glob.glob(FOLDER+"/output/datacards/*"): os.remove(f)
				else: 
					for f in glob.glob(FOLDEROLD+"/output/data*.root"): shutil.copy(f,FOLDER+'/'+os.path.split(f)[1])
				rootcmd = "./src/CreateDatacards.C'(%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",%s,%d)'"%(CATBOUNDS[0],CATBOUNDS[1],BRNORDER[0],BRNORDER[1],TRINFO[DATACARD][0],TRINFO[DATACARD][3],FOLDER,TRINFO[DATACARD][2]+("" if TRINFO[DATACARD][2]==TRINFO[DATACARD][5] else TRINFO[DATACARD][5]),CATVETO,MERGE,FREETF)
				fullcmd = "root -b %s -q"%rootcmd
				print '\t',fullcmd
				os.system(fullcmd)
				print
