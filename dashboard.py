from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def clean_numeric_value(value):
    """
    Convierte un valor string con comas/puntos a float.
    Maneja la lógica de limpieza en un solo lugar.
    """
    if not isinstance(value, str):
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

    # ❗️ Estos son los selectores que extraen los valores del dólar.
    #    Basado en tu log, los selectores de la "prehistoria" siguen funcionando.
    #    Los he hecho más explícitos para facilitar su mantenimiento.
    #    Si la página cambia, esta es la única sección que deberás actualizar.
    try:
        data = {
            'Dolar_MEP_Compra': soup.select_one('#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(1) > a > span:nth-child(1)').text,
            'Dolar_MEP_Venta': soup.select_one('#div_home_index > div.col-md-4 > div:nth-child(1) > div:nth-child(2) > a > span:nth-child(1)').text,
            'Dolar_CCL': soup.select_one('#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > span:nth-child(1)').text,
            'Dolar_Cable': soup.select_one('#div_home_index > div.col-md-8 > div.logged-pill.pull-left.fullWidth.money-resume > div:nth-child(2) > div:nth-child(3) > div:nth-child(2) > span:nth-child(1)').text
        }
        
        # Procesa y limpia los datos numéricos
        processed_data = {
            key: clean_numeric_value(value) 
            for key, value in data.items()
        }

        # Verifica si todos los valores se extrajeron correctamente
        if any(value is None for value in processed_data.values()):
            print("❌ ALERTA: Algunos valores del dólar no se encontraron. La página pudo haber cambiado.")
            # Si un valor no se encuentra, la clave queda en el diccionario. Se guarda lo que se pudo.
        
        df = pd.DataFrame([processed_data])
        
    except Exception as e:
        print(f"❌ ERROR: Fallo al extraer los datos del dashboard. Revisa los selectores. Error: {e}")
        df = pd.DataFrame()

    df['Fecha_Cotizacion'] = datetime.now().strftime('%Y-%m-%d')
    
    return df