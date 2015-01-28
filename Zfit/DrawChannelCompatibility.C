void DrawChannelCompatibility(double rMin = -5,double rMax=5)
{
  gROOT->ForceStyle();
  TFile *inf = TFile::Open("higgsCombineZ.ChannelCompatibilityCheck.mH120.root");
  RooFitResult *fit_nominal   = (RooFitResult *)inf->Get("fit_nominal");
  RooFitResult *fit_alternate = (RooFitResult *)inf->Get("fit_alternate");
  RooRealVar *rFit = (RooRealVar*)fit_nominal->floatParsFinal().find("r");
  
  TString prefix = TString::Format("_ChannelCompatibilityCheck_%s_","r");

  int nChann = 0;
  TIterator *iter = fit_alternate->floatParsFinal().createIterator();
  for (RooAbsArg *a = (RooAbsArg *) iter->Next(); a != 0; a = (RooAbsArg *) iter->Next()) {
    if (TString(a->GetName()).Index(prefix) == 0) nChann++;
  }
  TH2F *frame = new TH2F("frame",";best fit #sigma/#sigma_{SM};",1,rMin,rMax,nChann,0,nChann);

  iter->Reset(); 
  int iChann = 0; 
  TGraphAsymmErrors *points = new TGraphAsymmErrors(nChann);
  float chi2(0.0);
  for (RooAbsArg *a = (RooAbsArg *) iter->Next(); a != 0; a = (RooAbsArg *) iter->Next()) {
    if (TString(a->GetName()).Index(prefix) == 0) {
      RooRealVar *ri = (RooRealVar *) a;
      TString channel = a->GetName(); 
      channel.ReplaceAll(prefix,"");
      points->SetPoint(iChann,ri->getVal(),iChann+0.5);
      cout<<channel<<" "<<ri->getVal()<<" "<<ri->getAsymErrorLo()<<" +"<<ri->getAsymErrorHi()<<endl;
      chi2 += pow((ri->getVal()-rFit->getVal())/ri->getError(),2);
      points->SetPointError(iChann,-ri->getAsymErrorLo(),ri->getAsymErrorHi(),0,0);
      //points->SetPointError(iChann,ri->getAsymErrorHi(),ri->getAsymErrorHi(),0,0);
      iChann++;
      frame->GetYaxis()->SetBinLabel(iChann, channel);
    }
  }
  cout<<"Combined fit: "<<rFit->getVal()<<" "<<rFit->getAsymErrorLo()<<" +"<<rFit->getAsymErrorHi()<<endl;
  cout<<"chi2 = "<<chi2<<endl;
  points->SetLineColor(kRed);
  points->SetLineWidth(3);
  points->SetMarkerStyle(21);

  TCanvas *can = new TCanvas("ChannelCompatibility_Z","ChannelCompatibility_Z",900,600);
  frame->GetXaxis()->SetNdivisions(505);
  frame->GetXaxis()->SetTitleSize(0.06);
  frame->GetXaxis()->SetTitleOffset(0.9);
  frame->GetXaxis()->SetLabelSize(0.05);
  frame->GetYaxis()->SetLabelSize(0.1);
  frame->Draw(); 
  //gStyle->SetOptStat(0);
  TBox globalFitBand(rFit->getVal()+rFit->getAsymErrorLo(), 0, rFit->getVal()+rFit->getAsymErrorHi(), nChann);
  //TBox globalFitBand(rFit->getVal()-rFit->getAsymErrorHi(), 0, rFit->getVal()+rFit->getAsymErrorHi(), nChann);
  globalFitBand.SetFillStyle(3013);
  globalFitBand.SetFillColor(65);
  globalFitBand.SetLineStyle(0);
  globalFitBand.DrawClone();
  TLine globalFitLine(rFit->getVal(), 0, rFit->getVal(), nChann);
  globalFitLine.SetLineWidth(4);
  globalFitLine.SetLineColor(214);
  globalFitLine.DrawClone();
  points->Draw("P SAME");
  gPad->Update();

  TLine *ln0 = new TLine(1,gPad->GetFrame()->GetY1(),1,gPad->GetFrame()->GetY2());
  ln0->SetLineColor(kBlack);
  ln0->SetLineWidth(1);
  ln0->SetLineStyle(2);
  ln0->Draw("same");
}
