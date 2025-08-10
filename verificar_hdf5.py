import pandas as pd

# Ruta al archivo HDF5
HDF5_FILE = "cotizaciones_bullmarket_acumulado.h5"

def main():
    try:
        with pd.HDFStore(HDF5_FILE, mode='r') as store:
            print(f"📂 Tablas en {HDF5_FILE}:")
            for key in store.keys():
                df = store[key]
                print(f"- {key} → {len(df)} filas, {len(df.columns)} columnas")
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {HDF5_FILE}. Ejecute main.py primero.")
    except Exception as e:
        print(f"❌ Error al leer {HDF5_FILE}: {e}")

if __name__ == "__main__":
    main()
