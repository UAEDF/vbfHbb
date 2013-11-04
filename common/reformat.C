#include "reformat.h"
#include <TLorentzVector.h>

reformat::reformat(TString _nold, vector<TString> _variables, int _format) :
	nold(_nold), format(_format)
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
	
//	TLorentzVector jet1,jet2;
//	float mqqTrig = 0;
//	float dEtaqqTrig = 0;

	told->SetBranchStatus("triggerResult",1); // activate branch to loop over it
//	told->SetBranchStatus("jetPt",1); // activate branch to loop over it
//	told->SetBranchStatus("jetEta",1); // activate branch to loop over it
//	told->SetBranchStatus("jetPhi",1); // activate branch to loop over it
//	told->SetBranchStatus("jetMass",1); // activate branch to loop over it
	told->SetBranchAddress("triggerResult",&vb);
	TBranch *bc = tnew->Branch("triggerResult","std::vector<char>",&vc);			// new branch of different type in new tree
//	TBranch *bmqqTrig = tnew->Branch("mqqTrig",&mqqTrig,"mqqTrig/F"); 				// new branch of different type in new tree
//	TBranch *bdEtaqqTrig = tnew->Branch("dEtaqqTrig",&dEtaqqTrig,"dEtaqqTrig/F"); 	// new branch of different type in new tree
	tnew->SetBasketSize("triggerResult",512000); // use larger basket size
//	tnew->SetBasketSize("mqqTrig",512000); // use larger basket size
//	tnew->SetBasketSize("dEtaqqTrig",512000); // use larger basket size
	int nentries = told->GetEntries();
	printf("\tLooping to convert branch...\n");

	if (format==1) {
//		Float_t vjetPt[5], vjetEta[5], vjetPhi[5], vjetMass[5];
//		told->SetBranchAddress("jetPt",&vjetPt);
//		told->SetBranchAddress("jetEta",&vjetEta);
//		told->SetBranchAddress("jetPhi",&vjetPhi);
//		told->SetBranchAddress("jetMass",&vjetMass);
		for (int ientry=0; ientry<nentries; ++ientry) { // loop over tree to convert branch
			if (ientry%(nentries/20)==0) printf("\t\tevent %8i / %8i\n",ientry,nentries);
			told->GetEntry(ientry);
			vc->clear();
			for (int i=0; i<(int)(vb->size()); ++i) {
				char c = (char)(vb->at(i)+48); // chars 0 and 1 are values 48 and 49
				vc->push_back(c);
			}
/*			mqqTrig = -1;
			dEtaqqTrig = -1;
			for (int i=0; i<5; ++i) {
				for (int j=i+1; j<5; ++j) {
					//printf("%12f  %12f\n",vjetPt[i],vjetPt[j]);
					if (vjetPt[j]>35.)  { //vjetPt[i]>35. 
						jet1.SetPtEtaPhiM(vjetPt[i],vjetEta[i],vjetPhi[i],vjetMass[i]);
						jet2.SetPtEtaPhiM(vjetPt[j],vjetEta[j],vjetPhi[j],vjetMass[j]);
						if ((jet1+jet2).M() > mqqTrig) {
							mqqTrig = (jet1+jet2).M();
							dEtaqqTrig = abs(jet1.Eta() - jet2.Eta());
						}
					}
					else break;
					//printf("%12f  %12f  %12f  %12f\n",vjetPt[i],vjetPt[j],mqqTrig,dEtaqqTrig);
				}
			}
*/			bc->Fill();
//			bmqqTrig->Fill();
//			bdEtaqqTrig->Fill();
		}
	}
	if (format==2) {
//		vector<float> *vjetPt=0, *vjetEta=0, *vjetPhi=0, *vjetMass=0;
//		told->SetBranchAddress("jetPt",&vjetPt);
//		told->SetBranchAddress("jetEta",&vjetEta);
//		told->SetBranchAddress("jetPhi",&vjetPhi);
//		told->SetBranchAddress("jetMass",&vjetMass);
		for (int ientry=0; ientry<nentries; ++ientry) { // loop over tree to convert branch
			if (ientry%(nentries/20)==0) printf("\t\tevent %8i / %8i\n",ientry,nentries);
			told->GetEntry(ientry);
			vc->clear();
			for (int i=0; i<(int)(vb->size()); ++i) {
				char c = (char)(vb->at(i)+48); // chars 0 and 1 are values 48 and 49
				vc->push_back(c);
			}
/*			mqqTrig = -1;
			dEtaqqTrig = -1;
			for (int i=0; i<(int)(vjetPt->size()); ++i) {
				for (int j=i+1; j<(int)(vjetPt->size()); ++j) {
					//printf("%12f  %12f\n",vjetPt->at(i),vjetPt->at(j));
					if (vjetPt->at(j)>35.)  { //vjetPt->at(i)>35. 
						jet1.SetPtEtaPhiM(vjetPt->at(i),vjetEta->at(i),vjetPhi->at(i),vjetMass->at(i));
						jet2.SetPtEtaPhiM(vjetPt->at(j),vjetEta->at(j),vjetPhi->at(j),vjetMass->at(j));
						if ((jet1+jet2).M() > mqqTrig) {
							mqqTrig = (jet1+jet2).M();
							dEtaqqTrig = abs(jet1.Eta() - jet2.Eta());
						}
					}
					else break;
					//printf("%12f  %12f  %12f  %12f\n",vjetPt->at(i),vjetPt->at(j),mqqTrig,dEtaqqTrig);
				}
			}
*/			bc->Fill();
//			bmqqTrig->Fill();
//			bdEtaqqTrig->Fill();
		}
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
