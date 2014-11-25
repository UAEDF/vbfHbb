#!/usr/bin/env python

import os,sys,re,shutil,glob

if not os.system('[ "`root-config --version`" == "5.34/03" ]') == 0: sys.exit('Wrong ROOT version. Stopping.')

def main():
	dX=0.1
	XBOUNDSS=[[80,250,10]]#[80,250,-25],[80,250,-10]] #[80,230],[80,240]] #[80,250],[80,260]]
	
	BRNALTS=[\
	["expPow"],\
	["tanh"],\
	["modG"],\
	["sine1"],\
	["brn4"],\
	["brn5"],\
	["brn6"],\
	]
	#["expPow"],\
	#["tanh"],\
	#["modG"],\
	#["sine1"],\
	#["brn4"],\
	#["brn5"],\
	#["brn6"],\
	
	TRFALTS=[\
	["BRN"],\
	]
	#["FixedPOL1"],\
	#["FixedPOL2"],\
	#["FixedPOL3"],\
	#["POL1"],\
	#["POL2"],\
	#["POL3"],\
	
	BRNBASES=[[6,6]] #,[7,6]] #[5,4]
	
	CATBOUNDS=[0,6] # [0,3] # [4,6]
	CATVETOS=["","0,1,2,3","4,5,6","1,2,3,4,5,6","0,2,3,4,5,6","0,1,3,4,5,6","0,1,2,4,5,6","0,1,2,3,5,6","0,1,2,3,4,6","0,1,2,3,4,5"] #,"2,3","1,3","1,2"] #["","6","5"] #["","2,3","1,3","1,2"] # ["5,6","4,6","4,5"] #string of vetos, comma separated.
	
	MASSES=[125]
	
	PREFIX="BiasV9_"
	
	#RUN = [False,False,False,False,False,False,False]
	#RUN = [False,False,False,True,False,False,False]
	RUN = [False]*1 + [True]*4
		
	for XBOUNDS in XBOUNDSS:
		for BRNBASE in BRNBASES:
			
			XMAXDIFF=XBOUNDS[2]

			FOLDER=("%slimit_BRN%dp%d_dX%.1f_B%d-%d%d_CAT%d-%d"%(PREFIX,BRNBASE[0],BRNBASE[1],dX,XBOUNDS[0],XBOUNDS[1],"" if XMAXDIFF==0 else XBOUNDS[1]+XMAXDIFF,CATBOUNDS[0],CATBOUNDS[1])).replace(".","p")
			print "\033[0;43m%100s\n%100s\n\033[1;31;43mWorking in %-100s\n\033[0;43m%100s\n%100s\033[m"%(" "," ",FOLDER," "," ")
		
			if RUN[0]==True:
				for TR in [[x] for x in list(set([x[0].replace('F','') for x in TRFALTS]))]:
					ROOTTHIS("./src/TransferFunctions.C'(%d,%d,%d,%d,\"%s\",\"%s\")'"%(XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],TR[0],FOLDER))
		
			if RUN[1]==True:
				ROOTTHIS("./src/CreateBkgTemplates.C'(%d,%d,\"%s\",%d)'"%(XBOUNDS[0],XBOUNDS[1],FOLDER,XMAXDIFF))
		
			for MASS in MASSES:
				if RUN[2]==True:
					ROOTTHIS("./src/CreateSigTemplates.C'(%.2f,%d,%d,\"%s\",%d,%d)'"%(dX,XBOUNDS[0],XBOUNDS[1],FOLDER,MASS,XMAXDIFF))
		
			if RUN[3]==True:
				for BR in BRNALTS:
					for FITWITHSIGNAL in ["false"]:
						ROOTTHIS("./src/CreateDataTemplates.C'(%.2f,%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",%s,%d)'"%(dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],BRNBASE[0],BRNBASE[1],FOLDER,"",BR[0],FITWITHSIGNAL,XMAXDIFF))
				for TR in TRFALTS:
					ROOTTHIS("./src/CreateDataTemplates.C'(%.2f,%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",%s,%d)'"%(dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],BRNBASE[0],BRNBASE[1],FOLDER,TR[0],"","false",XMAXDIFF))
			
			for CATVETO in CATVETOS:
				if RUN[4]==True:
					for TR in TRFALTS:
						for MASS in MASSES:
							ROOTTHIS("./src/CreateDatacards.C'(%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",%d,%d)'"%(XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],BRNBASE[0],BRNBASE[1],TR[0],FOLDER,CATVETO,MASS,XMAXDIFF))
		
def ROOTTHIS(rootcmd):
	fullcmd = "root -b %s -q"%rootcmd
	print '\033[1;34;48;5;227m\t',fullcmd,'\033[m'
	os.system(fullcmd)
	print

if __name__=='__main__':
	main()
