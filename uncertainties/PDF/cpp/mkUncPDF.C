#include <TH1F.h>
#include <TTree.h>
#include <TFile.h>
#include <TCanvas.h>
#include <TString.h>
#include <TPad.h>
#include <TROOT.h>
#include <TInterpreter.h>

#include <cstdlib>
#include <vector>
#include <iomanip>
#include <iostream>
#include <string>
using namespace std;

#include "LHAPDF/LHAPDF.h"
using namespace LHAPDF;

int main() {
	string cut = "(triggerResult[0]||triggerResult[1])&&(jetPt[0]>80&&jetPt[1]>70&&jetPt[2]>50&&jetPt[3]>40&&mqq[1]>250&&abs(dEtaqq[1])>2.5 && jetBtag[btagIdx[0]]>0.244 && jetBtag[btagIdx[1]]>0.244) && (dPhibb[1]<2.0) && nLeptons==0";

	TFile *f = new TFile("/afs/cern.ch/work/s/salderwe/private/2014/flat/PDF/flatTree_VBFPowheg125.root","read");
	TTree *t = (TTree*)f->Get("Hbb/events");

	string pdfset0 = "cteq66.LHgrid";
	
	vector<string> pdfsets = vector<string>();
	pdfsets.push_back("MSTW2008nlo68cl.LHgrid");
//	pdfsets.push_back("cteq66alphas.LHgrid");

	vector<vector<TH1F*> > histosets = vector<vector<TH1F*>() >();

	TH1F *hmbbReg1 = new TH1F("vbfHbb_SEL_hmbbReg1_pdfPDF_memMEM","mbbReg1;mbbReg1;N",30,0,300);
	float xbins[6] = {-1.001,-0.6,0,0.7,0.84,1.001};
	TH1F *hmvaNOM  = new TH1F("vbfHbb_SEL_hmvaNOM_pdfPDF_memMEM","mvaNOM;mvaNOM;N",5,xbins);
	TH1F *hYield   = new TH1F("vbfHbb_SEL_hYield_pdfPDF_memMEM","yield;yield;N",1,0,1);
	histosets.push_back(vector<TH1F*>() ); 
	histosets.push_back(vector<TH1F*>() ); 
	histosets.push_back(vector<TH1F*>() ); 
	
	vector<int> nweights = vector<int>();
	vector<vector<double> > weights = vector<vector<double> >();

	initPDFSet(0,pdfset0);
	nweights.push_back(numberPDF(0));
	histosets[0].push_back(hmbbReg1->Clone());
	histosets[1].push_back(hmvaNOM->Clone());
	histosets[2].push_back(hYield->Clone());
	
	for (int iPDF=0; iPDF<pdfsets.size(); ++iPDF) {
		initPDFSet(iPDF+1,pdfsets[iPDF]);
		nweights.push_back(numberPDF(iPDF));
		histosets[0].push_back(hmbbReg1->Clone());
		histosets[1].push_back(hmvaNOM->Clone());
		histosets[2].push_back(hYield->Clone());
	}

	int nentries = t->GetEntries();
	nentries = 100;

	float x1(0),x2(0),pdf1(0),pdf2(0),Q(0);
	int id1(0),id2(0);
	float mbbReg[4],dPhibb[4],dEtaqq[4],mqq[4];
	vector<float> *jetPt=0, *jetBtag=0;
	vector<int> *btagIdx=0;	
	vector<bool> *triggerResult=0;
	float mvaNOM(0);
	int nLeptons(0);

	gInterpreter->ProcessLine("#include <vector>");

	t->SetBranchStatus("*",0);
	t->SetBranchStatus("mbbReg",1);
	t->SetBranchStatus("jetPt",1);
	t->SetBranchStatus("jetBtag",1);
	t->SetBranchStatus("dPhibb",1);
	t->SetBranchStatus("dEtaqq",1);
	t->SetBranchStatus("mqq",1);
	t->SetBranchStatus("btagIdx",1);
	t->SetBranchStatus("triggerResult",1);
	t->SetBranchStatus("mvaNOM",1);
	t->SetBranchStatus("nLeptons",1);
	t->SetBranchStatus("pdfX1",1);
	t->SetBranchStatus("pdfX2",1);
	t->SetBranchStatus("pdfQ",1);
	t->SetBranchStatus("pdf1",1);
	t->SetBranchStatus("pdf2",1);
	t->SetBranchStatus("pdfID1",1);
	t->SetBranchStatus("pdfID2",1);
	t->SetBranchAddress("mbbReg",&mbbReg);
	t->SetBranchAddress("jetPt",&jetPt);
	t->SetBranchAddress("jetBtag",&jetBtag);
	t->SetBranchAddress("dPhibb",&dPhibb);
	t->SetBranchAddress("dEtaqq",&dEtaqq);
	t->SetBranchAddress("mqq",&mqq);
	t->SetBranchAddress("btagIdx",&btagIdx);
	t->SetBranchAddress("triggerResult",&triggerResult);
	t->SetBranchAddress("mvaNOM",&mvaNOM);
	t->SetBranchAddress("nLeptons",&nLeptons);
	t->SetBranchAddress("pdfX1",&x1);
	t->SetBranchAddress("pdfX2",&x2);
	t->SetBranchAddress("pdfQ",&Q);
	t->SetBranchAddress("pdf1",&pdf1);
	t->SetBranchAddress("pdf2",&pdf2);
	t->SetBranchAddress("pdfID1",&id1);
	t->SetBranchAddress("pdfID2",&id2);

	t->Draw(TString::Format("mbbReg[1]>>%s",histosets[0][0]->GetName()));
	t->Draw(TString::Format("mvaNOM>>%s",histosets[1][0]->GetName()));
	t->Draw(TString::Format("1.>>%s",histosets[2][0]->GetName()));

	for (int iEntry=0; iEntry<nentries; ++iEntry) {
		t->GetEntry(iEntry);

		if ( ! ( jetPt->at(0)>80. && jetPt->at(1)>70. && jetPt->at(2)>50. && jetPt->at(3)>40. && dEtaqq[1]>2.5 && mqq[1]>250. && dPhibb[1]<2.0 && nLeptons==0 && jetBtag->at(btagIdx->at(0))>0.244 && jetBtag->at(btagIdx->at(1))>0.244 && (triggerResult->at(0)==1 || triggerResult->at(1)==1) ) ) continue;

//recalculate
		pdf1 = xfx(0,x1,Q,id1)/x1;
		pdf2 = xfx(0,x2,Q,id2)/x2;
		//cout << pdf1 << " -- " << pdf2 << endl;

//others
		for (int iPDF=0; iPDF<pdfsets.size(); ++iPDF) {
			weights.push_back(vector<float>());
			for (int iMEM=0; iMEM<nweights[iPDF+1]; ++iMEM) {
				usePDFMember(iPDF,iMEM);
				double newpdf1 = xfx(iPDF,x1,Q,id1)/x1;
				double newpdf2 = xfx(iPDF,x2,Q,id2)/x2;
				double wght = newpdf1/pdf1*newpdf2/pdf2;
				//cout << "\t" << iPDF << " -- " << iMEM << " -- " << newpdf1 << " -- " <<  newpdf2 << endl;
				weights[iPDF].push_back(wght);
			}
		}
	}
	
	return 0;
}
