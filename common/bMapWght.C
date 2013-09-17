#include <TH2F.h>

TH2F *bMap = 0;
double bMapWght(double csv0 = -1, double csv1 = -1)
{
	  if (!bMap) {
		  printf("map not found.\n");
		  return 0.;
	  }
	return bMap->GetBinContent(bMap->GetXaxis()->FindBin(csv0),bMap->GetYaxis()->FindBin(csv1));	  
}
