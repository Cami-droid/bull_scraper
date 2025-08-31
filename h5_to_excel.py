
import pandas as pd
import os
import sys
from datetime import datetime  # puede no usarse, se mantiene por compatibilidad
from typing import Optional

# Añadir el directorio padre al sys.path para las importaciones relativas
# Esto permite que el script encuentre 'config.py' sin importar desde dónde se ejecute
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import HDF5_FILE, OUTPUT_DIR


def _ensure_excel_dir(output_dir: str, excel_dir: Optional[str] = None) -> str:
    """
    Asegura que exista la carpeta data/excel_dumps al mismo nivel que data/hdf5_dumps.
    Devuelve la ruta final a usar para los .xlsx.
    """
    parent_dir = os.path.dirname(output_dir.rstrip(os.sep))  # -> data
    target = excel_dir or os.path.join(parent_dir, "excel_dumps")
    os.makedirs(target, exist_ok=True)
    return target


def _compute_excel_name(h5_path: str) -> str:
    """
    Deriva el nombre del .xlsx a partir del .h5.
    - data_YYYY-MM-DD_HH-MM.h5 -> cotizaciones_bullmarket_YYYY-MM-DD_HH-MM.xlsx
    - otros -> cotizaciones_bullmarket_completo.xlsx
    """
    base = os.path.basename(h5_path)
    name, _ = os.path.splitext(base)
    if name.startswith("data_"):
        suffix = name[len("data_"):]
        return f"cotizaciones_bullmarket_{suffix}.xlsx"
    else:
        return "cotizaciones_bullmarket_completo.xlsx"

def h5_to_excel(h5_input=None, output_dir=OUTPUT_DIR, excel_output=None, process_all_daily=False,
                skip_existing=True, excel_dir: Optional[str] = None):

    """
    Convierte tablas de archivos HDF5 a un archivo Excel.

    Args:
        h5_input (str, optional): Ruta al archivo HDF5 a procesar. Si None, usa HDF5_FILE (histórico).
        output_dir (str): Carpeta donde están los archivos HDF5 diarios (p.ej. data/hdf5_dumps).
        excel_output (str, optional): Nombre o ruta del archivo Excel de salida. Si None, se genera automáticamente.
        process_all_daily (bool): Si True, procesa todos los archivos HDF5 en output_dir.
        skip_existing (bool): Si True, evita recrear el Excel si ya existe.
        excel_dir (str, optional): Carpeta destino para los Excel. Por defecto, data/excel_dumps.
    """
    try:
        # Asegurar carpeta de destino (hermana de hdf5_dumps)
        excel_dir = _ensure_excel_dir(output_dir, excel_dir)

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

        for h5_file in sorted(h5_files):
            # Generar ruta del archivo Excel
            if excel_output:
                # Si se pasa un nombre relativo, guardarlo dentro de excel_dir
                excel_file = excel_output if os.path.isabs(excel_output) else os.path.join(excel_dir, excel_output)
            else:
                excel_file = os.path.join(excel_dir, _compute_excel_name(h5_file))

            # Si ya existe y no queremos duplicar trabajo, saltar
            if skip_existing and os.path.exists(excel_file):
                print(f"⏭️ Saltado (ya existe): {os.path.basename(excel_file)}")
                continue

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

                    print(f"✔️ Conversión completada! Archivo creado: {excel_file}")

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
    # Procesar todos los HDF5 en data/hdf5_dumps y guardar Excel en data/excel_dumps
    h5_to_excel(process_all_daily=True, skip_existing=True)
