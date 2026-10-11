"""This program reads a dataframe from a CSV file and produce a new dataframe with the information of the discarded events for each channel modules: total number of events, number of events discarded by each filter and the percentage of discarded events by each filter. The program also produces a bar plot with the percentage of discarded events by each filter."""

import pandas as pd
from channel_mapping import CHANNELS, MODULES
import numpy as np

file_path = "data/processed_dataframe_bot.csv"
discarded_filter = {"noHit": -1, "ok": 0, "preFilter": 1, "postFilter": 2, "preANDpost": 3}

def read_csv_file(file_path):
    """Reads a CSV file and returns a dataframe with only the discarded columns."""
    df = pd.read_csv(file_path)
    return df[[f'discarded_{m}' for m in CHANNELS]]


def calculate_discarded_events(df):
    """Calculates the number of discarded events and the percentage of discarded events for each filter."""
    total_events = len(df)
    df_discarded = pd.DataFrame({key: [0] * len(CHANNELS) for key in discarded_filter.keys() }, index = np.array(CHANNELS))
    for m in CHANNELS:
        col_name = f'discarded_{m}'
        if col_name in df.columns:
            counts = df[col_name].value_counts()
            for key, val in discarded_filter.items():
                n = counts.get(val, 0) 
                perc = 100 * n / total_events 
                df_discarded.loc[m, key] = f"{n} ({perc:.1f}%)"

    df_module_ok = pd.DataFrame({'ok_totale': [0]*len(MODULES), 'not_ok_totale': [0]*len(MODULES)}, index=MODULES)

    for m in MODULES:
        col_1 = f"discarded_{m}_1"
        col_2 = f"discarded_{m}_2"
        if col_1 in df.columns and col_2 in df.columns:
            ok_mask = (df[col_1] == 0) & (df[col_2] == 0)
            n_ok = ok_mask.sum()
            n_not_ok = (~ok_mask).sum()
            df_module_ok.loc[m, 'ok_totale'] = n_ok
            df_module_ok.loc[m, 'not_ok_totale'] = n_not_ok
    print(df_module_ok)
    return df_discarded

def main():
    df = read_csv_file(file_path)
    df_discarded = calculate_discarded_events(df)
    df_discarded.to_csv("data/new_discarded_events.csv")
    print(df_discarded)

if __name__ == "__main__":
    main()

