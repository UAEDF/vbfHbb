#!/usr/bin/env python
import ROOT
from ROOT import *
import sys,re,os
from optparse import OptionParser

####################################################################################################
def parser():
	mp = OptionParser()
	return mp

####################################################################################################
def printWToText(w):
	old = os.dup( sys.stdout.fileno() )
	out = file('stdouterr.txt','w')
	os.dup2( out.fileno(), sys.stdout.fileno() )
	w.Print()
	os.dup2( old, sys.stdout.fileno() )
	out.close()
	#
	out = file('stdouterr.txt','r')
	text = out.read()
	out.close()
	#
	os.remove('stdouterr.txt')
	return text

####################################################################################################
def getObject(w,nam):
	obj = w.obj(nam)
	return obj

####################################################################################################
def line(nam,fun,x1,x2):
	lin = TF1(nam,fun,x1,x2)
	lin.SetLineColor(kViolet+3)
	lin.SetLineStyle(kDashed)
	return lin

####################################################################################################
def legend(a,b,c,d):
	leg = TLegend(a,b,c,d)
	leg.SetFillColor(0)
	leg.SetFillStyle(0)
	leg.SetTextFont(62)
	leg.SetTextColor(kBlack)
	leg.SetTextSize(0.045)
	leg.SetBorderSize(0)
	return leg
	
####################################################################################################
def pave(a,b,c,d):
	pav = TPaveText(a,b,c,d,"NDC")
	pav.SetFillColor(0)
	pav.SetFillStyle(0)
	pav.SetTextFont(62)
	pav.SetTextColor(kViolet+3)
	pav.SetTextSize(0.045)
	pav.SetBorderSize(0)
	pav.SetTextAlign(11)
	return pav

####################################################################################################
def main():
	mp = parser()
	opts,args = mp.parse_args()

	gROOT.SetBatch(1)
	gROOT.ProcessLineSync(".x ../../common/styleCMSSara.C")

	archive = {}
	cplain = TCanvas("cplain","cplain",3600,1500)
	cplain.Divide(4,2)
	cratio = TCanvas("cratio","cratio",3600,1500)
	cratio.Divide(4,2)
	cplains = TCanvas("cplains","cplains",2400,1000)
	cplains.Divide(4,2)
	cratios = TCanvas("cratios","cratios",2400,1000)
	cratios.Divide(4,2)

	ftransfer = TFile.Open('transferFunctions.root','read')
	tran = {}
	for i in range(7):
		if not (i==0 or i==4): tran[i] = [ftransfer.Get("fitRatio_sel%s_CAT%d_POL1"%('NOM' if i<4 else 'PRK',i)).Clone("trans_CAT%d"%i),ftransfer.Get("gUnc_sel%s_CAT%d_POL1"%('NOM' if i<4 else 'PRK',i)).Clone("trans_CAT%d"%i)]
		else: tran[i] = [ftransfer.Get("fitRatio_sel%s_CAT%d_POL1"%('NOM' if i<4 else 'PRK',i)).Clone("trans_CAT%d"%i),None]
		tran[i][0].SetLineColor(kGreen+3)
		tran[i][0].SetLineStyle(kSolid)
		if not tran[i][1]==None:
			tran[i][1].SetFillColor(kGray+1)
			tran[i][1].SetFillStyle(3454)
	
	for fname in args:
		fopen = TFile.Open(fname,'read')
		w = fopen.Get("w")
		print fname
		alt = re.search('.*Alt([A-Za-z0-9_]*).root',fname).group(1)
		text = printWToText(w)

		for Line in text.split('\n'):
			if '::qcd_model' in Line: 
				typ = re.search('(.*)::.*',Line).group(1)
				nam = re.search('.*::(.*)\[.*',Line).group(1)
				cat = re.search('.*CAT([0-9]*).*',nam).group(1)
				obj = getObject(w,nam)
				th1 = obj.createHistogram("mbbReg_CAT%d"%int(cat),240)
				th1.SetName("h"+nam)
				#print alt, cat, nam, '(%s)'%typ, obj, th1
				archive[(alt,cat)] = {}
				archive[(alt,cat)]['alt'] = alt
				archive[(alt,cat)]['cat'] = cat
				archive[(alt,cat)]['typ'] = typ
				archive[(alt,cat)]['nam'] = nam
				archive[(alt,cat)]['obj'] = obj
				archive[(alt,cat)]['th1'] = th1
				rat = th1.Clone("r"+nam)
				rat.Divide(archive[(alt,cat)]['th1'],archive[(alt,'0' if int(cat)<4 else '4')]['th1'])
				rat.GetYaxis().SetRangeUser(0.92,1.08)
				pav = pave(0.6,0.7,0.9,0.9)
				pav.AddText('Function: %s'%alt)
				lin = line("lin","1.",th1.GetXaxis().GetXmin(),th1.GetXaxis().GetXmax())
				archive[(alt,cat)]['rat'] = rat
				
				cplain.cd(int(cat)+1)
				th1.Draw()
				#for ibin in range(th1.GetNbinsX()):
				#	print th1.GetBinContent(ibin), th1.GetBinError(ibin)
				#print
				pav.Draw()

				cratio.cd(int(cat)+1)
				archive[(alt,cat)]['pav'] = pav
				archive[(alt,cat)]['lin'] = lin
				rat.Draw("axis")
				if not (int(cat)==0 or int(cat)==4): tran[int(cat)][1].Draw("E3")
				tran[int(cat)][0].Draw("same")
				rat.Draw("same")
				pav.Draw("same")
				lin.Draw("same")
				gPad.Update()
				pav.SetY1NDC(pav.GetY2NDC()-len(pav.GetListOfLines())*0.055)
				leg = legend(0.6,0.5,0.9,pav.GetY1NDC()-0.02)
				leg.AddEntry(rat,"CAT%d / CAT%d"%(int(cat),0 if int(cat)<4 else 4),"L")
				leg.AddEntry(tran[int(cat)][0],"TF POL1","L")
				leg.Draw()
				gPad.Update()
				leg.SetY1NDC(leg.GetY2NDC()-leg.GetNRows()*0.055)
				archive[(alt,cat)]['leg'] = leg

				cplains.cd(int(cat)+1)
				th1.Draw()
				pav.Draw()
				cratios.cd(int(cat)+1)
				rat.Draw()
				tran[int(cat)][0].Draw("same")
				if not (int(cat)==0 or int(cat)==4): tran[int(cat)][1].Draw("sameE3")
				pav.Draw()
				lin.Draw("same")
				leg.Draw()

		if not os.path.exists('plots'): os.makedirs('plots')
		cplain.SaveAs("plots/c_%s_plain.pdf"%alt)
		cratio.SaveAs("plots/c_%s_ratio.pdf"%alt)
		cplains.SaveAs("plots/c_%s_plain.png"%alt)
		cratios.SaveAs("plots/c_%s_ratio.png"%alt)
		
		fopen.Close()
	
	ftransfer.Close()

	cplain.Close()
	cratio.Close()

####################################################################################################
if __name__=='__main__':
	main()
