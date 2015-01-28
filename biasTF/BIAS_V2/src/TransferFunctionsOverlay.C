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
  //float SCALE[3][NSEL][NCAT[0]] = {
  //   {{0.5,0.5,0.5,0.5},{0.5,0.5,0.5}},
  //   {{0.05,0.05,0.05,0.05},{0.05,0.05,0.05,0.05}},
  //   {{0.01,0.01,0.01,0.01},{0.02,0.015,0.022}}
  //};
  float SCALE[3][NSEL][NCAT[0]] = {
	  {{1.1,1.1,0.6,0.4},{0.5,0.5,0.5}},
	  {{0.5,0.5,0.05,0.05},{0.05,0.05,0.05,0.05}},
	  {{0.01,0.01,0.01,0.01},{0.02,0.015,0.022}}
  };
  float YMAX[NSEL][NCAT[0]]  = {{1,1.1,1.2,1.25},{1,1.10,1.20}}; // {{1,1.1,1.2,1.25},{1,1.15,1.35}};
  float YMIN[NSEL][NCAT[0]]  = {{1,0.9,0.8,0.75},{1,0.85,0.75}}; // {{1,0.9,0.8,0.75},{1,0.85,0.65}};

  TFile *outf = TFile::Open("TransferFunctionsOverlay.root","RECREATE");

  TH1F *hData[NSEL][NCAT[0]];
  TH1F *hRatio[NSEL][NCAT[0]]; 
  TF1  *fitRatio1[NSEL][NCAT[0]],*fitRatio2[NSEL][NCAT[0]],*fitRatio3[NSEL][NCAT[0]]; 
  TGraphErrors *gUnc1[NSEL][NCAT[0]],*gUnc2[NSEL][NCAT[0]],*gUnc3[NSEL][NCAT[0]],*gUncEnl1[NSEL][NCAT[0]],*gUncEnl2[NSEL][NCAT[0]],*gUncEnl3[NSEL][NCAT[0]];
  TGraphErrors *gUncEnlFrac1[NSEL][NCAT[0]],*gUncEnlFrac2[NSEL][NCAT[0]],*gUncEnlFrac3[NSEL][NCAT[0]];
  TGraph *gUncEnlDiff11[NSEL][NCAT[0]*2],*gUncEnlDiff21[NSEL][NCAT[0]*2],*gUncEnlDiff31[NSEL][NCAT[0]*2];
  TGraph *gUncEnlDiff12[NSEL][NCAT[0]*2],*gUncEnlDiff22[NSEL][NCAT[0]*2],*gUncEnlDiff32[NSEL][NCAT[0]*2];
  TGraph *gUncEnlDiff13[NSEL][NCAT[0]*2],*gUncEnlDiff23[NSEL][NCAT[0]*2],*gUncEnlDiff33[NSEL][NCAT[0]*2];
  TVirtualFitter *fitter1,*fitter2,*fitter3;
  TMatrixDSym COV1,COV2,COV3;
  
  TCanvas *can1[NSEL];
  TCanvas *can2[NSEL];
  //TCanvas *can = new TCanvas("aux","aux");
 
  float vx[200],vy[200],vex[200],vey[200],vey_approx[200];
  
  int counter(0);
  for(int isel=0;isel<NSEL;isel++) { 
    TFile *infData = TFile::Open("flat/Fit_data_sel"+SELECTION[isel]+".root");
    TTree *trData = (TTree*)infData->Get("Hbb/events");
    can2[isel] = new TCanvas("transfer_sel"+SELECTION[isel],"transfer_sel"+SELECTION[isel],400*(NCAT[isel]-1),1200);
    can2[isel]->Divide(NCAT[isel]-1,4);
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
      TF1 *ln2 = new TF1("line2","0.",XMIN[isel],XMAX[isel]);
      ln2->SetLineColor(kBlack);
      ln2->SetLineWidth(1.0);
      ln2->SetLineStyle(2);
      ln2->SetMinimum(YMIN[isel][icat]);
      ln2->SetMaximum(YMAX[isel][icat]);
      ln2->GetXaxis()->SetTitle("M_{bb} (GeV)");
      ln2->GetYaxis()->SetTitle("Error Band - Mean");
      TString ss("sel"+SELTAG[isel]+TString::Format("_CAT%d",icat));
      hData[isel][icat] = new TH1F("hData_"+ss,"hData_"+ss,(XMAX[isel]-XMIN[isel])/BINSIZE[isel],XMIN[isel],XMAX[isel]);
      hData[isel][icat]->Sumw2();
      hData[isel][icat]->SetMarkerStyle(STYLE[icat]);
      hData[isel][icat]->SetMarkerColor(COLOR[icat]);
      hData[isel][icat]->SetLineColor(COLOR[icat]);
      if (isel == 0) {
        TCut cut(TString::Format("mvaNOM>%1.2f && mvaNOM<=%1.2f",MVA_BND[isel][icat],MVA_BND[isel][icat+1])); 
        can2[isel]->cd(1);
        trData->Draw("mbbReg[1]>>hData_"+ss,cut);
      }
      else {
        TCut cut(TString::Format("mvaVBF>%1.2f && mvaVBF<=%1.2f",MVA_BND[isel][icat],MVA_BND[isel][icat+1])); 
        can2[isel]->cd(1);
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
        gUncEnl1[isel][icat]  = getUnc(COV1,fitRatio1[isel][icat],hRatio[isel][icat],true,SCALE[0][isel][icat]);
        gUncEnl2[isel][icat]  = getUnc(COV2,fitRatio2[isel][icat],hRatio[isel][icat],true,SCALE[1][isel][icat]);
        gUncEnl3[isel][icat]  = getUnc(COV3,fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[2][isel][icat]);
        gUncEnlDiff11[isel][icat]  = getUncDiff(COV1,fitRatio1[isel][icat],fitRatio1[isel][icat],hRatio[isel][icat],true,SCALE[0][isel][icat],1);
        gUncEnlDiff21[isel][icat]  = getUncDiff(COV1,fitRatio2[isel][icat],fitRatio1[isel][icat],hRatio[isel][icat],true,SCALE[0][isel][icat],1);
        gUncEnlDiff31[isel][icat]  = getUncDiff(COV1,fitRatio3[isel][icat],fitRatio1[isel][icat],hRatio[isel][icat],true,SCALE[0][isel][icat],1);
        gUncEnlDiff11[isel][icat+NCAT[isel]]  = getUncDiff(COV1,fitRatio1[isel][icat],fitRatio1[isel][icat],hRatio[isel][icat],true,SCALE[0][isel][icat],-1);
        gUncEnlDiff21[isel][icat+NCAT[isel]]  = getUncDiff(COV1,fitRatio2[isel][icat],fitRatio1[isel][icat],hRatio[isel][icat],true,SCALE[0][isel][icat],-1);
        gUncEnlDiff31[isel][icat+NCAT[isel]]  = getUncDiff(COV1,fitRatio3[isel][icat],fitRatio1[isel][icat],hRatio[isel][icat],true,SCALE[0][isel][icat],-1);
        gUncEnlDiff12[isel][icat]  = getUncDiff(COV2,fitRatio1[isel][icat],fitRatio2[isel][icat],hRatio[isel][icat],true,SCALE[1][isel][icat],1);
        gUncEnlDiff22[isel][icat]  = getUncDiff(COV2,fitRatio2[isel][icat],fitRatio2[isel][icat],hRatio[isel][icat],true,SCALE[1][isel][icat],1);
        gUncEnlDiff32[isel][icat]  = getUncDiff(COV2,fitRatio3[isel][icat],fitRatio2[isel][icat],hRatio[isel][icat],true,SCALE[1][isel][icat],1);
        gUncEnlDiff12[isel][icat+NCAT[isel]]  = getUncDiff(COV2,fitRatio1[isel][icat],fitRatio2[isel][icat],hRatio[isel][icat],true,SCALE[1][isel][icat],-1);
        gUncEnlDiff22[isel][icat+NCAT[isel]]  = getUncDiff(COV2,fitRatio2[isel][icat],fitRatio2[isel][icat],hRatio[isel][icat],true,SCALE[1][isel][icat],-1);
        gUncEnlDiff32[isel][icat+NCAT[isel]]  = getUncDiff(COV2,fitRatio3[isel][icat],fitRatio2[isel][icat],hRatio[isel][icat],true,SCALE[1][isel][icat],-1);
        gUncEnlDiff13[isel][icat]  = getUncDiff(COV3,fitRatio1[isel][icat],fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[2][isel][icat],1);
        gUncEnlDiff23[isel][icat]  = getUncDiff(COV3,fitRatio2[isel][icat],fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[2][isel][icat],1);
        gUncEnlDiff33[isel][icat]  = getUncDiff(COV3,fitRatio3[isel][icat],fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[2][isel][icat],1);
        gUncEnlDiff13[isel][icat+NCAT[isel]]  = getUncDiff(COV3,fitRatio1[isel][icat],fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[2][isel][icat],-1);
        gUncEnlDiff23[isel][icat+NCAT[isel]]  = getUncDiff(COV3,fitRatio2[isel][icat],fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[2][isel][icat],-1);
        gUncEnlDiff33[isel][icat+NCAT[isel]]  = getUncDiff(COV3,fitRatio3[isel][icat],fitRatio3[isel][icat],hRatio[isel][icat],true,SCALE[2][isel][icat],-1);
        gUncEnlFrac1[isel][icat]  = getUncFrac(COV1,hRatio[isel][icat],SCALE[0][isel][icat]);
        gUncEnlFrac2[isel][icat]  = getUncFrac(COV2,hRatio[isel][icat],SCALE[1][isel][icat]);
        gUncEnlFrac3[isel][icat]  = getUncFrac(COV3,hRatio[isel][icat],SCALE[2][isel][icat]);
        gUnc1[isel][icat]->SetFillColor(kBlack);
        gUnc2[isel][icat]->SetFillColor(kBlue); 
        gUnc3[isel][icat]->SetFillColor(kRed); 
        gUncEnl1[isel][icat]->SetFillColor(kGray+1);
        gUncEnl2[isel][icat]->SetFillColor(kBlue+1);
        gUncEnl3[isel][icat]->SetFillColor(kRed+1);
        gUncEnlFrac1[isel][icat]->SetFillColor(kGray+1);
        gUncEnlFrac2[isel][icat]->SetFillColor(kBlue+1);
        gUncEnlFrac3[isel][icat]->SetFillColor(kRed+1);
        gUncEnlDiff11[isel][icat]->SetLineColor(kBlack);
        gUncEnlDiff21[isel][icat]->SetLineColor(kBlue);
        gUncEnlDiff31[isel][icat]->SetLineColor(kRed);
        gUncEnlDiff11[isel][icat+NCAT[isel]]->SetLineColor(kBlack);
        gUncEnlDiff21[isel][icat+NCAT[isel]]->SetLineColor(kBlue);
        gUncEnlDiff31[isel][icat+NCAT[isel]]->SetLineColor(kRed);
        gUncEnlDiff11[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff21[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff31[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff12[isel][icat]->SetLineColor(kBlack);
        gUncEnlDiff22[isel][icat]->SetLineColor(kBlue);
        gUncEnlDiff32[isel][icat]->SetLineColor(kRed);
        gUncEnlDiff12[isel][icat+NCAT[isel]]->SetLineColor(kBlack);
        gUncEnlDiff22[isel][icat+NCAT[isel]]->SetLineColor(kBlue);
        gUncEnlDiff32[isel][icat+NCAT[isel]]->SetLineColor(kRed);
        gUncEnlDiff12[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff22[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff32[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff13[isel][icat]->SetLineColor(kBlack);
        gUncEnlDiff23[isel][icat]->SetLineColor(kBlue);
        gUncEnlDiff33[isel][icat]->SetLineColor(kRed);
        gUncEnlDiff13[isel][icat+NCAT[isel]]->SetLineColor(kBlack);
        gUncEnlDiff23[isel][icat+NCAT[isel]]->SetLineColor(kBlue);
        gUncEnlDiff33[isel][icat+NCAT[isel]]->SetLineColor(kRed);
        gUncEnlDiff13[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff23[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUncEnlDiff33[isel][icat+NCAT[isel]]->SetLineStyle(kDashed);
        gUnc1[isel][icat]->SetFillStyle(3004);
        gUnc2[isel][icat]->SetFillStyle(3004);
        gUnc3[isel][icat]->SetFillStyle(3004);
        gUncEnl1[isel][icat]->SetFillStyle(3005); 
        gUncEnl2[isel][icat]->SetFillStyle(3006); 
        gUncEnl3[isel][icat]->SetFillStyle(3007); 
        gUncEnlFrac1[isel][icat]->SetFillStyle(3004); 
        gUncEnlFrac2[isel][icat]->SetFillStyle(3004); 
        gUncEnlFrac3[isel][icat]->SetFillStyle(3004); 
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

		  cout << icat << endl;
        can2[isel]->cd(icat);
        ln->Draw();
        gUncEnl2[isel][icat]->Draw("sameE3");
        ln->Draw("same");
        gUnc2[isel][icat]->Draw("sameE3"); 
        hRatio[isel][icat]->Draw("same");

        TLegend *leg1 = new TLegend(0.12,0.13,0.6,0.42);
        leg1->SetHeader("sel"+SELTAG[isel]+TString::Format("_CAT%d",counter));
        leg1->AddEntry(hRatio[isel][icat],"data","P");
        leg1->AddEntry(fitRatio1[isel][icat],TString::Format("pol1 fit (%1.2f) (%.3f)",fitRatio1[isel][icat]->GetProb(),fitRatio1[isel][icat]->GetChisquare()/fitRatio1[isel][icat]->GetNDF()),"L");
        leg1->AddEntry(fitRatio2[isel][icat],TString::Format("pol2 fit (%1.2f) (%.3f)",fitRatio2[isel][icat]->GetProb(),fitRatio2[isel][icat]->GetChisquare()/fitRatio2[isel][icat]->GetNDF()),"L"); 
        leg1->AddEntry(fitRatio3[isel][icat],TString::Format("pol3 fit (%1.2f) (%.3f)",fitRatio3[isel][icat]->GetProb(),fitRatio3[isel][icat]->GetChisquare()/fitRatio3[isel][icat]->GetNDF()),"L");
        leg1->AddEntry(gUncEnl2[isel][icat],"syst. unc.","F");
        leg1->AddEntry(gUnc2[isel][icat],"cor. unc. (pol3)","F"); 
        leg1->SetFillStyle(-1);
        leg1->SetBorderSize(0);
        leg1->SetTextFont(42);
        leg1->SetTextSize(0.035);
        leg1->Draw();      

		  gPad->Update();
		  can2[isel]->cd(icat+NCAT[isel]-1);
		  ln2->SetMinimum(-0.05);
		  ln2->SetMaximum(+0.05);
		  ln2->Draw();
	//	  float a[6] = {TMath::MaxElement(200,gUncEnlDiff11[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff21[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff31[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff11[isel][icat+NCAT[isel]]->GetY()),TMath::MaxElement(200,gUncEnlDiff21[isel][icat+NCAT[isel]]->GetY()),TMath::MaxElement(200,gUncEnlDiff31[isel][icat+NCAT[isel]]->GetY())};
	//     float m = TMath::MaxElement(6,a);
	//	  gUncEnlDiff11[isel][icat]->GetYaxis()->SetRangeUser(-0.05,m*1.05);
		  gUncEnlDiff11[isel][icat]->GetYaxis()->SetRangeUser(-0.05,0.05);
		  gUncEnlDiff11[isel][icat]->GetXaxis()->SetLimits(XMIN[isel],XMAX[isel]);
		  gUncEnlDiff11[isel][icat]->Draw("L");  
		  gUncEnlDiff21[isel][icat]->Draw("L");  
		  gUncEnlDiff31[isel][icat]->Draw("L");  
		  gUncEnlDiff11[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlDiff21[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlDiff31[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlFrac1[isel][icat]->Draw("same3");
		  ln2->Draw("same");

		  gPad->Update();
		  can2[isel]->cd(icat+2*(NCAT[isel]-1));
		  ln2->SetMinimum(-0.05);
		  ln2->SetMaximum(+0.05);
		  ln2->Draw();
	//	  float a[6] = {TMath::MaxElement(200,gUncEnlDiff12[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff22[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff32[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff12[isel][icat+NCAT[isel]]->GetY()),TMath::MaxElement(200,gUncEnlDiff22[isel][icat+NCAT[isel]]->GetY()),TMath::MaxElement(200,gUncEnlDiff32[isel][icat+NCAT[isel]]->GetY())};
	//     float m = TMath::MaxElement(6,a);
	//	  gUncEnlDiff12[isel][icat]->GetYaxis()->SetRangeUser(-0.05,m*1.05);
		  gUncEnlDiff12[isel][icat]->GetYaxis()->SetRangeUser(-0.05,0.05);
		  gUncEnlDiff12[isel][icat]->GetXaxis()->SetLimits(XMIN[isel],XMAX[isel]);
		  gUncEnlDiff12[isel][icat]->Draw("L");  
		  gUncEnlDiff22[isel][icat]->Draw("L");  
		  gUncEnlDiff32[isel][icat]->Draw("L");  
		  gUncEnlDiff12[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlDiff22[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlDiff32[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlFrac2[isel][icat]->Draw("same3");
		  ln2->Draw("same");

		  gPad->Update();
		  can2[isel]->cd(icat+3*(NCAT[isel]-1));
		  ln2->SetMinimum(-0.12);
		  ln2->SetMaximum(+0.12);
		  ln2->Clone()->Draw();
	//	  float a[6] = {TMath::MaxElement(200,gUncEnlDiff13[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff23[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff33[isel][icat]->GetY()),TMath::MaxElement(200,gUncEnlDiff13[isel][icat+NCAT[isel]]->GetY()),TMath::MaxElement(200,gUncEnlDiff23[isel][icat+NCAT[isel]]->GetY()),TMath::MaxElement(200,gUncEnlDiff33[isel][icat+NCAT[isel]]->GetY())};
	//     float m = TMath::MaxElement(6,a);
	//	  gUncEnlDiff13[isel][icat]->GetYaxis()->SetRangeUser(-0.05,m*1.05);
		  gUncEnlDiff13[isel][icat]->GetYaxis()->SetRangeUser(-0.12,0.12);
		  gUncEnlDiff13[isel][icat]->GetXaxis()->SetLimits(XMIN[isel],XMAX[isel]);
		  gUncEnlDiff13[isel][icat]->Draw("L");  
		  gUncEnlDiff23[isel][icat]->Draw("L");  
		  gUncEnlDiff33[isel][icat]->Draw("L");  
		  gUncEnlDiff13[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlDiff23[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlDiff33[isel][icat+NCAT[isel]]->Draw("L");  
		  gUncEnlFrac3[isel][icat]->Draw("same3");
		  ln2->Draw("same");
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

TGraph *getUncDiff(TMatrixDSym COV, TF1 *fit, TF1 *fitref, TH1F *h, bool APPROX, float SCALE, float upperlower)
{
  int N = COV.GetNrows();
  float vx[200],vy[200];
  float dx = (h->GetBinLowEdge(h->GetNbinsX())+h->GetBinWidth(1)-h->GetBinLowEdge(1))/200;
  for(int b=0; b<200; b++) {
    vx[b]  = h->GetBinLowEdge(1)+(b+1)*dx;
	 float vey = 0;
    for(int i=0;i<N;i++) {
      vey += SCALE*SCALE*pow(vx[b],i)*pow(vx[b],i)*COV(i,i);
    }
	 vey = sqrt(vey);
    vy[b]  = fit->Eval(vx[b]) / fitref->Eval(vx[b]) - 1.;
  }
  TGraph *g = new TGraph(200,vx,vy);
  return g;
}

TGraphErrors *getUncFrac(TMatrixDSym COV, TH1F *h, float SCALE)
{
  int N = COV.GetNrows();
  float vx[200],vy[200],vex[200],vey[200];
  float dx = (h->GetBinLowEdge(h->GetNbinsX())+h->GetBinWidth(1)-h->GetBinLowEdge(1))/200;
  for(int b=0; b<200; b++) {
    vx[b]  = h->GetBinLowEdge(1)+(b+1)*dx;
    vex[b] = 0.0;
	 vey[b] = 0.0;
    for(int i=0;i<N;i++) {
      vey[b] += SCALE*SCALE*pow(vx[b],i)*pow(vx[b],i)*COV(i,i);
    }
	 vey[b] = sqrt(vey[b]);
	 vy[b]  = 0.0; 
  }
  TGraphErrors *g = new TGraphErrors(200,vx,vy,vex,vey);
  return g;
}













