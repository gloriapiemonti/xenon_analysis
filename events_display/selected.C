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
 
void selected(const int entry=0, const string& filename = "./xecrt.root") {
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
    vector<bool>   *trkIsSelected = nullptr; 
                             
    t->SetBranchAddress("trkstartx", &trkstartx);
    t->SetBranchAddress("trkstarty", &trkstarty);
    t->SetBranchAddress("trkstartz", &trkstartz);
    t->SetBranchAddress("trkendx", &trkendx);
    t->SetBranchAddress("trkendy", &trkendy);
    t->SetBranchAddress("trkendz", &trkendz);
    t->SetBranchAddress("trkIsTrack", &trkIsTrack);
    t->SetBranchAddress("trkIsSelected", &trkIsSelected);

    Long64_t nentries = t->GetEntries();
    cout << "Number of events: " << nentries << endl;
         
    vector<Track> tracks;
              
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
        IsMuon(trkIsSelected->at(j), tr);
        tracks.push_back(tr);
    }

    TCanvas *ccb = new TCanvas("ccb", "ccb", 1920, 0, 1900, 900);
     
    drawBox();

    vector<TObject*> keepAlive;
    for (const auto& b : CRT_triggers) drawCRT(b, keepAlive);
    
    drawTracks(tracks);

    ccb->Update();
}
