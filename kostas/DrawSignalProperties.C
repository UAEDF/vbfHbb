void DrawSignalProperties(TString OPTION)
{
  gROOT->ForceStyle();
  const int NCAT = 7;
  const int N = 5;
  const int MASS[N] = {115,120,125,130,135};
  int COLOR[N] = {kBlack,kGreen+1,kRed+1,kBlue,kMagenta};
  int STYLE[N] = {20,21,22,23,24};
 
  TFile *fSig  = TFile::Open("signal_shapes_workspace_"+OPTION+".root");
  RooWorkspace *wSig = (RooWorkspace*)fSig->Get("w");

  float x[N],yMean[N][NCAT],ySigma[N][NCAT],yWidth[N][NCAT],eMean[N][NCAT],eSigma[N][NCAT];  

  TH1F *hWidth[N],*hMean[N],*hSigma[N];
  TH2F *hFractionGF = new TH2F("FractionGF","FractionGF",NCAT,0,NCAT,N,0,N); 
  for(int icat=0;icat<NCAT;icat++) {
    hFractionGF->GetXaxis()->SetBinLabel(icat+1,TString::Format("CAT%d",icat)); 
  }
  for(int im=0;im<N;im++) {
    hFractionGF->GetYaxis()->SetBinLabel(im+1,TString::Format("%d",MASS[im])); 
  }

  //---------------------------------------------------------------------
  TCanvas *can = new TCanvas("SignalProperties","SignalProperties",900,600);
  can->Divide(2,2);
  TCanvas *can2 = new TCanvas("GFFraction","GFFraction",900,600);
  TLegend *leg = new TLegend(0.18,0.2,0.9,0.9);
  leg->SetFillColor(0);
  leg->SetBorderSize(0);
  leg->SetTextFont(42);
  leg->SetTextSize(0.07);
  

  for(int im=0;im<N;im++) {
    hWidth[im]      = new TH1F(TString::Format("width_m%d",MASS[im]),TString::Format("width_m%d",MASS[im]),NCAT,0,NCAT);
    hMean[im]       = new TH1F(TString::Format("mean_m%d",MASS[im]),TString::Format("mean_m%d",MASS[im]),NCAT,0,NCAT);
    hSigma[im]      = new TH1F(TString::Format("sigma_m%d",MASS[im]),TString::Format("sigma_m%d",MASS[im]),NCAT,0,NCAT);
    hWidth[im]->SetLineColor(COLOR[im]);
    hWidth[im]->SetMarkerColor(COLOR[im]);
    hWidth[im]->SetMarkerStyle(STYLE[im]);
    hMean[im]->SetLineColor(COLOR[im]);
    hMean[im]->SetMarkerColor(COLOR[im]);
    hMean[im]->SetMarkerStyle(STYLE[im]);
    hSigma[im]->SetLineColor(COLOR[im]);
    hSigma[im]->SetMarkerColor(COLOR[im]);
    hSigma[im]->SetMarkerStyle(STYLE[im]);
    x[im] = MASS[im];
    for(int icat=0;icat<NCAT;icat++) {
      if (im == 0) {
        hWidth[im]->GetXaxis()->SetBinLabel(icat+1,TString::Format("CAT%d",icat)); 
        hMean[im]->GetXaxis()->SetBinLabel(icat+1,TString::Format("CAT%d",icat));
        hSigma[im]->GetXaxis()->SetBinLabel(icat+1,TString::Format("CAT%d",icat));
      }
      
      yMean[im][icat]  = (RooRealVar*)wSig->var(TString::Format("mean_m%d_CAT%d",MASS[im],icat))->getValV(); 
      eMean[im][icat]  = (RooRealVar*)wSig->var(TString::Format("mean_m%d_CAT%d",MASS[im],icat))->getError();
      ySigma[im][icat] = (RooRealVar*)wSig->var(TString::Format("sigma_m%d_CAT%d",MASS[im],icat))->getValV(); 
      eSigma[im][icat] = (RooRealVar*)wSig->var(TString::Format("sigma_m%d_CAT%d",MASS[im],icat))->getError();  
      yWidth[im][icat] = (RooRealVar*)wSig->var(TString::Format("fwhm_m%d_CAT%d",MASS[im],icat))->getValV()/yMean[im][icat]; 

      hWidth[im]->SetBinContent(icat+1,yWidth[im][icat]);
      hMean[im]->SetBinContent(icat+1,yMean[im][icat]/x[im]);
      hMean[im]->SetBinError(icat+1,eMean[im][icat]/x[im]);
      hSigma[im]->SetBinContent(icat+1,ySigma[im][icat]/yMean[im][icat]);
      hSigma[im]->SetBinError(icat+1,(ySigma[im][icat]/yMean[im][icat])*sqrt(pow(eMean[im][icat]/yMean[im][icat],2)+pow(eSigma[im][icat]/ySigma[im][icat],2)));

      float gf  = (RooRealVar*)wSig->var(TString::Format("yield_signalGF_mass%d_CAT%d",MASS[im],icat))->getValV();
      float vbf = (RooRealVar*)wSig->var(TString::Format("yield_signalVBF_mass%d_CAT%d",MASS[im],icat))->getValV();
      float f   = gf/(gf+vbf);
      hFractionGF->SetBinContent(icat+1,im+1,f);
    }
    leg->AddEntry(hWidth[im],TString::Format("M_{H} = %d GeV",MASS[im]),"P");
    
    if (im == 0) {
      hWidth[im]->GetYaxis()->SetRangeUser(0.1,0.3);
      hWidth[im]->GetYaxis()->SetTitle("FWHM / m");
      hMean[im]->GetYaxis()->SetRangeUser(0.9,1.1);
      hMean[im]->GetYaxis()->SetTitle("m / M_{H}");
      hSigma[im]->GetYaxis()->SetRangeUser(0.04,0.16);
      hSigma[im]->GetYaxis()->SetTitle("#sigma / m");
      can->cd(1);
      hWidth[im]->Draw("LP");
      can->cd(2);
      hMean[im]->Draw("LP");
      can->cd(3);
      hSigma[im]->Draw("LP");
    }
    else {
      can->cd(1);
      hWidth[im]->Draw("LPsame");
      can->cd(2); 
      hMean[im]->Draw("LPsame");
      can->cd(3); 
      hSigma[im]->Draw("LPsame");
    }
    
  }

  can->cd(4);
  leg->Draw();
  can2->cd();
  gStyle->SetPalette(42,0);
  gStyle->SetPaintTextFormat("1.2g");
  hFractionGF->SetMarkerSize(2.0);
  hFractionGF->GetYaxis()->SetTitle("Higgs mass (GeV)");
  hFractionGF->GetXaxis()->SetTitle("Category");
  hFractionGF->Draw("COL TEXT");
}
