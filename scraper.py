import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from utils import sanitize_column_names # Asegúrate de tener esta función en tu archivo utils.py

def extract_table(driver, url=None, cookies=None, is_loaded=False):
    """
    Extrae una tabla de una URL o de la página ya cargada.

    Args:
        driver (webdriver): La instancia del WebDriver de Selenium.
        url (str, opcional): La URL de la página a scrapear. Si es None, no recarga la página.
        cookies (list, opcional): Lista de cookies para la sesión.
        is_loaded (bool): Si True, asume que la URL ya está cargada y no la recarga.
    """
    try:
        # Si la URL no está cargada, navega e inyecta las cookies
        if not is_loaded and url:
            print(f"🌍 Navegando a la URL: {url}")
            driver.get("https://www.bullmarketbrokers.com/")
            if cookies:
                for cookie in cookies:
                    cookie_copy = cookie.copy()
                    if 'domain' in cookie_copy: del cookie_copy['domain']
                    if 'expiry' in cookie_copy: del cookie_copy['expiry']
                    if 'expires' in cookie_copy: del cookie_copy['expires']
                    try:
                        driver.add_cookie(cookie_copy)
                    except Exception:
                        pass
            driver.get(url)

        # Espera a que la tabla esté presente antes de intentar extraerla
        # Ahora usamos el ID que me proporcionaste, lo que lo hace más fiable
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "prices-table"))
        )
        
        # Lee la tabla con pandas
        df_list = pd.read_html(driver.page_source, attrs={'id': 'prices-table'})
        df = df_list[0]
        
        return df

    except TimeoutException:
        print("❗ Tiempo de espera agotado. La tabla no se encontró.")
        return None
    except Exception as e:
        print(f"❌ Error al extraer la tabla: {e}")
        return None
