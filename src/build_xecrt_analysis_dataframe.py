"""This program creates a DataFrame for the Xenon CRT data analysis from data extracted with LArSoft and stored in an anaTree."""
import numpy as np
import pandas as pd
import uproot
import re
import awkward as ak
import argparse
import glob
from channel_mapping import channel_label, ALL_CHANNELS, module_mapping, MODULES


filename = "data/merged_xecrt_bot.root"
ana_dir = "xeana/t1"
acceptance_window = {"start": -1.5, "end": 20}
pre_end = -10.0
post_end = 35.0
pe_threshold = 0.3
TIME_CORRECTION = -2.0 #correction in #mus to account for the time delay between membrane and cathode modules. The membrane modules are delayed by 2 mus with respect to the cathode modules. 


def load_ana_tree_data(filename):
    """Load all relevant data from the anaTree."""
    print("Loading data...")
    data = uproot.open(filename)
    tree = data[ana_dir]
    branches_unique =  ["run", "event", "nselected"]
    branches_track = tree.keys(filter_name="trk*")
    branches_light = [ x for x in tree.keys() if x not in branches_track and x not in tree.keys(filter_typename="int32_t") ]

    mask_selected = "(trkIsSelected == 1) & (nselected==1)"

    arr_track = tree.arrays(branches_track, mask_selected, library="ak")
    arr_unique = tree.arrays(branches_unique, library="ak")
    arr_light = tree.arrays(branches_light, library="ak")

    event_has_track = ak.any(arr_track.trkIsSelected, axis = 1)
    arr_unique = arr_unique[event_has_track]
    arr_light = arr_light[event_has_track]
    arr_track = arr_track[event_has_track]

    for field in arr_track.fields:
        counts = ak.num(arr_track[field], axis=-1)
        if not ak.all(counts == 1):
            raise ValueError(f"Field {field!r} has entries that aren't length 1")

    arr_track = ak.zip({field: ak.flatten(arr_track[field], axis=-1) for field in arr_track.fields})

    
    return arr_unique, arr_track, arr_light


def extract_pe_information(light, arr_unique):
    """Evaluate for each event the number of PEs in the pre-trigger, post-trigger and trigger region and the total #PE in the trigger window.""" 
    print("Extracting OpHit information...")                            
    opchannel = light.ophit_opchannel
    pe = light.ophit_pe
    time = light.ophit_time
    
    df_hits = ak.to_dataframe(ak.zip({
        "run": arr_unique.run,
        "event": arr_unique.event,
        "opchannel": opchannel,
        "pe": pe,
        "time": time,
    })).reset_index(drop=True)

    mask = df_hits["opchannel"] >= 2000
    df_hits.loc[mask, "time"] = df_hits.loc[mask, "time"] + TIME_CORRECTION

    df_hits["is_trg"]  = (df_hits["time"] >= acceptance_window["start"]) & (df_hits["time"] <= acceptance_window["end"])
    df_hits["is_pre"]  = (df_hits["time"] > pre_end) & (df_hits["time"] < acceptance_window["start"])
    df_hits["is_post"] = (df_hits["time"] < post_end) & (df_hits["time"] > acceptance_window["end"])

    grouped = df_hits.groupby(["run", "event", "opchannel"]).apply(
        lambda g: pd.Series({
            "pe_trg":  g.loc[g.is_trg,  "pe"].sum(),
            "pe_pre":  g.loc[g.is_pre,  "pe"].sum(),
            "pe_post": g.loc[g.is_post, "pe"].sum(),
        }),
    include_groups=False).reset_index()
    

    limit = pe_threshold * grouped["pe_trg"]
    pre  = grouped["pe_pre"]  > limit
    post = grouped["pe_post"] > limit

    grouped["discarded"] = 0
    grouped.loc[pre & ~post, "discarded"] = 1
    grouped.loc[~pre & post, "discarded"] = 2
    grouped.loc[pre & post,  "discarded"] = 3

    pe_wide = grouped.pivot(index=["run", "event"], columns="opchannel", values="pe_trg").fillna(0)
    pe_wide.columns = [f"PE_{channel_label(c)}" for c in pe_wide.columns]
    
    pe_pre_wide = grouped.pivot(index=["run", "event"], columns="opchannel", values="pe_pre").fillna(0)
    pe_pre_wide.columns = [f"PRE_PE_{channel_label(c)}" for c in pe_pre_wide.columns]
    
    pe_post_wide = grouped.pivot(index=["run", "event"], columns="opchannel", values="pe_post").fillna(0)
    pe_post_wide.columns = [f"POST_PE_{channel_label(c)}" for c in pe_post_wide.columns]

    disc_wide = grouped.pivot(index=["run", "event"], columns="opchannel", values="discarded").fillna(-1).astype(int)
    disc_wide.columns = [f"discarded_{channel_label(c)}" for c in disc_wide.columns]

    df = pe_wide.join(disc_wide).reset_index()
    ordered_columns = ["run", "event"]
    for channel in ALL_CHANNELS:
        pecol = f"PE_{channel_label(channel)}" 
        disccol = f"discarded_{channel_label(channel)}" 
        if pecol not in df.columns:
            print("well... shiiit happens...", channel)
            grouped[pecol] = 0
        if disccol not in df.columns:
            grouped[disccol] = -1

    for channel in ALL_CHANNELS:
        ordered_columns.extend([f"PE_{channel_label(channel)}", f"discarded_{channel_label(channel)}"])

    return df[ordered_columns]


def add_xenon_concentration(df):
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTXuwLxht-9hnNHvNCYqQRQulTMk7ymE1gRTpo1LGHfey4HGaGqz0CqIFo8IBYevtVXsqj_9aitUD5t/pub?output=xlsx"
    df_ppm = pd.read_excel(url, sheet_name="XeRuns")
    print(df_ppm.head())
    df_ppm = df_ppm[df_ppm["HV"] == 154]
    df = df.merge(df_ppm[["Run Number", "ppm"]], left_on="run", right_on="Run Number", how='left').drop(columns="Run Number")
    
    return df

def build_dataframe(filename):
    arr_unique, arr_track, arr_light = load_ana_tree_data(filename)
    arr_track["run"] = arr_unique.run
    arr_track["event"] = arr_unique.event
    dftrack:pd.DataFrame = ak.to_dataframe(arr_track) # type: ignore
    dftrack = dftrack.reset_index(drop=True)
    df_pes = extract_pe_information(arr_light, arr_unique)
    df = dftrack.merge(df_pes, on=["run", "event"], how="left")
    cols = ["run", "event"] + [c for c in df.columns if c not in ["run", "event"]]
    df = df[cols]
    #df = radial_distance(df)
    df = add_xenon_concentration(df)

    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", nargs="?", default=filename)
    #parser.add_argument("--pre", action="store_true")
    args = parser.parse_args()
    df = build_dataframe(args.filename)
    df.to_csv("data/processed_dataframe_bot.csv", index=False)

if __name__ == "__main__":
    main()

