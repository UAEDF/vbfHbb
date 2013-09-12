#include "reformat.h"

reformat::reformat(TString _nold, vector<TString> _variables) :
	nold(_nold)
{
	nnew = TString(nold(0,nold.Length()-5)) + "_reformatted.root";
	printf("\tWriting to: %s\n",nnew.Data());
	
	fold = TFile::Open(nold);
	told = (TTree*)fold->Get("Hbb/events"); 
	told->SetBranchStatus("*",0);
	for (int ivar=0; ivar<(int)_variables.size(); ++ivar) told->SetBranchStatus(_variables[ivar].Data(),1);
	told->SetBranchStatus("triggerResult",0); // deactivate branch to copy tree
	
	fnew = new TFile(nnew,"recreate");
	fnew->mkdir("Hbb");
	gDirectory->cd("Hbb");
	tnew = new TTree("events","events");

	printf("\tCopying main parts...\n");
	tnew = told->CopyTree(""); // copy tree without triggerResult branch
	std::vector<bool> *vb = 0;
	std::vector<char> *vc = 0;
	told->SetBranchStatus("triggerResult",1); // activate branch to loop over it
	told->SetBranchAddress("triggerResult",&vb);
	TBranch *bc = tnew->Branch("triggerResult","std::vector<char>",&vc); // new branch of different type in new tree
	tnew->SetBasketSize("triggerResult",512000); // use larger basket size
	int nentries = told->GetEntries();
	printf("\tLooping to convert branch...\n");
	for (int ientry=0; ientry<nentries; ++ientry) { // loop over tree to convert branch
		if (ientry%(nentries/20)==0) printf("\t\tevent %8i / %8i\n",ientry,nentries);
		told->GetEntry(ientry);
		vc->clear();
		for (int i=0; i<(int)(vb->size()); ++i) {
			char c = (char)(vb->at(i)+48); // chars 0 and 1 are values 48 and 49
			vc->push_back(c);
		}
		bc->Fill();
	}
	tnew->SetEntries(nentries);

	tnew->Print();
	fnew->Write(fnew->GetName(),TH1::kOverwrite);
}

reformat::~reformat() {
	delete tnew;
	delete told;
	fnew->Close();
	fold->Close();
	delete fnew;
	delete fold;
}
