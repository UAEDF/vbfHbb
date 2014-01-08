#include <TH2F.h>
//#include <iostream>
//#include <iomanip>
//using namespace std;

TH2F *wghtHist = 0;
double twoDWght(double var1 = -1, double var2 = -1)
{
	if (!wghtHist) {
		printf("2D map not found.\n");
		return 0.;
	}
	return wghtHist->GetBinContent(min(wghtHist->GetXaxis()->FindBin(var1),wghtHist->GetNbinsX()),min(wghtHist->GetYaxis()->FindBin(var2),wghtHist->GetNbinsY()));	  
//	return wghtHist->GetBinContent(wghtHist->GetXaxis()->FindBin(var1),wghtHist->GetYaxis()->FindBin(var2));	  
}
