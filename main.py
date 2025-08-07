from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from config import *
from login import perform_login
from scraper import extract_table
from storage import save_to_hdf5
import os

def main():
    if not os.path.exists(CHROMEDRIVER_PATH):
        print("Chromedriver no encontrado.")
        return

    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)
    if not cookies:
        print("Login fallido.")
        driver.quit()
        return

    dataframes = {}
    for url in URLS:
        print(f"Procesando {url}")
        df = extract_table(driver, url, cookies)
        if df is not None:
            name = url.split("/")[-1].replace('%20', ' ')
            dataframes[name] = df

    driver.quit()
    if dataframes:
        save_to_hdf5(HDF5_FILE, dataframes)
        print(f"Tablas guardadas en {HDF5_FILE}")

if __name__ == "__main__":
    main()
