# clean_old_h5.py
# ---------------------------------------------------------
# Limpia archivos HDF5 históricos generados por el scraper
# y los guarda en una carpeta aparte sin sobrescribir nada.
# ---------------------------------------------------------

import os
import pandas as pd
from cleaning import clean_dataframe

# Configuración de carpetas
INPUT_DIR = "data/hdf5_dumps"
OUTPUT_DIR = "data/hdf5_cleaned"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_h5_file(input_path, output_path):
    """Lee un archivo HDF5, limpia cada tabla y guarda una copia nueva."""
    try:
        with pd.HDFStore(input_path, "r") as store_in, pd.HDFStore(output_path, "w") as store_out:
            for key in store_in.keys():
                print(f"🧹 Limpiando tabla {key} de {os.path.basename(input_path)}...")
                df = store_in[key]

                # Aplicar limpieza completa
                df_clean = clean_dataframe(df)

                # Guardar tabla limpia
                store_out.put(key, df_clean, format="table", data_columns=True)

        print(f"✔️ Archivo limpio guardado en: {output_path}\n")

    except Exception as e:
        print(f"❌ Error procesando {input_path}: {e}")


def main():
    """Limpia todos los HDF5 del directorio INPUT_DIR."""
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".h5"):
            continue

        input_path = os.path.join(INPUT_DIR, fname)
        output_path = os.path.join(OUTPUT_DIR, fname.replace(".h5", "_cleaned.h5"))

        clean_h5_file(input_path, output_path)

    print("🏁 Limpieza completa. Todos los archivos limpios están en:")
    print(f"➡️ {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
