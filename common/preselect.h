#include <vector>
#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TBranch.h"
#include "TLeaf.h"
#include "TH1.h"

class preselect {
	public:
		preselect(TString, TString, vector<TString>, TString, TString);
		~preselect();

	private:
		TFile *fnew, *fold;
		TTree *tnew1, *tnew2, *told;
		TString nnew, nold;
};
