#include <TF2.h>

TF2 *wghtFun = 0;
double twoDWghtFun(double var1 = -1, double var2 = -1)
{
	if (!wghtFun) {
		printf("2D fun not found.\n");
		return 0.;
	}
//	return wghtHist->GetBinContent(min(wghtHist->GetXaxis()->FindBin(var1),wghtHist->GetNbinsX()),min(wghtHist->GetYaxis()->FindBin(var2),wghtHist->GetNbinsY()));	  
//	return wghtHist->GetBinContent(wghtHist->GetXaxis()->FindBin(var1),wghtHist->GetYaxis()->FindBin(var2));	  
	return wghtFun->Eval(var1,var2);
}

