import pandas as pd
import os

def save_to_hdf5(hdf5_file, dataframes):
    """Guarda múltiples DataFrames en un archivo HDF5 acumulando histórico."""
    try:
        mode = 'a' if os.path.exists(hdf5_file) else 'w'
        with pd.HDFStore(hdf5_file, mode=mode) as store:
            for name, df_new in dataframes.items():
                key = name.replace(" ", "_").lower()

                # Leer histórico si existe
                if key in store:
                    df_old = store[key]
                    combined = pd.concat([df_old, df_new], ignore_index=True)
                    combined.drop_duplicates(inplace=True)
                else:
                    combined = df_new

                store.put(key, combined, format='table', data_columns=True)

        print(f"💾 Tablas guardadas/acumuladas en {hdf5_file}")

    except ImportError as e:
        print("❌ Falta instalar la librería 'tables'. Use: pip install tables")
        print(f"Detalles: {e}")
    except Exception as e:
        print(f"❌ Error al guardar/acumular en {hdf5_file}: {e}")
