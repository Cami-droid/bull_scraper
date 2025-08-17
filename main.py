from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from config import *
from login import perform_login
from scraper import extract_table
from storage import save_to_hdf5
from dashboard import extract_dashboard_data
from utils import sanitize_column_names
import os

def main():
    try:
        if not os.path.exists(CHROMEDRIVER_PATH):
            print("❌ Chromedriver no encontrado.")
            return

        service = ChromeService(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service)

        cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)
        if not cookies:
            print("❌ Login fallido.")
            return

        dataframes = {}

        # 🔹 Extraer dashboard
        print("📊 Extrayendo datos del dashboard...")
        df_dashboard = extract_dashboard_data(driver, "https://www.bullmarketbrokers.com/Clients/Dashboard")
        if df_dashboard is not None and not df_dashboard.empty:
            df_dashboard = sanitize_column_names(df_dashboard)  # Limpiar nombres de columnas
            dataframes['dashboard'] = df_dashboard
            print("✔️ Datos del dashboard extraídos exitosamente.")
            print(df_dashboard)
        else:
            print("❌ No se pudieron extraer los datos del dashboard.")

        # 🔹 Extraer otras tablas
        for url in URLS:
            nombre_tabla = url.split("/")[-1].replace('%20', ' ')
            print(f"📥 Procesando: {nombre_tabla}")
            df = extract_table(driver, url, cookies)
            if df is not None and not df.empty:
                df = sanitize_column_names(df)  # Limpiar nombres de columnas
                dataframes[nombre_tabla] = df
                print(f"✔️ Tabla '{nombre_tabla}' extraída. Dimensiones: {df.shape}")
            else:
                print(f"❌ No se pudo extraer la tabla '{nombre_tabla}'.")

        if dataframes:
            save_to_hdf5(dataframes, output_dir=OUTPUT_DIR, accumulate=ACCUMULATE, hdf5_file=HDF5_FILE)
            print(f"💾 Tablas guardadas en {OUTPUT_DIR} (diario) {'y ' + HDF5_FILE if ACCUMULATE else ''}")
        else:
            print("⚠️ No se obtuvieron datos para guardar.")

    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")
    finally:
        driver.quit()  # Asegurar que el driver se cierre siempre

if __name__ == "__main__":
    main()