#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TString.h"
#include "TCut.h"
#include "TDirectory.h"

#include <iostream>
#include <iomanip>
#include <vector>
using namespace std;

class sample {
	public:
		sample(TString,TString,float,vector<TString>);
		~sample();
		void draw(TString,TString,TString);
		TFile* getf();
		TTree* gett();
		void delf();
		void delt();
	
	private:
		TFile *f;
		TTree *t;
		float w;
};

