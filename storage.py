import pandas as pd
import os
from datetime import datetime

def save_to_hdf5(dataframes, output_dir="data/hdf5_dumps", accumulate=False, hdf5_file="historical_data.h5"):
    """
    Guarda DataFrames en archivos HDF5. Por defecto, guarda un archivo por ejecución con fecha.
    Si accumulate=True, también guarda/acumula en un archivo histórico.

    Args:
        dataframes (dict): Diccionario con nombres de tablas y sus DataFrames.
        output_dir (str): Carpeta donde se guardan los HDF5 diarios.
        accumulate (bool): Si True, acumula en un archivo histórico.
        hdf5_file (str): Nombre del archivo histórico si accumulate=True.
    """
    try:
        # Crear carpeta de salida si no existe
        os.makedirs(output_dir, exist_ok=True)

        # Generar nombre de archivo con fecha y hora de ejecución
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        daily_file = os.path.join(output_dir, f"data_{timestamp}.h5")

        # Guardar archivo HDF5 diario
        with pd.HDFStore(daily_file, mode='w') as store:
            for name, df_new in dataframes.items():
                # Saltar DataFrames vacíos o nulos
                if df_new is None or df_new.empty:
                    print(f"⚠️ Saltando la tabla '{name}'. No hay datos válidos para guardar.")
                    continue
                
                # Sanitizar nombre de la tabla
                key = name.replace(" ", "_").lower()
                store.put(key, df_new, format='table', data_columns=True)
        
        print(f"💾 Tablas guardadas en {daily_file}")

        # Opcional: acumular en archivo histórico
        if accumulate:
            mode = 'a' if os.path.exists(hdf5_file) else 'w'
            with pd.HDFStore(hdf5_file, mode=mode) as store:
                for name, df_new in dataframes.items():
                    if df_new is None or df_new.empty:
                        continue
                    
                    key = name.replace(" ", "_").lower()
                    if key in store:
                        df_old = store[key]
                        combined = pd.concat([df_old, df_new], ignore_index=True)
                        combined.drop_duplicates(inplace=True)
                    else:
                        combined = df_new
                    
                    store.put(key, combined, format='table', data_columns=True)
            
            print(f"💾 Tablas acumuladas en {hdf5_file}")

    except ImportError as e:
        print("❌ Falta instalar la librería 'tables'. Use: pip install tables")
        print(f"Detalles: {e}")
    except Exception as e:
        print(f"❌ Error al guardar en {daily_file}: {e}")