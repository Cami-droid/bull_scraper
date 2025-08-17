from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

def clean_numeric_value(value):
    if not isinstance(value, str):
        return None
    value = value.replace('.', '').replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return None

def extract_dashboard_data(driver, url):
    try:
        driver.get(url)
        selectors = {
            "Dolar_MEP_Compra": "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(1) > a > span:nth-child(1)",
            "Dolar_MEP_Venta": "#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(2) > a",
            "Dolar_CCL": "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > span:nth-child(1)",
            "Dolar_Cable": "#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(3) > div:nth-child(3) > span:nth-child(1)"
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
            except:
                print(f"  ❗ Error al extraer '{name}'")
                data[name] = None

        df = pd.DataFrame([data])
        df['fecha_scraping'] = datetime.now()
        return df

    except Exception as e:
        print(f"❌ ERROR: Fallo al extraer datos. Error: {e}")
        return pd.DataFrame()