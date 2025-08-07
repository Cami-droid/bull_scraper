import pandas as pd

def save_to_hdf5(hdf5_file, dataframes_dict):
    with pd.HDFStore(hdf5_file, mode='a') as store:
        for name, df in dataframes_dict.items():
            key = name.replace(' ', '_').lower()
            store.append(f"/{key}", df, format='table', data_columns=True)
