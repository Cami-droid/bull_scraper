import pandas as pd
import os

HDF5_FILE = r"data/hdf5_dumps\dolar_acumulado.h5"
HDF5_KEY = "/cotizaciones_dolar"

# columnas correctas según el scraper actual
expected_columns = [
    "dolar_mep_compra",
    "dolar_mep_venta",
    "dolar_mep",
    "dolar_cable_ccl",
    "fecha_scraping",
    "diferencia_mep_ccl"
]

print("📂 Cargando HDF5...")
df = pd.read_hdf(HDF5_FILE, key=HDF5_KEY)

print("\nColumnas ANTES de limpiar:")
print(df.columns.tolist())

# Conservar solo lo que el scraper usa
df_clean = df.reindex(columns=expected_columns)

print("\nColumnas DESPUÉS de limpiar:")
print(df_clean.columns.tolist())

print("\n💾 Guardando archivo limpio...")
df_clean.to_hdf(HDF5_FILE, key=HDF5_KEY, mode="w", format="table")

print("\n🎉 Listo: el HDF5 ahora es compatible con tu scraper.")
