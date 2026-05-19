import os
from dotenv import load_dotenv

load_dotenv()

# Credenciales y configuración de Selenium
BMB_USERNAME = os.getenv("BMB_USERNAME")
BMB_PASSWORD = os.getenv("BMB_PASSWORD")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
LOGIN_URL = "https://inversiones.bullmarket.com.ar/Security/SignIn"
# "https://bullmarketbrokers.com/Security/SignIn"
DASHBOARD_URL = "https://inversiones.bullmarket.com.ar/clients/dashboard/"
# "https://www.bullmarketbrokers.com/Clients/Dashboard"
CAUCIONES_URL = "https://inversiones.bullmarket.com.ar/Cotizaciones/cauciones"
# "https://www.bullmarketbrokers.com/Cotizaciones/cauciones"



# Configuración de almacenamiento HDF5
HDF5_FILE = "cotizaciones_bullmarket_acumulado.h5"
OUTPUT_DIR = "data/hdf5_dumps"  # Carpeta para archivos HDF5 diarios
ACCUMULATE = False  # True para acumular en archivo histórico, False para solo diarios

# URLs de extracción
URLS = [
    "https://inversiones.bullmarket.com.ar/Cotizaciones/merval",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/panel%20general",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/cedears",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/bonos",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/opciones",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/letras",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/rofex",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/licitaciones",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/fondos",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/fideicomisos",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/cauciones",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/obligacionesNegociables",
    "https://inversiones.bullmarket.com.ar/Cotizaciones/US"
]