#!/usr/bin/env python

import os,sys,re,shutil,glob

if not os.system('[ "`root-config --version`" == "5.34/03" ]') == 0: sys.exit('Wrong ROOT version. Stopping.')

def main():
	dX=0.1
	XBOUNDSS=[[80,200]] #[80,230],[80,240]] #[80,250],[80,260]]
	XMAXDIFF=0
	
	BRNALTS=[\
	]
	#["expPow"],\
	#["tanh"],\
	#["modG"],\
	#["sine1"],\
	#["brn4"],\
	#["brn5"],\
	#["brn6"],\
	
	TRFALTS=[\
	["POL1-POL2"],\
	]
	###["EXPO"],\
	###["FixedPOL1"],\
	###["FixedPOL2"],\
	###["POL1"],\
	###["POL2"],\
	#["BRN"],\
	#["EXPO"],\
	#["FixedPOL1"],\
	#["FixedPOL2"],\
	#["FixedPOL3"],\
	#["POL1"],\
	#["POL2"],\
	#["POL3"],\
	
	BRNBASES=[[5,4]] #,[7,6]] #[6,5]
	
	CATBOUNDS=[0,6] # [0,3] # [4,6]
	CATVETOS=["","0,1,2,3","4,5,6","1","2","3","5","6"] ##"" ###,"1,2,3,4,5,6","0,2,3,4,5,6","0,1,3,4,5,6","0,1,2,4,5,6","0,1,2,3,5,6","0,1,2,3,4,6","0,1,2,3,4,5"] #,"2,3","1,3","1,2"] #["","6","5"] #["","2,3","1,3","1,2"] # ["5,6","4,6","4,5"] #string of vetos, comma separated.
	
	MASSES=[115,120,125,130,135] #[125]
	
	PREFIX="BiasV10plots_"
	
	#RUN = [False,False,False,False,False,False,False]
	#RUN = [False,False,False,True,False,False,False]
	RUN = [False]*0 + [True]*1 + [False]*0 + [True]*0 + [False]*5
		
	for XBOUNDS in XBOUNDSS:
		for BRNBASE in BRNBASES:
			FOLDER=("%slimit_BRN%dp%d_dX%.1f_B%d-%d%s_CAT%d-%d"%(PREFIX,BRNBASE[0],BRNBASE[1],dX,XBOUNDS[0],XBOUNDS[1],"" if XMAXDIFF==0 else "%d"%(XBOUNDS[1]+XMAXDIFF),CATBOUNDS[0],CATBOUNDS[1])).replace(".","p")
			print "\033[0;43m%100s\n%100s\n\033[1;31;43mWorking in %-100s\n\033[0;43m%100s\n%100s\033[m"%(" "," ",FOLDER," "," ")
		
			if RUN[0]==True:
				for TR in [[x] for x in list(set([x[0].replace('Fixed','') for x in TRFALTS]))]:
					ROOTTHIS("./src/TransferFunctions.C'(%d,%d,%d,%d,\"%s\",\"%s\",%d)'"%(XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],TR[0],FOLDER,XMAXDIFF))
		
			if RUN[1]==True:
				ROOTTHIS("./src/CreateBkgTemplates.C'(%d,%d,\"%s\",%d)'"%(XBOUNDS[0],XBOUNDS[1],FOLDER,XMAXDIFF))
		
			if RUN[2]==True:
				ROOTTHIS("./src/CreateSigTemplates.C'(%.2f,%d,%d,\"%s\",\"%s\",%d)'"%(dX,XBOUNDS[0],XBOUNDS[1],FOLDER,','.join(["%d"%x for x in MASSES]),XMAXDIFF))
		
			MASS=125
			if RUN[3]==True:
				for BR in BRNALTS:
					for FITWITHSIGNAL in ["false"]:
						ROOTTHIS("./src/CreateDataTemplates.C'(%.2f,%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",%s,%d,%d)'"%(dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],BRNBASE[0],BRNBASE[1],FOLDER,"",BR[0],FITWITHSIGNAL,MASS,XMAXDIFF))
				for TR in TRFALTS:
					ROOTTHIS("./src/CreateDataTemplates.C'(%.2f,%d,%d,%d,%d,%d,%d,\"%s\",\"%s\",\"%s\",%s,%d,%d)'"%(dX,XBOUNDS[0],XBOUNDS[1],CATBOUNDS[0],CATBOUNDS[1],BRNBASE[0],BRNBASE[1],FOLDER,TR[0],"","false",MASS,XMAXDIFF))
			
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
