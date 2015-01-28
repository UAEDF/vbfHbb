#include "preselect.h"
#include <TLorentzVector.h>
#include <TObjString.h>

preselect::preselect(TString _nglobal, TString _nname, vector<TString> _variables, TString selection, TString _nsource)
{
	nold = (_nsource == "") ? TString::Format("%s/%s",_nglobal.Data(),_nname.Data()) : TString::Format("%s/%s",_nsource.Data(),_nname.Data());

	TString base = _nname(0,_nname.Length()-5);
	nnew = TString::Format("%s/%s_preselected.root",_nglobal.Data(),base.Data());
	printf("\tWriting to: %s\n",nnew.Data());
	
	fold = TFile::Open(nold);
	told = (TTree*)fold->Get("Hbb/events"); 
	told->SetBranchStatus("*",0);
	for (int ivar=0; ivar<(int)_variables.size(); ++ivar) told->SetBranchStatus(_variables[ivar].Data(),1);
	
	fnew = new TFile(nnew,"recreate");
	fnew->mkdir("Hbb");
	gDirectory->cd("Hbb");
	
	// FIRST COPY FOR SELECTION
	tnew1 = new TTree("events1","events1");
	printf("\tCopying main parts (original triggerResults)...\n");
	tnew1 = told->CopyTree(selection); 

	// SECOND COPY FOR TRIGGER RESULT BRANCH
	tnew1->SetBranchStatus("triggerResult",0);
	tnew2 = new TTree("events","events");
	printf("\tCopying main parts (bool triggerResults)...\n");
	tnew2 = tnew1->CopyTree(selection); 

	std::vector<bool> *vb = 0;
	std::vector<char> *vc = 0;
	
	tnew1->SetBranchStatus("triggerResult",1); // activate branch to loop over it
	tnew1->SetBranchAddress("triggerResult",&vb);
	TBranch *bc = tnew2->Branch("triggerResult","std::vector<char>",&vc);			// new branch of different type in new tree
	tnew2->SetBasketSize("triggerResult",512000); // use larger basket size
	int nentries = tnew1->GetEntries();
	printf("\tLooping to convert branch...\n");

	for (int ientry=0; ientry<nentries; ++ientry) { // loop over tree to convert branch
		if (ientry%(nentries/20)==0) printf("\t\tevent %8i / %8i\n",ientry,nentries);
		tnew1->GetEntry(ientry);
		vc->clear();
		for (int i=0; i<(int)(vb->size()); ++i) {
			char c = (char)(vb->at(i)+48); // chars 0 and 1 are values 48 and 49
			vc->push_back(c);
		}
		bc->Fill();
	}
	tnew2->SetEntries(nentries);
	TObjString *runinfo = new TObjString(selection);
	tnew2->GetUserInfo()->Add(runinfo);

	tnew2->Print();
	tnew2->GetUserInfo()->Print("");
	tnew2->Write(tnew2->GetName(),TH1::kOverwrite);
}

preselect::~preselect() {
	delete tnew2;
	delete told;
	fnew->Close();
	fold->Close();
	delete fnew;
	delete fold;
}
