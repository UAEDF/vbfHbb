#include <TH2F.h>
//#include <iostream>
//#include <iomanip>
//using namespace std;

TH2F *wghtTwoHist = 0;
double twoDWght(double var1 = -1, double var2 = -1)
{
	if (!wghtTwoHist) {
		printf("2D map not found.\n");
		return 0.;
	}
	return wghtTwoHist->GetBinContent(min(wghtTwoHist->GetXaxis()->FindBin(var1),wghtTwoHist->GetNbinsX()),min(wghtTwoHist->GetYaxis()->FindBin(var2),wghtTwoHist->GetNbinsY()));	  
//	return wghtTwoHist->GetBinContent(wghtTwoHist->GetXaxis()->FindBin(var1),wghtTwoHist->GetYaxis()->FindBin(var2));	  
}
