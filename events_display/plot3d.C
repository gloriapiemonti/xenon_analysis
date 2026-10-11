#include "display.h"
#include <iostream>
#include <string>
#include <vector>
 
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TGraph2D.h"
#include "TPolyLine3D.h"
#include "TAxis.h"
#include <limits>
#include <algorithm>

using namespace std;
 
void plot3d(const int entry=0, const string& filename = "./xecrt.root") {
     TFile *f = TFile::Open(filename.c_str(), "READ");
     if (!f || f->IsZombie()) {
         cerr << "Errore: impossibile aprire il file " << filename << endl;
         return;
         }

    TTree *t = nullptr;
    f->GetObject("xeana/t1", t);
    if (!t) {
        cerr << "Errore: TTree 't1' non trovato nel file." << endl;
        f->Close();
        return;
        }
    
    vector<float> *trkstartx = nullptr;
    vector<float> *trkstarty = nullptr;
    vector<float> *trkstartz = nullptr;
    vector<float> *trkendx = nullptr;
    vector<float> *trkendy = nullptr;
    vector<float> *trkendz = nullptr;
    vector<bool>   *trkIsTrack = nullptr;   // 0 = non è una traccia, 1 = è una traccia
                             
    t->SetBranchAddress("trkstartx", &trkstartx);
    t->SetBranchAddress("trkstarty", &trkstarty);
    t->SetBranchAddress("trkstartz", &trkstartz);
    t->SetBranchAddress("trkendx", &trkendx);
    t->SetBranchAddress("trkendy", &trkendy);
    t->SetBranchAddress("trkendz", &trkendz);
    t->SetBranchAddress("trkIsTrack", &trkIsTrack);

    Long64_t nentries = t->GetEntries();
    cout << "Numero di eventi: " << nentries << endl;
         
    vector<Track> tracks;
              
    // double xmin =  numeric_limits<double>::max(), xmax = -numeric_limits<double>::max();
    // double ymin =  numeric_limits<double>::max(), ymax = -numeric_limits<double>::max();
    // double zmin =  numeric_limits<double>::max(), zmax = -numeric_limits<double>::max();

    t->GetEntry(entry);

    size_t ntracks = trkstartx->size();
    for (size_t j = 0; j < ntracks; ++j) {

        //Check if it is a track for Pandora
        if (!trkIsTrack->at(j)) continue;

        Track tr;

        tr.x0 = trkstartz->at(j);
        tr.y0 = trkstarty->at(j);
        tr.z0 = trkstartx->at(j);
        tr.x1 = trkendz->at(j);
        tr.y1 = trkendy->at(j);
        tr.z1 = trkendx->at(j);
        tr.mycolor = kBlue;
       // IsMuon(trkIsMuon->at(j), tr);
        tracks.push_back(tr);

        // xmin = min({xmin, tr.x0, tr.x1});
        // xmax = max({xmax, tr.x0, tr.x1});
        // ymin = min({ymin, tr.y0, tr.y1});

        // ymax = max({ymax, tr.y0, tr.y1});
        // zmin = min({zmin, tr.z0, tr.z1});
        // zmax = max({zmax, tr.z0, tr.z1});
    }

    TCanvas *ccb = new TCanvas("ccb", "ccb", 1920, 0, 900, 900);
     
    drawBox();

    vector<TObject*> keepAlive;
    for (const auto& b : CRT_triggers) drawCRT(b, keepAlive);
    
    drawTracks(tracks);

    ccb->Update();
    //ccb->SaveAs("tracks.root");
}
