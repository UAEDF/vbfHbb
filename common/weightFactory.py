#!/usr/bin/env python

import sys
import os,re,json,datetime
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath)

from toolkit import *

class weightFactory:
	def __init__(self,samples,Lumi=None,KFWght=None):
		if not os.path.exists(samples)   : sys.exit('Input file doesn\'t exist : '+samples)
		self.samples   = json.loads(filecontent(samples))
		self.wOut      = '1.'
		self.Lumi      = Lumi if not Lumi==None else 19000.
		self.KFWght    = KFWght if not KFWght==None else 1.3

	def getFormula(self,weights,sample_tag):
		self.wOut='1.'
		for iWght in weights.split(','):
			if iWght == 'PU'   : self.addPUWght(sample_tag)
			if iWght == 'XSEC' : self.addXSWght(sample_tag)
			if iWght == 'LUMI' : self.addLUWght(sample_tag)
			if iWght == 'KFAC' : self.addKFWght(sample_tag)
			if iWght == 'BMAP' : self.addBMWght(sample_tag)
			if iWght == 'TRSF' : self.addTRWght(sample_tag)
		return self.wOut

	def addPUWght(self,tag):
		for iFile in self.samples["files"]:
		   if self.samples["files"][iFile]["tag"] == tag and self.samples["files"][iFile]["xsec"] > 0 : self.wOut += '*puWt'

	def addXSWght(self,tag):
		for iFile in self.samples["files"]:
		   if self.samples["files"][iFile]["tag"] == tag and self.samples["files"][iFile]["xsec"] > 0 : self.wOut += '*(1./'+self.samples["files"][iFile]["scale"]+')'

	def addLUWght(self,tag):
		for iFile in self.samples["files"]:
		   if self.samples["files"][iFile]["tag"] == tag and self.samples["files"][iFile]["xsec"] > 0 : self.wOut += '*%s'%(str(self.Lumi))

	def addKFWght(self,tag):
		for iFile in self.samples["files"]:
		   if self.samples["files"][iFile]["tag"] == tag and 'QCD' in self.samples["files"][iFile]["tag"] : self.wOut += '*%s'%(str(self.KFWght))

	def addBMWght(self,tag):
		for iFile in self.samples["files"]:
		   if self.samples["files"][iFile]["tag"] == tag and self.samples["files"][iFile]["xsec"] > 0 :  self.wOut += '*bMapWght(jetBtag[btagIdx[0]],jetBtag[btagIdx[1]])'

	def addTRWght(self,tag):
		for iFile in self.samples["files"]:
			if self.samples["files"][iFile]["tag"] == tag and self.samples["files"][iFile]["xsec"] > 0 : self.wOut += '*0.85'


# Examples:
if __name__=='__main__':
  wf = weightFactory('vbfHbb_samples_XJ_2012Paper.json',18500)
  print 'Data   : ' , wf.getFormula('PU,XSEC,KFAC,LUMI','Data') 
  print 'QCD100 : ' , wf.getFormula('PU,XSEC,KFAC,LUMI','QCD100')
  print 'QCD250 : ' , wf.getFormula('PU,XSEC,KFAC,LUMI','QCD250')
  print 'QCD500 : ' , wf.getFormula('PU,XSEC,KFAC,LUMI','QCD500')
  print 'QCD1000: ' , wf.getFormula('PU,XSEC,KFAC,LUMI','QCD1000')
  print 'ZJets  : ' , wf.getFormula('PU,XSEC,KFAC,LUMI','ZJets')
  print 'TTJets : ' , wf.getFormula('PU,XSEC,KFAC,LUMI','TTJets')
