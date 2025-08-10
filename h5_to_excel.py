import pandas as pd

# Nombre de tu archivo HDF5 y del archivo de Excel de salida
h5_file = "cotizaciones_bullmarket_acumulado.h5"
excel_output = "cotizaciones_bullmarket_completo.xlsx"

try:
    # Abre el archivo HDF5 para obtener todas sus tablas (keys)
    with pd.HDFStore(h5_file) as store:
        keys = store.keys()
        
    print(f"Tablas encontradas en el archivo HDF5: {keys}")

    # Usa ExcelWriter para crear un nuevo archivo de Excel
    # El motor 'xlsxwriter' es robusto y recomendado
    with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
        # Itera sobre cada tabla (key) que encontraste
        for key in keys:
            print(f"Convirtiendo la tabla '{key.strip('/')}' a una hoja de cálculo...")
            
            # Lee cada tabla del archivo .h5 en un DataFrame
            df = pd.read_hdf(h5_file, key=key)
            
            # Convierte el DataFrame a una hoja de Excel
            # El nombre de la hoja será el mismo que el nombre de la tabla
            sheet_name = key.strip('/')  # Elimina el '/' inicial para el nombre de la hoja
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
    print("\n¡Conversión completada!")
    print(f"El archivo '{excel_output}' ha sido creado exitosamente con todas las tablas.")

except FileNotFoundError:
    print(f"Error: El archivo '{h5_file}' no fue encontrado.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")