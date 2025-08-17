import pandas as pd
import os
from datetime import datetime
from config import HDF5_FILE, OUTPUT_DIR

def h5_to_excel(h5_input=None, output_dir=OUTPUT_DIR, excel_output=None, process_all_daily=False):
    """
    Convierte tablas de archivos HDF5 a un archivo Excel.

    Args:
        h5_input (str, optional): Ruta al archivo HDF5 a procesar. Si None, usa HDF5_FILE (histórico).
        output_dir (str): Carpeta donde están los archivos HDF5 diarios.
        excel_output (str, optional): Nombre del archivo Excel de salida. Si None, se genera automáticamente.
        process_all_daily (bool): Si True, procesa todos los archivos HDF5 en output_dir.
    """
    try:
        if process_all_daily:
            # Procesar todos los archivos HDF5 en output_dir
            h5_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.h5')]
            if not h5_files:
                print(f"⚠️ No se encontraron archivos HDF5 en {output_dir}")
                return
        else:
            # Usar h5_input o HDF5_FILE por defecto
            h5_file = h5_input if h5_input else HDF5_FILE
            if not os.path.exists(h5_file):
                print(f"❌ Error: El archivo '{h5_file}' no fue encontrado.")
                return
            h5_files = [h5_file]

        for h5_file in h5_files:
            # Generar nombre del archivo Excel
            if not excel_output:
                timestamp = h5_file.split('_')[-2] + '_' + h5_file.split('_')[-1].replace('.h5', '') if 'data_' in h5_file else 'completo'
                excel_file = os.path.join(output_dir, f"cotizaciones_bullmarket_{timestamp}.xlsx")
            else:
                excel_file = excel_output

            # Abrir archivo HDF5 en modo lectura
            try:
                with pd.HDFStore(h5_file, mode='r') as store:
                    keys = store.keys()
                    if not keys:
                        print(f"⚠️ No se encontraron tablas en {h5_file}")
                        continue
                    
                    print(f"Tablas encontradas en {h5_file}: {keys}")

                    # Crear archivo Excel
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                        for key in keys:
                            print(f"Convirtiendo la tabla '{key.strip('/')}' a una hoja de cálculo...")
                            df = pd.read_hdf(h5_file, key=key)
                            sheet_name = key.strip('/')[:31]  # Limitar a 31 caracteres (límite de Excel)
                            df.to_excel(writer, sheet_name=sheet_name, index=False)

                    print(f"\n✔️ Conversión completada! Archivo creado: {excel_file}")

            except ValueError as ve:
                if "already opened" in str(ve):
                    print(f"❌ Error: El archivo '{h5_file}' está abierto por otro proceso. Ciérrelo e intente de nuevo.")
                else:
                    raise ve

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo o directorio especificado.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    # Por defecto, convierte el archivo histórico
    #h5_to_excel()
    
    # Opcional: convertir todos los archivos diarios
    h5_to_excel(process_all_daily=True)
    
    # Opcional: convertir un archivo diario específico
    # h5_to_excel(h5_input="data/hdf5_dumps/data_2025-08-17_18-32.h5")