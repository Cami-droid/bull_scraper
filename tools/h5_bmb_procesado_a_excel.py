import pandas as pd
import os

# Nombres de los archivos
HDF5_FILE = r"D:\Documents\bull_scraper\cotizaciones_bmb_procesado.h5"
EXCEL_FILE = "cotizaciones_bmb_procesado.xlsx"

def convertir_h5_a_excel(h5_path, excel_path):
    """
    Convierte todas las tablas de un archivo HDF5 a un archivo de Excel,
    donde cada tabla es una hoja de cálculo.
    """
    if not os.path.exists(h5_path):
        print(f"❌ Error: El archivo '{h5_path}' no fue encontrado.")
        return

    print(f"✔️ Archivo HDF5 '{h5_path}' encontrado. Iniciando conversión...")
    
    try:
        # Abre el archivo HDF5 y obtiene todas las claves (nombres de tablas)
        with pd.HDFStore(h5_path, mode='r') as store:
            keys = store.keys()
            
        print(f"Tablas encontradas: {keys}")

        # Crea un nuevo archivo de Excel para escribir las hojas
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            for key in keys:
                # Lee cada tabla en un DataFrame
                df = pd.read_hdf(h5_path, key=key)
                
                # Usa el nombre de la tabla como nombre de la hoja
                sheet_name = key.strip('/').replace('_', ' ').title()
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                print(f"✅ Tabla '{key}' convertida a hoja '{sheet_name}'.")

        print(f"\n🎉 ¡Conversión completada!")
        print(f"El archivo '{excel_path}' ha sido creado exitosamente con todas las tablas.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante la conversión: {e}")

# Ejecuta la función
if __name__ == "__main__":
    convertir_h5_a_excel(HDF5_FILE, EXCEL_FILE)