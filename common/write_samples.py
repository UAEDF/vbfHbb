#!/usr/bin/env python

from optparse import OptionParser
import datetime,sys,os,re,json

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv 

from toolkit import * 

today = datetime.date.today().strftime('%Y%m%d')

class info:
	def __init__(self,oname):
		self.oname = oname
		self.content = {}
		self.content['files'] = {}
		self.content['other'] = []
		self.content['fields'] = {'fname':80,'npassed':12,'xsec':12,'scale':15,'tag':8,'trigger':25,'colour':8} # field lengths
		self.content['trigger'] = ['HLT_QuadPFJet75_55_35_20_BTagCSV_VBF_v* OR HLT_QuadPFJet75_55_38_20_BTagCSV_VBF_v* OR HLT_QuadPFJet78_61_44_31_BTagCSV_VBF_v* OR HLT_QuadPFJet82_65_48_35_BTagCSV_VBF_v*','HLT_QuadJet75_55_35_20_BTagIP_VBF_v* OR HLT_QuadJet75_55_38_20_BTagIP_VBF_v*','HLT_QuadPFJet75_55_35_20_BTagCSV_VBF_v*','HLT_QuadPFJet75_55_38_20_BTagCSV_VBF_v*','HLT_QuadPFJet78_61_44_31_BTagCSV_VBF_v*','HLT_QuadPFJet82_65_48_35_BTagCSV_VBF_v*','HLT_QuadJet75_55_35_20_BTagIP_VBF_v*','HLT_QuadJet75_55_38_20_BTagIP_VBF_v*','HLT_DiJet35_MJJ650_AllJets_DEta3p5_VBF_v*','HLT_DiJet35_MJJ700_AllJets_DEta3p5_VBF_v*','HLT_DiJet35_MJJ750_AllJets_DEta3p5_VBF_v*','HLT_QuadJet50_v*','HLT_PFJet80_v*']
		self.read_info()

	def print_info(self):
		l1("Printing content for %s"%self.oname)
		l2("samples:")
		if len(self.content['files'])>0:
			for kfield,vfield in sorted(self.content['fields'].iteritems()):
				template="%s%%%is | %s"%(cyan,vfield,plain)
				print (template)%kfield,
			print
			print '-'*(170+6*4)
		for k,v in sorted(self.content['files'].iteritems()):
			for kfield,vfield in sorted(self.content['fields'].iteritems()):
				template="%%%is | "%vfield
				print (template)%self.content['files'][k][kfield], 
			print
		print
		l2("trigger indices for:")
		for tname in self.content['trigger']: print (" "*6)+tname
		print
		l2("other:")
		for line in self.content['other']: print (" "*6)+line

	def read_info(self):
		l1("Reading %s"%self.oname)
		if os.path.exists(self.oname):
			self.content = json.loads(filecontent(self.oname),encoding="utf-8")
		else: l2("%s will be a new file."%self.oname)
	
	def clean_info(self):
		l1("Cleaning content for %s"%self.oname)
		for k in sorted(self.content['files'].keys()):
			keep = False if raw_input("Keep %s? [(y)/n] "%k)=='n' else True
			if not keep: del self.content['files'][k]
		for line in sorted(self.content['other']):
			keep = False if raw_input("Keep %s? [(y)/n] "%line)=='n' else True
			if not keep: self.content['other'].remove(line)
		self.print_info()
		self.write_info()


	def add_info(self,infojson,passed_content):
		fields = [None,None,None,None,None,None,None]
		if type(passed_content)==str: 
			f = TFile.Open(iname)
			h1 = f.FindObjectAny('TriggerPass;1')
			if not h1: sys.exit('TriggerPass;1 problematic for %s. Exiting'%iname)
			npassed = h1.GetBinContent(1)
			h2 = f.FindObjectAny('TriggerNames;1')
			if not h2: sys.exit('TriggerNames;1 problematic for %s. Exiting'%iname)
			trigarray = []
			for tname in self.content['trigger']: 
				found=False
				for i in range(h2.GetXaxis().GetNbins()):
					if h2.GetXaxis().GetBinLabel(i+1)==tname: 
						trigarray.append('%i'%i)
						found=True
						break
				if not found: trigarray.append('-')
			fields[0] = iname
			fields[1] = "%i"%npassed
			done = False
			if fields[0] in self.content['files']: pass
			else:
				l2("Adding %s:"%fields[0])
				for tag in infojson['tags'].iterkeys():
					for possibility in infojson['tags'][tag]:
						if possibility in fields[0]:
							fields[4] = tag
							new_value = raw_input("      --> sample %s: tag? [%s]"%(fields[0],fields[4]))
							if not new_value=="": fields[4]=new_value
							done = True
						if done: continue
					if done: continue
				fields[2] = infojson['crosssections'][fields[4]]
				new_value = raw_input("      --> sample %s: cross section? [%s]"%(fields[0],fields[2]))
				if not new_value=="": fields[2]=new_value
#				fields[2] = str(raw_input("    --> Cross section for sample %s? "%iname))
				fields[3] = "%f"%(float(fields[1])/float(fields[2])) if not fields[2]=="-1" else "-1"
#				fields[4] = re.search('(VBF|QCD|RUN|TRG|OTH)',iname.upper().replace('FLATTREE','').replace('_T','_OTH').replace('_Z','_OTH').replace('_W','_OTH').replace('DATA','RUN').replace('MULTIJET','RUN').replace('BJET','RUN').replace('JET','TRG')).group(1)
				fields[5] = ','.join(trigarray)
#				fields[6] = str(raw_input("    --> Colour for sample %s? "%iname))
				fields[6] = infojson['colours'][fields[4]]
				new_value = raw_input("      --> sample %s: colour? [%s]"%(fields[0],fields[6]))
				if not new_value=="": fields[2]=new_value
				if fields[6]=="": fields[6]="1"
			f.Close()
		elif type(passed_content)==list: 
			fields=passed_content
			if not fields[0] in self.content['files']: l2("Adding %s:"%fields[0])
		else: l2(yellow+"Unknown passed content. Skipping."+plain)
		#
		if not fields[0] in self.content['files']:
			self.content['files'][fields[0]] = {}
			self.content['files'][fields[0]]['fname'] = fields[0]
			self.content['files'][fields[0]]['npassed'] = fields[1]
			self.content['files'][fields[0]]['xsec'] = fields[2]
			self.content['files'][fields[0]]['scale'] = fields[3]
			self.content['files'][fields[0]]['tag'] = fields[4]
			self.content['files'][fields[0]]['trigger'] = fields[5]
			self.content['files'][fields[0]]['colour'] = fields[6]
		elif fields[0] in self.content['files'] and self.content['files'][fields[0]]['npassed']==fields[1]: l2("%s%s already in dict. Skipping.%s"%(yellow,fields[0],plain))
		elif fields[0] in self.content['files'] and self.content['files'][fields[0]]['npassed']!=fields[1]: l2("%s%s already in dict. NPASSED doesn\'t match. CHECK!!!.%s"%(Red,fields[0],plain))

	def write_info(self):
		l1("Writing content for %s"%self.oname)
		f = file(self.oname,'w+')	# overwrite
		f.write(json.dumps(self.content))
		f.close()

	def update_info(self):
		l1("Updating content for %s"%self.oname)
		for f in sorted(self.content['files'].keys()):
			l2("%s: "%f)
			for field in self.content['files'][f].keys():
				new_value = raw_input("%s? [%s]"%(field,str(self.content['files'][f][field])))
				if not new_value == "": self.content['files'][f][field] = new_value
		self.print_info()
		self.write_info()

def parser():
	mp = OptionParser()
	mp.add_option('-i','--input',help='Comma separated list of input files (including prefix).',dest='input',type='str',default='')
	mp.add_option('-o','--output',help='Output file name (including prefix).',dest='output',type='str',default='vbfHbb_samples_%s.json'%today)
	mp.add_option('-r','--readonly',help='Print content of output file.',dest='readonly',action='store_true',default=False)
	mp.add_option('-c','--clean',help='Clean json file.',dest='clean',action='store_true',default=False)
	mp.add_option('-u','--update',help='Update json file.',dest='update',action='store_true',default=False)
	mp.add_option('-b','--baseinfo',help='File with cross section info (including prefix).',dest='baseinfo',type='str',default='vbfHbb_info.json')
	return mp



if __name__=='__main__':
	mp = parser()
	opts,args = mp.parse_args()
	
	mybaseinfo = json.loads(filecontent(opts.baseinfo),encoding='utf-8') 
 
	myinfo = info(opts.output)
	myinfo.print_info()

	if opts.clean and not opts.readonly:
		myinfo.clean_info()
	
	if opts.update and not opts.readonly:
		myinfo.update_info()

	if not opts.readonly and not opts.clean:
		l1("Looping over new inputs:")
		for iname in opts.input.split(','):
			if not os.path.exists(iname): 
				l2("Skipping non-existant %s."%iname)
				continue
			myinfo.add_info(mybaseinfo,iname)
		myinfo.print_info()
		myinfo.write_info()