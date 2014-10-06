void TransferFunctions(float XMIN_NOM, float XMAX_NOM, int TRORDER_NOM, TString TR_NOM, TString TRTAG_NOM, float XMIN_VBF, float XMAX_VBF, int TRORDER_VBF, TString TR_VBF, TString TRTAG_VBF, TString OUTPATH)
{
  if (TRORDER_NOM==-1 && TRORDER_VBF==-1) return 0;
  gROOT->ProcessLineSync(".x ../common/styleCMSTDR.C");
  gROOT->ForceStyle();
  gStyle->SetPadRightMargin(0.04);
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};
  TString SELECTION[2] = {"NOM","VBF"};  
  TString SELTAG[2] = {"NOM","PRK"};
  int STYLE[NCAT[0]] = {20,20,23,21};
  int COLOR[NCAT[0]] = {kBlack,kBlue,kRed,kGreen+2};
  //float XMIN[NSEL]   = {80,80};
  //float XMAX[NSEL]   = {300,200};
  float BINSIZE[NSEL]= {10,5};
  TString MBB[NSEL]={"mbbReg[1]","mbbReg[2]"};
  TString MVA[NSEL]={"mvaNOM","mvaVBF"};
  float XMIN[NSEL]={XMIN_NOM,XMIN_VBF};
  float XMAX[NSEL]={XMAX_NOM,XMAX_VBF};
  int TRORDER[NSEL]={TRORDER_NOM,TRORDER_VBF};
  TString TR[NSEL]={TR_NOM,TR_VBF};
  TString TRTAG[NSEL]={TRTAG_NOM,TRTAG_VBF};
  float SCALE[3][NSEL][NCAT[0]] = {
	  {{0.5,0.5,0.5,0.5},{0.5,0.5,0.5}},
	  {{0.05,0.05,0.05,0.05},{0.05,0.05,0.05}},
	  {{0.01,0.01,0.01,0.01},{0.02,0.015,0.022}}
  };

  system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
  system(TString::Format("[ ! -d %s/output ] && mkdir %s/output",OUTPATH.Data(),OUTPATH.Data()).Data());
  TFile *outf = TFile::Open(TString::Format("%s/output/transferFunctions.root",OUTPATH.Data()),"UPDATE");

  TH1F *hData[NSEL][NCAT[0]];
  TH1F *hRatio[NSEL][NCAT[0]]; 
  TF1  *fitRatio[NSEL][NCAT[0]]; 
  TGraphErrors *gUnc[NSEL][NCAT[0]],*gUnc_approx[NSEL][NCAT[0]];
  TVirtualFitter *fitter;
  TMatrixDSym COV;

  for (int isel=0; isel<NSEL; isel++) {
	  for (int icat=0; icat<NCAT[isel]; icat++) {
		  hData[isel][icat] = NULL;
		  hRatio[isel][icat] = NULL;
		  fitRatio[isel][icat] = NULL;
		  gUnc[isel][icat] = NULL;
		  gUnc_approx[isel][icat] = NULL;
	  }
  }
  
  TCanvas *can1[NSEL];
  TCanvas *can2[NSEL];
  TCanvas *can = new TCanvas("aux","aux");
 
  float vx[200],vy[200],vex[200],vey[200],vey_approx[200];
  
  int counter(0);
  for(int isel=0;isel<NSEL;isel++) {
    TF1 *ln = new TF1("line","1",XMIN[isel],XMAX[isel]);
    ln->SetLineColor(kBlack);
    ln->SetLineWidth(1.0);
    ln->SetLineStyle(2);
    ln->SetMinimum(0.8);
    ln->SetMaximum(1.2);
    ln->GetXaxis()->SetTitle("M_{bb} (GeV)");
    ln->GetYaxis()->SetTitle("Signal/Control"); 
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
      TString ss("sel"+SELTAG[isel]+TString::Format("_CAT%d",counter)+TString::Format("%s",TRTAG[isel].Data()));
		cout << "\n\033[1;34mWorking on: " << ss << "\033[m" << endl;
      hData[isel][icat] = new TH1F("hData_"+ss,"hData_"+ss,(XMAX[isel]-XMIN[isel])/BINSIZE[isel],XMIN[isel],XMAX[isel]);
      hData[isel][icat]->Sumw2();
      hData[isel][icat]->SetMarkerStyle(STYLE[icat]);
      hData[isel][icat]->SetMarkerColor(COLOR[icat]);
      hData[isel][icat]->SetLineColor(COLOR[icat]);
		TCut cut(TString::Format("%s>%1.2f && %s<=%1.2f",MVA[isel].Data(),MVA_BND[isel][icat],MVA[isel].Data(),MVA_BND[isel][icat+1]));
		can->cd();
		trData->Draw(TString::Format("%s>>hData_%s",MBB[isel].Data(),ss.Data()),cut);
      Blind(hData[isel][icat],100,150);
      hData[isel][icat]->Scale(1./hData[isel][icat]->Integral());
      hData[isel][icat]->SetDirectory(0);
      hRatio[isel][icat] = (TH1F*)hData[isel][icat]->Clone("Ratio_"+ss); 
      hRatio[isel][icat]->SetMarkerStyle(STYLE[icat]);
      hRatio[isel][icat]->SetMarkerColor(COLOR[icat]);
      hRatio[isel][icat]->SetLineColor(COLOR[icat]); 
      hRatio[isel][icat]->Divide(hData[isel][0]);
      hRatio[isel][icat]->SetDirectory(0);

		fitRatio[isel][icat] = new TF1("fitRatio_"+ss,TString::Format("%s",TR[isel].Data()).Data(),XMIN[isel],XMAX[isel]);
      fitRatio[isel][icat]->SetLineColor(COLOR[icat]);
      
      if (icat > 0) {
        hRatio[isel][icat]->Fit(fitRatio[isel][icat],"R");
        fitter = TVirtualFitter::GetFitter();
        COV.Use(fitter->GetNumberTotalParameters(),fitter->GetCovarianceMatrix());
        //---------------------------------------------
        float dx = (hRatio[isel][icat]->GetBinLowEdge(hRatio[isel][icat]->GetNbinsX())+hRatio[isel][icat]->GetBinWidth(1)-hRatio[isel][icat]->GetBinLowEdge(1))/200;
        for(int i=0;i<200;i++) {
          vx[i] = hRatio[isel][icat]->GetBinLowEdge(1)+(i+1)*dx;
          vy[i] = fitRatio[isel][icat]->Eval(vx[i]);
          vex[i] = 0.;

			 if (TR[isel]=="pol1") {
            vey[i] = sqrt(pow(vx[i],2)*COV(1,1)+COV(0,0)+2*COV(0,1)*vx[i]); // linear
            vey_approx[i] = SCALE[0][isel][icat]*sqrt(pow(vx[i],2)*COV(1,1)+COV(0,0)); // linear
          }
          else if (TR[isel]=="pol2") {
            vey[i] = sqrt(COV(0,0)+2*vx[i]*COV(0,1)+(2*COV(0,2)+COV(1,1))*pow(vx[i],2)+2*COV(1,2)*pow(vx[i],3)+COV(2,2)*pow(vx[i],4));// quadratic
            // approximate quadratic error band: ignore correlations but shrink the errors
            vey_approx[i] =  SCALE[1][isel][icat]*sqrt(COV(0,0)+COV(1,1)*pow(vx[i],2)+COV(2,2)*pow(vx[i],4));
          } 
          else if (TR[isel]=="pol3") {
            vey[i] = sqrt(COV(0,0)+2*vx[i]*COV(0,1)+(2*COV(0,2)+COV(1,1))*pow(vx[i],2)+2*(COV(1,2)+COV(0,3))*pow(vx[i],3)+(2*COV(1,3)+COV(2,2))*pow(vx[i],4)+2*COV(2,3)*pow(vx[i],5)+COV(3,3)*pow(vx[i],6));
            // approximate quadratic error band: ignore correlations but shrink the errors
            vey_approx[i] = SCALE[2][isel][icat]*sqrt(COV(0,0)+COV(1,1)*pow(vx[i],2)+COV(2,2)*pow(vx[i],4)+COV(3,3)*pow(vx[i],6));
          } 
//          else if (TR[isel]=="expo") {
//			 }
			 else {
				 if (i==0) cout << "\033[1;31mERROR NOT DEFINED FOR THIS TRANSFER FUNCTION ORDER\033[m" << endl;
				 vey[i] = 0;
				 vey_approx[i] = 0;
			 }
        }
        gUnc[isel][icat] = new TGraphErrors(200,vx,vy,vex,vey);
        gUnc_approx[isel][icat] = new TGraphErrors(200,vx,vy,vex,vey_approx);
        gUnc[isel][icat]->SetName("gUnc_"+ss);
        gUnc_approx[isel][icat]->SetName("gUncApprox_"+ss);
        gUnc[isel][icat]->SetFillColor(COLOR[icat]);
        gUnc[isel][icat]->SetFillColor(COLOR[icat]); 
        gUnc[isel][icat]->SetFillStyle(3004);
        gUnc_approx[isel][icat]->SetFillColor(kGray);
        gUnc_approx[isel][icat]->SetFillStyle(1001); 
      }
      if (icat == 0) {
        can1[isel] = new TCanvas("MbbShape_"+ss,"MbbShape_"+ss,900,600);
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

    	  TLegend *leg1 = new TLegend(0.2,0.15,0.6,0.4);
        leg1->SetHeader(ss); //"sel"+SELTAG[isel]+TString::Format("_CAT%d",counter));
        leg1->AddEntry(hRatio[isel][icat],"data","P");
        leg1->AddEntry(fitRatio[isel][icat],"fit","L");
        leg1->AddEntry(gUnc_approx[isel][icat],"unc.","F");
        leg1->AddEntry(gUnc[isel][icat],"unc. (stat)","F"); 
        leg1->SetFillColor(0);
        leg1->SetBorderSize(0);
        leg1->SetTextFont(42);
        leg1->SetTextSize(0.05);
        leg1->Draw();
		  TPaveText *pave = new TPaveText(0.2,0.75,0.6,0.9,"NDC");
		  pave->SetTextAlign(11);
		  pave->SetTextSize(0.05);
		  pave->SetTextFont(42);
		  pave->SetFillStyle(-1);
		  pave->SetBorderSize(0);
		  pave->AddText(TString::Format("#chi^{2}/ndf = %f",fitRatio[isel][icat]->GetChisquare()/fitRatio[isel][icat]->GetNDF()).Data());
		  pave->SetTextSize(0.035);
		  for (int i=0; i<fitRatio[isel][icat]->GetNpar(); i++) pave->AddText(TString::Format("p%d = %.2g #pm %.2g",i,fitRatio[isel][icat]->GetParameter(i),fitRatio[isel][icat]->GetParError(i)).Data());
		  pave->SetY1NDC(pave->GetY2NDC()-0.04*(fitRatio[isel][icat]->GetNpar()+1));
		  pave->Draw();
      }

      outf->cd();
		write(hData[isel][icat]);
		write(hRatio[isel][icat]);
		write(fitRatio[isel][icat]);
		write(gUnc[isel][icat]);
		write(gUnc_approx[isel][icat]);
		
      COV.Write("COV_"+ss,TH1::kOverwrite);
      counter++;
    }
    can1[isel]->cd();
    leg->Draw();
	 system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
	 system(TString::Format("[ ! -d %s/plots ] && mkdir %s/plots",OUTPATH.Data(),OUTPATH.Data()).Data());
	 system(TString::Format("[ ! -d %s/plots/transferFunctions/ ] && mkdir %s/plots/transferFunctions/",OUTPATH.Data(),OUTPATH.Data()).Data());
	 can1[isel]->SaveAs(TString::Format("%s/plots/transferFunctions/%s_%s%s-%.f-%.f_%s%s-%.f-%.f.png",OUTPATH.Data(),can1[isel]->GetName(),SELTAG[0].Data(),TRTAG[0].Data(),XMIN[0],XMAX[0],SELTAG[1].Data(),TRTAG[1].Data(),XMIN[1],XMAX[1]).Data());
	 can1[isel]->SaveAs(TString::Format("%s/plots/transferFunctions/%s_%s%s-%.f-%.f_%s%s-%.f-%.f.pdf",OUTPATH.Data(),can1[isel]->GetName(),SELTAG[0].Data(),TRTAG[0].Data(),XMIN[0],XMAX[0],SELTAG[1].Data(),TRTAG[1].Data(),XMIN[1],XMAX[1]).Data());
	 can2[isel]->SaveAs(TString::Format("%s/plots/transferFunctions/%s_%s%s-%.f-%.f_%s%s-%.f-%.f.png",OUTPATH.Data(),can2[isel]->GetName(),SELTAG[0].Data(),TRTAG[0].Data(),XMIN[0],XMAX[0],SELTAG[1].Data(),TRTAG[1].Data(),XMIN[1],XMAX[1]).Data());
	 can2[isel]->SaveAs(TString::Format("%s/plots/transferFunctions/%s_%s%s-%.f-%.f_%s%s-%.f-%.f.pdf",OUTPATH.Data(),can2[isel]->GetName(),SELTAG[0].Data(),TRTAG[0].Data(),XMIN[0],XMAX[0],SELTAG[1].Data(),TRTAG[1].Data(),XMIN[1],XMAX[1]).Data());
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

void write(TH1F *obj) {
	if (obj) {
		obj->Write(obj->GetName(),TH1::kOverwrite);
		cout << "\033[0;36m" << obj->GetName() << " written to file.\033[m" << endl;
	}
}
void write(TGraphErrors *obj) {
	if (obj) {
		obj->Write(obj->GetName(),TH1::kOverwrite);
		cout << "\033[0;36m" << obj->GetName() << " written to file.\033[m" << endl;
	}
}
void write(TLegend *obj, TString name) {
	if (obj) {
		obj->Write(name.Data(),TH1::kOverwrite);
		cout << "\033[0;36m" << name.Data() << " written to file.\033[m" << endl;
	}
}
void write(TF1 *obj) {
	if (obj) {
		obj->Write(obj->GetName(),TH1::kOverwrite);
		cout << "\033[0;36m" << obj->GetName() << " written to file.\033[m" << endl;
	}
}
