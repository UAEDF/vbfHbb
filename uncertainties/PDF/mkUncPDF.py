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
	mp.add_option('--PDFS',help='List of PDFsets to use.',type='str',action='callback',callback=optsplit)
	mp.add_option('--ncut',help='Only run n events.',type='int',default=-1)
	mp.add_option('-P','--jsonpdfs',help='Json file for pdfs to be used.',default='',type='str')

	mp.add_option('--refPDF',help='Reference PDF.',type='str',action='callback',callback=optsplitlist)

	mp.add_option('--mkTree',help='Recreate flatTree weight branches.',action='store_true',default=False)
	mp.add_option('--rdTree',help='Read flatTree weight branches.',action='store_true',default=False)
	mp.add_option('--mkHistos',help='Recreate weighted histos.',action='store_true',default=False)
	mp.add_option('--rdHistos',help='Read weighted histos.',action='store_true',default=False)
	mp.add_option('--gendiv',help='Acceptance calculation instead of yields.',action='store_true',default=False)

	mp.add_option('--mvaBins',help='mva bins: var#3#1;3;6;9,...',type='str',action='callback',callback=optsplitdict)
	
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
	jsonpdfs = json.loads(filecontent(opts.jsonpdfs))
	jsons = {'samp':jsonsamp,'vars':jsonvars,'info':jsoninfo,'pdfs':jsonpdfs}
	# fix binning
	if opts.binning:
		for v in opts.binning:
			#print v
			jsons['vars']['variables'][v[0]]['nbins_x'] = v[1]
			jsons['vars']['variables'][v[0]]['xmin'] = v[2]
			jsons['vars']['variables'][v[0]]['xmax'] = v[3]
	return jsons

####################################################################################################
####################################################################################################
####################################################################################################
class sample():
	def __init__(self,opts,name,filename,npassed,xsec,scale,ref):
		self.name = name
		self.filename = filename
		self.path = opts.globalpath
		self.npassed = float(npassed)
		self.xsec = float(xsec)
		self.scale = float(scale)
		self.file = TFile.Open('/'.join([self.path,self.filename]))
		self.tree = self.file.Get("Hbb/events")
		self.ref = ref

####################################################################################################
####################################################################################################
####################################################################################################
class pdf():
	def __init__(self,name,tag,purpose,id,nmax,refname,reftag,refmem):
		self.name = name
		self.tag = tag
		self.purpose = purpose
		self.id = id
		self.pdf = lhapdf.mkPDFs(self.name)
		self.nmem = min(len(self.pdf),nmax) if nmax>0 else len(self.pdf)
		self.wghts = std.vector('double')()
		self.wghts.resize(self.nmem)
		self.wghtsalphas = std.vector('double')()
		self.wghtsalphas.resize(self.nmem)
		self.refname = refname
		self.reftag = reftag
		self.refmem = refmem
		self.refpdf = lhapdf.mkPDFs(self.refname)[self.refmem]
	
	def pdfmem(self,i):
		return self.pdf[i]

	def xfx(self,i,id,x,Q):
		return self.pdf[i].xfxQ(id,x,Q)

	def xfxref(self,id,x,Q):
		return self.refpdf.xfxQ(id,x,Q)

####################################################################################################
####################################################################################################
####################################################################################################
class hblock():
	def __init__(self,nmem):
		self.hs = [None]*nmem
		self.hp = None
		self.hm = None
		self.us = [None]*nmem
		self.up = None
		self.um = None
	
	def GetIBinH0(self,iBin):
		return self.hs[0].GetBinContent(iBin)

	def GetIBinU0(self,iBin):
		#return self.us[0].GetBinContent(iBin)
		return self.us[0].GetBinContent(1)

	def GetIBinHoverU0(self,iBin):
		#return self.hs[0].GetBinContent(iBin)/self.us[0].GetBinContent(iBin)
		return self.hs[0].GetBinContent(iBin)/self.us[0].GetBinContent(1)

	def GetIBinMemH(self,iBin,iMem,single=False):
		if not single: return self.hs[iMem].GetBinContent(iBin),self.hs[iMem+1].GetBinContent(iBin)
		else:          return self.hs[iMem].GetBinContent(iBin)

	def GetIBinMemU(self,iBin,iMem,single=False):
		#if not single: return self.us[iMem].GetBinContent(iBin),self.us[iMem+1].GetBinContent(iBin)
		#else:          return self.us[iMem].GetBinContent(iBin)
		if not single: return self.us[iMem].GetBinContent(1),self.us[iMem+1].GetBinContent(1)
		else:          return self.us[iMem].GetBinContent(1)

	def GetIBinMemHoverU(self,iBin,iMem,single=False):
		#if not single: return (self.hs[iMem].GetBinContent(iBin)/self.us[iMem].GetBinContent(iBin)),(self.hs[iMem+1].GetBinContent(iBin)/self.us[iMem+1].GetBinContent(iBin))
		#else:          return self.hs[iMem].GetBinContent(iBin)/self.us[iMem].GetBinContent(iBin)
		if not single: return (self.hs[iMem].GetBinContent(iBin)/self.us[iMem].GetBinContent(1)),(self.hs[iMem+1].GetBinContent(iBin)/self.us[iMem+1].GetBinContent(1))
		else:          return self.hs[iMem].GetBinContent(iBin)/self.us[iMem].GetBinContent(1)

	def GetIBinH(self,iBin):
		return self.hs[0].GetBinContent(iBin),self.hp.GetBinContent(iBin),self.hm.GetBinContent(iBin)
	
	def GetIBinU(self,iBin):
		#return self.us[0].GetBinContent(iBin),self.up.GetBinContent(iBin),self.um.GetBinContent(iBin)
		return self.us[0].GetBinContent(1),self.up.GetBinContent(1),self.um.GetBinContent(1)
	
	def GetIBinHoverU(self,iBin):
		#return (self.hs[0].GetBinContent(iBin)/self.us[0].GetBinContent(iBin)),(self.hp.GetBinContent(iBin)/self.up.GetBinContent(iBin)),(self.hm.GetBinContent(iBin)/self.um.GetBinContent(iBin))
		return (self.hs[0].GetBinContent(iBin)/self.us[0].GetBinContent(1)),(self.hp.GetBinContent(iBin)/self.up.GetBinContent(1)),(self.hm.GetBinContent(iBin)/self.um.GetBinContent(1))

####################################################################################################
####################################################################################################
####################################################################################################
class rblock():
	def __init__(self,nlab):
		self.rs = [None]*nlab
		self.rsacc = [None]*nlab
	
	def GetIBinLab(self,iLab,iBin):
		return self.rs[iLab].GetBinContent(iBin)

	def GetIBinLabs(self,iLabs,iBin):
		return [self.rs[iLab].GetBinContent(iBin) for iLab in iLabs]

	def SetIBinLab(self,iLab,iBin,value):
		self.rs[iLab].SetBinContent(iBin,value)

####################################################################################################
####################################################################################################
####################################################################################################
def mkUncPDF():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = prepare(opts)
	gROOT.ProcessLine("TH1::SetDefaultSumw2(1);")

########################################
	l1("List of samples:")
	SAMPLES = {}
	l2("| %20s | %20s | %20s | %20s | %20s |"%("sample","entries","cross section","scale factor","ref sample"))
	l2("-"*(23+23+23+23+23+1)) 
	for s in sorted(samples): 
		S = sample(opts,jsons['samp']['files'][s]['tag'],s,jsons['samp']['files'][s]['npassed'],jsons['samp']['files'][s]['xsec'],jsons['samp']['files'][s]['scale'],jsons['samp']['files'][s]['ref'])	
		SAMPLES[S.name] = S
		l2("| %20s | %20.f | %20.3f | %20.6f | %20s |"%(S.name,S.npassed,S.xsec,S.scale,S.ref))

########################################
	l1("List of PDF sets:")
	PSETS = {}
	l2("| %20s | %20s | %5s | %5s | %60s |"%("tag","purpose","id","nmem","name"))
	l2("-"*(23+23+8+8+63+1))
	if opts.PDFS:
		for ps in opts.PDFS: 
			if not any([ps in x for x in jsons['pdfs']]): sys.exit("\n%s!! %s unknown, exiting.%s\n"%(Red,ps,plain))
	reftag,refmem = opts.refPDF[0]
	refmem = int(refmem)
	refname = [x['name'] for x in jsons['pdfs'].itervalues() if x['tag']==reftag][0]
	for pstag,ps in sorted(jsons['pdfs'].iteritems(),key=lambda (x,y):(y['id'],not y['purpose']=='main',y['name'])):
		if opts.PDFS and not any([x in pstag for x in opts.PDFS]): continue
		if (not opts.alphas) and ps['purpose']=='alphas': continue
		PS = pdf(ps['name'],ps['tag'],ps['purpose'],ps['id'],ps['nmax'],refname,reftag,refmem)
		PSETS[PS.name] = PS
		l2("| %20s | %20s | %5d | %5d | %60s |"%(PS.tag,PS.purpose,PS.id,PS.nmem,PS.name))
	l2("-"*(23+23+8+8+63+1))
	l2("refpdf: %s(%s)"%(reftag,refmem))
		
########################################
########################################
########################################
	l1("Working with trees:")

	for kS,S in sorted(SAMPLES.iteritems(),key=lambda (x,y):(x)):
		l2("%s"%S.name)
		l3("Directory %s in %s"%(S.name,fout.GetName()))
		makeDirsRoot(fout,S.name)
		gDirectory.cd("%s:/%s"%(fout.GetName(),S.name))

####################

		if opts.mkTree:
			tnew = S.tree.CloneTree()
# container for wghts
			PDFwghts = std.vector(std.vector('double'))()
			PDFwghts.resize(len(PSETS.keys()))
			bnew = tnew.Branch("PDFwghts","vector<vector<double> >",PDFwghts)
# container for wghts alphas
			PDFwghtsalphas = std.vector(std.vector('double'))()
			PDFwghtsalphas.resize(len(PSETS.keys()))
			bnewalphas = tnew.Branch("PDFwghtsalphas","vector<vector<double> >",PDFwghtsalphas)
# container for labels
			PDFlabels = std.vector('TString')()
			PDFlabels.resize(len(PSETS.keys()))
			blabels = tnew.Branch("PDFlabels","vector<TString>",PDFlabels)
# nentries
			nentries = tnew.GetEntries()
	
# event loop
			pdf1, pdf2, newpdf1, newpdf2, alphas, newalphas = 0.,0.,0.,0.,0.,0.
			flagSkip=False
			for iev,ev in enumerate(tnew):
				if not opts.ncut==-1 and iev > opts.ncut: break
				if iev % int(float(nentries)/10.) == 0: l5("%d / %d"%(iev,nentries))
				flagSkip=False
				for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
# reference pdf
					pdf1 = PS.xfxref(ev.pdfID1,ev.pdfX1,ev.pdfQ)/ev.pdfX1
					pdf2 = PS.xfxref(ev.pdfID2,ev.pdfX2,ev.pdfQ)/ev.pdfX2
					alphas = PS.refpdf.alphasQ(ev.pdfQ)
# other pdfs
					for imem in range(PS.nmem if not ('+' in PS.purpose or '-' in PS.purpose) else 1):
						newpdf1 = PS.xfx(imem,ev.pdfID1,ev.pdfX1,ev.pdfQ)/ev.pdfX1
						newpdf2 = PS.xfx(imem,ev.pdfID2,ev.pdfX2,ev.pdfQ)/ev.pdfX2
						newalphas = PS.pdfmem(imem).alphasQ(ev.pdfQ)
# weights
						PS.wghts[imem] = newpdf1/pdf1*newpdf2/pdf2
						PS.wghtsalphas[imem] = newalphas/alphas

						if 'GF' in S.name:
							if PS.wghts[imem]>1.5 and (ev.pdfX1>0.7 or ev.pdfX2>0.7): 
								flagSkip=True
###						if PS.wghts[imem]>2.0 and (ev.pdfX1>0.8 or ev.pdfX2>0.8):  #VBF
###							print "wght new1 pdf1 new2 pdf2 imem iev Q x1 xfx1 x2 xfx2"
###							print "%12.2f | %12.9f %12.9f | %12.9f %12.9f | %8d %8d | %12.8f | %12.8f %12.8f | %12.8f %12.8f" % (PS.wghts[imem],newpdf1, pdf1, newpdf2, pdf2, imem, iev, ev.pdfQ, ev.pdfX1, PS.xfx(imem,ev.pdfID1,ev.pdfX1,ev.pdfQ), ev.pdfX2,PS.xfx(imem,ev.pdfID2,ev.pdfX2,ev.pdfQ))
	
					PDFwghts[iPS] = PS.wghts
					PDFwghtsalphas[iPS] = PS.wghtsalphas
					PDFlabels[iPS] = TString(PS.tag)

				# veto ridiculous weight factors
					if any([x>2000 for x in PS.wghts]): 
						flagSkip=True
						break
				if flagSkip==True: 
					l5('Skipped ev %d with bad weight.'%(iev))
					continue
# storing
				bnew.Fill()
				bnewalphas.Fill()
				blabels.Fill()
# writing and closing
			tnew.Write(tnew.GetName(),TH1.kOverwrite)

		gDirectory.cd("%s:/"%(fout.GetName()))

####################

	l1("Working with weights:")

	if opts.mkHistos:
		for kS,S in sorted(SAMPLES.iteritems(),key=lambda (x,y):(x)):

			if 'NOM' in S.name: allvariables = [x for x in opts.variable if not ('VBF' in x or '2' in x)]
			elif '5VBF' in S.name: allvariables = [x for x in opts.variable if not ('NOM' in x or '1' in x)]
			elif '5REF' in S.name: allvariables = [x for x in opts.variable if x=='plain']
			else: allvariables = opts.variable

			l2("%s"%S.name)
			l3("Directory %s_histos in %s"%(S.name,fout.GetName()))
			makeDirsRoot(fout,S.name+'_histos')
			gDirectory.cd("%s:/%s_histos"%(fout.GetName(),S.name))
			tree = fout.Get("%s/%s"%(S.name,"events"))
			tree.SetBranchStatus("*",0)
			nentries = tree.GetEntries()
			br = ['PDFlabels','PDFwghts','PDFwghtsalphas']
			bv = []
			for v in allvariables:
				v = jsons['vars']['variables'][v]
				if v['var']=='plain': continue
				bv += [v['bare']]
			for b in list(set(bv+br)):
				tree.SetBranchStatus(b,1)

			histos = {}
# loop over sets
			for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
				l4("%s(%d)"%(kPS,PS.nmem))
				histos[kPS] = {}
# loop over variables
				for v in allvariables:
					v = jsons['vars']['variables'][v]
					if 'REF' in S.name and not v['var']=='plain': continue
					if v['var'] in opts.mvaBins:
						v['nbins_x'] = opts.mvaBins[v['var']][0]
						v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
						v['xmin'] = opts.mvaBins[v['var']][1][0]
						v['xmax'] = opts.mvaBins[v['var']][1][-1]
					l5('var %s'%(v['var']))
					histos[kPS][v['var']] = hblock(PS.nmem)
# loop over tree
				for iev,ev in enumerate(tree):
					if opts.ncut>-1 and iev>=opts.ncut: break
					if (iev%int(nentries/10)==0): l6("%8s / %8s"%(iev,nentries))
					vPS = ev.PDFwghts[iPS]
					vPSas = ev.PDFwghtsalphas[iPS]
					PSl = ev.PDFlabels[iPS]
					if not PSl == TString(PS.tag): sys.exit("PDFs don't match (%s,%s). Exiting."%PSl.Data(),PS.tag)
# loop over variables and members
					for v in allvariables:
						v = jsons['vars']['variables'][v]
						if 'REF' in S.name and not v['var']=='plain': continue
						if v['var'] in opts.mvaBins:
							v['nbins_x'] = opts.mvaBins[v['var']][0]
							v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
							v['xmin'] = opts.mvaBins[v['var']][1][0]
							v['xmax'] = opts.mvaBins[v['var']][1][-1]
						hb = histos[kPS][v['var']]
						for imem in range(PS.nmem):
							if iev==0:
								hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,imem)
								if not 'xs' in v: hb.hs[imem] = TH1F(hname,hname,int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
								else: hb.hs[imem] = TH1F(hname,hname,int(v['nbins_x']),v['xs'])
							h = hb.hs[imem]
# fill histos
#							tree.Draw("%s>>%s"%(v['root'],h.GetName()),"(1.)*(PDFwghts[%d][%d])*(PDFwghtsalphas[%d][%d])"%(iPS,imem,iPS,imem),"",opts.ncut)
###							if 'mbbReg' in v['var']: 
###								if iev>20000 and ev.mbbReg[2] > 100 and ev.mbbReg[2] < 112 and imem>49 and (vPS[imem] < 0.25 or vPS[imem]>3): print "%12.6f %12.6f %12.1f %12d %12d" % (ev.mbbReg[2], vPS[imem], vPSas[imem], imem, iev)
							h.Fill(eval("ev.%s"%v['root']) if not v['var']=='plain' else 0.,vPS[imem]*vPSas[imem])
# save histos
				for v in allvariables:
					v = jsons['vars']['variables'][v]
					if 'REF' in S.name and not v['var']=='plain': continue
					for imem in range(PS.nmem):
#						h.Write(h.GetName(),TH1.kOverwrite)
						histos[kPS][v['var']].hs[imem].Write(histos[kPS][v['var']].hs[imem].GetName(),TH1.kOverwrite)
	
			gDirectory.cd("%s:/"%(fout.GetName()))
	
####################

	l1("Working with weighted histos:")

	if opts.mkHistos or opts.rdHistos:
		for kS,S in sorted(SAMPLES.iteritems(),key=lambda (x,y):(x)):
			
			if 'NOM' in S.name: allvariables = [x for x in opts.variable if not ('VBF' in x or '2' in x)]
			elif '5VBF' in S.name: allvariables = [x for x in opts.variable if not ('NOM' in x or '1' in x)]
			elif '5REF' in S.name: allvariables = [x for x in opts.variable if x=='plain']
			else: allvariables = opts.variable

			l2("%s"%S.name)
			l3("Directory %s_results%s in %s"%(S.name,'_acc' if opts.gendiv else '',fout.GetName()))
			makeDirsRoot(fout,S.name+'_results%s'%('_acc' if opts.gendiv else ''))
			gDirectory.cd("%s:/%s_results%s"%(fout.GetName(),S.name,'_acc' if opts.gendiv else ''))
	
			histos = {}
			results = {}
			labels = ['cl','up','dn','upas','dnas','upcb','dncb']
			colours = [kBlack,kRed+1,kBlue+1,kMagenta+1,kGreen+1,kOrange+1,kCyan+1]
			dashes = [10,1,7,9]
			for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
				if not any([x in ['main','alphas0'] for x in PS.purpose.split(',')]): continue
				l4("%s(%d)"%(kPS,PS.nmem))
				histos[kPS] = {}
				results[kPS] = {}
				for v in allvariables:
					v = jsons['vars']['variables'][v]
					vu = jsons['vars']['variables']['plain']
					if 'REF' in S.name and not v['var']=='plain': continue
					l5('var %s'%(v['var']))
					if v['var'] in opts.mvaBins:
						v['nbins_x'] = opts.mvaBins[v['var']][0]
						v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
						v['xmin'] = opts.mvaBins[v['var']][1][0]
						v['xmax'] = opts.mvaBins[v['var']][1][-1]
					# histograms for h, h+, h-, gen, gen+ and gen-
					histos[kPS][v['var']] = hblock(PS.nmem)
					hb = histos[kPS][v['var']]
					hs = hb.hs                 # h histograms
					us = hb.us                 # gen histograms
					# histograms for r
					results[kPS][v['var']] = rblock(len(labels))
					rb = results[kPS][v['var']]  
					rs = rb.rs                 # r histograms 
	# load histos
					for imem in range(PS.nmem): 
						hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,imem)
						uname = "%s-B%s-%s-%s_%s_%s-%03d"%(vu['var'],vu['nbins_x'],vu['xmin'],vu['xmax'],S.ref,PS.tag,imem)
						#if imem<3: print hname, uname
						hs[imem] = fout.Get("%s_histos/%s"%(S.name,hname))
						us[imem] = fout.Get("%s_histos/%s"%(S.ref,uname))
					#print us[0], us[0].GetBinContent(1)
					for ilab in range(len(labels)):						
						#print hs[0]
						rs[ilab] = hs[0].Clone(('-'.join(hs[0].GetName().split('-')[:-1]))+"_%s"%labels[ilab]) 
						rs[ilab].SetTitle(rs[ilab].GetName())
						rs[ilab].SetLineColor(colours[ilab])
						rs[ilab].SetLineStyle(dashes[PS.id-1])
	# use histos
					if any([x=='main' for x in PS.purpose.split(',')]):
						l6("main")
	# ct10 & mstw
						if PS.tag == 'CT10' or PS.tag == 'MSTW2008':
							for iBin in range(1,rs[0].GetNbinsX()+1):
								w0 = hb.GetIBinHoverU0(iBin) if opts.gendiv else hb.GetIBinH0(iBin)
#								w0 = hs[0].GetBinContent(iBin)
								wp = 0.
								wm = 0.
								if not w0==0: 
									for i in range(1,int(float(PS.nmem)/2.)):
										wa,wb = hb.GetIBinMemHoverU(iBin,2*i-1) if opts.gendiv else hb.GetIBinMemH(iBin,2*i-1)
#										wa = hs[2*i-1].GetBinContent(iBin)
#										wb = hs[2*i].GetBinContent(iBin)
										wp += pow(max((wa/w0-1.),(wb/w0-1.),0),2.)
										wm += pow(max((1.-wa/w0),(1.-wb/w0),0),2.)
								#	print '\t\t',wp, wa, wb, i, PS.nmem
								wp = sqrt(wp)/1.64485
								wm = sqrt(wm)/1.64485
								#print wp

								rb.SetIBinLab(labels.index('cl'),iBin,w0)
								rb.SetIBinLab(labels.index('up'),iBin,(1.+wp)*w0)
								rb.SetIBinLab(labels.index('dn'),iBin,(1.-wm)*w0)
#								rs[labels.index('cl')].SetBinContent(iBin,w0)
#								rs[labels.index('up')].SetBinContent(iBin,(1.+wp)*w0)
#								rs[labels.index('dn')].SetBinContent(iBin,(1.-wm)*w0)
								
							for r in rs[0:3]+rs[-2:]: 
								l6("Writing %s"%r.GetName())
								r.Write(r.GetName(),TH1.kOverwrite)
	
					if any([x=='alphas0' for x in PS.purpose.split(',')]):
	# ct10 & mstw	
						if 'CT10as' in PS.tag or 'MSTW' in PS.tag:
							PSp = [psp for psp in PSETS.itervalues() if psp.purpose=='alphas+' and psp.id==PS.id][0]
							PSm = [psm for psm in PSETS.itervalues() if psm.purpose=='alphas-' and psm.id==PS.id][0]
							l6("alphas")
							for (tag,his,uis) in [(PS.tag,'hs[0]','us[0]'),(PSp.tag,'hb.hp','hb.up'),(PSm.tag,'hb.hm','hb.um')]:
								hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,tag,0)
								uname = "%s-B%s-%s-%s_%s_%s-%03d"%(vu['var'],vu['nbins_x'],vu['xmin'],vu['xmax'],S.ref,tag,0)
								exec("%s"%his+" = fout.Get('%s_histos/%s'%(S.name,hname))")
								exec("%s"%uis+" = fout.Get('%s_histos/%s'%(S.ref,uname))")
#							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,0)
#							hs[0] = fout.Get("%s_histos%s/%s"%(S.name,"_ref" if 'REF' in S.name else "",hname))
#							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PSp.tag,0)
#							hsp = fout.Get("%s_histos%s/%s"%(S.name,"_ref" if 'REF' in S.name else "",hname))
#							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PSm.tag,0)
#							hsm = fout.Get("%s_histos%s/%s"%(S.name,"_ref" if 'REF' in S.name else "",hname))
							for iBin in range(1,rs[0].GetNbinsX()+1):
								w0,wp,wm = hb.GetIBinHoverU(iBin) if opts.gendiv else hb.GetIBinH(iBin)
								wa,wb = 0,0
								#print w0,wp,wm
#								w0 = hs[0].GetBinContent(iBin)
#								wp = 0.
#								wm = 0.
								if not w0==0:
									if 'CT10as' in PS.tag:
#										wp = (hsp.GetBinContent(iBin)/w0 - 1.)*6./5.
#										wm = (1.-hsm.GetBinContent(iBin)/w0)*6./5.
										wa = (wp/w0 - 1.)*6./5.
										wb = (1. - wm/w0)*6./5.
									elif 'MSTW' in PS.tag:
#										wp = (hsp.GetBinContent(iBin)/w0 - 1.)
#										wm = (1.-hsm.GetBinContent(iBin)/w0)*4./5.
										wa = (wp/w0 - 1.)
										wb = (1. - wm/w0)*4./5.
#								rs[labels.index('upas')].SetBinContent(iBin,(1.+wp)*w0)
#								rs[labels.index('dnas')].SetBinContent(iBin,(1.-wm)*w0)
								rb.SetIBinLab(labels.index('upas'),iBin,(1.+wa)*w0)
								rb.SetIBinLab(labels.index('dnas'),iBin,(1.-wb)*w0)
	
							for r in rs[-4:-2]: 
								l6("Writing %s"%r.GetName())
								r.Write(r.GetName(),TH1.kOverwrite)
	
	
	# combine
			tags = [None]*len(labels)
			for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
	# ct10 & mstw
				if 'CT10' in kPS or 'MSTW' in kPS:
					if not any([x in ['main'] for x in PS.purpose.split(',')]): continue
					for ii,i in enumerate(['main','main','main','alphas0','alphas0','main','main']):
						tags[ii] = [ps.tag for ps in PSETS.itervalues() if (i in ps.purpose) and (ps.id==PS.id)][0]
					l4("%s(%d)"%(kPS,PS.nmem))
					results[kPS] = {}
					for v in allvariables:
						v = jsons['vars']['variables'][v]
						if 'REF' in S.name and not v['var']=='plain': continue
						l5('var %s'%(v['var']))
						if v['var'] in opts.mvaBins:
							v['nbins_x'] = opts.mvaBins[v['var']][0]
							v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
							v['xmin'] = opts.mvaBins[v['var']][1][0]
							v['xmax'] = opts.mvaBins[v['var']][1][-1]
#						results[kPS][v['var']] = [None]*len(labels)
#						rs = results[kPS][v['var']]
						results[kPS][v['var']] = rblock(len(labels))
						rb = results[kPS][v['var']]
						rs = rb.rs                         # r histograms
						for il,l in enumerate(labels):
							hname = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,tags[il],l)
							rs[il] = fout.Get("%s_results%s/%s"%(S.name,'_acc' if opts.gendiv else '',hname))
						for	iBin in range(1,rs[0].GetNbinsX()+1):
#							w0 = rs[labels.index('cl')].GetBinContent(iBin)
#							wp = rs[labels.index('up')].GetBinContent(iBin)/w0 - 1.
#							wm = 1. - rs[labels.index('dn' if not 'MSTW' in PS.tag else 'up')].GetBinContent(iBin)/w0
#							wpas = rs[labels.index('upas')].GetBinContent(iBin)/w0 - 1.
#							wmas = 1. - rs[labels.index('dnas')].GetBinContent(iBin)/w0
							w0, wp, wm, wpas, wmas = rb.GetIBinLabs([labels.index(x) for x in ['cl','up','dn' if not 'MSTW' in PS.tag else 'up','upas','dnas']],iBin)
							wa,wb,waas,wbas = 0,0,0,0
							if not w0==0:
								wa = wp/w0 - 1.
								wb = 1. - wm/w0
								waas = wpas/w0 - 1.
								wbas = 1. - wmas/w0
#							rs[labels.index('upcb')].SetBinContent( iBin, (1.+sqrt( pow(wp,2.) + pow(wpas,2.) ))*w0 )
#							rs[labels.index('dncb')].SetBinContent( iBin, (1.-sqrt( pow(wm,2.) + pow(wmas,2.) ))*w0 ) 
							rb.SetIBinLab(labels.index('upcb'),iBin, (1.+sqrt( pow(wa,2.) + pow(waas,2.) ))*w0 )
							rb.SetIBinLab(labels.index('dncb'),iBin, (1.-sqrt( pow(wa,2.) + pow(wbas,2.) ))*w0 )

						for r in rs[-2:]:
							l6("Writing %s"%r.GetName())
							r.SetLineColor(colours[rs.index(r)])
							r.SetLineStyle(dashes[PS.id-1])
							r.Write(r.GetName(),TH1.kOverwrite)
	# nnpdf
				if 'NNPDF' in kPS:
					if not any([x in ['main'] for x in PS.purpose.split(',')]): continue
					l4("%s(%d)"%(kPS,PS.nmem))
					friends = dict([(ps.tag,ps) for ps in PSETS.itervalues() if ps.id==PS.id])
					histos[kPS] = {}
					results[kPS] = {}
					labelsnnpdf = ['cl','upcb','dncb']
					coloursnnpdf = [kBlack,kOrange+1,kCyan+1]
					for v in allvariables:
						v = jsons['vars']['variables'][v]
						vu = jsons['vars']['variables']['plain']
						if 'REF' in S.name and not v['var']=='plain': continue
						l5('var %s'%(v['var']))
						if v['var'] in opts.mvaBins:
							v['nbins_x'] = opts.mvaBins[v['var']][0]
							v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
							v['xmin'] = opts.mvaBins[v['var']][1][0]
							v['xmax'] = opts.mvaBins[v['var']][1][-1]
						histos[kPS][v['var']] = {}
#						results[kPS][v['var']] = [None]*3
						results[kPS][v['var']] = rblock(len(labelsnnpdf))
						rb = results[kPS][v['var']]
						rs = rb.rs
						for ri in range(len(labelsnnpdf)):
							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,0)
							hr = fout.Get("%s_histos/%s"%(S.name,hname))
							rs[ri] = hr.Clone(('-'.join(hr.GetName().split('-')[:-1]))+"_%s"%labelsnnpdf[ri])
							r = rs[ri] 
							r.SetTitle(r.GetName())
							r.SetLineColor(coloursnnpdf[ri])
							r.SetLineStyle(dashes[PS.id-1])
	
	#					central + other (load)
						for ifPS,(kfPS,fPS) in enumerate(sorted(friends.iteritems())):
#							histos[kPS][v['var']][kfPS] = [None]*fPS.nmem
#							hs = histos[kPS][v['var']][kfPS]
							histos[kPS][v['var']][kfPS] = hblock(fPS.nmem)
							hb = histos[kPS][v['var']][kfPS]
							hs = hb.hs
							us = hb.us
							for imem in range(fPS.nmem):
								hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,fPS.tag,imem)
								uname = "%s-B%s-%s-%s_%s_%s-%03d"%(vu['var'],vu['nbins_x'],vu['xmin'],vu['xmax'],S.ref,fPS.tag,imem)
								hs[imem] = fout.Get("%s_histos/%s"%(S.name,hname))
								us[imem] = fout.Get("%s_histos/%s"%(S.ref,uname))
	#					central
						for iBin in range(1,hs[0].GetNbinsX()+1):
							w0 = 0.
							for ifPS,(kfPS,fPS) in enumerate(sorted(friends.iteritems())):
								hb = histos[kPS][v['var']][kfPS]
								hs = hb.hs
								us = hb.us
								for imem in range(fPS.nmem):
#									w0 += histos[kPS][v['var']][kfPS][imem].GetBinContent(iBin)
									w0 += hb.GetIBinMemHoverU(iBin,imem,True) if opts.gendiv else hb.GetIBinMemH(iBin,imem,True)
							w0 = w0/sum([x.nmem for x in friends.itervalues()])
	#					other
							ws = 0.
							if not w0==0:
								for ifPS,(kfPS,fPS) in enumerate(sorted(friends.iteritems())):
									hb = histos[kPS][v['var']][kfPS]
									hs = hb.hs
									us = hb.us
									for imem in range(fPS.nmem):
#										wf = histos[kPS][v['var']][kfPS][imem].GetBinContent(iBin)
										wf = hb.GetIBinMemHoverU(iBin,imem,True) if opts.gendiv else hb.GetIBinMemH(iBin,imem,True)
										ws += pow(wf/w0 - 1.,2.)
							ws = ws/(sum([x.nmem for x in friends.itervalues()])-1.)
							ws = sqrt(ws)
	# fill
#							results[kPS][v['var']][0].SetBinContent(iBin,w0)
#							results[kPS][v['var']][1].SetBinContent(iBin,(1.+ws)*w0)
#							results[kPS][v['var']][2].SetBinContent(iBin,(1.-ws)*w0)
							rb.SetIBinLab(labelsnnpdf.index('cl'),iBin,w0)
							rb.SetIBinLab(labelsnnpdf.index('upcb'),iBin,(1.+ws)*w0)
							rb.SetIBinLab(labelsnnpdf.index('dncb'),iBin,(1.-ws)*w0)
	# write
						for ir,r in enumerate(rs):
							l6("Writing %s"%r.GetName())
							r.Write(r.GetName(),TH1.kOverwrite)


	# final band
			bandinput = {}
			print
			l4("Final band combination:")
			for v in allvariables:
				v = jsons['vars']['variables'][v]
				if 'REF' in S.name and not v['var']=='plain': continue
				l5('var %s'%(v['var']))
				if v['var'] in opts.mvaBins:
					v['nbins_x'] = opts.mvaBins[v['var']][0]
					v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
					v['xmin'] = opts.mvaBins[v['var']][1][0]
					v['xmax'] = opts.mvaBins[v['var']][1][-1]
				bandinput[v['var']] = {}
				b = bandinput[v['var']]
				for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
					if not 'main' in PS.purpose: continue
					b[PS.tag] = {}
					for il,l in enumerate(['upcb','dncb','cl']):
						hname = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,l)
						b[PS.tag][l] = fout.Get("%s_results%s/%s"%(S.name,'_acc' if opts.gendiv else '',hname))

				results = {}
				for tag in ['U','L','M','denv','dpm','rpm']:
					hget = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,'CT10','cl')
					hname = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,'band',tag)
					results[tag] = fout.Get("%s_results%s/%s"%(S.name,'_acc' if opts.gendiv else '',hget)).Clone(hname)
					results[tag].SetTitle(results[tag].GetName())
					results[tag].SetLineColor(kBlack)
					results[tag].SetLineStyle(1)

				for iBin in range(1,b['CT10']['cl'].GetNbinsX()+1):
					Ul = []
					Ll = []
					for kb,vb in b.iteritems():
						Ul += [vb['upcb'].GetBinContent(iBin)]
						Ll += [vb['dncb'].GetBinContent(iBin)]
					results['U'].SetBinContent(iBin,max(Ul))
					results['L'].SetBinContent(iBin,min(Ll))
					results['M'].SetBinContent(iBin,(max(Ul)+min(Ll))/2.)
	#				print b['CT10']['cl'].GetBinContent(iBin)
	#				print [k for k in b.iterkeys()]
	#				print Ul 
	#				print Ll
	#				print
					if 'MSTW' in opts.PDFS: 
						results['denv'].SetBinContent(iBin,results['U'].GetBinContent(iBin)/results['M'].GetBinContent(iBin) - 1. if ((not 'REF' in S.name) and (not results['M'].GetBinContent(iBin)==0)) else 0.)
						results['dpm'].SetBinContent(iBin,b['MSTW2008']['upcb'].GetBinContent(iBin)/b['MSTW2008']['cl'].GetBinContent(iBin)-1. if ((not 'REF' in S.name) and (not b['MSTW2008']['cl'].GetBinContent(iBin)==0)) else 0.)
						results['rpm'].SetBinContent(iBin,results['denv'].GetBinContent(iBin)/results['dpm'].GetBinContent(iBin) if ((not 'REF' in S.name) and (not results['dpm'].GetBinContent(iBin)==0)) else 0.)

				for ir,r in enumerate(sorted(results.itervalues())):
					l6("Writing %s"%r.GetName())
					r.Write(r.GetName(),TH1.kOverwrite)
	
			gDirectory.cd("%s:/"%(fout.GetName()))

####################
	

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
