import os
from dotenv import load_dotenv

load_dotenv()

BMB_USERNAME = os.getenv("BMB_USERNAME")
BMB_PASSWORD = os.getenv("BMB_PASSWORD")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
LOGIN_URL = "https://bullmarketbrokers.com/Security/SignIn"

HDF5_FILE = "cotizaciones_bullmarket_acumulado.h5"

URLS = [
    "https://www.bullmarketbrokers.com/Cotizaciones/merval",
    # ...
]
