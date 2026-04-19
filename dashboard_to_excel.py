import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import re
from datetime import datetime

from config import BMB_USERNAME, BMB_PASSWORD, CHROMEDRIVER_PATH, LOGIN_URL, DASHBOARD_URL, OUTPUT_DIR
from login import perform_login  # ← reutilizamos el login central

# ─── CONFIGURACIÓN DE ARCHIVOS DE SALIDA ─────────────────────────────────────
EXCEL_ACCUMULATED_FILE = os.path.join(OUTPUT_DIR, "dolar_acumulado.xlsx")
HDF5_ACCUMULATED_FILE  = os.path.join(OUTPUT_DIR, "dolar_acumulado.h5")
HDF5_DASHBOARD_KEY     = "/cotizaciones_dolar"
# ─────────────────────────────────────────────────────────────────────────────


def clean_numeric_value(text):
    """Extrae el primer número válido de un string con formato argentino."""
    if text is None:
        return None
    match = re.search(r'[-]?\d[\d\.,]*', text)
    if match:
        numeric_part = match.group(0)
        cleaned = numeric_part.replace('.', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def extract_dashboard_data(driver, dashboard_url, cookies):
    """Navega al dashboard e extrae las cotizaciones del dólar."""
    print("📊 Extrayendo datos del dashboard...")
    try:
        driver.get("https://www.bullmarketbrokers.com/")
        for cookie in cookies:
            cookie_copy = cookie.copy()
            for key in ('domain', 'expiry', 'expires'):
                cookie_copy.pop(key, None)
            try:
                driver.add_cookie(cookie_copy)
            except Exception:
                pass

        driver.get(dashboard_url)

        selectors = {
            "dolar_mep_compra": "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(1) > a > span:nth-child(1)",
            "dolar_mep_venta":  "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(2) > a",
            "dolar_mep":        "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > span:nth-child(1)",
            "dolar_cable_ccl":  "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(3) > div:nth-child(3) > span:nth-child(1)",
        }

        data = {}
        for name, selector in selectors.items():
            try:
                element = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                data[name] = clean_numeric_value(element.text)
                print(f"  ✔️  {name}: {data[name]}")
            except TimeoutException:
                print(f"  ⚠️  Timeout: no se encontró '{name}'")
                data[name] = None
            except NoSuchElementException:
                print(f"  ⚠️  Elemento no encontrado: '{name}'")
                data[name] = None

        df = pd.DataFrame([data])
        df['fecha_scraping'] = pd.Timestamp(datetime.now()).as_unit('us')
        df['diferencia_mep_ccl'] = (df['dolar_mep'] - df['dolar_cable_ccl']).round(2)
        return df

    except Exception as e:
        print(f"❌ Error al extraer datos del dashboard: {e}")
        return pd.DataFrame()


# ─── EJECUCIÓN PRINCIPAL ──────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(CHROMEDRIVER_PATH):
        print("❌ Chromedriver no encontrado.")
        exit()

    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver  = webdriver.Chrome(service=service)

    try:
        cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)
        if not cookies:
            print("❌ Login fallido. Saliendo.")
            driver.quit()
            exit()

        df_dashboard = extract_dashboard_data(driver, DASHBOARD_URL, cookies)

        if df_dashboard is not None and not df_dashboard.empty:
            print("\n✔️  Datos extraídos:")
            print(df_dashboard)

            os.makedirs(OUTPUT_DIR, exist_ok=True)

            # ── Guardar HDF5 ─────────────────────────────────────────────
            print(f"💾 Guardando en HDF5: {HDF5_ACCUMULATED_FILE}")
            try:
                # Forzar datetime64[us] para compatibilidad con HDFStore format='table'
                df_dashboard['fecha_scraping'] = df_dashboard['fecha_scraping'].astype('datetime64[us]')
                with pd.HDFStore(HDF5_ACCUMULATED_FILE, mode='a', complib='blosc', complevel=9) as store:
                    store.put(HDF5_DASHBOARD_KEY, df_dashboard, format='table', append=True, data_columns=True)
                print("  ✔️  HDF5 guardado.")
            except Exception as e:
                print(f"  ❌  Error HDF5: {e}")

            # ── Guardar Excel ────────────────────────────────────────────
            print(f"💾 Guardando en Excel: {EXCEL_ACCUMULATED_FILE}")
            try:
                if os.path.exists(EXCEL_ACCUMULATED_FILE):
                    existing_df  = pd.read_excel(EXCEL_ACCUMULATED_FILE)
                    combined_df  = pd.concat([existing_df, df_dashboard], ignore_index=True)
                else:
                    combined_df = df_dashboard

                combined_df.to_excel(EXCEL_ACCUMULATED_FILE, index=False)
                print("  ✔️  Excel guardado.")
            except Exception as e:
                print(f"  ❌  Error Excel: {e}")
        else:
            print("❌ No se pudieron extraer los datos del dashboard.")

    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")
    finally:
        driver.quit()