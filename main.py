import logging
import os
import sys
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import *
from login import perform_login
from scraper import extract_table
from storage import save_to_hdf5
from utils import sanitize_column_names

# ─── ARCHIVO DE LOG (solo resumen) ───────────────────────────────────────────
timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_RESUMEN = f"log_resumen_{timestamp_str}.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_RESUMEN, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)
# ─────────────────────────────────────────────────────────────────────────────


def main():
    log.info("=" * 60)
    log.info("INICIO DE EJECUCIÓN")
    log.info(f"Python: {sys.version.split()[0]}")
    log.info(f"Directorio: {os.getcwd()}")
    log.info(f"CHROMEDRIVER_PATH: {CHROMEDRIVER_PATH}")
    log.info(f"BMB_USERNAME: {BMB_USERNAME}")
    log.info(f"URLs a procesar: {len(URLS)}")
    log.info("=" * 60)

    driver = None
    try:
        # ── ChromeDriver ──────────────────────────────────────────────────
        if not CHROMEDRIVER_PATH or not os.path.exists(CHROMEDRIVER_PATH):
            log.error(f"Chromedriver NO encontrado en: '{CHROMEDRIVER_PATH}'")
            return

        log.info("Iniciando Chrome...")
        service = ChromeService(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service)
        log.info("Chrome iniciado OK")

        # ── Login ─────────────────────────────────────────────────────────
        log.info("Iniciando login...")
        cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)

        if not cookies:
            log.error("Login FALLIDO — no se obtuvieron cookies.")
            return

        log.info(f"Login OK. Cookies obtenidas: {len(cookies)}")

        # 🔐 MFA — SACAR estas dos líneas si no pide verificación SMS/WhatsApp
        log.info("Esperando verificación MFA manual...")
        input("➡️  Presiona ENTER cuando hayas completado la verificación (SMS/WhatsApp)...")

        dataframes = {}

        # ── Iterar URLs ───────────────────────────────────────────────────
        for url in URLS:
            nombre_tabla = url.split("/")[-1].replace('%20', ' ')
            log.info("-" * 50)
            log.info(f"Procesando: {url}")

            # ── Cauciones ────────────────────────────────────────────────
            if 'cauciones' in url:
                log.info("Cauciones — extrayendo pesos...")
                df_pesos = extract_table(driver, url, cookies)

                if df_pesos is None or df_pesos.empty:
                    log.warning(f"[{nombre_tabla}_pesos] vacía — intentando rescate")
                    try:
                        driver.execute_script(
                            "document.querySelector('#div_priceActives > div > label').click();"
                        )
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "#prices-table"))
                        )
                        df_pesos = extract_table(driver, is_loaded=True)

                        if df_pesos is not None and not df_pesos.empty:
                            df_pesos = sanitize_column_names(df_pesos)
                            dataframes[f'{nombre_tabla}_pesos'] = df_pesos
                            log.info(f"[{nombre_tabla}_pesos] rescatada. Shape: {df_pesos.shape}")
                        else:
                            log.error(f"[{nombre_tabla}_pesos] falló incluso después del rescate.")
                    except Exception:
                        log.error(f"Excepción en rescate cauciones pesos:\n{traceback.format_exc()}")
                else:
                    df_pesos = sanitize_column_names(df_pesos)
                    dataframes[f'{nombre_tabla}_pesos'] = df_pesos
                    log.info(f"[{nombre_tabla}_pesos] OK. Shape: {df_pesos.shape}")

                # Cambiar a dólares
                log.info("Cambiando a vista Dólares...")
                try:
                    boton_dolares = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                            "#panelFilters > div > div > div > div > div.filter-group > ul > li:nth-child(2) > button"))
                    )
                    boton_dolares.click()
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "#prices-table"))
                    )
                    df_dolar = extract_table(driver, is_loaded=True)

                    if df_dolar is not None and not df_dolar.empty:
                        df_dolar = sanitize_column_names(df_dolar)
                        dataframes[f'{nombre_tabla}_dolar'] = df_dolar
                        log.info(f"[{nombre_tabla}_dolar] OK. Shape: {df_dolar.shape}")
                    else:
                        log.error(f"[{nombre_tabla}_dolar] vacía.")
                except Exception:
                    log.error(f"Excepción cauciones dólares:\n{traceback.format_exc()}")

            elif 'lebacs' in url:
                log.info("LEBACs...")
                df_lebacs = extract_table(driver, url, cookies)

                if df_lebacs is None or df_lebacs.empty:
                    log.warning(f"[{nombre_tabla}] vacía — intentando rescate")
                    try:
                        driver.execute_script(
                            "document.querySelector('#div_priceActives > div > label').click();"
                        )
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "#prices-table"))
                        )
                        df_lebacs = extract_table(driver, is_loaded=True)

                        if df_lebacs is not None and not df_lebacs.empty:
                            df_lebacs = sanitize_column_names(df_lebacs)
                            dataframes[nombre_tabla] = df_lebacs
                            log.info(f"[{nombre_tabla}] rescatada. Shape: {df_lebacs.shape}")
                        else:
                            log.error(f"[{nombre_tabla}] falló incluso después del rescate.")
                    except Exception:
                        log.error(f"Excepción rescate LEBACs:\n{traceback.format_exc()}")
                else:
                    df_lebacs = sanitize_column_names(df_lebacs)
                    dataframes[nombre_tabla] = df_lebacs
                    log.info(f"[{nombre_tabla}] OK. Shape: {df_lebacs.shape}")

            else:
                df = extract_table(driver, url, cookies)
                if df is not None and not df.empty:
                    df = sanitize_column_names(df)
                    dataframes[nombre_tabla] = df
                    log.info(f"[{nombre_tabla}] OK. Shape: {df.shape}")
                else:
                    log.error(f"[{nombre_tabla}] FALLÓ — tabla vacía o no encontrada.")

        # ── Guardar ───────────────────────────────────────────────────────
        log.info("-" * 50)
        if dataframes:
            tablas_ok = list(dataframes.keys())
            log.info(f"Tablas obtenidas ({len(tablas_ok)}): {tablas_ok}")
            save_to_hdf5(dataframes, output_dir=OUTPUT_DIR, accumulate=ACCUMULATE, hdf5_file=HDF5_FILE)
            log.info(f"Guardado en {OUTPUT_DIR}")
        else:
            log.warning("No se obtuvieron datos para guardar.")

    except Exception:
        log.critical(f"Error fatal:\n{traceback.format_exc()}")
    finally:
        if driver:
            driver.quit()
            log.info("Chrome cerrado.")
        log.info(f"Log resumen guardado en: {LOG_RESUMEN}")
        log.info("=== FIN ===")


if __name__ == "__main__":
    main()