from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
from login import perform_login
from scraper import extract_table
from storage import save_to_hdf5
from dashboard import extract_dashboard_data
from utils import sanitize_column_names
import os
import time

def main():
    try:
        if not os.path.exists(CHROMEDRIVER_PATH):
            print("❌ Chromedriver no encontrado.")
            return

        service = ChromeService(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service)

        print("\nIniciando proceso de autenticación...")
        cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)

        if not cookies:
            print("❌ Login fallido o no se obtuvieron cookies. Saliendo del script.")
            return

        dataframes = {}

        # 🔹 Extraer dashboard
        print("📊 Extrayendo datos del dashboard...")
        # NOTA: Se está usando un archivo que proporcionaste anteriormente, "dashboard_to_excel.py", para la lógica.
        # Por lo tanto, la siguiente línea se deja como estaba, pero ten en cuenta que la lógica del dashboard ya está en tu otro script.
        df_dashboard = extract_dashboard_data(driver, "https://www.bullmarketbrokers.com/Clients/Dashboard", cookies)
        if df_dashboard is not None and not df_dashboard.empty:
            df_dashboard = sanitize_column_names(df_dashboard)
            dataframes['dashboard'] = df_dashboard
            print("✔️ Datos del dashboard extraídos exitosamente.")
            print(df_dashboard)
        else:
            print("❌ No se pudieron extraer los datos del dashboard.")

        # 🔹 Extraer otras tablas
        for url in URLS:
            nombre_tabla = url.split("/")[-1].replace('%20', ' ')
            
            # --- Lógica específica para la tabla de cauciones ---
            if 'cauciones' in url:
                print(f"📥 Procesando la tabla de cauciones (pesos)...")
                
                # Extraer la tabla de cauciones en pesos
                df_pesos = extract_table(driver, url, cookies)
                if df_pesos is not None and not df_pesos.empty:
                    df_pesos = sanitize_column_names(df_pesos)
                    dataframes[f'{nombre_tabla}_pesos'] = df_pesos
                    print(f"✔️ Tabla '{nombre_tabla}' en pesos extraída. Dimensiones: {df_pesos.shape}")
                else:
                    print(f"❌ No se pudo extraer la tabla '{nombre_tabla}' en pesos.")

                # Cambiar a la vista de Dólares haciendo clic en el botón
                print("🔄 Cambiando a la vista de Dólares...")
                try:
                    boton_dolares = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "#panelFilters > div > div > div > div > div.filter-group > ul > li:nth-child(2) > button"))
                    )
                    boton_dolares.click()
                    time.sleep(3) # Pausa para que la tabla se cargue
                    print("✔️ Botón 'Dólares' clickeado.")

                    # Extraer la tabla de cauciones en dólares
                    print(f"📥 Procesando la tabla de cauciones (dólares)...")
                    # Se asume que extract_table puede ser llamada sin URL si el driver ya está en la página correcta
                    df_dolar = extract_table(driver, url, cookies)
                    if df_dolar is not None and not df_dolar.empty:
                        df_dolar = sanitize_column_names(df_dolar)
                        dataframes[f'{nombre_tabla}_dolar'] = df_dolar
                        print(f"✔️ Tabla '{nombre_tabla}' en dólares extraída. Dimensiones: {df_dolar.shape}")
                    else:
                        print(f"❌ No se pudo extraer la tabla '{nombre_tabla}' en dólares.")
                except Exception as e:
                    print(f"❗ Error al intentar extraer la tabla de cauciones en dólares: {e}")

            # --- Lógica para el resto de tablas ---
            else:
                print(f"📥 Procesando: {nombre_tabla}")
                df = extract_table(driver, url, cookies)
                if df is not None and not df.empty:
                    df = sanitize_column_names(df)
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
        driver.quit()

if __name__ == "__main__":
    main()