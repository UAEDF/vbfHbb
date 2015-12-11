//#include "CMS_lumi.C"
using namespace RooFit;
void DrawMass(int iSEL)
{
  gROOT->ForceStyle();
  TString SET[2] = {"A","B"};
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  TString SELECTION[2] = {"NOM","VBF"};
  TString MASS_RAW[2]  = {"mbb[1]","mbb[2]"};
  TString MASS_REG[2]  = {"mbbReg[1]","mbbReg[2]"};

 // TFile *inf = TFile::Open("Fit_VBFPowheg125_sel"+SELECTION[iSEL]+".root");
  TFile *inf = TFile::Open("/usb/data2/UAData/2015/flatTree_VBFPowheg125.root");
  TTree *tr  = (TTree*)inf->Get("Hbb/events");

  TH1F *hRaw = new TH1F("hRawMass","hRawMass",150,0,300);
  TH1F *hReg = new TH1F("hRegMass","hRegMass",150,0,300);

  RooRealVar x("mbb","mbb",60,170);

  TCanvas *can = new TCanvas("Mbb_sel"+SELECTION[iSEL],"Mbb_sel"+SELECTION[iSEL],900,750);
  
  TCut ct1 = TCut("triggerResult[0]==1||triggerResult[1]==1");
  TCut cs1 = TCut("jetBtag[b1[1]]>0.244 && jetBtag[b2[1]]>0.244 && jetPt[3]>40. && jetPt[2]>50. && jetPt[1]>70. && jetPt[0]>80. && dEtaqq[1]>2.5 && mqq[1]>250 && dPhibb[1]<2.0 && nLeptons==0");
  tr->Draw(MASS_RAW[iSEL]+">>hRawMass",ct1&&cs1);
  tr->Draw(MASS_REG[iSEL]+">>hRegMass",ct1&&cs1);

  hRaw->Sumw2();
  hReg->Sumw2();
  hRaw->Scale(1./(hRaw->Integral()*hRaw->GetBinWidth(1)));
  hReg->Scale(1./(hReg->Integral()*hReg->GetBinWidth(1)));

  RooDataHist *rRaw = new RooDataHist("rRaw","rRaw",x,hRaw);
  RooDataHist *rReg = new RooDataHist("rReg","rReg",x,hReg);

  RooRealVar m1("m1","m1",125,110,140); 
  RooRealVar m2("m2","m2",125,110,140);
  RooRealVar sL1("sL1","sL1",12,3,30); 
  RooRealVar sL2("sL2","sL2",12,3,30);
  RooRealVar sR1("sR1","sR1",12,3,30); 
  RooRealVar sR2("sR2","sR2",12,3,30);
  RooRealVar a1("a1","a1",1,-10,10); 
  RooRealVar a2("a2","a2",1,-10,10); 
  RooRealVar n1("n1","n1",1,0,100); 
  RooRealVar n2("n2","n2",1,0,100);        
  RooRealVar b10("b10","b10",0.5,0.,1.);
  RooRealVar b11("b11","b11",0.5,0.,1.);
  RooRealVar b12("b12","b12",0.5,0.,1.);
  RooRealVar b13("b13","b13",0.5,0.,1.);
  RooRealVar b20("b20","b20",0.5,0.,1.);
  RooRealVar b21("b21","b21",0.5,0.,1.);
  RooRealVar b22("b22","b22",0.5,0.,1.); 
  RooRealVar b23("b23","b23",0.5,0.,1.);     
        
  RooBernstein bkg1("bkg1","bkg1",x,RooArgSet(b10,b11,b12,b13));
  RooBernstein bkg2("bkg2","bkg2",x,RooArgSet(b20,b21,b22,b23));
  RooRealVar fsig1("fsig1","fsig1",0.7,0.,1.); 
  RooRealVar fsig2("fsig2","fsig2",0.7,0.,1.);     
  RooBifurGauss sig1("sig1","sig1",x,m1,sL1,sR1);
  RooBifurGauss sig2("sig2","sig2",x,m2,sL2,sR2);
  //RooCBShape sig1("sig1","sig1",x,m1,s1,a1,n1);
  //RooCBShape sig2("sig2","sig2",x,m2,s2,a2,n2);
        
  RooAddPdf *model1 = new RooAddPdf("model1","model1",RooArgList(sig1,bkg1),fsig1);
  RooAddPdf *model2 = new RooAddPdf("model2","model2",RooArgList(sig2,bkg2),fsig2);

  model1->fitTo(*rRaw,SumW2Error(kFALSE),"q");
  model2->fitTo(*rReg,SumW2Error(kFALSE),"q");

  hRaw->SetLineWidth(2);
  hReg->SetLineWidth(2);
  hRaw->SetLineColor(kBlack);
  hReg->SetLineColor(kRed+1); 
  hReg->SetFillColor(kRed-10);
  hRaw->SetMarkerStyle(21);
  hReg->SetMarkerStyle(20);
  hRaw->SetMarkerSize(1.5);
  hReg->SetMarkerSize(1.5);
  hRaw->SetMarkerColor(kBlack);
  hReg->SetMarkerColor(kRed+1);
  
  RooPlot* frame = x.frame();
  rRaw->plotOn(frame,LineColor(kBlack),LineWidth(1),MarkerColor(kBlack),MarkerStyle(21));
  model1->plotOn(frame,LineColor(kBlack),LineWidth(2));
  rReg->plotOn(frame,LineColor(kRed+1),LineWidth(1),MarkerColor(kRed+1),MarkerStyle(20));
  model2->plotOn(frame,LineColor(kRed+1),LineWidth(2));

  
  TF1 *tmp_func1 = model1->asTF(x,fsig1,x);
  TF1 *tmp_func2 = model2->asTF(x,fsig2,x);
  double y01 = tmp_func1->GetMaximum();
  double x01 = tmp_func1->GetMaximumX();
  double x11 = tmp_func1->GetX(y01/2,60,x01);
  double x21 = tmp_func1->GetX(y01/2,x01,200);
  double FWHM1 = x21-x11;
  
  double y02 = tmp_func2->GetMaximum();
  double x02 = tmp_func2->GetMaximumX();
  double x12 = tmp_func2->GetX(y02/2,60,x02);
  double x22 = tmp_func2->GetX(y02/2,x02,200);
  double FWHM2 = x22-x12;
  
  hReg->GetXaxis()->SetRangeUser(60,170);
  hReg->GetXaxis()->SetTitle("m_{bb} (GeV)");
  hReg->GetYaxis()->SetTitle("1/N #times dN/dm_{bb} (GeV^{-1})");
  hReg->GetYaxis()->SetNdivisions(505);
  hReg->SetMaximum(0.035);
  hReg->Draw("HIST");
  hRaw->Draw("HIST SAME");
  frame->Draw("same");

  TLegend *leg = new TLegend(0.18,0.7,0.43,0.91);
  leg->SetTextFont(42);
  leg->SetTextSize(0.05);
  leg->SetBorderSize(0);
  leg->SetFillColor(0);
  leg->SetHeader("m_{H} = 125 GeV (set "+SET[iSEL]+")");
  leg->AddEntry(hReg,"Regressed","LP");
  leg->AddEntry(hRaw,"Raw","LP");
  leg->Draw();

  TPaveText *pave1 = new TPaveText(0.18,0.56,0.43,0.7,"NDC");
  pave1->AddText(TString::Format("PEAK = %1.1f GeV",x02));
  pave1->AddText(TString::Format("FWHM = %1.1f GeV",FWHM2));
  pave1->SetTextFont(42);
  pave1->SetTextSize(0.04);
  pave1->SetTextColor(kRed+1);
  pave1->SetBorderSize(0);
  pave1->SetFillColor(0);
  pave1->Draw();

  TPaveText *pave2 = new TPaveText(0.18,0.42,0.43,0.56,"NDC");
  pave2->AddText(TString::Format("PEAK = %1.1f GeV",x01));
  pave2->AddText(TString::Format("FWHM = %1.1f GeV",FWHM1));
  pave2->SetTextFont(42);
  pave2->SetTextSize(0.04);
  pave2->SetTextColor(kBlack);
  pave2->SetBorderSize(0);
  pave2->SetFillColor(0);
  pave2->Draw();


  can->SaveAs("regressionKost.pdf");
//  CMS_lumi(can,0,0); 
}
