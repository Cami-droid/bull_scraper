import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

# Asegúrate de importar esta función si la tienes en utils.py
# from utils import wait_for_element 

def clean_numeric_value(value):
    """Limpia el texto de un valor y lo convierte a float."""
    if not isinstance(value, str):
        return None
    value = value.replace('.', '').replace(',', '.')
    # Extraer solo el número si hay otros caracteres como el signo de pesos
    value = value.replace('$', '').strip()
    try:
        return float(value)
    except ValueError:
        return None

def extract_dashboard_data(driver, url):
    try:
        driver.get(url)
        
        # 🟢 Estos son los nuevos selectores para la estructura actual del dashboard
        selectors = {
            "Dolar_MEP_Compra": "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(1) > a > span:nth-child(1)",
            "Dolar_MEP_Venta": "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(2) > a",
            "Dolar_CCL": "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > span:nth-child(1)",
            "Dolar_Cable": "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(3) > div:nth-child(3) > span:nth-child(1)"
        }

        data = {}
        print("Extrayendo valores del dashboard...")

        # Usamos una única espera general para asegurar que al menos un elemento esté visible
        try:
            WebDriverWait(driver, 20).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, selectors['dolar_mep_compra']), "$")
            )
        except TimeoutException:
            print("⚠️ Timeout: Los datos del dólar MEP/CCL no se cargaron a tiempo. Se capturan como 'None'.")
            for name in selectors.keys():
                data[name] = None
            df = pd.DataFrame([data])
            df['fecha_scraping'] = datetime.now()
            return df
        
        # Si la espera general fue exitosa, procedemos a extraer todos los valores
        for name, selector in selectors.items():
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
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