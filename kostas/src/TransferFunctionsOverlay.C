void TransferFunctionsOverlay()
{
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};
  TString SELECTION[2] = {"NOM","VBF"};  
  TString SELTAG[2] = {"NOM","PRK"};
  int STYLE[NCAT[0]] = {20,20,23,21};
  int COLOR[NCAT[0]] = {kBlack,kBlue,kRed,kGreen+2};
  float XMIN[NSEL]   = {80,80};
  float XMAX[NSEL]   = {200,200};
  float BINSIZE[NSEL]= {5,5};
  float SCALE[NSEL][NCAT[0]] = {{0.01,0.01,0.01,0.01},{0.02,0.015,0.022}};
  float YMAX[NSEL][NCAT[0]]  = {{1,1.1,1.2,1.25},{1,1.10,1.20}}; // {{1,1.1,1.2,1.25},{1,1.15,1.35}};
  float YMIN[NSEL][NCAT[0]]  = {{1,0.9,0.8,0.75},{1,0.85,0.75}}; // {{1,0.9,0.8,0.75},{1,0.85,0.65}};

  TFile *outf = TFile::Open("TransferFunctionsOverlay.root","RECREATE");

  TH1F *hData[NSEL][NCAT[0]];
  TH1F *hRatio[NSEL][NCAT[0]]; 
  TF1  *fitRatio1[NSEL][NCAT[0]],*fitRatio2[NSEL][NCAT[0]],*fitRatio3[NSEL][NCAT[0]]; 
  TGraphErrors *gUnc1[NSEL][NCAT[0]],*gUnc2[NSEL][NCAT[0]],*gUnc3[NSEL][NCAT[0]],*gUnc[NSEL][NCAT[0]];
  TVirtualFitter *fitter1,*fitter2,*fitter3;
  TMatrixDSym COV1,COV2,COV3;
  
  TCanvas *can1[NSEL];
  TCanvas *can2[NSEL];
  TCanvas *can = new TCanvas("aux","aux");
 
  float vx[200],vy[200],vex[200],vey[200],vey_approx[200];
  
  int counter(0);
  for(int isel=0;isel<NSEL;isel++) { 
    TFile *infData = TFile::Open("flat/Fit_data_sel"+SELECTION[isel]+".root");
    TTree *trData = (TTree*)infData->Get("Hbb/events");
    can2[isel] = new TCanvas("transfer_sel"+SELECTION[isel],"transfer_sel"+SELECTION[isel],400*(NCAT[isel]-1),450);
    can2[isel]->Divide(NCAT[isel]-1,1);
    TLegend *leg = new TLegend(0.6,0.6,0.9,0.9);
    leg->SetHeader(SELTAG[isel]+" selection");
    leg->SetFillStyle(-1);
    leg->SetBorderSize(0);
    leg->SetTextFont(42);
    leg->SetTextSize(0.04);  
    for(int icat=0;icat<NCAT[isel];icat++) { 
      TF1 *ln = new TF1("line","1",XMIN[isel],XMAX[isel]);
      ln->SetLineColor(kBlack);
      ln->SetLineWidth(1.0);
      ln->SetLineStyle(2);
      ln->SetMinimum(YMIN[isel][icat]);
      ln->SetMaximum(YMAX[isel][icat]);
      ln->GetXaxis()->SetTitle("M_{bb} (GeV)");
      ln->GetYaxis()->SetTitle("Signal/Control");
      TString ss("sel"+SELTAG[isel]+TString::Format("_CAT%d",icat));
      hData[isel][icat] = new TH1F("hData_"+ss,"hData_"+ss,(XMAX[isel]-XMIN[isel])/BINSIZE[isel],XMIN[isel],XMAX[isel]);
      hData[isel][icat]->Sumw2();
      hData[isel][icat]->SetMarkerStyle(STYLE[icat]);
      hData[isel][icat]->SetMarkerColor(COLOR[icat]);
      hData[isel][icat]->SetLineColor(COLOR[icat]);
      if (isel == 0) {
        TCut cut(TString::Format("mvaNOM>%1.2f && mvaNOM<=%1.2f",MVA_BND[isel][icat],MVA_BND[isel][icat+1])); 
        can->cd();
        trData->Draw("mbbReg[1]>>hData_"+ss,cut);
      }
      else {
        TCut cut(TString::Format("mvaVBF>%1.2f && mvaVBF<=%1.2f",MVA_BND[isel][icat],MVA_BND[isel][icat+1])); 
        can->cd();
        trData->Draw("mbbReg[2]>>hData_"+ss,cut);
      }  
      Blind(hData[isel][icat],100,150);
      hData[isel][icat]->Scale(1./hData[isel][icat]->Integral());
      hData[isel][icat]->SetDirectory(0);
      hRatio[isel][icat] = (TH1F*)hData[isel][icat]->Clone("Ratio_"+ss); 
      hRatio[isel][icat]->SetMarkerStyle(20);
      hRatio[isel][icat]->SetMarkerColor(kBlack);
      hRatio[isel][icat]->SetLineColor(kBlack); 
      hRatio[isel][icat]->Divide(hData[isel][0]);
      hRatio[isel][icat]->SetDirectory(0);
      fitRatio1[isel][icat] = new TF1("fitRatio1_"+ss,"pol1",XMIN[isel],XMAX[isel]);
      fitRatio2[isel][icat] = new TF1("fitRatio2_"+ss,"pol2",XMIN[isel],XMAX[isel]);
      fitRatio3[isel][icat] = new TF1("fitRatio3_"+ss,"pol3",XMIN[isel],XMAX[isel]);
      fitRatio1[isel][icat]->SetLineColor(kBlack);
      fitRatio2[isel][icat]->SetLineColor(kBlue);
      fitRatio3[isel][icat]->SetLineColor(kRed);
      
      if (icat > 0) {
        hRatio[isel][icat]->Fit(fitRatio1[isel][icat],"RQ+");
        fitter1 = TVirtualFitter::GetFitter();
        COV1.Use(fitter1->GetNumberTotalParameters(),fitter1->GetCovarianceMatrix());
        hRatio[isel][icat]->Fit(fitRatio2[isel][icat],"RQ+");
        fitter2 = TVirtualFitter::GetFitter();
        COV2.Use(fitter2->GetNumberTotalParameters(),fitter2->GetCovarianceMatrix());
        hRatio[isel][icat]->Fit(fitRatio3[isel][icat],"RQ+"); 
        fitter3 = TVirtualFitter::GetFitter();
        COV3.Use(fitter3->GetNumberTotalParameters(),fitter3->GetCovarianceMatrix());
        //---------------------------------------------
        gUnc1[isel][icat] = getUnc(COV1,fitRatio1[isel][icat],hRatio[isel][icat],false,1);
        gUnc2[isel][icat] = getUnc(COV2,fitRatio2[isel][icat],hRatio[isel][icat],false,1);
        gUnc3[isel][icat] = getUnc(COV3,fitRatio3[isel][icat],hRatio[isel][icat],false,1); 
        gUnc[isel][icat]  = getUnc(COV3,fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[isel][icat]);
        gUnc1[isel][icat]->SetFillColor(kBlack);
        gUnc2[isel][icat]->SetFillColor(kBlue); 
        gUnc3[isel][icat]->SetFillColor(kRed); 
        gUnc[isel][icat]->SetFillColor(kGray);
        gUnc1[isel][icat]->SetFillStyle(3004);
        gUnc2[isel][icat]->SetFillStyle(3004);
        gUnc3[isel][icat]->SetFillStyle(3004);
        gUnc[isel][icat]->SetFillStyle(1001); 
      }
      if (icat == 0) {
        can1[isel] = new TCanvas("MbbShape_sel"+SELECTION[isel],"MbbShape_sel"+SELECTION[isel],900,600);
        can1[isel]->cd();
        hData[isel][icat]->SetFillColor(kGray);
        hData[isel][icat]->GetXaxis()->SetTitle("M_{bb} (GeV)"); 
        hData[isel][icat]->GetYaxis()->SetTitle("PDF"); 
        hData[isel][icat]->GetYaxis()->SetNdivisions(505);
        hData[isel][icat]->SetMaximum(0.25);
        hData[isel][icat]->Draw("HIST");
        leg->AddEntry(hData[isel][icat],TString::Format("CAT%d",counter),"F");
      }
      else {
        can1[isel]->cd();
        hData[isel][icat]->Draw("same E");
        leg->AddEntry(hData[isel][icat],TString::Format("CAT%d",counter),"P");

        can2[isel]->cd(icat);
        ln->Draw();
        gUnc[isel][icat]->Draw("sameE3");
        ln->Draw("same");
        gUnc3[isel][icat]->Draw("sameE3"); 
        hRatio[isel][icat]->Draw("same");

        TLegend *leg1 = new TLegend(0.12,0.13,0.6,0.42);
        leg1->SetHeader("sel"+SELTAG[isel]+TString::Format("_CAT%d",counter));
        leg1->AddEntry(hRatio[isel][icat],"data","P");
        leg1->AddEntry(fitRatio1[isel][icat],TString::Format("pol1 fit (%1.2f) (%.3f)",fitRatio1[isel][icat]->GetProb(),fitRatio1[isel][icat]->GetChisquare()/fitRatio1[isel][icat]->GetNDF()),"L");
        leg1->AddEntry(fitRatio2[isel][icat],TString::Format("pol2 fit (%1.2f) (%.3f)",fitRatio2[isel][icat]->GetProb(),fitRatio2[isel][icat]->GetChisquare()/fitRatio2[isel][icat]->GetNDF()),"L"); 
        leg1->AddEntry(fitRatio3[isel][icat],TString::Format("pol3 fit (%1.2f) (%.3f)",fitRatio3[isel][icat]->GetProb(),fitRatio3[isel][icat]->GetChisquare()/fitRatio3[isel][icat]->GetNDF()),"L");
        leg1->AddEntry(gUnc[isel][icat],"syst. unc.","F");
        leg1->AddEntry(gUnc3[isel][icat],"cor. unc. (pol3)","F"); 
        leg1->SetFillStyle(-1);
        leg1->SetBorderSize(0);
        leg1->SetTextFont(42);
        leg1->SetTextSize(0.035);
        leg1->Draw();      
      }
      outf->cd();
      fitRatio3[isel][icat]->Write();
      COV3.Write("COV_"+ss);
      counter++;
    }
    can1[isel]->cd();
    leg->Draw();
	 can1[isel]->SaveAs(TString::Format("%s.png",can1[isel]->GetName()).Data());
	 can2[isel]->SaveAs(TString::Format("%s.png",can2[isel]->GetName()).Data());
  }
  outf->Close();
  delete can;
}

void Blind(TH1F *h, float X1, float X2)
{
  for(int i=0;i<h->GetNbinsX();i++) {
    float x0 = h->GetBinCenter(i+1);
    if (x0 >= X1 && x0 <= X2) {
      h->SetBinContent(i+1,0);
      h->SetBinError(i+1,0);
    }
  }
}

TGraphErrors *getUnc(TMatrixDSym COV, TF1 *fit, TH1F *h, bool APPROX, float SCALE)
{
  int N = COV.GetNrows();
  float vx[200],vy[200],vex[200],vey[200];
  float dx = (h->GetBinLowEdge(h->GetNbinsX())+h->GetBinWidth(1)-h->GetBinLowEdge(1))/200;
  for(int b=0;b<200;b++) {
    vx[b]  = h->GetBinLowEdge(1)+(b+1)*dx;
    vy[b]  = fit->Eval(vx[b]);
    vex[b] = 0.0;
    float sum(0.0);
    if (APPROX) {
      for(int i=0;i<N;i++) {
        sum += SCALE*SCALE*pow(vx[b],i)*pow(vx[b],i)*COV(i,i);
      }
    }
    else { 
      for(int i=0;i<N;i++) {
        for(int j=0;j<N;j++) {
          sum += pow(vx[b],i)*pow(vx[b],j)*COV(i,j);
        }
      }
    }
    vey[b] = sqrt(sum);
  }  
  TGraphErrors *g = new TGraphErrors(200,vx,vy,vex,vey);
  return g;
}

















