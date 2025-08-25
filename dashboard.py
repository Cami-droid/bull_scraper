import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import re

def clean_numeric_value(value):
    """Limpia el texto de un valor y lo convierte a float."""
    if not isinstance(value, str):
        return None
    value = value.replace('.', '').replace(',', '.')
    value = value.replace('$', '').strip()
    try:
        return float(value)
    except ValueError:
        return None

def extract_dashboard_data(driver, dashboard_url, cookies):
    print(f"\nNavegando al Dashboard: {dashboard_url}")
    
    try:
        # Primero, vamos a una URL base del dominio para poder inyectar cookies
        driver.get("https://www.bullmarketbrokers.com/")

        # Inyectar las cookies de sesión capturadas
        for cookie in cookies:
            cookie_copy = cookie.copy()
            if 'domain' in cookie_copy: del cookie_copy['domain']
            if 'expiry' in cookie_copy: del cookie_copy['expiry']
            if 'expires' in cookie_copy: del cookie_copy['expires']
            try:
                driver.add_cookie(cookie_copy)
            except Exception:
                pass

        # Ahora, ir al dashboard con la sesión activa
        driver.get(dashboard_url)
        
        selectors = {
            "Dolar_MEP_Compra": "/html/body/div[2]/div/div[4]/div[2]/div[1]/div[1]/a/span[1]",
            "Dolar_MEP_Venta": "/html/body/div[2]/div/div[4]/div[2]/div[1]/div[2]/a",
            "Dolar_CCL": "/html/body/div[2]/div/div[4]/div[1]/div[5]/div[2]/div[2]/h4/a/span",
            "Dolar_Cable": "/html/body/div[2]/div/div[4]/div[1]/div[5]/div[2]/div[3]/h4/a[2]/span"
        }

        data = {}
        print("Extrayendo valores del dashboard...")

        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, selectors['Dolar_MEP_Compra']))
            )
        except TimeoutException:
            print("⚠️ Timeout: Los datos del dólar MEP/CCL no se cargaron a tiempo. Se capturan como 'None'.")
            for name in selectors.keys():
                data[name] = None
            df = pd.DataFrame([data])
            df['fecha_scraping'] = datetime.now()
            return df
        
        for name, selector in selectors.items():
            try:
                element = driver.find_element(By.XPATH, selector)
                data[name] = clean_numeric_value(element.text)
                print(f"  ✔️ {name}: {data[name]}")
            except NoSuchElementException:
                print(f"  ❗ Error: El selector para '{name}' no fue encontrado.")
                data[name] = None

        df = pd.DataFrame([data])
        df['fecha_scraping'] = datetime.now()
        return df

    except Exception as e:
        print(f"❌ ERROR: Fallo al extraer datos. Error: {e}")
        return pd.DataFrame()