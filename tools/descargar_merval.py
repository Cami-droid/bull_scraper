
import pandas as pd
from bs4 import BeautifulSoup
import os

# --- Parámetros de la Tarea ---
ARCHIVO_HTML_COPIADO = 'merval.csv' 
# HELP: #tenes que guardar "Copy Element" en inspeccionar de la tabla de esta pagina https://finance.yahoo.com/quote/%5EMERV/history/
OUTPUT_CSV_FINAL = 'merval_data_final_formato_fecha.csv'

if not os.path.exists(ARCHIVO_HTML_COPIADO):
    print(f"❌ Error: No se encuentra el archivo local: '{ARCHIVO_HTML_COPIADO}'.")
    exit()

print(f"Iniciando extracción y formateo de fechas del fragmento HTML en '{ARCHIVO_HTML_COPIADO}'...")

try:
    # 1. Leer el contenido del archivo local
    with open(ARCHIVO_HTML_COPIADO, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 2. Analizar el contenido HTML y extraer datos (mismo proceso)
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr')
    
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 7:
            extracted_data = [ele.text.strip() for ele in cols]
            data.append(extracted_data)

    if not data:
        print("❌ No se encontraron datos válidos (filas de 7 columnas).")
        exit()

    # 3. Crear el DataFrame
    column_names = ['Fecha', 'Apertura', 'Máximo', 'Mínimo', 'Cierre', 'Cierre_Ajustado', 'Volumen']
    df = pd.DataFrame(data, columns=column_names)
    
    # 4. Limpieza de Precios (misma que antes)
    for col in ['Apertura', 'Máximo', 'Mínimo', 'Cierre', 'Cierre_Ajustado', 'Volumen']:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 5. CONVERSIÓN Y FORMATO DE FECHA CLAVE:
    # a) Convertir la columna 'Fecha' a un objeto datetime de pandas
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # b) Formatear la columna 'Fecha' al formato deseado YYYY-MM-DD (ISO 8601)
    # .dt.strftime('%Y-%m-%d') aplica el formato de string deseado.
    df['Fecha'] = df['Fecha'].dt.strftime('%Y-%m-%d')


    # 6. Guardar el archivo limpio
    # La fecha se guarda sin comillas si el DataFrame no requiere una cotización estricta (que es el default)
    df.to_csv(OUTPUT_CSV_FINAL, index=False)

    print("-" * 50)
    print(f"✅ ¡Éxito! Datos extraídos y guardados en '{OUTPUT_CSV_FINAL}'")
    print(f"Formato de fecha aplicado: YYYY-MM-DD.")
    print(f"Primeras fechas del archivo:\n{df['Fecha'].head()}")
    print("-" * 50)
    
except Exception as e:
    print(f"Ocurrió un error inesperado durante el procesamiento del archivo: {e}")