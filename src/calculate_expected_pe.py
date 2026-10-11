"""This program calculates the expected number of PE produced by a crossing muon in absence of Rayleigh scattering. """
import pandas as pd
import numpy as np
from channel_mapping import GetValidModules

DATAFRAME = "../data/processed_dataframe_bot_distances.csv"
EFFICIENCY = 0.03 #assumed
DENSITY = 1.4 #g/cm^3
ENERGY_LOSS = 1.519 #MeV*cm^2/g
PHOTON_YIELD = 2.4 * 10**4 #photons/MeV

def n_gamma():
    return 1/(4*np.pi) * ENERGY_LOSS * DENSITY * PHOTON_YIELD

def n_pe(df):
    modules = GetValidModules()
    n_g = n_gamma()
    
   
    df_angular_accept = pd.DataFrame()
    df_angular_accept["run"] = df["run"]
    df_angular_accept["event"] = df["event"]
    df_angular_accept["ppm"] = df["ppm"]

    for m in modules: 
        df_angular_accept[f"solid_angle_{m}"] = df[f"solid_angle_{m}"] 
        df_angular_accept[f"Nhit_{m}"] = (n_g * df[f"solid_angle_{m}"])
        df_angular_accept[f"pe_{m}"] = (EFFICIENCY * n_g * df[f"solid_angle_{m}"])

    return df_angular_accept

def main():
    df = pd.read_csv(DATAFRAME)
    pe_df = n_pe(df)
    pe_df.to_csv("../data/new_angular_acceptance.csv", index=False)

if __name__ == "__main__":
    main()