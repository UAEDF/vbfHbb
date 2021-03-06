#include "sample.h"

sample::sample(TString fname, TString tname, vector<TString> variables) : //float weight
	f(TFile::Open(fname))//,w(weight)
{
	t = (TTree*)f->Get(tname);
//	t->SetWeight(w>0 ? w : 1.); // use w=-1 for data
	t->SetBranchStatus("*",0);
	for (int ivar=0; ivar<(int)variables.size(); ++ivar) t->SetBranchStatus(variables[ivar].Data(),1);
//	for (int ivar=0; ivar<(int)variables.size(); ++ivar) cout << variables[ivar] << endl;
}

sample::~sample() {
	f->Close();
}

void sample::draw(TString h, TString var, TString cut) {
	//cout << Form("%s>>+%s  ",var.Data(),h.Data()) << cut.Data() << endl;
	t->Draw(Form("%s>>+%s",var.Data(),h.Data()),TCut(cut.Data()));
}

float sample::count(TString cut) {
	//float n = t->GetEntries(TCut(cut.Data()));
	t->Draw("1.>>hcount",TCut(cut.Data()));
	TH1F *h = (TH1F*)gDirectory->Get("hcount");
	float n = h->Integral();
	return n;
}

TFile* sample::getf() {
	return f;
}

TTree* sample::gett() {
	return t;
}

void sample::delf() {
	delete f;
}

void sample::delt() {
	delete t;
}
