Hay que activar venv primero (está en llegar.bat el camino para hacerlo)
Hay que poner python main.py
El tipo empieza a scrapear tablas y mandarlas a h5
podés usar verificar si querés ver si se descargó todo como corresponde

Scraper de Datos de Bull Market Brokers
Este proyecto es un scraper de datos automatizado diseñado para extraer información de la plataforma de Bull Market Brokers, incluyendo el dashboard y varias tablas de datos, y luego guardar esta información en un archivo HDF5 para su posterior análisis.

⚙️ Requisitos
Para que este script funcione correctamente, necesitas tener instalado lo siguiente:

Python 3.x

Selenium: Para la automatización del navegador.

Pandas: Para la manipulación de datos.

xlrd: Mencionada en nuestra conversación previa. A pesar de que el código no lo usa directamente, es una dependencia común para el manejo de datos tabulares, especialmente si se trabaja con formatos Excel en el futuro.

h5py o similar: Para la gestión del archivo HDF5.

chromedriver: Un ejecutable de Chromedriver que corresponda a la versión de tu navegador Chrome.

🚀 Instalación y Configuración
Clona este repositorio:

Bash

git clone https://github.com/tu-usuario/nombre-del-proyecto.git
cd nombre-del-proyecto
Crea un entorno virtual:

Bash

python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
Instala las dependencias de Python:

Bash

pip install selenium pandas
Descarga chromedriver:

Asegúrate de descargar la versión de chromedriver que coincida con la de tu navegador Chrome.

Coloca el archivo chromedriver en una ruta accesible y actualiza la variable CHROMEDRIVER_PATH en el archivo config.py.

Configura las credenciales:

Crea un archivo config.py y añade tus credenciales de Bull Market Brokers y las URLs de las tablas a extraer.

Asegúrate de no subir este archivo a un repositorio público.

Python

# config.py
BMB_USERNAME = "tu_usuario"
BMB_PASSWORD = "tu_contraseña"
LOGIN_URL = "https://www.bullmarketbrokers.com/Clients/Login"
HDF5_FILE = "datos_bullmarket.h5"
CHROMEDRIVER_PATH = "/ruta/a/tu/chromedriver"
URLS = [
    "https://www.bullmarketbrokers.com/Clients/Portfolio/Resumen",
    "https://www.bullmarketbrokers.com/Clients/Portfolio/Historico"
    # Agrega aquí las URLs de las tablas que quieras extraer
]
🛠️ Uso
Para ejecutar el script y empezar a extraer datos, simplemente ejecuta el archivo principal:

Bash

python main.py
El programa iniciará el navegador, se logueará, extraerá los datos del dashboard y de las URLs especificadas, y finalmente guardará toda la información en el archivo HDF5 definido en config.py.

📁 Estructura del Proyecto
main.py: Punto de entrada del programa. Orquesta el proceso de login, scraping y almacenamiento.

login.py: Contiene la lógica para iniciar sesión en la plataforma.

scraper.py: Contiene la lógica para extraer las tablas de datos.

dashboard.py: Contiene la lógica específica para extraer la información del dashboard.

storage.py: Se encarga de guardar los dataframes extraídos en formato HDF5.

config.py: Archivo de configuración para las credenciales, URLs y rutas.

README.md: Este archivo, con la documentación del proyecto.
