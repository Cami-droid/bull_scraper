import h5py
import numpy as np

# Ruta del archivo
HDF5_FILE_ORIGEN = r"D:\Documents\bull_scraper\cotizaciones_bullmarket_acumulado.h5"

# Abrir el archivo en modo lectura
with h5py.File(HDF5_FILE_ORIGEN, 'r') as file:
    # Mostrar los grupos y datasets en la raíz
    print("Contenido del archivo:", list(file.keys()))

    # Función para explorar la estructura
    def mostrar_estructura(nombre, objeto):
        if isinstance(objeto, h5py.Group):
            print(f"Grupo: {nombre}")
        elif isinstance(objeto, h5py.Dataset):
            print(f"Dataset: {nombre}, Forma: {objeto.shape}, Tipo: {objeto.dtype}")
            # Mostrar los primeros 5 elementos del dataset
            datos = objeto[()]
            print(f"Datos (primeros 5): {datos[:5]}...")

    # Recorrer todo el archivo
    file.visititems(mostrar_estructura)