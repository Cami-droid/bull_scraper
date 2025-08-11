import pandas as pd
import os

# Ruta completa del archivo HDF5 de origen (el que tienes)

HDF5_FILE_ORIGEN = r"D:\Documents\bull_scraper\cotizaciones_bullmarket_acumulado.h5"

# Nombre del archivo HDF5 de destino
NOMBRE_ARCHIVO_DESTINO = "cotizaciones_bmb_procesado.h5"

# Obtiene la ruta del directorio del archivo de origen
directorio_origen = os.path.dirname(HDF5_FILE_ORIGEN)

# Construye la ruta completa del archivo de destino
HDF5_FILE_DESTINO = os.path.join(directorio_origen, NOMBRE_ARCHIVO_DESTINO)

def procesar_y_limpiar_tablas_h5(file_origen, file_destino):
    """
    Procesa cada tabla del archivo de origen para limpiar los datos y agrega
    una nueva columna 'tickers' antes de guardar el resultado en un nuevo archivo.
    """
    try:
        # Abre el archivo HDF5 de origen para leer sus claves
        with pd.HDFStore(file_origen, mode='r') as store:
            keys = store.keys()
        
        print(f"✔️ Archivo '{file_origen}' encontrado. Claves a procesar: {keys}")

        # Abre el nuevo archivo HDF5 de destino en modo de escritura
        with pd.HDFStore(file_destino, mode='w') as store_destino:
            for key in keys:
                print(f"Procesando la tabla '{key}'...")
                
                # 1. Lee la tabla completa del archivo de origen
                df = pd.read_hdf(file_origen, key=key)
                
                # 2. Extrae el ticker de la columna 'simbolo' si existe
                if 'simbolo' in df.columns:
                    tickers = df['simbolo'].str.split(' \|', n=1, expand=True)[0]
                    # Agrega la nueva columna al principio del DataFrame
                    df.insert(0, 'tickers', tickers)
                
                # 3. Eliminar filas duplicadas
                df.drop_duplicates(keep='last', inplace=True)
                
                # 4. Convertir la columna de fecha a formato datetime
                if 'fecha_cotizacion' in df.columns:
                    df['fecha_cotizacion'] = pd.to_datetime(df['fecha_cotizacion'], errors='coerce')
                
                # 5. Limpiar nombres de columnas
                df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
                
                # 6. Guarda el DataFrame limpio en el nuevo archivo
                store_destino.put(key, df, format='table', data_columns=True, index=False)
            
        print("\n✅ ¡Procesamiento completado!")
        print(f"El archivo '{file_origen}' ha sido procesado y el resultado, con la nueva columna 'tickers', guardado en '{file_destino}'.")

    except FileNotFoundError:
        print(f"❌ Error: El archivo '{file_origen}' no fue encontrado. Asegúrate de que la ruta sea correcta.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante el procesamiento: {e}")

# Ejecuta el procesamiento
if __name__ == "__main__":
    procesar_y_limpiar_tablas_h5(HDF5_FILE_ORIGEN, HDF5_FILE_DESTINO)