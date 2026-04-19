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


def _limpiar_columnas_numericas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Intenta convertir a número las columnas string que parecen numéricas.
    Maneja formato argentino: punto como separador de miles, coma como decimal.
    Ej: "1.456" -> 1456, "1.456,78" -> 1456.78
    Columnas con prefijo de moneda (ej: "ARS 107,88") se dejan como string.
    Columnas que ya son numéricas no se tocan.
    """
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            continue  # ya es número, no tocar

        muestra = df[col].dropna().astype(str)
        muestra = muestra[muestra != '-']
        if muestra.empty:
            continue

        # Si más del 20% de los valores empiezan con letra, no es columna numérica
        tiene_letra = muestra.str.match(r'^[A-Za-z]').mean()
        if tiene_letra > 0.2:
            continue

        # Detectar formato analizando la parte decimal:
        # - Punto con exactamente 3 decimales -> separador de miles (ej: "5.109", "52.105")
        # - Punto con != 3 decimales           -> decimal real      (ej: "210.0", "979.0")
        # - Con coma                           -> formato argentino (ej: "1.456,78")
        tiene_coma = muestra.str.contains(',', regex=False).mean() > 0.5

        con_punto = muestra[muestra.str.contains(r'\.', regex=True)]
        if not con_punto.empty and not tiene_coma:
            # Contar cuántos tienen exactamente 3 dígitos tras el punto
            tres_decimales = con_punto.str.match(r'^\d+\.\d{3}$').mean()
            punto_es_miles = tres_decimales > 0.5
        else:
            punto_es_miles = False

        if tiene_coma:
            # Formato argentino: "1.456,78" -> quitar punto de miles, coma a decimal
            intentar = (muestra
                        .str.replace('.', '', regex=False)
                        .str.replace(',', '.', regex=False))
        elif punto_es_miles:
            # Punto de miles: "5.109" -> "5109"
            intentar = muestra.str.replace('.', '', regex=False)
        else:
            # Punto decimal real: "210.0" -> convertir directo
            intentar = muestra

        convertido = pd.to_numeric(intentar, errors='coerce')

        # Solo reemplazar si la mayoria se convirtio bien (evitar falsos positivos)
        if convertido.notna().mean() > 0.8:
            if tiene_coma:
                df[col] = (df[col].astype(str)
                           .str.replace('.', '', regex=False)
                           .str.replace(',', '.', regex=False))
            elif punto_es_miles:
                df[col] = df[col].astype(str).str.replace('.', '', regex=False)
            df[col] = pd.to_numeric(df[col].astype(str), errors='coerce')

    return df


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

                            # Limpiar columnas numéricas guardadas como string (ej: "1.456" -> 1456)
                            df = _limpiar_columnas_numericas(df)

                            sheet_name = key.strip('/')[:31]  # Limitar a 31 caracteres (límite de Excel)
                            df.to_excel(writer, sheet_name=sheet_name, index=False)

                            # No se aplica formato de visualizacion argentino:
                            # hacerlo causa que pandas lea los numeros como texto al reabrir el Excel.
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