import pandas as pd
import os
from datetime import datetime
from typing import Optional, List

# Define las carpetas, ajusta estas variables si son diferentes a las que usas.
H5_INPUT_DIR = "../data/hdf5_dumps"
EXCEL_OUTPUT_FILE = "../data/excel_dumps/cotizaciones_bullmarket_historico_completo.xlsx"

def _get_h5_files(directory: str) -> List[str]:
    """
    Obtiene la lista de archivos HDF5 en un directorio, ordenados por fecha.
    """
    h5_files = sorted([
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith('.h5') and os.path.isfile(os.path.join(directory, f))
    ])
    return h5_files

def h5_to_single_excel(
    input_dir: str = H5_INPUT_DIR,
    output_file: str = EXCEL_OUTPUT_FILE,
):
    """
    Convierte múltiples archivos HDF5 a un único archivo Excel con hojas para cada tabla.
    """
    h5_files = _get_h5_files(input_dir)

    if not h5_files:
        print(f"⚠️ No se encontraron archivos HDF5 en '{input_dir}' para procesar.")
        return

    merged_data = {}

    print("Iniciando la consolidación de datos de HDF5 a un único Excel...")
    print(f"Archivos a procesar: {len(h5_files)}")

    for h5_path in h5_files:
        print(f"Procesando '{os.path.basename(h5_path)}'...")
        try:
            with pd.HDFStore(h5_path, 'r') as store:
                for key in store.keys():
                    key_clean = key.strip('/')
                    df = pd.read_hdf(h5_path, key=key)

                    if key_clean in merged_data:
                        merged_data[key_clean] = pd.concat([merged_data[key_clean], df], ignore_index=True)
                    else:
                        merged_data[key_clean] = df
        except Exception as e:
            print(f"❌ Error al leer '{h5_path}': {e}. Se saltará este archivo.")
            continue
    
    if not merged_data:
        print("⚠️ No se encontraron datos para guardar en el archivo Excel.")
        return
        
    excel_dir = os.path.dirname(output_file)
    os.makedirs(excel_dir, exist_ok=True)
        
    print(f"\nGuardando datos consolidados en '{output_file}'...")
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            for key, df in merged_data.items():
                print(f"  - Procesando tabla '{key}'...")
                
                # NO SE REALIZAN CONVERSIONES NUMÉRICAS AQUÍ.
                # Las columnas se guardarán tal como están en los archivos HDF5.
                # Esto preserva la información del tipo de moneda ("ARS ", "USD ", etc.).
                
                if 'ticker' in df.columns and 'fecha_scraping' in df.columns:
                    df.drop_duplicates(subset=['ticker', 'fecha_scraping'], keep='last', inplace=True)
                
                sheet_name = key[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
            print(f"✔️ Conversión completada exitosamente! Archivo creado: {output_file}")
            
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al escribir el archivo Excel: {e}")

if __name__ == "__main__":
    h5_to_single_excel()