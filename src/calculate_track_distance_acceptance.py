"""This program reads a DataFrame from a CSV file and evaluates different distances between the track and the modules of the detector."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import os
from channel_mapping import CAT_MODULES, MEM_MODULES, MODULES, GetValidModules, module_mapping

DATAFRAME = "data/processed_dataframe_bot.csv"
ARAPUCA_DIMENSIONS = (5, 60, 60) #cm
MODULES_COORD = module_mapping()
N_SEGMENTS = 100

class DistanceCalculator:
    def __init__(self, df:pd.DataFrame, n_segments = 100):
        self.df = df
        self.n_segments = n_segments
        self.track_start, self.track_end = self.track_coordinates(df)


    def track_coordinates(self, df):
        """Extract the start and end coordinates of the track from the DataFrame."""
        start = df[['trkstartx', 'trkstarty', 'trkstartz']].to_numpy()
        end   = df[['trkendx', 'trkendy', 'trkendz']].to_numpy()
        return start, end

    #---------------------------- MINIMAL DISTANCE ------------------------------------
    def radial_distance(self):
        """Calculate the radial distance as the area of a parallelogram defined by the cross product between the track and the track_start-module vector, divided by the length of the track."""
        track_start, track_end = self.track_start, self.track_end
        for m in MODULES:
            x, y, z = MODULES_COORD[m]
            module_position = np.array([x, y, z])

            d = track_end - track_start                            
            w = module_position - track_start               
            cross = np.cross(d, w)
            radial_dist = np.linalg.norm(cross, axis=1) / np.linalg.norm(d, axis=1)

            self.df[f"radial_dist_{m}"] = radial_dist
        

    #------------------------------- INTEGRATED ANGULAR ACCEPTANCE ------------------------------------------------------
    def vertex_position(self):
        """Calculate the vertexes position of the module, knowing its center coordinates and the module dimensions."""
        R = {}
        for m in MODULES:
            x, y, z = MODULES_COORD[m]
            dx, dy, dz = ARAPUCA_DIMENSIONS
            
            if m in CAT_MODULES:
                r1 = (x, y + dy/2, z + dz/2)
                r2 = (x, y + dy/2, z - dz/2)
                r3 = (x, y - dy/2, z - dz/2)
                r4 = (x, y - dy/2, z + dz/2)
            
            else: 
                r1 = (x - dy/2, y, z + dz/2)
                r2 = (x + dy/2, y, z + dz/2)
                r3 = (x + dy/2, y, z - dz/2)
                r4 = (x - dy/2, y, z - dz/2)
            
            R[m] = (r1, r2, r3, r4)

        return R

    def get_track_segments(self, start, end):
        """Divide the track into N segments and calculate the center of each."""
        P = []
        for s, e in zip(start, end):
            d = e - s
            points = []
            for i in range(self.n_segments):
                t = (i + 0.5) / self.n_segments
                points.append(s + t*d)
            P.append(np.array(points))  
        
        return P

    def lenght_segment(self, start, end): 
        """Evaluate the segment length of each track."""
        l = []
        for s, e in zip(start, end):
            d = np.linalg.norm(e - s)
            l.append(d/self.n_segments)
        return l

    def solid_angle(self, v1:np.ndarray, v2:np.ndarray, v3:np.ndarray) -> np.ndarray:
        """Implement the Van Oosterom & Strackee formula to compute the solid angle of each triangular"""
        cross = np.cross(v2, v3, axis=-1)
        num = np.sum(v1 * cross, axis=-1)
        den = 1 + np.sum(v1 * v2, axis=-1) + np.sum(v2 * v3, axis=-1) + np.sum(v3 * v1, axis=-1)
        return 2 * np.abs(np.arctan(num/den)) 

    def integrated_angular_acceptance(self):
        """Calculate the integrated angular acceptance of the track with respect to the module."""
        start, end = self.track_start, self.track_end
        tracks_segments = self.get_track_segments(start, end)
        vertices = self.vertex_position()
        seg_lenghts = self.lenght_segment(start, end)
        angles = {m:[] for m in MODULES}
        for i, track in enumerate(tracks_segments):
            for m, vert in vertices.items():
                r1, r2, r3, r4 = [np.array(v) for v in vert] 
                v1 = (r1 - track)/np.linalg.norm(r1 - track, axis=1, keepdims=True)
                v2 = (r2 - track)/np.linalg.norm(r2 - track, axis=1, keepdims=True)
                v3 = (r3 - track)/np.linalg.norm(r3 - track, axis=1, keepdims=True)
                v4 = (r4 - track)/np.linalg.norm(r4 - track, axis=1, keepdims=True)
                
                omega_1 = self.solid_angle(v1, v2, v3)
                omega_2 = self.solid_angle(v1, v3, v4)
                omega = (omega_1.sum() + omega_2.sum())*seg_lenghts[i]
                angles[m].append(omega)

        self.df = self.df.assign(**{f"solid_angle_{m}": angles[m] for m in angles})

def main():
    df = pd.read_csv(DATAFRAME)
    distCalc = DistanceCalculator(df, n_segments=N)

    print("Calculating radial distance...")
    distCalc.radial_distance()

    print("Calculating angular distance...")
    distCalc.integrated_angular_acceptance()

    outname = os.path.splitext(DATAFRAME)[0]
    distCalc.df.to_csv(f"{outname}_distances.csv", index=False)


if __name__ == "__main__":
    main()


