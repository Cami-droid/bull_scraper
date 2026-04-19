import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils import sanitize_column_names
from datetime import datetime

def extract_table(driver, url=None, cookies=None, is_loaded=False):
    """
    Extrae una tabla de una URL o de la página ya cargada.
    Los valores se capturan como texto crudo desde el HTML, sin conversión de pandas,
    preservando el formato original de cada celda (ej: "5.109", "ARS 107,88").
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

        # Esperar a que la tabla exista en el DOM
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "prices-table"))
        )

        # Esperar a que haya al menos una fila con datos reales (JS terminó de renderizar)
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#prices-table tbody tr[data-key]")) > 0
        )

        # Leer el HTML directo del elemento del DOM
        table_element = driver.find_element(By.ID, "prices-table")
        table_html = table_element.get_attribute("outerHTML")

        # Usar read_html para obtener estructura y nombres de columnas correctos
        from io import StringIO
        df = pd.read_html(StringIO(table_html))[0]

        # Reemplazar valores con textos crudos de BeautifulSoup (preserva "5.109", "ARS 107,88", etc.)
        soup = BeautifulSoup(table_html, 'html.parser')
        raw_rows = []
        for tr in soup.select('tbody tr[data-key]'):
            cells = [td.get_text(strip=True) for td in tr.find_all('td')]
            raw_rows.append(cells)

        if raw_rows and len(raw_rows[0]) == len(df.columns):
            df = pd.DataFrame(raw_rows, columns=df.columns)
        else:
            # fallback: columnas no coinciden, usar read_html con astype str
            df = df.astype(str)

        df['fecha_scraping'] = pd.Timestamp(datetime.now())

        return df

    except TimeoutException:
        print("❗ Tiempo de espera agotado. La tabla no se encontró.")
        return None
    except Exception as e:
        print(f"❌ Error al extraer la tabla: {e}")
        return None