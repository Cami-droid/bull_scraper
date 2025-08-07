from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime
from .utils import sanitize_column_names

def extract_table(driver, url, cookies):
    driver.get("https://www.bullmarketbrokers.com/Clients/Dashboard")
    for cookie in cookies:
        cookie = {k: v for k, v in cookie.items() if k not in ['domain', 'expiry', 'expires']}
        try: driver.add_cookie(cookie)
        except: continue
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "prices-table")))
        time.sleep(2)  # por si acaso
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', id='prices-table')
        if table:
            df = pd.read_html(str(table))[0]
            df['Tipo_Tabla'] = url.split('/')[-1].replace('%20', ' ')
            df['Fecha_Cotizacion'] = datetime.now().strftime('%Y-%m-%d')
            return sanitize_column_names(df)
        return None
    except:
        return None
