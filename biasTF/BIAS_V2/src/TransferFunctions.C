void makeDirs(TString);

void TransferFunctions(float XMIN, float XMAX, int CATMIN, int CATMAX, TString TR, TString OUTPATH, float XMAXDIFF=0.)
{
  gROOT->ProcessLineSync(".x ../../common/styleCMSTDR.C");
  gROOT->ForceStyle();
  gStyle->SetPadRightMargin(0.04);
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};
  TString SELECTION[2] = {"NOM","VBF"};  
  TString SELTAG[2] = {"NOM","PRK"};
  int STYLE[NCAT[0]] = {20,20,23,21};
  int COLOR[NCAT[0]] = {kBlack,kBlue,kRed,kGreen+2};
  float BINSIZE[NSEL]= {10,5};
  TString MBB[NSEL]={"mbbReg[1]","mbbReg[2]"};
  TString MVA[NSEL]={"mvaNOM","mvaVBF"};
  
  const int dictsize=4;
  float SCALE[dictsize][NSEL][NCAT[0]] = {
	  {{1.0,0.5,0.62,0.67},{1.0,1.2,1.7}},
	  {{1.0,0.04,0.05,0.07},{1.0,0.085,0.1}},
	  {{1.0,0.01,0.01,0.01},{1.0,0.015,0.022}}
	  {{1.0,1.0,1.0,1.0},{1.0,1.0,1.0}}
  };
  TString TRKEYS[dictsize] = {"POL1","POL2","POL3","EXPO"};	
  TString TRVALS[dictsize] = {"pol1","pol2","pol3","expo"};
	
  makeDirs(OUTPATH);
  makeDirs(OUTPATH+"/output");
//  system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
//  system(TString::Format("[ ! -d %s/output ] && mkdir %s/output",OUTPATH.Data(),OUTPATH.Data()).Data());
  if (XMAXDIFF==0.) TFile *outf = TFile::Open(TString::Format("%s/output/transferFunctions_B%.f-%.f.root",OUTPATH.Data(),XMIN,XMAX),"UPDATE");
else                TFile *outf = TFile::Open(TString::Format("%s/output/transferFunctions_B%.f-%.f%.f.root",OUTPATH.Data(),XMIN,XMAX,XMAX+XMAXDIFF),"UPDATE");

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
  gStyle->SetPadTopMargin(0.06);
  gStyle->SetPadLeftMargin(0.12);
 
  float vx[200],vy[200],vex[200],vey[200],vey_approx[200];
  
  TString TROLD = TR;

  int counter(CATMIN);
  for(int isel=0;isel<NSEL;isel++) {
	 if (isel==0 && NCAT[0]<=CATMIN) continue;
	 if (isel==1 && CATMAX<NCAT[0]) continue;
	 if (TR.First('-') > -1) { 
		 vector<TString> TRvec = splitString(TR);
		 TR = TRvec[isel];
	 }
		 

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
    can2[isel] = new TCanvas("transfer_sel"+SELECTION[isel],"transfer_sel"+SELECTION[isel],400*(NCAT[isel]-1),400);
    can2[isel]->Divide(NCAT[isel]-1,1);
    TLegend *leg = new TLegend(0.6,0.6,0.9,0.9);
    leg->SetHeader(SELTAG[isel]+" selection");
    leg->SetFillColor(0);
    leg->SetBorderSize(0);
    leg->SetTextFont(42);
    leg->SetTextSize(0.05);  

    for(int icat=0;icat<NCAT[isel];icat++) { 
      TString ss("sel"+SELTAG[isel]+TString::Format("_CAT%d",counter)+TString::Format("_%s",TR.Data()));
		cout << "\n\033[1;34mWorking on: " << ss << "\033[m" << endl;
      hData[isel][icat] = new TH1F("hData_"+ss,"hData_"+ss,(XMAX-XMIN)/BINSIZE[isel],XMIN,XMAX);
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

		int match(-1);
		for (int im=0; im<dictsize; im++) {
		   if (TRKEYS[im]==TR) {
		 	  match=im;
		 	  break;
		   }
		}

		fitRatio[isel][icat] = new TF1("fitRatio_"+ss,TString::Format("%s",TRVALS[match].Data()).Data(),XMIN,XMAX);
      fitRatio[isel][icat]->SetLineColor(COLOR[icat]);
      
      if (icat > 0) {
        hRatio[isel][icat]->Fit(fitRatio[isel][icat],"R");
        fitter = TVirtualFitter::GetFitter();
        COV.Use(fitter->GetNumberTotalParameters(),fitter->GetCovarianceMatrix());

		  gUnc[isel][icat] = getUnc(COV,fitRatio[isel][icat],hRatio[isel][icat],false,0.);
		  gUnc_approx[isel][icat] = getUnc(COV,fitRatio[isel][icat],hRatio[isel][icat],true,SCALE[match][isel][icat]);
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
        hData[isel][icat]->GetXaxis()->SetTitleOffset(1.015); 
        hData[isel][icat]->GetYaxis()->SetTitleOffset(1.0); 
        hData[isel][icat]->GetYaxis()->SetTitle("PDF"); 
        hData[isel][icat]->GetYaxis()->SetNdivisions(505);
        hData[isel][icat]->SetMaximum(isel==0 ? 0.30 : 0.20);
        hData[isel][icat]->Draw("HIST");
        leg->AddEntry(hData[isel][icat],TString::Format("CAT%d",counter),"F");
      }
      else {
        can1[isel]->cd();
        hData[isel][icat]->Draw("same E");
        leg->AddEntry(hData[isel][icat],TString::Format("CAT%d",counter),"P");
        can2[isel]->cd(icat);
		  gPad->SetLeftMargin(0.17);
		  ln->GetYaxis()->SetTitleOffset(1.5);
        ln->Draw();
        gUnc_approx[isel][icat]->Draw("sameE3");
        ln->Draw("same");
        gUnc[isel][icat]->Draw("sameE3");
        hRatio[isel][icat]->Draw("same");

    	  TLegend *leg1 = new TLegend(gPad->GetLeftMargin()+0.02,gPad->GetBottomMargin()+0.02,0.6,0.4);
        leg1->SetHeader(TString::Format("%s selection CAT%d/CAT%d",SELTAG[isel].Data(),icat+(isel==0 ? 0 : NCAT[isel-1]),(isel==0 ? 0 : 4)).Data());//ss); 
        leg1->AddEntry(hRatio[isel][icat],"data","P");
        leg1->AddEntry(fitRatio[isel][icat],"fit","L");
        leg1->AddEntry(gUnc_approx[isel][icat],"uncert.","F");
        leg1->AddEntry(gUnc[isel][icat],"uncert. (stat)","F"); 
        leg1->SetFillColor(0);
        leg1->SetBorderSize(0);
        leg1->SetTextFont(42);
        leg1->SetTextSize(gPad->GetTopMargin()*2.8/4.0);//0.05);
        leg1->Draw();
		  gPad->Update();
		  leg1->SetY2(leg1->GetY1()+leg1->GetNRows()*gPad->GetTopMargin());
		  gPad->Update();
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
		  //pave->Draw();
		  gPad->RedrawAxis();
      }

    TPaveText *paveCMS = new TPaveText(gPad->GetLeftMargin()+0.01,1.-gPad->GetTopMargin(),gPad->GetLeftMargin()+0.15,1.,"NDC");
	 paveCMS->SetTextFont(62);
	 paveCMS->SetTextSize(gStyle->GetPadTopMargin()*3./4.);
	 paveCMS->SetBorderSize(0);
	 paveCMS->SetFillStyle(-1);
	 paveCMS->SetTextAlign(12);
	 paveCMS->AddText("CMS");
	 paveCMS->Draw();
	 gPad->Update();
	 float scale= (float)gPad->GetCanvas()->GetWindowHeight()/(float)(gPad->GetCanvas()->GetWindowWidth()*gPad->GetAbsWNDC());
	 scale = (float)floor(scale*3)/3.);
    TPaveText *paveCMS2 = new TPaveText(gPad->GetLeftMargin()+0.105*scale,1.-gPad->GetTopMargin(),gPad->GetLeftMargin()+0.32,1.-0.008,"NDC");
	 paveCMS2->SetTextFont(52);
	 paveCMS2->SetTextSize(gStyle->GetPadTopMargin()*2.55/4.);
	 paveCMS2->SetBorderSize(0);
	 paveCMS2->SetFillStyle(-1);
	 paveCMS2->SetTextAlign(12);
    paveCMS2->AddText("Preliminary");
	 //paveCMS2->Draw();
	 gPad->Update();

	 TPaveText *paveLumi = new TPaveText(0.5,1.-gStyle->GetPadTopMargin(),0.98,1.00,"NDC");
	 paveLumi->SetTextFont(42);
	 paveLumi->SetTextSize(gStyle->GetPadTopMargin()*3./4.);
	 paveLumi->SetBorderSize(0);
	 paveLumi->SetFillStyle(-1);
	 paveLumi->SetTextAlign(32);
	 paveLumi->AddText("19.8 fb^{-1} (8TeV)");//+ 18.2 ;
	 paveLumi->Draw();

      outf->cd();
		write(hData[isel][icat]);
		write(hRatio[isel][icat]);
		write(fitRatio[isel][icat]);
		write(gUnc[isel][icat]);
		write(gUnc_approx[isel][icat]);
		
      COV.Write("COV_"+ss,TH1::kOverwrite);
      counter++;
    } // --end icat

	 TR = TROLD;

    can1[isel]->cd();
    leg->Draw();
	 makeDirs(OUTPATH+"/plots");
	 makeDirs(OUTPATH+"/plots/transferFunctions");
	 TString n="";
	 n = TString::Format("%s/plots/transferFunctions/%s_%s-%.f-%.f",OUTPATH.Data(),can1[isel]->GetName(),TR.Data(),XMIN,XMAX);
	 can1[isel]->SaveAs(n+".png");
	 can1[isel]->SaveAs(n+".pdf");
	 n = TString::Format("%s/plots/transferFunctions/%s_%s-%.f-%.f",OUTPATH.Data(),can2[isel]->GetName(),TR.Data(),XMIN,XMAX);
	 can2[isel]->SaveAs(n+".png");
	 can2[isel]->SaveAs(n+".pdf");
  } // --end isel
  outf->Close();
  delete can;
  delete can1;
  delete can2;
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


void makeDirs(TString dirName) {
	 system(TString::Format("[ ! -d %s ] && mkdir %s",dirName.Data(),dirName.Data()).Data());
}

TGraphErrors *getUnc(TMatrixDSym COV, TF1 *fit, TH1F *h, bool APPROX, float SCALE)
{
  int N = COV.GetNrows();
  float vx[200],vy[200],vex[200],vey[200];
  float dx = (h->GetBinLowEdge(h->GetNbinsX())+h->GetBinWidth(1)-h->GetBinLowEdge(1))/200.;
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

vector<TString> splitString(TString s) {
 vector<TString> split;
 TObjArray *t = s.Tokenize("-");
 const int n = t->GetEntries();
 split.clear();
 for (int i=0; i<n; i++) {
    split.push_back(((TObjString*)t->At(i))->String());
 }
 return split;
}
