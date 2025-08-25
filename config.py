import os
from dotenv import load_dotenv

load_dotenv()

# Credenciales y configuración de Selenium
BMB_USERNAME = os.getenv("BMB_USERNAME")
BMB_PASSWORD = os.getenv("BMB_PASSWORD")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
LOGIN_URL = "https://bullmarketbrokers.com/Security/SignIn"
DASHBOARD_URL = "https://www.bullmarketbrokers.com/Clients/Dashboard"


# Configuración de almacenamiento HDF5
HDF5_FILE = "cotizaciones_bullmarket_acumulado.h5"
OUTPUT_DIR = "data/hdf5_dumps"  # Carpeta para archivos HDF5 diarios
ACCUMULATE = False  # True para acumular en archivo histórico, False para solo diarios

# URLs de extracción
URLS = [
    "https://www.bullmarketbrokers.com/Cotizaciones/merval",
    "https://www.bullmarketbrokers.com/Cotizaciones/panel%20general",
    "https://www.bullmarketbrokers.com/Cotizaciones/cedears",
    "https://www.bullmarketbrokers.com/Cotizaciones/bonos",
    "https://www.bullmarketbrokers.com/Cotizaciones/opciones",
    "https://www.bullmarketbrokers.com/Cotizaciones/lebacs",
    "https://www.bullmarketbrokers.com/Cotizaciones/rofex",
    "https://www.bullmarketbrokers.com/Cotizaciones/licitaciones",
    "https://www.bullmarketbrokers.com/Cotizaciones/fondos",
    "https://www.bullmarketbrokers.com/Cotizaciones/cauciones",
    "https://www.bullmarketbrokers.com/Cotizaciones/obligacionesNegociables",
    "https://www.bullmarketbrokers.com/Cotizaciones/US"
]