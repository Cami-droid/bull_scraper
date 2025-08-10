from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from config import *
from login import perform_login
from scraper import extract_table
from storage import save_to_hdf5
import os

def main():
    # 1️⃣ Verificar chromedriver
    if not os.path.exists(CHROMEDRIVER_PATH):
        print("❌ Chromedriver no encontrado en la ruta especificada.")
        return

    # 2️⃣ Iniciar driver
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # 3️⃣ Login
    cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)
    if not cookies:
        print("❌ Login fallido.")
        driver.quit()
        return

    # 4️⃣ Extraer tablas
    dataframes = {}
    for url in URLS:
        nombre_tabla = url.split("/")[-1].replace('%20', ' ')
        print(f"📥 Procesando: {nombre_tabla}")
        df = extract_table(driver, url, cookies)
        if df is not None:
            dataframes[nombre_tabla] = df

    driver.quit()

    # 5️⃣ Guardar resultados
    if dataframes:
        save_to_hdf5(HDF5_FILE, dataframes)
    else:
        print("⚠️ No se obtuvieron datos de ninguna URL.")

if __name__ == "__main__":
    main()
