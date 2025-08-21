import pandas as pd

# Ruta al archivo HDF5
HDF5_FILE = r"D:\Documents\bull_scraper\data\hdf5_dumps\data_2025-08-17_19-13.h5"


def main():
    try:
        with pd.HDFStore(HDF5_FILE, mode='r') as store:
            print(f"📂 Tablas en {HDF5_FILE}:")
            for key in store.keys():
                df = store[key]
                print(f"- {key} → {len(df)} filas, {len(df.columns)} columnas")
                print(df.head())         # Muestra las primeras 5 filas
                print(df.dtypes)         # Muestra los tipos de datos por columna
                print(df['operaciones'].head(10))
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {HDF5_FILE}. Ejecute main.py primero.")
    except Exception as e:
        print(f"❌ Error al leer {HDF5_FILE}: {e}")

if __name__ == "__main__":
    main()
