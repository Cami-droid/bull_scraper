import pandas as pd
import os

HDF5_FILE = r"data/hdf5_dumps\dolar_acumulado.h5"
HDF5_KEY = "/cotizaciones_dolar"

if not os.path.exists(HDF5_FILE):
    print("El archivo HDF5 no existe.")
    exit()

print("📂 Cargando HDF5 existente...")
df = pd.read_hdf(HDF5_FILE, key=HDF5_KEY)

print("Columnas actuales:")
print(df.columns)

# Solo agregar si no existe
if "diferencia_mep_ccl" not in df.columns:
    print("➕ Agregando columna diferencia_mep_ccl...")
    df["diferencia_mep_ccl"] = (df["dolar_mep"] - df["dolar_cable_ccl"]).round(2)

else:
    print("✔️ La columna diferencia_mep_ccl ya existe. No se modifica.")

print("💾 Guardando archivo reparado...")
df.to_hdf(HDF5_FILE, key=HDF5_KEY, mode="w", format="table")

print("🎉 Listo. El HDF5 está actualizado y el scraper va a funcionar sin errores.")
