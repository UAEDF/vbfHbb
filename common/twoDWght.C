#include <TH2F.h>

TH2F *wghtHist = 0;
double twoDWght(double var1 = -1, double var2 = -1)
{
	if (!wghtHist) {
		printf("2D map not found.\n");
		return 0.;
	}
//	return wghtHist->GetBinContent(min(wghtHist->GetXaxis()->FindBin(var1),nbins1),min(wghtHist->GetYaxis()->FindBin(var2),nbins2));	  
	return wghtHist->GetBinContent(wghtHist->GetXaxis()->FindBin(var1),wghtHist->GetYaxis()->FindBin(var2));	  
}
