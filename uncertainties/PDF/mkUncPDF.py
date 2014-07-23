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
	mp.add_option('--ncut',help='Only run n events.',type='int',default=-1)

	mp.add_option('--refPDF',help='Reference PDF.',type='str',action='callback',callback=optsplitlist)

	mp.add_option('--mkTree',help='Recreate flatTree weight branches.',action='store_true',default=False)
	mp.add_option('--rdTree',help='Read flatTree weight branches.',action='store_true',default=False)
	mp.add_option('--mkHistos',help='Recreate weighted histos.',action='store_true',default=False)
	mp.add_option('--rdHistos',help='Read weighted histos.',action='store_true',default=False)
	mp.add_option('--mkCombi',help='Make combination.',action='store_true',default=False)

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
	jsonpdfs = json.loads(filecontent("%s/vbfHbb_pdfsets_2013.json"%basepath))
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
def mkUncPDF():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = prepare(opts)
	gROOT.ProcessLine("TH1::SetDefaultSumw2(1);")

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
			for iev,ev in enumerate(tnew):
				if not opts.ncut==-1 and iev > opts.ncut: break
				if iev % int(float(nentries)/10.) == 0: l5("%d / %d"%(iev,nentries))
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
	
					PDFwghts[iPS] = PS.wghts
					PDFwghtsalphas[iPS] = PS.wghtsalphas
					PDFlabels[iPS] = TString(PS.tag)
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
			l2("%s"%S.name)
			l3("Directory %s_histos in %s"%(S.name,fout.GetName()))
			makeDirsRoot(fout,S.name+'_histos')
			gDirectory.cd("%s:/%s_histos"%(fout.GetName(),S.name))
			tree = fout.Get("%s/%s"%(S.name,"events"))
			tree.SetBranchStatus("*",1)
			nentries = tree.GetEntries()
			bvbf = ['mvaVBF','selVBF','selNOM','trigWtNOM','trigWtVBF','triggerResult','nLeptons','dPhibb','mbb','puWt','pdfID1','pdfID2','pdfX1','pdfX2','pdfQ']
			bnom = ['mvaNOM','selVBF','selNOM','trigWtNOM','trigWtVBF','triggerResult','nLeptons','dPhibb','mbb','puWt','pdfID1','pdfID2','pdfX1','pdfX2','pdfQ']
			if 'NOM' in S.name:
				for b in bvbf: tree.SetBranchStatus(b,0)
			else:
				for b in bnom: tree.SetBranchStatus(b,0)
			
			histos = {}
# loop over sets
			for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
				l4("%s(%d)"%(kPS,PS.nmem))
				histos[kPS] = {}
# loop over variables
				for v in opts.variable:
					v = jsons['vars']['variables'][v]
					if v['var'] in opts.mvaBins:
						v['nbins_x'] = opts.mvaBins[v['var']][0]
						v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
						v['xmin'] = opts.mvaBins[v['var']][1][0]
						v['xmax'] = opts.mvaBins[v['var']][1][-1]
					l5('var %s'%(v['var']))
					histos[kPS][v['var']] = [None]*(PS.nmem)
# loop over tree
				for iev,ev in enumerate(tree):
					if opts.ncut>-1 and iev>=opts.ncut: break
					if (iev%int(nentries/10)==0): l6("%8s / %8s"%(iev,nentries))
					vPS = ev.PDFwghts[iPS]
					vPSas = ev.PDFwghtsalphas[iPS]
					PSl = ev.PDFlabels[iPS]
					if not PSl == TString(PS.tag): sys.exit("PDFs don't match (%s,%s). Exiting."%PSl.Data(),PS.tag)
# loop over variables and members
					for v in opts.variable:
						v = jsons['vars']['variables'][v]
						if v['var'] in opts.mvaBins:
							v['nbins_x'] = opts.mvaBins[v['var']][0]
							v['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
							v['xmin'] = opts.mvaBins[v['var']][1][0]
							v['xmax'] = opts.mvaBins[v['var']][1][-1]
						for imem in range(PS.nmem):
							if iev==0:
								hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,imem)
								if not 'xs' in v: histos[kPS][v['var']][imem] = TH1F(hname,hname,int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
								else: histos[kPS][v['var']][imem] = TH1F(hname,hname,int(v['nbins_x']),v['xs'])
							h = histos[kPS][v['var']][imem]
# fill histos
#							tree.Draw("%s>>%s"%(v['root'],h.GetName()),"(1.)*(PDFwghts[%d][%d])*(PDFwghtsalphas[%d][%d])"%(iPS,imem,iPS,imem),"",opts.ncut)
							h.Fill(eval("ev.%s"%v['root']) if not v['var']=='plain' else 0.,vPS[imem]*vPSas[imem])
# save histos
				for v in opts.variable:
					v = jsons['vars']['variables'][v]
					for imem in range(PS.nmem):
#						h.Write(h.GetName(),TH1.kOverwrite)
						histos[kPS][v['var']][imem].Write(histos[kPS][v['var']][imem].GetName(),TH1.kOverwrite)
	
			gDirectory.cd("%s:/"%(fout.GetName()))
	
####################

	l1("Working with weighted histos:")

	if opts.mkHistos or opts.rdHistos:
		for kS,S in sorted(SAMPLES.iteritems(),key=lambda (x,y):(x)):
			l2("%s"%S.name)
			l3("Directory %s_results in %s"%(S.name,fout.GetName()))
			makeDirsRoot(fout,S.name+'_results')
			gDirectory.cd("%s:/%s_results"%(fout.GetName(),S.name))
	
			histos = {}
			histosp = {}
			histosm = {}
			results = {}
			labels = ['cl','up','dn','upas','dnas','upcb','dncb']
			colours = [kBlack,kRed+1,kBlue+1,kMagenta+1,kGreen+1,kOrange+1,kCyan+1]
			dashes = [10,1,7,9]
			for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
				if not any([x in ['main','alphas0'] for x in PS.purpose.split(',')]): continue
				l4("%s(%d)"%(kPS,PS.nmem))
				histos[kPS] = {}
				histosp[kPS] = {}
				histosm[kPS] = {}
				results[kPS] = {}
				for v in opts.variable:
					v = jsons['vars']['variables'][v]
					l5('var %s'%(v['var']))
					histos[kPS][v['var']] = [None]*(PS.nmem)
					hs = histos[kPS][v['var']]
					histosp[kPS][v['var']] = None 
					hsp = histosp[kPS][v['var']]
					histosm[kPS][v['var']] = None
					hsm = histosm[kPS][v['var']]
					results[kPS][v['var']] = [None]*len(labels)
					rs = results[kPS][v['var']]
	# load histos
					for imem in range(PS.nmem): 
						hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,imem)
						hs[imem] = fout.Get("%s_histos/%s"%(S.name,hname))
					for i in range(len(labels)):						
						rs[i] = hs[0].Clone(('-'.join(hs[0].GetName().split('-')[:-1]))+"_%s"%labels[i]) 
						rs[i].SetTitle(rs[i].GetName())
						rs[i].SetLineColor(colours[i])
						rs[i].SetLineStyle(dashes[PS.id-1])
	# use histos
					if any([x=='main' for x in PS.purpose.split(',')]):
						l6("main")
	# ct10 & mstw
						if PS.tag == 'CT10' or PS.tag == 'MSTW2008':
							for iBin in range(1,rs[0].GetNbinsX()+1):
								w0 = hs[0].GetBinContent(iBin)
								wp = 0.
								wm = 0.
								for i in range(1,int(float(PS.nmem)/2.)):
									wa = hs[2*i-1].GetBinContent(iBin)
									wb = hs[2*i].GetBinContent(iBin)
									wp += pow(max((wa/w0-1.),(wb/w0-1.),0),2.)
									wm += pow(max((1.-wa/w0),(1.-wb/w0),0),2.)
								wp = sqrt(wp)*1.64485
								wm = sqrt(wm)*1.64485
								rs[labels.index('cl')].SetBinContent(iBin,w0)
								rs[labels.index('up')].SetBinContent(iBin,(1.+wp)*w0)
								rs[labels.index('dn')].SetBinContent(iBin,(1.-wm)*w0)
								
							for r in rs[0:3]+rs[-2:]: 
								l6("Writing %s"%r.GetName())
								r.Write(r.GetName(),TH1.kOverwrite)
	
					if any([x=='alphas0' for x in PS.purpose.split(',')]):
	# ct10 & mstw	
						if 'CT10as' in PS.tag or 'MSTW' in PS.tag:
							PSp = [psp for psp in PSETS.itervalues() if psp.purpose=='alphas+' and psp.id==PS.id][0]
							PSm = [psm for psm in PSETS.itervalues() if psm.purpose=='alphas-' and psm.id==PS.id][0]
							l6("alphas")
							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,0)
							hs[0] = fout.Get("%s_histos/%s"%(S.name,hname))
							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PSp.tag,0)
							hsp = fout.Get("%s_histos/%s"%(S.name,hname))
							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PSm.tag,0)
							hsm = fout.Get("%s_histos/%s"%(S.name,hname))
							for iBin in range(1,rs[0].GetNbinsX()+1):
								w0 = hs[0].GetBinContent(iBin)
								wp = 0.
								wm = 0.
								if 'CT10as' in PS.tag:
									wp = (hsp.GetBinContent(iBin)/w0 - 1.)*6./5.
									wm = (1.-hsm.GetBinContent(iBin)/w0)*6./5.
								elif 'MSTW' in PS.tag:
									wp = (hsp.GetBinContent(iBin)/w0 - 1.)
									wm = (1.-hsm.GetBinContent(iBin)/w0)*4./5.
								rs[labels.index('upas')].SetBinContent(iBin,(1.+wp)*w0)
								rs[labels.index('dnas')].SetBinContent(iBin,(1.-wm)*w0)
	
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
					for v in opts.variable:
						v = jsons['vars']['variables'][v]
						l5('var %s'%(v['var']))
						results[kPS][v['var']] = [None]*len(labels)
						rs = results[kPS][v['var']]
						for il,l in enumerate(labels):
							hname = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,tags[il],l)
							rs[il] = fout.Get("%s_results/%s"%(S.name,hname))
						for	iBin in range(1,rs[0].GetNbinsX()+1):
							w0 = rs[labels.index('cl')].GetBinContent(iBin)
							wp = rs[labels.index('up')].GetBinContent(iBin)/w0 - 1.
							wm = 1. - rs[labels.index('dn' if not 'MSTW' in PS.tag else 'up')].GetBinContent(iBin)/w0
							wpas = rs[labels.index('upas')].GetBinContent(iBin)/w0 - 1.
							wmas = 1. - rs[labels.index('dnas')].GetBinContent(iBin)/w0
							rs[labels.index('upcb')].SetBinContent( iBin, (1.+sqrt( pow(wp,2.) + pow(wpas,2.) ))*w0 )
							rs[labels.index('dncb')].SetBinContent( iBin, (1.-sqrt( pow(wm,2.) + pow(wmas,2.) ))*w0 ) 
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
					for v in opts.variable:
						v = jsons['vars']['variables'][v]
						l5('var %s'%(v['var']))
						histos[kPS][v['var']] = {}
						results[kPS][v['var']] = [None]*3
						for ri in range(len(labelsnnpdf)):
							hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,0)
							hr = fout.Get("%s_histos/%s"%(S.name,hname))
							results[kPS][v['var']][ri] = hr.Clone(('-'.join(hr.GetName().split('-')[:-1]))+"_%s"%labelsnnpdf[ri])
							r = results[kPS][v['var']][ri] 
							r.SetTitle(r.GetName())
							r.SetLineColor(coloursnnpdf[ri])
							r.SetLineStyle(dashes[PS.id-1])
	
	#					central + other (load)
						for ifPS,(kfPS,fPS) in enumerate(sorted(friends.iteritems())):
							histos[kPS][v['var']][kfPS] = [None]*fPS.nmem
							hs = histos[kPS][v['var']][kfPS]
							for imem in range(fPS.nmem):
								hname = "%s-B%s-%s-%s_%s_%s-%03d"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,fPS.tag,imem)
								hs[imem] = fout.Get("%s_histos/%s"%(S.name,hname))
	#					central
						for iBin in range(1,hs[0].GetNbinsX()+1):
							w0 = 0.
							for ifPS,(kfPS,fPS) in enumerate(sorted(friends.iteritems())):
								for imem in range(fPS.nmem):
									w0 += histos[kPS][v['var']][kfPS][imem].GetBinContent(iBin)
							w0 = w0/sum([x.nmem for x in friends.itervalues()])
	#					other
							ws = 0.
							for ifPS,(kfPS,fPS) in enumerate(sorted(friends.iteritems())):
								for imem in range(fPS.nmem):
									wf = histos[kPS][v['var']][kfPS][imem].GetBinContent(iBin)
									ws += pow(wf/w0 - 1.,2.)
							ws = ws/(sum([x.nmem for x in friends.itervalues()])-1.)
							ws = sqrt(ws)
	# fill
							results[kPS][v['var']][0].SetBinContent(iBin,w0)
							results[kPS][v['var']][1].SetBinContent(iBin,(1.+ws)*w0)
							results[kPS][v['var']][2].SetBinContent(iBin,(1.-ws)*w0)
	# write
						for ir,r in enumerate(results[kPS][v['var']]):
							l6("Writing %s"%r.GetName())
							r.Write(r.GetName(),TH1.kOverwrite)


	# final band
			bandinput = {}
			print
			l4("Final band combination:")
			for v in opts.variable:
				v = jsons['vars']['variables'][v]
				l5('var %s'%(v['var']))
				bandinput[v['var']] = {}
				b = bandinput[v['var']]
				for iPS,(kPS,PS) in enumerate(sorted(PSETS.iteritems(),key=lambda (x,y):(not y.purpose=='main',y.name))):
					if not 'main' in PS.purpose: continue
					b[PS.tag] = {}
					for il,l in enumerate(['upcb','dncb','cl']):
						hname = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,PS.tag,l)
						b[PS.tag][l] = fout.Get("%s_results/%s"%(S.name,hname))

				results = {}
				for tag in ['U','L','M','denv','dpm','rpm']:
					hget = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,'CT10','cl')
					hname = "%s-B%s-%s-%s_%s_%s_%s"%(v['var'],v['nbins_x'],v['xmin'],v['xmax'],S.name,'band',tag)
					results[tag] = fout.Get("%s_results/%s"%(S.name,hget)).Clone(hname)
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
					results['denv'].SetBinContent(iBin,results['U'].GetBinContent(iBin)/results['M'].GetBinContent(iBin) - 1.)
					results['dpm'].SetBinContent(iBin,b['MSTW2008']['upcb'].GetBinContent(iBin)/b['MSTW2008']['cl'].GetBinContent(iBin)-1.)
					results['rpm'].SetBinContent(iBin,results['denv'].GetBinContent(iBin)/results['dpm'].GetBinContent(iBin))

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
