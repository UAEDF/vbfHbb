void BlikPerformance(TString SELECTION)
{
  TString TAG("");
  if (SELECTION == "NOM") {
    TAG = "NOM";
  }
  else {
    TAG = "PRK";
  }
  TFile *inf = TFile::Open("bjetId_"+SELECTION+"_MVA.root");
  TTree *tr  = (TTree*)inf->Get("TestTree");

  float NTrue = tr->GetEntries("classID==0");
  float NFake = tr->GetEntries("classID==1");

  TH1F *hBtagTrue = new TH1F("hBtagTrue","hBtagTrue",100,-10,1.01); 
  TH1F *hBtagFake = new TH1F("hBtagFake","hBtagFake",100,-10,1.01);
  TH1F *hBlikTrue = new TH1F("hBlikTrue","hBlikTrue",100,-1,1.01); 
  TH1F *hBlikFake = new TH1F("hBlikFake","hBlikFake",100,-1,1.01);
  TH1F *hEtaTrue  = new TH1F("hEtaTrue", "hEtaTrue" ,50,0,5);
  TH1F *hEtaFake  = new TH1F("hEtaFake", "hEtaFake" ,50,0,5);

  TCanvas *canBtag = new TCanvas("Btag_"+SELECTION,"Btag_"+SELECTION,900,600);
  gPad->SetLogy();
  tr->Draw("btag>>hBtagTrue","classID==0");
  tr->Draw("btag>>hBtagFake","classID==1");
  hBtagTrue->Scale(1./NTrue);
  hBtagFake->Scale(1./NFake);
  hBtagTrue->SetLineColor(kBlue);
  hBtagTrue->SetFillColor(kBlue-9);
  hBtagTrue->SetFillStyle(1001);
  hBtagFake->SetLineColor(kRed);
  hBtagFake->SetFillColor(kRed);
  hBtagFake->SetFillStyle(3004);
  //hBtagTrue->SetMinimum(1e-4);
  //hBtagTrue->SetMaximum(1);
  hBtagTrue->GetXaxis()->SetTitle("CSV");
  hBtagTrue->Draw();
  hBtagFake->Draw("same");
  TLegend *leg1 = new TLegend(0.2,0.7,0.5,0.9);
  leg1->SetHeader(TAG+" selection");
  leg1->SetFillColor(0);
  leg1->SetBorderSize(0);
  leg1->SetTextFont(42);
  leg1->SetTextSize(0.06);
  leg1->AddEntry(hBtagTrue,"signal","F");
  leg1->AddEntry(hBtagFake,"background","F");
  leg1->Draw();
  canBtag->SaveAs("canBtag.pdf");

  TCanvas *canBlik = new TCanvas("Blik_"+SELECTION,"Blik_"+SELECTION,900,600);
  gPad->SetLogy();
  tr->Draw("BDT_GRAD2>>hBlikTrue","classID==0");
  tr->Draw("BDT_GRAD2>>hBlikFake","classID==1");
  hBlikTrue->Scale(1./NTrue);
  hBlikFake->Scale(1./NFake);
  hBlikTrue->SetLineColor(kBlue);
  hBlikTrue->SetFillColor(kBlue-9);
  hBlikTrue->SetFillStyle(1001);
  hBlikFake->SetLineColor(kRed);
  hBlikFake->SetFillColor(kRed);
  hBlikFake->SetFillStyle(3004);
  //hBlikTrue->SetMinimum(1e-4);
  //hBlikTrue->SetMaximum(1);
  hBlikTrue->GetXaxis()->SetTitle("b-likelihood");
  hBlikTrue->Draw();
  hBlikFake->Draw("same");
  leg1->Draw();
  canBlik->SaveAs("canBlik.pdf");

  TCanvas *canEta = new TCanvas("Eta_"+SELECTION,"Eta_"+SELECTION,900,600);
  //gPad->SetLogy();
  tr->Draw("abs(eta)>>hEtaTrue","classID==0");
  tr->Draw("abs(eta)>>hEtaFake","classID==1");
  hEtaTrue->Scale(1./NTrue);
  hEtaFake->Scale(1./NFake);
  hEtaTrue->SetLineColor(kBlue);
  hEtaTrue->SetFillColor(kBlue-9);
  hEtaTrue->SetFillStyle(1001);
  hEtaFake->SetLineColor(kRed);
  hEtaFake->SetFillColor(kRed);
  hEtaFake->SetFillStyle(3004);
  //hEtaTrue->SetMinimum(1e-4);
  //hEtaTrue->SetMaximum(1);
  hEtaTrue->GetXaxis()->SetTitle("|#eta|");
  hEtaTrue->Draw();
  hEtaFake->Draw("same");
  leg1->Draw();
  canEta->SaveAs("canEta.pdf");

  float xtrue[1000];
  float yfake[1000];

  for(int i=0;i<hBtagFake->GetNbinsX();i++) {
    yfake[i] = 1-hBtagFake->Integral(i,hBtagFake->GetNbinsX());
    xtrue[i] = hBtagTrue->Integral(i,hBtagFake->GetNbinsX());
  }

  TGraph *gBtag = new TGraph(hBtagFake->GetNbinsX(),xtrue,yfake);
  gBtag->SetLineColor(kRed);
  gBtag->SetLineWidth(2);

  for(int i=0;i<hBlikFake->GetNbinsX();i++) {
    yfake[i] = 1-hBlikFake->Integral(i,hBlikFake->GetNbinsX());
    xtrue[i] = hBlikTrue->Integral(i,hBlikFake->GetNbinsX()); 
  }

  TGraph *gBlik = new TGraph(hBlikFake->GetNbinsX(),xtrue,yfake);
  gBlik->SetLineColor(kBlue); 
  gBlik->SetLineWidth(2); 
  
  for(int i=0;i<hEtaFake->GetNbinsX();i++) {
    yfake[i] = hEtaFake->Integral(i,hEtaFake->GetNbinsX());
    xtrue[i] = 1-hEtaTrue->Integral(i,hEtaFake->GetNbinsX());
  }

  TGraph *gEta = new TGraph(hEtaFake->GetNbinsX(),xtrue,yfake);
  gEta->SetLineColor(kGreen+2);
  gEta->SetLineWidth(2);

  TCanvas *canROC = new TCanvas("BlikROC_"+SELECTION,"BlikROC_"+SELECTION,900,600);
  gBtag->GetXaxis()->SetTitle("Efficiency of matched b-jets");
  gBtag->GetYaxis()->SetTitle("Rejection of matched non b-jets");
  gBtag->Draw("AL");
  gBlik->Draw("sameL");
  gEta->Draw("sameL");
  TLegend *leg = new TLegend(0.2,0.2,0.5,0.5);
  leg->SetHeader(TAG+" selection");
  leg->SetFillColor(0);
  leg->SetBorderSize(0);
  leg->SetTextFont(42);
  leg->SetTextSize(0.06);
  leg->AddEntry(gEta,"|#eta|","L");
  leg->AddEntry(gBtag,"btag","L");
  leg->AddEntry(gBlik,"b-likelihood","L");
  leg->Draw();
  canROC->SaveAs("canROC.pdf");
}
