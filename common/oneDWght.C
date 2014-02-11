#include <TH1F.h>
#include <iostream>
#include <iomanip>
using namespace std;

TH1F *wghtOneHist = 0;
double oneDWght(double var1 = -1)
{
	if (!wghtOneHist) {
		printf("1D map not found.\n");
		return 0.;
	}
	return wghtOneHist->GetBinContent(min(wghtOneHist->GetXaxis()->FindBin(var1),wghtOneHist->GetNbinsX()));	  
//	return wghtOneHist->GetBinContent(wghtOneHist->GetXaxis()->FindBin(var1));	  
}
