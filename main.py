from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from config import *
from login import perform_login
from scraper import extract_table
from storage import save_to_hdf5
from dashboard import extract_dashboard_data
import os

def main():
    if not os.path.exists(CHROMEDRIVER_PATH):
        print("Chromedriver no encontrado.")
        return

    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)
    if not cookies:
        print("❌ Login fallido.")
        driver.quit()
        return

    dataframes = {}

    # 🔹 Extraer dashboard inmediatamente después del login
    print("📊 Extrayendo datos del dashboard...")
    df_dashboard = extract_dashboard_data(driver, "https://www.bullmarketbrokers.com/Clients/Dashboard")
    if df_dashboard is not None and not df_dashboard.empty:
        dataframes['dashboard'] = df_dashboard
        print("✔️ Datos del dashboard extraídos exitosamente.")
        print(df_dashboard)
    else:
        print("❌ No se pudieron extraer los datos del dashboard.")

    # 🔹 Extraer todas las demás tablas
    for url in URLS:
        nombre_tabla = url.split("/")[-1].replace('%20', ' ')
        print(f"📥 Procesando: {nombre_tabla}")
        df = extract_table(driver, url, cookies)
        if df is not None and not df.empty:
            dataframes[nombre_tabla] = df
            print(f"✔️ Tabla '{nombre_tabla}' extraída. Dimensiones: {df.shape}")
        else:
            print(f"❌ No se pudo extraer la tabla '{nombre_tabla}'.")

    driver.quit()

    if dataframes:
        save_to_hdf5(HDF5_FILE, dataframes)
        print(f"💾 Tablas guardadas en {HDF5_FILE}")
    else:
        print("⚠️ No se obtuvieron datos para guardar.")       

if __name__ == "__main__":
    main()