import pandas as pd
import os
from datetime import datetime


def _coerce_df_for_hdf5(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte columnas con tipos mixtos o problemáticos para que
    pd.HDFStore con format='table' no lance TypeError/ValueError.

    - Columnas object con contenido mixto  → str
    - Columnas con listas/dicts embebidos  → str
    - Columnas datetime ya son soportadas  → se dejan tal cual
    """
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            # Intentar detectar si es realmente numérica
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                # Forzar a string para evitar tipos mixtos
                df[col] = df[col].astype(str)
    return df


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
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        daily_file = os.path.join(output_dir, f"data_{timestamp}.h5")

        # ── Archivo diario ────────────────────────────────────────────────
        with pd.HDFStore(daily_file, mode='w', complib='blosc', complevel=5) as store:
            for name, df_new in dataframes.items():
                if df_new is None or df_new.empty:
                    print(f"⚠️  Saltando '{name}': sin datos válidos.")
                    continue

                key = "/" + name.replace(" ", "_").lower()
                df_clean = _coerce_df_for_hdf5(df_new)

                try:
                    store.put(key, df_clean, format='table', data_columns=True)
                    print(f"  ✔️  '{name}' guardada. Shape: {df_clean.shape}")
                except Exception as e:
                    # Fallback: guardar en formato fixed si table falla
                    print(f"  ⚠️  '{name}' falló en format='table' ({e}). Intentando format='fixed'...")
                    try:
                        store.put(key, df_clean, format='fixed')
                        print(f"  ✔️  '{name}' guardada en format='fixed'.")
                    except Exception as e2:
                        print(f"  ❌  '{name}' no se pudo guardar: {e2}")

        print(f"💾 Tablas guardadas en {daily_file}")

        # ── Archivo histórico acumulado ───────────────────────────────────
        if accumulate:
            mode = 'a' if os.path.exists(hdf5_file) else 'w'
            with pd.HDFStore(hdf5_file, mode=mode, complib='blosc', complevel=5) as store:
                for name, df_new in dataframes.items():
                    if df_new is None or df_new.empty:
                        continue

                    key = "/" + name.replace(" ", "_").lower()
                    df_clean = _coerce_df_for_hdf5(df_new)

                    try:
                        if key in store:
                            df_old = store[key]
                            combined = pd.concat([df_old, df_clean], ignore_index=True)
                            combined.drop_duplicates(inplace=True)
                        else:
                            combined = df_clean

                        store.put(key, combined, format='table', data_columns=True)
                    except Exception as e:
                        print(f"  ❌  Error acumulando '{name}': {e}")

            print(f"💾 Tablas acumuladas en {hdf5_file}")

    except ImportError:
        print("❌ Falta instalar 'tables'. Ejecutá: pip install tables")
    except Exception as e:
        print(f"❌ Error al guardar HDF5: {e}")