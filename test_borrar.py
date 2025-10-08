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

for url in URLS:
    if 'cauciones' in url:
        print("este url incluye la palabra cauciones")
    else:
        print("ya no")
    