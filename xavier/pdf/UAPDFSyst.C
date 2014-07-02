
#include <iostream>
#include <iomanip>
#include <iterator>
#include <math.h>
using namespace std;

#include "LHAPDF/LHAPDF.h"

#include <TROOT.h>
#include <TCanvas.h>
#include <TStyle.h>
#include <TSystem.h>
#include <TLegend.h>
#include <TFrame.h>
#include <TText.h>
#include <TLatex.h>

#include <TFile.h>
#include <TH1F.h>
#include <TH2F.h>

#include "src/UAPDFSystConfig.C"
#include "src/UAPDFSystAna.C"
#include "src/UAPDFSystTH1F.C"
#include "src/UAPDFSystReader.C"
#include "src/LatinoStyle2.C"


void Usage(string name){
  cerr << "\nUsage  : " << name << " <ConfigFile> <Option(s)>\n"
       << "Options:\n"
       << "\t-h,--help \t\tShow this help message\n"
       << "\t-r,--read \t\tRead the Trees\n"
       << "\t-t,--tree \t\tSave the Trees with weight branches\n"
       << "\t-p,--print\t\tCompute Results and print\n"
       << "\t-n,--nmax <nMax> \tUse only <nMax> first events from the Trees\n"
       << std::endl; 
}

int main(int argc, char **argv) {

  // -------- Arguments -------

  string  ConFile  = "Config.cfg";
  bool    bRead    = false;
  bool    bTree    = false;
  bool    bPrint   = false;
  int     nMax     = 0;

  if ( argc < 2 ) /* At least 1 argument */
  {
    cerr << "\n[ERROR] No argument(s) passed !\n";
    Usage(argv[0]);
    return 1;
  } else {
    int    nconf = 0;
    for (int i = 1; i < argc; ++i) {     
      string arg   = argv[i];
      if        ((arg == "-h") || (arg == "--help")) {
        Usage(argv[0]);
        return 0;
      } else if ((arg == "-r") || (arg == "--read")) {
        bRead = true ;
      } else if ((arg == "-t") || (arg == "--tree")) {
        bTree  = true ; 
      } else if ((arg == "-p") || (arg == "--print")) {
        bPrint = true ;
      } else if ((arg == "-n") || (arg == "--nmax")) {
        nMax = atoi(argv[i+1]);++i;
      } else {
        ConFile = arg ;
        ++nconf;
      }
    }
    // Check arguments
    if ( nconf != 1 ) { cerr << "\n[ERROR] No or more than 1 Config !\n" ;  Usage(argv[0]) ; return 1; }
    if ( ! (bRead||bPrint) )  
                      { cerr << "\n[ERROR] No valid argument passed !\n" ;  Usage(argv[0]) ; return 1; }
    if ( bTree && ! bRead ) 
                      { cerr << "\n[ERROR] -t argument request -r   !\n" ;  Usage(argv[0]) ; return 1; }
  }

  // ROOT Style
  LatinoStyle2();
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  gStyle->SetHatchesLineWidth(2);

  // Parse the config file 
  UAPDFSystConfig Cfg ;  
  Cfg.ReadCfg(ConFile);
  Cfg.SetbTree(bTree);
  Cfg.SetNMax(nMax);

  // Read the Trees
  if (bRead) UAPDFSystReader(Cfg);
  else       { cerr << "Recreate class from Root file not available \n" ; return 1 ; }
   
 
 

  return 0;
}

