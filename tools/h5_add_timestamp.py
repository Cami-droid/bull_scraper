import pandas as pd
import os
from datetime import datetime
from typing import List, Optional  # <-- ¡Aquí está la importación que faltaba!

# Define las carpetas, ajusta si es necesario
H5_INPUT_DIR = "data/hdf5_dumps"

def _extract_datetime_from_filename(filename: str) -> Optional[datetime]:
    """
    Extrae la fecha y hora de un nombre de archivo HDF5.
    Ej: 'data_2025-08-19_01-16.h5' -> datetime(2025, 8, 19, 1, 16)
    """
    try:
        # Asumimos el formato 'data_YYYY-MM-DD_HH-MM.h5'
        date_str = filename.split('_')[1] + '_' + filename.split('_')[2].split('.')[0]
        return datetime.strptime(date_str, '%Y-%m-%d_%H-%M')
    except (ValueError, IndexError):
        print(f"⚠️ No se pudo extraer la fecha de '{filename}'. Se saltará este archivo.")
        return None

def add_timestamp_to_h5_files(input_dir: str = H5_INPUT_DIR):
    """
    Recorre los archivos HDF5 en un directorio, añade la columna 'fecha_scraping'
    usando la fecha del nombre del archivo si no existe.
    """
    h5_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.h5')]
    
    if not h5_files:
        print(f"⚠️ No se encontraron archivos HDF5 en '{input_dir}'.")
        return

    print("Iniciando el proceso de agregar la columna 'fecha_scraping' a los archivos HDF5...")
    print(f"Archivos a procesar: {len(h5_files)}")

    for h5_path in sorted(h5_files):
        filename = os.path.basename(h5_path)
        print(f"\nProcesando '{filename}'...")
        
        # Extraer el timestamp del nombre del archivo
        timestamp = _extract_datetime_from_filename(filename)
        if not timestamp:
            continue

        try:
            with pd.HDFStore(h5_path, 'r+') as store:
                for key in store.keys():
                    key_clean = key.strip('/')
                    df = store.get(key)
                    
                    if 'fecha_scraping' in df.columns:
                        print(f"  - La tabla '{key_clean}' ya tiene 'fecha_scraping'. No se modifica.")
                    else:
                        df['fecha_scraping'] = timestamp
                        store.put(key, df, format='table', data_columns=True)
                        print(f"  - Columna 'fecha_scraping' añadida a la tabla '{key_clean}'.")
        except Exception as e:
            print(f"❌ Error al procesar '{filename}': {e}. Se saltará este archivo.")
            continue
            
    print("\n✔️ Proceso de actualización completado exitosamente.")

if __name__ == "__main__":
    add_timestamp_to_h5_files()