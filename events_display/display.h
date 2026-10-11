#pragma once

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

struct Track {
    double x0, y0, z0;
    double x1, y1, z1;
    Color_t mycolor;
};

struct trigger {
    double xmin, xmax;
    double ymin, ymax;
    double zmin, zmax;
};

struct box {
    double xmin, xmax;
    double ymin, ymax;
    double zmin, zmax;
};

const box DETECTOR = { -20, 320, -350, 350, -360, 360 }; //(z, y, x)

inline vector<trigger> CRT_triggers = { //(x, y, z)
    {140, 320, 310, 340, 80, 214}, //nTCO CRT
    {140, 320, -340, -310, 80, 214}, //TCO CRT - top position
    {-226, -46, -340, -310, 80, 214} //TCO CRT - bottom position
};

inline void drawBox(){
        vector<double> blankx = {DETECTOR.xmin, DETECTOR.xmax};
        vector<double> blanky = {DETECTOR.ymin, DETECTOR.ymax};
        vector<double> blankz = {DETECTOR.zmin, DETECTOR.zmax};

        TGraph2D *gphantom = new TGraph2D(2, blankx.data(), blanky.data(), blankz.data());
        gphantom->SetNameTitle("box", "box");
        gphantom->GetXaxis()->SetTitle("z (cm)");
        gphantom->GetYaxis()->SetTitle("y (cm)");
        gphantom->GetZaxis()->SetTitle("x (cm)");

        gphantom->SetMarkerColor(kWhite);
        gphantom->SetMarkerSize(0.001);
        gphantom->Draw("P");

    }

inline void drawCRT(const trigger& b, vector<TObject*>& keepAlive){
    //First face
    double px1[5] = {b.zmin, b.zmax, b.zmax, b.zmin, b.zmin};
    double py1[5] = {b.ymin, b.ymin, b.ymin, b.ymin, b.ymin};
    double pz1[5] = {b.xmin, b.xmin, b.xmax, b.xmax, b.xmin};

    TPolyLine3D *facelow = new TPolyLine3D(5, px1, py1, pz1);
    facelow->SetLineColor(kBlack);
    facelow->SetLineWidth(2);
    facelow->Draw("same");
    keepAlive.push_back(facelow);

    //Second face
    double px2[5] = {b.zmin, b.zmax, b.zmax, b.zmin, b.zmin};
    double py2[5] = {b.ymax, b.ymax, b.ymax, b.ymax, b.ymax};
    double pz2[5] = {b.xmin, b.xmin, b.xmax, b.xmax, b.xmin};

    TPolyLine3D *facehigh = new TPolyLine3D(5, px2, py2, pz2);
    facehigh->SetLineColor(kBlack);
    facehigh->SetLineWidth(2);
    facehigh->Draw("same");
    keepAlive.push_back(facehigh);

    //Connect the two faces
    double vx[4] = {b.zmin, b.zmax, b.zmax, b.zmin};
    double vz[4] = {b.xmin, b.xmin, b.xmax, b.xmax};
    for (int i=0; i<4; i++){
        double ex[2] = {vx[i], vx[i]};
        double ey[2] = {b.ymin, b.ymax};
        double ez[2] = {vz[i], vz[i]};
        TPolyLine3D *edge = new TPolyLine3D(2, ex,ey,ez);
        edge->SetLineColor(kBlack);
        edge->SetLineWidth(2);
        edge->Draw("same");
        keepAlive.push_back(edge);
    }

}

inline void drawTracks(const vector<Track>& tracks){
    vector<TPolyLine3D*> lines;
    for (const auto& tr : tracks) {
        TPolyLine3D *line = new TPolyLine3D(2);
        line->SetPoint(0, tr.x0, tr.y0, tr.z0);
        line->SetPoint(1, tr.x1, tr.y1, tr.z1);
        line->SetLineColor(tr.mycolor);
        line->SetLineWidth(2);
        line->Draw("same");
        lines.push_back(line);
    }

}

inline void IsMuon(bool TrackIsSelected, Track& tr){
    if (TrackIsSelected == 1) tr.mycolor = kRed;
}



