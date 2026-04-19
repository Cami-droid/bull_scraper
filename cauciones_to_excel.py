import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
from datetime import datetime
import re
from config import BMB_USERNAME, BMB_PASSWORD, CHROMEDRIVER_PATH, LOGIN_URL, CAUCIONES_URL, OUTPUT_DIR

# --- CONFIGURACIÓN DE ARCHIVOS DE SALIDA ---
EXCEL_ACCUMULATED_FILE = os.path.join(OUTPUT_DIR, "cauciones_acumulado.xlsx")
HDF5_ACCUMULATED_FILE = os.path.join(OUTPUT_DIR, "cauciones_acumulado.h5")
HDF5_CAUCIONES_KEY = "/tasas_cauciones"
# --- FIN DE CONFIGURACIÓN ---

def clean_numeric_value(text):
    """Convierte un texto como '95,50%' en float 95.5"""
    if text is None:
        return None
    match = re.search(r'[-]?\d[\d\.,]*', text)
    if match:
        numeric_part = match.group(0)
        cleaned_text = numeric_part.replace('.', '').replace(',', '.')
        try:
            return float(cleaned_text)
        except ValueError:
            return None
    return None

def perform_login(driver, username, password, login_url):
    print(f"🌍 Navegando a la página de login: {login_url}")
    driver.get(login_url)

    try:
        email_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "Email"))
        )
        email_field.send_keys(username)

        password_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "Password"))
        )
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "submitButton"))
        )
        login_button.click()

        WebDriverWait(driver, 30).until(
            EC.url_contains("/Clients/Dashboard")
        )
        print(f"✅ Login exitoso. URL actual: {driver.current_url}")

        return driver.get_cookies()

    except TimeoutException:
        print("❗ ERROR: Tiempo de espera agotado para el login.")
        return None
    except Exception as e:
        print(f"❗ ERROR al intentar iniciar sesión: {e}")
        return None

def extract_cauciones_rates(driver, cauciones_url, cookies):
    print("📊 Extrayendo tasas de cauciones (ARS / USD)...")
    driver.get("https://www.bullmarketbrokers.com/")
    for c in cookies:
        c = c.copy()
        for k in ("domain", "expiry", "expires"): c.pop(k, None)
        try: driver.add_cookie(c)
        except: pass
    driver.get(cauciones_url)

    # 1️⃣ Ver si la tabla aparece
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#prices-table")))
    except TimeoutException:
        print("⚠️ Tabla no visible, aplicando empujón...")
        driver.execute_script("document.querySelector('#div_priceActives > div > label').click();")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#prices-table")))

    data = {}

    # 2️⃣ Extraer tasa en pesos
    try:
        tna_ars = driver.find_element(By.CSS_SELECTOR, "#prices-table tbody tr:nth-child(1) td:nth-child(2)").text
        data["caucion_tna_ars"] = clean_numeric_value(tna_ars)
    except Exception as e:
        print("❗ No se pudo leer caución ARS:", e)
        data["caucion_tna_ars"] = None

    # 3️⃣ Cambiar a dólares y extraer
    try:
        boton_dolares = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#panelFilters li:nth-child(2) button"))
        )
        boton_dolares.click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#prices-table")))
        tna_usd = driver.find_element(By.CSS_SELECTOR, "#prices-table tbody tr:nth-child(1) td:nth-child(2)").text
        data["caucion_tna_usd"] = clean_numeric_value(tna_usd)
    except Exception as e:
        print("❗ No se pudo leer caución USD:", e)
        data["caucion_tna_usd"] = None

    df = pd.DataFrame([data])
    df['fecha_scraping'] = pd.Timestamp(datetime.now()).as_unit('us')

    return df


if __name__ == "__main__":
    if not os.path.exists(CHROMEDRIVER_PATH):
        print("❌ Chromedriver no encontrado.")
        exit()

    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    try:
        cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)
        if not cookies:
            print("❌ Login fallido. Saliendo.")
            driver.quit()
            exit()

        df_rates = extract_cauciones_rates(driver, CAUCIONES_URL, cookies)

        if not df_rates.empty:
            print("\n✔️ Tasas extraídas:")
            print(df_rates)

            os.makedirs(OUTPUT_DIR, exist_ok=True)

            # Guardar en HDF5
            try:
                df_rates['fecha_scraping'] = df_rates['fecha_scraping'].astype('datetime64[us]')
                with pd.HDFStore(HDF5_ACCUMULATED_FILE, mode="a", complib="blosc", complevel=9) as store:
                    store.put(HDF5_CAUCIONES_KEY, df_rates, format="table", append=True, data_columns=True)
                print("✔️ HDF5 guardado exitosamente.")
            except Exception as e:
                print(f"❗ Error al guardar en HDF5: {e}")

            # Guardar en Excel
            try:
                if os.path.exists(EXCEL_ACCUMULATED_FILE):
                    existing_df = pd.read_excel(EXCEL_ACCUMULATED_FILE)
                    combined_df = pd.concat([existing_df, df_rates], ignore_index=True)
                else:
                    combined_df = df_rates
                combined_df.to_excel(EXCEL_ACCUMULATED_FILE, index=False)
                print("✔️ Excel guardado exitosamente.")
            except Exception as e:
                print(f"❗ Error al guardar en Excel: {e}")
        else:
            print("\n❌ No se pudieron extraer tasas de cauciones.")

    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        driver.quit()