import pandas as pd

def save_to_hdf5(hdf5_file, dataframes):
    """Guarda múltiples DataFrames en un archivo HDF5."""
    try:
        with pd.HDFStore(hdf5_file, mode='a') as store:
            for name, df in dataframes.items():
                key = name.replace(" ", "_").lower()
                store.put(key, df, format='table', data_columns=True)
        print(f"💾 Tablas guardadas en {hdf5_file}")
    except ImportError as e:
        print("❌ ERROR: Falta instalar la librería necesaria para guardar en HDF5.")
        print("Instale con: pip install tables")
        print(f"Detalles técnicos: {e}")
    except Exception as e:
        print(f"❌ ERROR al guardar el archivo HDF5: {e}")
