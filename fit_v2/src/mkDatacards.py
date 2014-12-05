#!/usr/bin/env python

import os,sys,re,json,datetime
from glob import glob
from array import array
from optparse import OptionParser,OptionGroup

basepath=os.path.split(os.path.abspath(__file__))[0]+"/../../"
sys.path.append(basepath+"common/")

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *

colours = ["\033[m"] + ["\033[%d;%dm"%(x,y) for (x,y) in [(0,z) for z in range(31,37)]+[(1,z) for z in range(31,37)]]

####################################################################################################
def parser(mp=None):
	if not mp: mp = OptionParser()
#	mp.add_option('','',help=colours[5]+''+colours[0],default='',type='',dest='')
#
	mp.add_option('--workdir',help=colours[5]+'Case workdir.'+colours[0],default='case0',type='str')

	mg1 = OptionGroup(mp,'Selection setup')
	mg1.add_option('--SELCATs',help=colours[5]+'Selection/Category setup: "NOM;NOM;-0.6#0.0#0.7#0.84#1.0,VBF;PRK;-0.1#0.4#0.8#1.0,...".'+colours[0],default='NOM;NOM;-0.6#0.0#0.7#0.84#1.0,VBF;PRK;-0.1#0.4#0.8#1.0',type='str',action='callback',callback=SELsetup,dest='SC')
	mp.add_option_group(mg1)

	mg2 = OptionGroup(mp,'Datacard settings')
	mg2.add_option('--bounds',help=colours[5]+'Template boundaries: 80,200 (min,max)'+colours[0],default=[80.,200.],type='str',action='callback',callback=optsplitfloat,dest='X')
	mg2.add_option('--lumi',help=colours[5]+'Luminosity: 19784.,18281. (NOM,VBF)'+colours[0],default=[19784.,18281.],type='str',action='callback',callback=optsplitfloat,dest='LUMI')
	mg2.add_option('--TF',help=colours[5]+'Transfer function label: POL1,POL2 (NOM,VBF)'+colours[0],default=['POL1','POL2'],type='str',action='callback',callback=optsplit)
	mg2.add_option('--BRN',help=colours[5]+'Bernstein order: 5,4 (NOM,VBF)'+colours[0],default=[5,4],type='str',action='callback',callback=optsplitint)
	mg2.add_option('--MASS',help=colours[5]+'Signal masspoint: 125'+colours[0],default=[115,120,125,130,135],type='int')
	mg2.add_option('--prefix',help=colours[5]+'Datacard prefix (folder): 125'+colours[0],default="datacards/",type='str')
	mp.add_option_group(mg2)
#	mg1.add_option('','',help=colours[5]+''+colours[0],default='',type='',dest='')
	mp.add_option_group(mg1)
#
	return mp

####################################################################################################
def style():
	gROOT.SetBatch(1)
	gROOT.ProcessLineSync(".x %s/styleCMSTDR.C"%basepath)
	gROOT.ForceStyle()
	gStyle.SetPadTopMargin(0.06)
	gStyle.SetPadRightMargin(0.04)
	gROOT.ProcessLineSync("gErrorIgnoreLevel = kWarning;")
	RooMsgService.instance().setSilentMode(kTRUE)
	for i in range(2): RooMsgService.instance().setStreamStatus(i,kFALSE)

####################################################################################################
def main():
	mp = parser()
	opts,args = mp.parse_args()
# Style
	style()

# Create directories if needed
	makeDirs('%s'%opts.workdir)
	makeDirs('%s/plot'%opts.workdir)
	makeDirs('%s/root'%opts.workdir)
	
# Settings
	SC = opts.SC if not type(opts.SC)==str else SELsetup(opts.SC)
	TF = opts.TF
	MASS = opts.MASS
	ncats = sum(SC.ncats)
	nmass = len(MASS)
	prefix = (opts.prefix).strip('/')
	makeDirs('%s/%s'%(opts.workdir,prefix))

# Read files
	uncertainties = json.loads(filecontent("%s/vbfHbb_uncertainties_2014.json"%basepath))
	fBKG = TFile.Open("%s/root/bkg_shapes_workspace.root"%opts.workdir)
	fSIG = TFile.Open("%s/root/sig_shapes_workspace.root"%opts.workdir)
	fDAT = TFile.Open("%s/root/data_shapes_workspace.root"%opts.workdir)
	wBKG = fBKG.Get("w")
	wSIG = fSIG.Get("w")
	wDAT = fDAT.Get("w")

# Load yields
	yD,yZ,yT,yVBF,yGF = [],[],[],[],[]
	for i in range(sum(SC.ncats)):
		yD += [wDAT.var("yield_data_CAT%d"%i).getValV()]
		yZ += [wDAT.var("yield_ZJets_CAT%d"%i).getValV()]
		yT += [wDAT.var("yield_Top_CAT%d"%i).getValV()]
		for j,jmass in enumerate(range(115,140,5)):
			if j==0: 
				yVBF += [[]]
				yGF  += [[]]
			if not jmass in MASS: continue
			yVBF[i] += [wSIG.var("yield_signalVBF_mass%d_CAT%d"%(jmass,i)).getValV()]
			yGF[i]  += [wSIG.var("yield_signalGF_mass%d_CAT%d"%(jmass,i)).getValV()]
# Print card
	for j,jmass in enumerate(range(115,140,5)):
		if not jmass in MASS: continue
		fout = open("%s/%s/datacard_m%d.txt"%(opts.workdir,prefix,jmass),"w+")
 ## numbers
		fout.write("imax %d\n"%sum(SC.ncats))
		fout.write("jmax *\nkmax *\n")
		fout.write("-"*100+"\n")
		fname = os.path.split(fDAT.GetName())[1]
 ## files
		fout.write("%-15s %-15s *   %s/%-30s %-30s\n"%("shapes","data_obs",prefix,fname,"w:data_hist_$CHANNEL"))
		fout.write("%-15s %-15s *   %s/%-30s %-30s\n"%("shapes","qcd     ",prefix,fname,"w:qcd_model_$CHANNEL"))
		fout.write("%-15s %-15s *   %s/%-30s %-30s\n"%("shapes","top     ",prefix,fname,"w:Top_model_$CHANNEL"))
		fout.write("%-15s %-15s *   %s/%-30s %-30s\n"%("shapes","zjets   ",prefix,fname,"w:Z_model_$CHANNEL"))
 ## top info
		fout.write("-"*100+"\n")
		fout.write("%-15s"%"bin")
		for i in range(sum(SC.ncats)):
			fout.write("%-10s"%("CAT%d"%i))
		fout.write("\n")
		fout.write("%-15s"%"observation")
		for i in range(sum(SC.ncats)):
			fout.write("%-10d"%(-1))
		fout.write("\n"+"-"*100+"\n")
		fout.write("%-15s"%"bin")
		labels = ["qqH","ggH","qcd","top","zjets"]
		for i in range(sum(SC.ncats)):
			for l in labels:
				fout.write("%-10s"%("CAT%d"%i))
		fout.write("\n")
		fout.write("%-15s"%"process")
		for i in range(sum(SC.ncats)):
			for l in labels:
				fout.write("%-10s"%l)
		fout.write("\n")
		fout.write("%-15s"%"process")
		for i in range(sum(SC.ncats)):
			fout.write("%-10d"%(0))
			fout.write("%-10d"%(-1))
			fout.write("%-10d"%(1))
			fout.write("%-10d"%(1))
			fout.write("%-10d"%(1))
		fout.write("\n")
		fout.write("%-15s"%"rate")
		for i in range(sum(SC.ncats)):
			fout.write("%-10d"%(yD[i]))
			fout.write("%-10.3f"%(yVBF[i][j]))
			fout.write("%-10.3f"%(yGF[i][j]))
			fout.write("%-10.3f"%(yT[i]))
			fout.write("%-10.3f"%(yZ[i]))
		fout.write("\n"+"-"*100+"\n")
  ## fixed parts
  		labels = ["BR","QCDscale_qqh","QCDscale_ggh","pdf_qqbar","pdf_gg","lumi","CMS_scale_j_ACCEPT","pdf_ACCEPT","CMS_res_j_ACCEPT","CMS_qqH_hbb_trigger","CMS_qqH_hbb_btag","CMS_qqH_hbb_qgl","UEPS","CMS_qqH_hbb_QCDscale","CMS_ggH_hbb_QCDscale","CMS_qqH_hbb_pdf","CMS_ggH_hbb_pdf"]
		for l in labels:
			fout.write("%-25s %-8s"%(l,"lnN"))
			k = j if len(uncertainties[l][0])==5 else i if len(uncertainties[l][0])==ncats else 0
			if len(uncertainties[l])==2: 
				fout.write("%-10.3f %-10.3f %-10s %-10s %-10s\n"%(uncertainties[l][0][k],uncertainties[l][1][k],"-","-","-"))
			elif len(uncertainties[l])==1 and "qq" in l:
				fout.write("%-10.3f %-10s %-10s %-10s %-10s\n"%(uncertainties[l][0][k],"-","-","-","-"))
			elif len(uncertainties[l])==1 and "gg" in l:
				fout.write("%-10s %-10.3f %-10s %-10s %-10s\n"%("-",uncertainties[l][0][k],"-","-","-"))
			elif len(uncertainties[l])==1:
				fout.write("%-10.3f %-10.3f %-10s %-10s %-10s\n"%(uncertainties[l][0][k],uncertainties[l][0][k],"-","-","-"))
		fout.write("-"*100+"\n")
  ## QCD part
		for i in range(sum(SC.ncats)):
  			fout.write("%-25s %-8s"%("CMS_vbfbb_qcd_norm_CAT%d"%i,"lnU"))
			for j in range(sum(SC.ncats)):
				if i==j: fout.write("%-10s %-10s %-10.3f %-10s %-10s"%("-","-",uncertainties['qcd_norm'],"-","-"))
				else:    fout.write("%-10s %-10s %-10s %-10s %-10s"%("-","-","-","-","-"))
			fout.write("\n")
		fout.write("-"*100+"\n")
  ## Z part
		for i in range(sum(SC.ncats)):
  			fout.write("%-25s %-8s"%("CMS_vbfbb_zjets_norm_CAT%d"%i,"lnN"))
			for j in range(sum(SC.ncats)):
				if i==j: fout.write("%-10s %-10s %-10s %-10.3f %-10s"%("-","-","-",uncertainties['zjets_norm'],"-"))
				else:    fout.write("%-10s %-10s %-10s %-10s %-10s"%("-","-","-","-","-"))
			fout.write("\n")
  ## T part
		for i in range(sum(SC.ncats)):
  			fout.write("%-25s %-8s"%("CMS_vbfbb_top_norm_CAT%d"%i,"lnN"))
			for j in range(sum(SC.ncats)):
				if i==j: fout.write("%-10s %-10s %-10s %-10s %-10.3f"%("-","-","-","-",uncertainties['top_norm']))
				else:    fout.write("%-10s %-10s %-10s %-10s %-10s"%("-","-","-","-","-"))
			fout.write("\n")
		fout.write("-"*100+"\n")
  ## scale/res part
  		labels = ["CMS_vbfbb_scale_mbb_selNOM","CMS_vbfbb_scale_mbb_selVBF","CMS_vbfbb_res_mbb_selNOM","CMS_vbfbb_res_mbb_selVBF"]
		for l in labels:
			fout.write("%-30s %-10s %9.2f %9.2f\n"%(l,"param",uncertainties[l][0],uncertainties[l][1]))
		fout.write("\n"+"-"*100+"\n")
  ## mean/sigma part
  		labels = ["mean","sigma"]
		for l in labels:
	  		for i in range(sum(SC.ncats)):
				n = "%s_m%d_CAT%d"%(l,jmass,i)
				v = wSIG.var(n)
				fout.write("%-30s %-10s %9.4f %9.4f\n"%(n,"param",v.getValV(),v.getError()))
		labels = ["Top_mean","Top_sigma","Z_mean","Z_sigma"]
		for l in labels:
	  		for i in range(sum(SC.ncats)):
				n = "%s_CAT%d"%(l,i)
				v = wDAT.var(n)
				fout.write("%-30s %-10s %9.4f %9.4f\n"%(n,"param",v.getValV(),v.getError()))
  ## transfer functions
  		for iS,S in enumerate(SC.selections):
			if 'Fix' in opts.TF[iS]:
				for i in range(S.ncat):
					if i==0: continue
					o = int(re.search('.*([0-9]{1})',opts.TF[iS]).group(1))
					for j in range(o+1):
						v = wDAT.var("trans_%s_CAT%d_p%d"%(opts.TF[iS],i+sum(SC.ncats[0:iS]),j))
						fout.write("%-30s %-10s %9.2e %9.2e\n"%(v.GetName(),"param",v.getValV(),v.getError()))
		
# Close
		fout.close()
		fDAT.Close()
		fSIG.Close()
		fBKG.Close()


				

		fout.close()
if __name__=='__main__':
	main()
