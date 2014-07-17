#!/usr/bin/env python

import sys,os,re
from optparse import OptionParser
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from main import *

import lhapdf
import ROOT
from ROOT import *

####################################################################################################
####################################################################################################
####################################################################################################
def parser():
	mp = OptionParser()
	mp.add_option('-a','--verbosity',help="Verbosity.",action="count",default=0)
	mp.add_option('--main',help='run main reweighting.',action='store_true',default=False)
	mp.add_option('--alphas',help='run alphas reweighting.',action='store_true',default=False)
	mp.add_option('-P','--PDFS',help='List of PDFsets to use.',type='str',action='callback',callback=optsplit)
	return mp

####################################################################################################
####################################################################################################
####################################################################################################
def prepare(opts):
	lhapdf.setVerbosity(opts.verbosity)
	makeDirs(os.path.split(opts.fout)[0])
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	jsonvars = json.loads(filecontent(opts.jsonvars))
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsonpdfs = json.loads(filecontent("vbfHbb_pdfsets_2013.json"))
	jsons = {'samp':jsonsamp,'vars':jsonvars,'info':jsoninfo,'pdfs':jsonpdfs}
	return jsons

####################################################################################################
####################################################################################################
####################################################################################################
class sample():
	def __init__(self,opts,name,filename,npassed,xsec,scale):
		self.name = name
		self.filename = filename
		self.path = opts.globalpath
		self.npassed = float(npassed)
		self.xsec = float(xsec)
		self.scale = float(scale)
		self.file = TFile.Open('/'.join([self.path,self.filename]))
		self.tree = self.file.Get("Hbb/events")

####################################################################################################
####################################################################################################
####################################################################################################
class pdf():
	def __init__(self,name,tag,purpose,id):
		self.name = name
		self.tag = tag
		self.purpose = purpose
		self.id = id
		self.pdf = lhapdf.mkPDFs(self.name)
		self.nmem = len(self.pdf)
		self.wghts = std.vector('double')()
		self.wghts.resize(self.nmem)
	
	def mem(self,i):
		return self.pdf[i]

	def xfx(self,i,x,Q):
		return self.pdf[i].xfxQ(i,x,Q)

####################################################################################################
####################################################################################################
####################################################################################################
def mkUncPDF():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = prepare(opts)

########################################
	l1("List of samples:")
	SAMPLES = {}
	l2("| %20s | %20s | %20s | %20s |"%("sample","entries","cross section","scale factor"))
	l2("-"*(23+23+23+23+1)) 
	for s in sorted(samples): 
		S = sample(opts,jsons['samp']['files'][s]['tag'],s,jsons['samp']['files'][s]['npassed'],jsons['samp']['files'][s]['xsec'],jsons['samp']['files'][s]['scale'])	
		SAMPLES[S.name] = S
		l2("| %20s | %20.f | %20.3f | %20.6f |"%(S.name,S.npassed,S.xsec,S.scale))

########################################
	l1("List of PDF sets:")
	PSETS = {}
	l2("| %20s | %20s | %5s | %5s | %60s |"%("tag","purpose","id","nmem","name"))
	l2("-"*(23+23+8+8+63+1))
	for ps in opts.PDFS: 
		if not ps in jsons['pdfs']: sys.exit("\n%s!! %s unknown, exiting.%s\n"%(Red,ps,plain))
	for pstag,ps in sorted(jsons['pdfs'].iteritems(),key=lambda (x,y):(y['id'],not y['purpose']=='main',y['name'])):
		if not pstag in opts.PDFS: continue
		if (not opts.alphas) and ps['purpose']=='alphas': continue
		PS = pdf(ps['name'],ps['tag'],ps['purpose'],ps['id'])
		PSETS[PS.name] = PS
		l2("| %20s | %20s | %5d | %5d | %60s |"%(PS.tag,PS.purpose,PS.id,PS.nmem,PS.name))
		
########################################
########################################
########################################
	l1("Working with trees:")
	print opts.globalpath
	for kS,S in sorted(SAMPLES.iteritems(),key=lambda (x,y):(x)):
		l2("%s"%S.name)
		l3("Directory %s in %s"%(S.name,fout.GetName()))
		makeDirsRoot(fout,S.name)
		gDirectory.cd("%s:/%s"%(fout.GetName(),S.name))

		tnew = S.tree.CloneTree()
		PDFwghts = std.vector(std.vector('double'))()
		PDFwghts.resize(len(PSETS.keys()))
		bnew = tnew.Branch("PDFwghts","vector<vector<double> >",PDFwghts)
		nentries = tnew.GetEntries()

		for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
			l4("%s --> nmembers: %d --> filling wghts vector."%(PS.tag,PS.nmem))
			PS.wghts.resize(PS.nmem)

		for iev,ev in enumerate(tnew):
			if iev % int(float(nentries)/10.) == 0: l5("%d / %d"%(iev,nentries))
			for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
				for imem in range(PS.nmem):
#					pdf1 = 0.0
#					pdf2 = 0.0
#					pdfnew1 = 0.0
#					pdfnew2 = 0.0
					PS.wghts[imem] = 0.0
				PDFwghts[iPS] = PS.wghts
			bnew.Fill()
		
		tnew.Write()
		gDirectory.cd("%s:/"%(fout.GetName()))

########################################
########################################
########################################
	l1("Cleaning and closing:")
	for S in SAMPLES.itervalues(): 
		l2("Closing %s/%s."%(opts.globalpath,S.name))
		S.file.Close()
	l2("Closing %s."%(fout.GetName()))
	fout.Close()

########################################
########################################
########################################
	l1("Done.")

####################################################################################################
####################################################################################################
####################################################################################################
if __name__=='__main__':
	mkUncPDF()
