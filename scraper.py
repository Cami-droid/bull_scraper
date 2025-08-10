import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
from utils import sanitize_column_names

# 🔧 Cambiar a True para activar guardado de HTMLs debug
DEBUG = False

def extract_table(driver, url, cookies):
    """Extrae tabla de una URL de BullMarket con cookies de sesión."""
    
    # 1️⃣ Ir al dashboard antes de inyectar cookies
    driver.get("https://www.bullmarketbrokers.com/Clients/Dashboard")

    # 2️⃣ Inyectar cookies
    for cookie in cookies:
        cookie = {k: v for k, v in cookie.items() if k not in ['domain', 'expiry', 'expires']}
        try:
            driver.add_cookie(cookie)
        except:
            continue

    # 3️⃣ Cargar la URL real
    driver.get(url)

    # 4️⃣ Guardar HTML solo si DEBUG está activado
    html_path = None
    if DEBUG:
        html_path = os.path.join(os.getcwd(), f"debug_{url.split('/')[-1]}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[DEBUG] HTML guardado en {html_path}")

    try:
        # 5️⃣ Esperar la tabla
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "prices-table")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', id='prices-table')

        if table:
            df = pd.read_html(str(table))[0]
            df['Tipo_Tabla'] = url.split('/')[-1].replace('%20', ' ')
            df['fecha_cotizacion'] = datetime.now().strftime('%Y-%m-%d')
            
            # Eliminar el debug si está activado pero ya no se necesita
            if DEBUG and html_path and os.path.exists(html_path):
                os.remove(html_path)

            return sanitize_column_names(df)

        print(f"[DEBUG] No se encontró tabla en {url}")
        return None

    except Exception as e:
        print(f"[DEBUG] Error procesando {url}: {e}")
        return None

