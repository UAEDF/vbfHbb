void DrawNLL()
{
  gROOT->ForceStyle();
  TFile *inf[2];
  TTree *tr[2];
  TString FILENAME[2] = {"higgsCombineZ.MultiDimFit.mH120.root","higgsCombineExpectedZ.MultiDimFit.mH120.root"};
  TGraph *g[2];
  float deltaNLL,r;
  float vx[100],vy[100];
  for(int k=0;k<2;k++) {
    inf[k] = TFile::Open(FILENAME[k]);
    tr[k]  = (TTree*)inf[k]->Get("limit");
    
    tr[k]->SetBranchAddress("deltaNLL",&deltaNLL);
    tr[k]->SetBranchAddress("r",&r);
    for(int i=0;i<tr[k]->GetEntries();i++) {
      tr[k]->GetEntry(i);
      vx[i] = r; 
      vy[i] = 2*deltaNLL;
    }
    g[k] = new TGraph(tr[k]->GetEntries(),vx,vy);
    g[k]->SetLineWidth(2);
  }

  TCanvas *can = new TCanvas("nll_Z","nll_Z",600,600);
  g[1]->SetLineStyle(7);
  
  g[0]->GetYaxis()->SetRangeUser(0,6);
  g[0]->GetXaxis()->SetRangeUser(0,2.5);
  g[0]->GetXaxis()->SetTitle("#mu");
  g[0]->GetYaxis()->SetTitle("-2#Delta lnL");
  g[0]->Draw("AC");
  g[1]->Draw("sameC");

  gPad->Update();
  TLine *ln = new TLine(gPad->GetFrame()->GetX1(),1,gPad->GetFrame()->GetX2(),1);
  ln->SetLineColor(kBlack);
  ln->SetLineWidth(1);
  ln->SetLineStyle(9);
  ln->Draw("same");
  
  TLegend *leg = new TLegend(0.4,0.65,0.7,0.85); 
  leg->SetHeader("Fit for the Z boson");
  leg->AddEntry(g[0],"Observed","L");
  leg->AddEntry(g[1],"Expected","L");
  leg->SetFillColor(0);
  leg->SetLineColor(0);
  leg->SetTextFont(42);
  leg->SetTextSize(0.05);
  leg->Draw();
}
