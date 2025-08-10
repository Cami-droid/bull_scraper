from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def clean_numeric_value(value):
    """Convierte un valor string con comas/puntos a float."""
    if value is None:
        return None
    value = value.replace('.', '').replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return None

def extract_dashboard_data(driver, url):
    """
    Extrae precios del dólar y otros datos del dashboard.
    Retorna un DataFrame con fecha_cotizacion.
    """
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    data = {}

    # Ejemplo: buscar elementos por clase o id (ajustar a HTML real del dashboard)
    # Suponga que los precios están en <span class="dashboard-price" data-name="Dólar MEP">
    # Debemos adaptar estas líneas según la estructura real
    for item in soup.select('.dashboard-price'):
        nombre = item.get('data-name', '').strip()
        valor = clean_numeric_value(item.text.strip())
        if nombre:
            data[nombre] = valor

    # Convertir a DataFrame
    df = pd.DataFrame([data])
    df['fecha_cotizacion'] = datetime.now().strftime('%Y-%m-%d')

    return df
