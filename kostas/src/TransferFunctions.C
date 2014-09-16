void TransferFunctions(float XMIN,float XMAX)
{
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};
  TString SELECTION[2] = {"NOM","VBF"};  
  TString SELTAG[2] = {"NOM","PRK"};
  int STYLE[NCAT[0]] = {20,20,23,21};
  int COLOR[NCAT[0]] = {kBlack,kBlue,kRed,kGreen+2};

  TFile *outf = TFile::Open("output/TransferFunctions.root","RECREATE");

  TH1F *hData[NSEL][NCAT[0]];
  TH1F *hRatio[NSEL][NCAT[0]]; 
  TF1  *fitRatio[NSEL][NCAT[0]]; 
  TGraphErrors *gUnc[NSEL][NCAT[0]],*gUnc_approx[NSEL][NCAT[0]];
  TVirtualFitter *fitter;
  TMatrixDSym COV;
  
  TCanvas *can1[NSEL];
  TCanvas *can2[NSEL];
  TCanvas *can = new TCanvas("aux","aux");
 
  float vx[200],vy[200],vex[200],vey[200],vey_approx[200];
  
  TF1 *ln = new TF1("line","1",XMIN,XMAX);
  ln->SetLineColor(kBlack);
  ln->SetLineWidth(1.0);
  ln->SetLineStyle(2);
  ln->SetMinimum(0.7);
  ln->SetMaximum(1.3);
  ln->GetXaxis()->SetTitle("M_{bb} (GeV)");
  ln->GetYaxis()->SetTitle("Signal/Control");
  int counter(0);
  for(int isel=0;isel<NSEL;isel++) {
    TFile *infData = TFile::Open("flat/Fit_data_sel"+SELECTION[isel]+".root");
    TTree *trData = (TTree*)infData->Get("Hbb/events");
    can2[isel] = new TCanvas("transfer_sel"+SELECTION[isel],"transfer_sel"+SELECTION[isel],400*(NCAT[isel]-1),450);
    can2[isel]->Divide(NCAT[isel]-1,1);
    TLegend *leg = new TLegend(0.6,0.6,0.9,0.9);
    leg->SetHeader(SELTAG[isel]+" selection");
    leg->SetFillColor(0);
    leg->SetBorderSize(0);
    leg->SetTextFont(42);
    leg->SetTextSize(0.05);  
    for(int icat=0;icat<NCAT[isel];icat++) { 
      TString ss("sel"+SELTAG[isel]+TString::Format("_CAT%d",icat));
      hData[isel][icat] = new TH1F("hData_"+ss,"hData_"+ss,(XMAX-XMIN)/5.0,XMIN,XMAX);
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
      hRatio[isel][icat]->SetMarkerStyle(STYLE[icat]);
      hRatio[isel][icat]->SetMarkerColor(COLOR[icat]);
      hRatio[isel][icat]->SetLineColor(COLOR[icat]); 
      hRatio[isel][icat]->Divide(hData[isel][0]);
      hRatio[isel][icat]->SetDirectory(0);
      fitRatio[isel][icat] = new TF1("fitRatio_"+ss,"pol2",XMIN,XMAX);
      fitRatio[isel][icat]->SetLineColor(COLOR[icat]);
      
      if (icat > 0) {
        hRatio[isel][icat]->Fit(fitRatio[isel][icat],"RQ");
        fitter = TVirtualFitter::GetFitter();
        COV.Use(fitter->GetNumberTotalParameters(),fitter->GetCovarianceMatrix());
        float dx = (hRatio[isel][icat]->GetBinLowEdge(hRatio[isel][icat]->GetNbinsX())+hRatio[isel][icat]->GetBinWidth(1)-hRatio[isel][icat]->GetBinLowEdge(1))/200;
        for(int i=0;i<200;i++) {
          vx[i] = hRatio[isel][icat]->GetBinLowEdge(1)+(i+1)*dx;
          vy[i] = fitRatio[isel][icat]->Eval(vx[i]);
          vex[i] = 0.0;
          //vey[i] = sqrt(pow(vx[i],2)*COV(1,1)+COV(0,0)); // linear
          vey[i] = sqrt(COV(0,0)+2*vx[i]*COV(0,1)+(2*COV(0,2)+COV(1,1))*pow(vx[i],2)+2*COV(1,2)*pow(vx[i],3)+COV(2,2)*pow(vx[i],4));// quadratic
          // approximate quadratic error band: ignore correlations but shrink the errors
          vey_approx[i] = sqrt(0.0025*COV(0,0)+0.0025*COV(1,1)*pow(vx[i],2)+0.0025*COV(2,2)*pow(vx[i],4));
        }
        gUnc[isel][icat] = new TGraphErrors(200,vx,vy,vex,vey);
        gUnc_approx[isel][icat] = new TGraphErrors(200,vx,vy,vex,vey_approx);
        gUnc[isel][icat]->SetFillColor(COLOR[icat]);
        gUnc[isel][icat]->SetFillStyle(3004);
        gUnc_approx[isel][icat]->SetFillColor(kGray);
        gUnc_approx[isel][icat]->SetFillStyle(1001); 
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
        gUnc_approx[isel][icat]->Draw("sameE3");
        ln->Draw("same");
        gUnc[isel][icat]->Draw("sameE3");
        hRatio[isel][icat]->Draw("same");
        TPaveText *pave = new TPaveText(0.2,0.8,0.5,0.9,"NDC");
        pave->AddText("sel"+SELTAG[isel]+TString::Format("_CAT%d",counter));
        pave->SetFillColor(0);
        pave->SetBorderSize(0);
        pave->SetTextFont(42);
        pave->SetTextSize(0.05);
        pave->Draw(); 
      }
      outf->cd();
      fitRatio[isel][icat]->Write();
      counter++;
    }
    can1[isel]->cd();
   	leg->Draw(); 
	can1[isel]->SaveAs(TString::Format("plots/transfer/%s.png",can1[isel]->GetName()));
	can2[isel]->SaveAs(TString::Format("plots/transfer/%s.png",can2[isel]->GetName()));
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
