#include <vector>
#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TBranch.h"
#include "TLeaf.h"
#include "TH1.h"

class reformat {
	public:
		reformat(TString, TString, vector<TString>, int, TString);
		~reformat();

	private:
		TFile *fnew, *fold;
		TTree *tnew, *told;
		TString nnew, nold;
		int format;
};
