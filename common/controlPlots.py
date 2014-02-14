#!/usr/bin/env python

from string import Template
from glob import glob
import subprocess 
import threading
from time import sleep,strftime,gmtime,localtime
import Queue
import os,sys,shutil
from optparse import OptionParser,OptionGroup

def tasks(opts,workQueue):
#	kfac = {}
#	trg = "NOMMC"
#	dtrgs = ["NOM"]
#	extrano = ",DataVA,DataVB,DataVC,DataVD"

#	# two datatriggers --> 80 plots
#	for dtrg in dtrgs:
#		## (5x2) global
#		for opt in ['']:#,';FUN#mqq[2]#ht']:
#			vars = "dEtaqq1,mqq1,mbbReg1,ht,mvaVBF"
#			sel = "NOMplusPhi1;BtagMM0"
#			kfac = setKfac(opt,sel,kfac)
#			cmd = makeCmd(opt,sel,trg,dtrg,vars,kfac[opt],extrano,"19012.") 
#			workQueue.put((1 if "FUN" in opt else 10,cmd))
		
	kfac = {}
	trg = "VBF"
	dtrgs = ["VBFOR"]#,"VBF"]
	extrano = ",DataA,DataB,DataC,DataD"

	# two datatriggers --> 80 plots
	for dtrg in dtrgs:
		## (5x2) global
		for opt in ['',';FUN#mqq[2]#ht']:
			for vars in ["dEtaqq2,mqq2","mbbReg2,ht","mvaVBF","jetPt0,jetPt1"]:
				sel = "run194270;dEtaqq2;dPhi;mqq3600;BtagML0;nLeptons;NOMtrgveto"
				kfac = setKfac(opt,sel,kfac)
				cmd = makeCmd(opt,sel,trg,dtrg,vars,kfac[opt],extrano,"18000.") 
				workQueue.put((1 if "FUN" in opt else 10,cmd))
#		
#		## (5x2) global, extra ht cut
#		for opt in ['',';FUN#mqq[2]#ht']:
#			vars = "dEtaqq2,mqq2,mbbReg2,ht,mvaVBF"
#			sel = "run194270;dEtaqq2;dPhi;mqq3600;HT300;BtagML2"
#			kfac = setKfac(opt,sel,kfac)
#			cmd = makeCmd(opt,sel,trg,dtrg,vars,kfac[opt],extrano,"18000.") 
#			workQueue.put((1 if "FUN" in opt else 10,cmd))
#	
#		## (5x2) HTgt400
#		for opt in ['',';FUN#mqq[2]#ht']:
#			vars = "dEtaqq2,mqq2,mbbReg2,ht,mvaVBF"
#			sel = "run194270;dEtaqq2;dPhi;mqq3600;HTgt400;BtagML2"
#			kfac = setKfac(opt,sel,kfac)
#			cmd = makeCmd(opt,sel,trg,dtrg,vars,kfac[opt],extrano,"18000.") 
#			workQueue.put((1 if "FUN" in opt else 10,cmd))
#		
#		## (5x2) HTlt400 dEtaqq2,ht,mqq2
#		for opt in ['',';FUN#mqq[2]#ht']:
#			vars = "dEtaqq2,mqq2,mbbReg2,ht,mvaVBF"
#			sel = "run194270;dEtaqq2;dPhi;mqq3600;HT100;HTlt400;BtagML2"
#			kfac = setKfac(opt,sel,kfac)
#			cmd = makeCmd(opt,sel,trg,dtrg,vars,kfac[opt],extrano,"18000.") 
#			workQueue.put((1 if "FUN" in opt else 10,cmd))

####################################################################################################
####################################################################################################
def setKfac(opt,sel,kfac={}):
	inp = raw_input("%s: \033[1;31mKFAC\033[m(%s)\033[1;31m?\033[m "%(sel,opt))
	kfac[opt] = float(inp) if inp else None
	return kfac

####################################################################################################
####################################################################################################
def myparser():
	cyangrey = "\033[0;36;47m"
	cyan = "\033[0;36m"
	green = "\033[0;32m"
	plain = "\033[m"
	mp = OptionParser()
	mg0 = OptionGroup(mp,cyangrey+"Main options"+plain)
	mg0.add_option('--tag',help=cyan+'Suffix tag for filenames.'+plain,type='str',default='')
	mg0.add_option('-p','--print-only',help=cyan+'Only print commands to run.'+plain,action='store_true',default=False)
	mg0.add_option('-t','--threads',help=cyan+'Number of threads to use.'+plain,type='int',default=4)
	mg0.add_option('--delete',help=cyan+'Delete root files.'+plain,action='store_true',default=False)
	mg0.add_option('--no-colour',help=cyan+'B/W output.'+plain,action='store_true',default=False)
	mg0.add_option('--redo',help=cyan+'Rerun with existing file.',action='store_true',default=False)
	mg0.add_option('--first',help=cyan+'Only do redrawstack.',action='store_true',default=False)
	mp.add_option_group(mg0)
	return mp
	
def now():
	return strftime("%Y%m%d-%H%M%S",localtime())

####################################################################################################
####################################################################################################
def makeCmd(opt,sel,trg,dtrg,vars,kfac,extrano,lumi):
	cmd = ' '.join([ \
		baseline.safe_substitute(T=trg,DT=dtrg,EXTRANO=extrano),\
		options,\
		selection.safe_substitute(SEL=sel),\
		variables.safe_substitute(VARS=vars),\
		weight.safe_substitute(LUM=lumi,WEIGHT=opt,THEKFAC=str(kfac) if not kfac==None else ''),\
		])
	return cmd

def execCmd(opts,id,name,cmd):
	out = output.safe_substitute(SUFFIX=str(id) if not opts.redo else "",SUFTAG=opts.tag)
	redi = redirect.safe_substitute(REDI=id,SUFTAG=opts.tag)
	fullcmd = ' '.join([cmd,out,redi])

	if opts.no_colour: print "\033[1;31;42m%s processing\033[m:\n" % (name), fullcmd, '\n'
	else: print "\033[1;31;42m%s processing\033[m:\n" % (name),colours[id],fullcmd,'\n',colours[-1]

	if not opts.print_only:
		p = subprocess.Popen(fullcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		lstdout, lstderr = p.communicate()
	else: lstdout, lstderr = "",""
	return lstdout,lstderr

class myThread(threading.Thread):
    def __init__(self, opts, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
		self.stdout = None 
		self.stderr = None
		self.opts = opts
    def run(self):
		print "\033[1;31mStarting " + self.name + "\033[m\n"
		self.stdout,self.stderr = processData(self.opts,self.threadID,self.name,self.q)
		if not self.opts.print_only:
			print self.stdout
			print self.stderr
		print "\033[1;31mExiting " + self.name + "\033[m\n"

def processData(opts, threadID, threadName, q):
	global queueLock
	global workQueue
	global exitFlag
	stdout = ""
	stderr = ""
	while not exitFlag:
		queueLock.acquire()
		if not workQueue.empty():
			data = q.get()
			queueLock.release()
			for drawopt in drawopts: 
				if opts.redo and 're' in drawopt: continue
				if opts.first and not 're' in drawopt: continue
				lstdout,lstderr = execCmd(opts,threadID,threadName,' '.join([data[1],drawopt]))
				stdout += lstdout
				stderr += lstderr
		else:
			queueLock.release()
	return stdout,stderr	

####################################################################################################
# GLOBALS ##########################################################################################
colours = ["\033[0;31m","\033[0;32m","\033[0;33m","\033[0;34m","\033[0;35m","\033[0;36m","\033[m"]
drawopts = ["--redrawstack","--drawstack"]
exitFlag = 0
queueLock = None
workQueue = None

baseline=Template('''./mkHist.py -D "../common/vbfHbb_defaultOpts_2013.json" -G "/data/UAData/autumn2013" -t "$T" --datatrigger "$DT" --binning "mqq2;50;500;3000,mbb2;30;0;300,mqq1;50;500;3000,mbb1;30;0;300,ht;75;0;1500,dEtaqq2;60;2;8,mbbReg2;30;0;300,dEtaqq1;60;2;8,mbbReg1;30;0;300,jetPt0;40;0;400,jetPt1;30;0;300,mvaVBF;20;-1;1" --nosample "JetMon,VBF115,VBF120,VBF130,VBF135$EXTRANO"''')
selection=Template('''-p "$SEL"''')
weight=Template('''-w "$LUM,XSEC;LUMI;PU;KFAC$WEIGHT,,$THEKFAC,../trigger/rootfiles/vbfHbb_2DMaps_corrections_mqq2-ht.root;2DFits/2DFun_QCD-Rat_sdEtaqq2-jetPt1-run194270-tVBF-rAV40-dVBFOR_mqq2-ht_HT400AV40AV80;1"''')
options='''-d -K'''
variables=Template('''-v "$VARS"''')
#-
outputbase="vbfHbb_2013_2DFunCorrected_controlplots"
outputtemp=Template('''%s$SUFTAG'''%outputbase)
output=Template('''-o "rootfiles/%s$SUFTAG$SUFFIX.root"'''%outputbase)
redirect=Template('''>> log/log$REDI$SUFTAG.log''')

####################################################################################################
# MAIN #############################################################################################
def main():
	mp = myparser()
	opts,args = mp.parse_args()

	global queueLock
	global workQueue
	global exitFlag
	outputfile=outputtemp.safe_substitute(SUFTAG=opts.tag)
	
	nthreads = opts.threads if not (opts.print_only or opts.redo) else 1
	
	if not opts.print_only:
		if not os.path.exists('log/'): os.makedirs('log/')
		for i in range(nthreads):
			open('log/log%i%s.log'%((i+1),opts.tag),'w').close()
	
	if not opts.print_only:
		if opts.delete:
			if os.path.exists("rootfiles/%s.root"%outputfile): 
				os.remove("rootfiles/%s.root"%outputfile)
			for i in range(nthreads): 
				if os.path.exists("rootfiles/%s%i.root"%(outputfile,i+1)): os.remove("rootfiles/%s%i.root"%(outputfile,i+1))
		elif opts.redo:
			if not os.path.exists("rootfiles/%s.root"%outputfile): sys.exit("rootfiles/%s.root doesn't exist. Stopping."%outputfile)
		else:
			if os.path.exists("rootfiles/%s.root"%outputfile): 
				os.rename("rootfiles/%s.root"%outputfile,"rootfiles/%s.root.%s"%(outputfile,now()))
			for i in range(nthreads): 
				if os.path.exists("rootfiles/%s%i.root"%(outputfile,i+1)): sys.exit("rootfiles/%s%i.root exists. Stopping."%(outputfile,i+1))

	
	threadList = []
	for i in range(nthreads): threadList += ["Thread-%i"%(i+1)]
	queueLock = threading.Lock()
	workQueue = Queue.PriorityQueue(100)
	threads = []
	threadID = 1
	
	# Create new threads
	for tName in threadList:
	    thread = myThread(opts, threadID, tName, workQueue)
	    thread.start()
	    threads.append(thread)
	    threadID += 1
	
	# Fill the queue
	queueLock.acquire()
	tasks(opts,workQueue)
	queueLock.release()

	# Wait for queue to empty
	while not workQueue.empty():
	    pass
	
	# Notify threads it's time to exit
	exitFlag = 1
	
	# Wait for all threads to complete
	for t in threads:
	    t.join()
	print "\033[1;31;43mExiting Main Thread\033[m"
	
	if not (opts.print_only or opts.redo):
		allroot = []
		for i in range(nthreads): allroot += ["rootfiles/%s%i.root"%(outputfile,(i+1))]
		os.system("hadd rootfiles/%s.root "%outputfile + " ".join(allroot))
		for i in range(nthreads): 
			os.system("cp -RT plots/%s%i/ plots/%s/"%(outputfile,(i+1),outputfile))
			shutil.rmtree("plots/%s%i"%(outputfile,(i+1)))
			os.remove("rootfiles/%s%i.root"%(outputfile,(i+1)))
	
if __name__=='__main__':
	main()
