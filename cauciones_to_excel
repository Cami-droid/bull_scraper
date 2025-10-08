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
from config import BMB_USERNAME, BMB_PASSWORD, CHROMEDRIVER_PATH, LOGIN_URL, DASHBOARD_URL, OUTPUT_DIR

# --- CONFIGURACIÓN DE ARCHIVOS DE SALIDA ---
EXCEL_ACCUMULATED_FILE = os.path.join(OUTPUT_DIR, "dolar_acumulado.xlsx")
HDF5_ACCUMULATED_FILE = os.path.join(OUTPUT_DIR, "dolar_acumulado.h5")
HDF5_DASHBOARD_KEY = "/cotizaciones_dolar"
# --- FIN DE CONFIGURACIÓN ---

# --- FUNCIÓN PARA LIMPIAR VALORES NUMÉRICOS ---
def clean_numeric_value(text):
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
    else:
        return None

# --- FUNCIÓN PARA EL LOGIN ---
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

# --- FUNCIÓN PARA EXTRAER DATOS DEL DASHBOARD ---
def extract_dashboard_data(driver, dashboard_url, cookies):
    print(f"📊 Extrayendo datos del dashboard...")
    try:
        driver.get("https://www.bullmarketbrokers.com/")
        for cookie in cookies:
            cookie_copy = cookie.copy()
            if 'domain' in cookie_copy: del cookie_copy['domain']
            if 'expiry' in cookie_copy: del cookie_copy['expiry']
            if 'expires' in cookie_copy: del cookie_copy['expires']
            try:
                driver.add_cookie(cookie_copy)
            except Exception:
                pass

        driver.get(dashboard_url)
        
        # Selectores actualizados con los nombres de columna corregidos
        selectors = {
            "dolar_mep_compra": "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(1) > a > span:nth-child(1)",
            "dolar_mep_venta": "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(2) > a",
            "dolar_mep": "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > span:nth-child(1)",
            "dolar_cable_ccl": "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(3) > div:nth-child(3) > span:nth-child(1)"
        }
        
        data = {}
        print("Extrayendo valores del dashboard...")
        
        for name, selector in selectors.items():
            try:
                element = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                data[name] = clean_numeric_value(element.text)
                print(f"  ✔️ {name}: {data[name]}")
            except TimeoutException:
                print(f"  ❗ Timeout: No se encontró el elemento para '{name}'")
                data[name] = None
            except NoSuchElementException:
                print(f"  ❗ Error: El elemento para '{name}' no fue encontrado.")
                data[name] = None
                
        df = pd.DataFrame([data])
        df['fecha_scraping'] = datetime.now()
        
        return df

    except Exception as e:
        print(f"❌ ERROR: Fallo al extraer datos. Error: {e}")
        return pd.DataFrame()

# --- BLOQUE DE EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    if not os.path.exists(CHROMEDRIVER_PATH):
        print("❌ Chromedriver no encontrado.")
        exit()
        
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    try:
        cookies = perform_login(driver, BMB_USERNAME, BMB_PASSWORD, LOGIN_URL)
        if not cookies:
            print("❌ Login fallido o no se obtuvieron cookies. Saliendo del script.")
            driver.quit()
            exit()
            
        df_dashboard = extract_dashboard_data(driver, DASHBOARD_URL, cookies)

        if df_dashboard is not None and not df_dashboard.empty:
            print("\n✔️ Misión completada con éxito. Datos extraídos:")
            print(df_dashboard)

            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            print(f"💾 Guardando datos en HDF5: {HDF5_ACCUMULATED_FILE}")
            try:
                with pd.HDFStore(HDF5_ACCUMULATED_FILE, mode='a', complib='blosc', complevel=9) as store:
                    store.put(HDF5_DASHBOARD_KEY, df_dashboard, format='table', append=True, data_columns=True)
                print("✔️ HDF5 guardado exitosamente.")
            except Exception as e:
                print(f"❗ Error al guardar en HDF5: {e}")
            
            print(f"💾 Guardando datos en Excel: {EXCEL_ACCUMULATED_FILE}")
            try:
                if os.path.exists(EXCEL_ACCUMULATED_FILE):
                    existing_df = pd.read_excel(EXCEL_ACCUMULATED_FILE)
                    combined_df = pd.concat([existing_df, df_dashboard], ignore_index=True)
                else:
                    combined_df = df_dashboard
                
                combined_df.to_excel(EXCEL_ACCUMULATED_FILE, index=False)
                print("✔️ Excel guardado exitosamente.")
            except Exception as e:
                print(f"❗ Error al guardar en Excel: {e}")
        else:
            print("\n❌ Misión fallida. No se pudieron extraer los datos del dashboard.")
            
    except Exception as e:
        print(f"❌ Error en la ejecución de la misión: {e}")
    finally:
        driver.quit()