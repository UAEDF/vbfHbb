#include <RooMsgService.h>
#include <RooDataHist.h>
#include <RooRealVar.h>
#include <RooFormulaVar.h>
#include <RooWorkspace.h>
#include <RooGlobalFunc.h>
#include <RooAddPdf.h>
#include <RooFitResult.h>
#include <RooBernstein.h>
#include <RooCBShape.h>
#include <RooPlot.h>

#include <TCanvas.h>
#include <TF1.h>
#include <TH1.h>
#include <TString.h>
#include <TROOT.h>
#include <TSystem.h>
#include <TPad.h>
#include <TLine.h>

void fitTF1(TCanvas *canvas, TH1F h, double XMIN_, double XMAX_, double dX_, double params[], Color_t LC_=kBlack) { //double& FWHM_, double& x0_, double& x1_, double& x2_, double& y0_, double& y1_, double& INT_, double& YIELD_) {
//TCanvas* fitTF1(TH1F h, double HSCALE_, double XMIN_, double XMAX_) {
//TF1* fitTF1(TH1F h, double HSCALE_, double XMIN_, double XMAX_) {
	gROOT->ForceStyle();
	RooMsgService::instance().setSilentMode(kTRUE);
	for(int i=0;i<2;i++) RooMsgService::instance().setStreamStatus(i,kFALSE);

	//TCanvas *canvas = new TCanvas(TString::Format("canvas_%s",h.GetName()),TString::Format("canvas_%s",h.GetName()),1800,1200);

	RooDataHist *RooHistFit = 0;
	RooAddPdf *model = 0;

	RooWorkspace w = RooWorkspace("w","workspace");

	RooRealVar x("mbbReg","mbbReg",XMIN_,XMAX_);
	RooRealVar kJES("CMS_scale_j","CMS_scale_j",1,0.9,1.1);
	RooRealVar kJER("CMS_res_j","CMS_res_j",1,0.8,1.2);
	kJES.setConstant(kTRUE);
	kJER.setConstant(kTRUE);

	TString hname = h.GetName();

	RooHistFit = new RooDataHist("fit_"+hname,"fit_"+hname,x,&h);


	RooRealVar YieldVBF = RooRealVar("yield_"+hname,"yield_"+hname,h.Integral());
	RooRealVar m("mean_"+hname,"mean_"+hname,125,100,150);
	RooRealVar s("sigma_"+hname,"sigma_"+hname,12,3,30);
	RooFormulaVar mShift("mShift_"+hname,"@0*@1",RooArgList(m,kJES));
	RooFormulaVar sShift("sShift_"+hname,"@0*@1",RooArgList(m,kJER));
	RooRealVar a("alpha_"+hname,"alpha_"+hname,1,-10,10);
	RooRealVar n("exp_"+hname,"alpha_"+hname,1,0,100);
	RooRealVar b0("b0_"+hname,"b0_"+hname,0.5,0.,1.);
	RooRealVar b1("b1_"+hname,"b1_"+hname,0.5,0.,1.);
	RooRealVar b2("b2_"+hname,"b2_"+hname,0.5,0.,1.);
	RooRealVar b3("b3_"+hname,"b3_"+hname,0.5,0.,1.);
	RooBernstein bkg("signal_bkg_"+hname,"signal_bkg_"+hname,x,RooArgSet(b0,b1,b2));
	RooRealVar fsig("fsig_"+hname,"fsig_"+hname,0.7,0.0,1.0);
	RooCBShape sig("signal_gauss_"+hname,"signal_gauss_"+hname,x,mShift,sShift,a,n);

	model = new RooAddPdf("signal_model_"+hname,"signal_model_"+hname,RooArgList(sig,bkg),fsig);

	//RooFitResult *res = model->fitTo(*RooHistFit,RooFit::Save(),RooFit::SumW2Error(kFALSE),"q");
	model->fitTo(*RooHistFit,RooFit::Save(),RooFit::SumW2Error(kFALSE),"q");

	canvas->cd();
	canvas->SetTopMargin(0.1);
	RooPlot *frame = x.frame();
// no scale
	RooHistFit->plotOn(frame);
	model->plotOn(frame,RooFit::LineColor(LC_),RooFit::LineWidth(2),RooFit::LineStyle(kDotted));
	model->plotOn(frame,RooFit::Components(bkg),RooFit::LineColor(LC_),RooFit::LineWidth(2),RooFit::LineStyle(kDashed));
// with scale
//	RooHistFit->plotOn(frame,RooFit::Normalization(HSCALE_,RooAbsReal::NumEvent));
//	model->plotOn(frame,RooFit::Normalization(HSCALE_,RooAbsReal::NumEvent),RooFit::LineWidth(1));
//	model->plotOn(frame,RooFit::Components(bkg),RooFit::LineColor(kBlue),RooFit::LineWidth(1),RooFit::LineStyle(kDashed),RooFit::Normalization(HSCALE_,RooAbsReal::NumEvent));
	 
	frame->GetXaxis()->SetLimits(50,200);
	frame->GetXaxis()->SetNdivisions(505);
	frame->GetXaxis()->SetTitle("M_{b#bar{b}} (GeV)");
	frame->GetYaxis()->SetTitle("Events");
	frame->Draw();
	h.SetFillColor(kGray);
	h.Draw("hist,same");
	frame->Draw("same");
	gPad->RedrawAxis();

	TF1 *tmp = model->asTF(x,fsig,x);
	double y0_ = tmp->GetMaximum();
	double x0_ = tmp->GetMaximumX();
	double x1_ = tmp->GetX(y0_/2.,XMIN_,x0_);
	double x2_ = tmp->GetX(y0_/2.,x0_,XMAX_);
	double FWHM_ = x2_-x1_;
	double INT_ = tmp->Integral(XMIN_,XMAX_);
	double YIELD_= YieldVBF.getVal();
	double y1_ = dX_*0.5*y0_*(YieldVBF.getVal()/tmp->Integral(XMIN_,XMAX_));

	params[0] = x0_;
	params[1] = x1_;
	params[2] = x2_;
	params[3] = y0_;
	params[4] = y1_;
	params[5] = FWHM_;
	params[6] = INT_;
	params[7] = YIELD_;

	//cout<<"Int = "<<tmp->Integral(XMIN_,XMAX_)<<", Yield = "<<YieldVBF->getVal()<<", y0 = "<<y0_<<", y1 = "<<y1_ <<", x0 = "<< x0_ << ", x1 = "<<x1_<<", x2 = "<<x2_<<", FWHM = "<<FWHM_<<endl;

	TLine ln = TLine(x1_,y1_,x2_,y1_);
	ln.SetLineColor(kMagenta+3);
	ln.SetLineStyle(7);
	ln.SetLineWidth(2);
	ln.Draw();
	
	canvas->Update();
	//canvas->SaveAs("testpre.pdf");
	
	tmp->Delete();
//	frame->Delete();
//	res->Delete();
//	TF1 *f1 = model->asTF(x,fsig,x);
//	return f1;
	
	////tmp->Delete();
	////ln->Delete();
	////model->Delete();
	////RooHistFit->Delete();
	////w->Delete();
	////YieldVBF->Delete();
	////frame->Delete();
	////res->Delete();
	//delete tmp;
	//delete ln;
	//delete model;
	//delete RooHistFit;
	//delete w;
	//delete YieldVBF;
	//delete frame;
	//delete res;

//	return canvas;
}
