void DrawChannelCompatibility(int MASS,double rMin = -30,double rMax=40)
{
  gROOT->ProcessLineSync(".x ../../../common/styleCMSTDR.C");
  gROOT->ProcessLineSync("gErrorIgnoreLevel=kWarning;");
  gROOT->SetBatch(1);
  gStyle->SetPadLeftMargin(0.085);
  gStyle->SetTitleOffset(0.7,"Y");
  gStyle->SetPadRightMargin(0.04);
  gStyle->SetPadTopMargin(0.04);
  gStyle->SetPadLeftMargin(0.14);

  TFile *inf = TFile::Open(TString::Format("combine/higgsCombine_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2.ChannelCompatibilityCheck.mH%d.root",MASS));
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
	
  TPaveText *ExtraPaves[7];

  iter->Reset(); 
  int iChann = 0; 
  TGraphAsymmErrors *points = new TGraphAsymmErrors(nChann);
  for (RooAbsArg *a = (RooAbsArg *) iter->Next(); a != 0; a = (RooAbsArg *) iter->Next()) {
    if (TString(a->GetName()).Index(prefix) == 0) {
      RooRealVar *ri = (RooRealVar *) a;
      TString channel = a->GetName(); 
      channel.ReplaceAll(prefix,"");
      points->SetPoint(iChann,ri->getVal(),iChann+0.5);
      cout<<channel<<" "<<ri->getVal()<<" "<<ri->getAsymErrorLo()<<" +"<<ri->getAsymErrorHi()<<endl;
      points->SetPointError(iChann,-ri->getAsymErrorLo(),ri->getAsymErrorHi(),0,0);
//	ExtraPaves[iChann] = new TPaveText(-27.5,points->GetYaxis()->GetBinCenter(iChann),-15,points->GetYaxis()->GetBinCenter(iChann) + points->GetYaxis()->GetBinWidth(iChann)/2.);
		float space=1.-gStyle->GetPadTopMargin()-gStyle->GetPadBottomMargin();
		ExtraPaves[iChann] = new TPaveText(0.2,gStyle->GetPadBottomMargin()+space/7.*(iChann+0.5),0.35,gStyle->GetPadBottomMargin() + space/7.*(iChann+0.9),"NDC");
		ExtraPaves[iChann]->SetTextSize(0.03);
		ExtraPaves[iChann]->SetTextFont(42);
		ExtraPaves[iChann]->SetTextAlign(12);
		ExtraPaves[iChann]->SetFillStyle(-1);
		ExtraPaves[iChann]->SetBorderSize(0);
		ExtraPaves[iChann]->AddText(TString::Format("%.1f^{%+.1f}_{%+.1f}",ri->getVal(),ri->getAsymErrorHi(),ri->getAsymErrorLo()));
      //points->SetPointError(iChann,ri->getAsymErrorHi(),ri->getAsymErrorHi(),0,0);
      iChann++;
      frame->GetYaxis()->SetBinLabel(iChann, channel);
    }
  }
  cout<<"Combined fit: "<<rFit->getVal()<<" "<<rFit->getAsymErrorLo()<<" +"<<rFit->getAsymErrorHi()<<endl;
  points->SetLineColor(kRed);
  points->SetLineWidth(3);
  points->SetMarkerStyle(21);

  TCanvas *can = new TCanvas(TString::Format("ChannelCompatibility_m%d",MASS),TString::Format("ChannelCompatibility_m%d",MASS),900,750);
  gPad->SetTicks(1,1);
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

  TPaveText *pave = new TPaveText(0.60,0.82,0.9,0.95,"NDC");
  pave->AddText(TString::Format("m_{H} = %d GeV",MASS));
  pave->AddText(TString::Format("combined fit: %.1f^{%+.1f}_{%+.1f}",rFit->getVal(),rFit->getAsymErrorHi(),rFit->getAsymErrorLo()));
  pave->SetFillColor(0);
  pave->SetTextFont(62);
  pave->SetTextAlign(12);
  pave->SetTextSize(0.042);
  pave->SetBorderSize(0);
  pave->Draw();

  TLine *ln0 = new TLine(1,gPad->GetFrame()->GetY1(),1,gPad->GetFrame()->GetY2());
  ln0->SetLineColor(kBlack);
  ln0->SetLineWidth(1);
  ln0->SetLineStyle(2);
  ln0->Draw("same");

	can->SaveAs(TString::Format("channelComp_mH%d.pdf",MASS));
	can->SaveAs(TString::Format("channelComp_mH%d.png",MASS));

	for (int i=0; i<7; i++) {
		ExtraPaves[i]->Draw();
	}
	can->SaveAs(TString::Format("channelComp_mH%d_2.pdf",MASS));
	can->SaveAs(TString::Format("channelComp_mH%d_2.png",MASS));

}
