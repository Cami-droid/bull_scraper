import pandas as pd
import re
import unicodedata
from collections import Counter
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# 🟢 CORRECTO: La importación de WebDriverWait debe ir aquí, al principio del archivo.
from selenium.webdriver.support.ui import WebDriverWait


def sanitize_column_names(df):
    replacements = {
        ' ': '_', '/': '_', '.': '_', '-': '_',
        '(': '', ')': '', '%': 'pct'
    }
    
    name_counts = Counter()
    new_columns = {}
    
    for col in df.columns:
        sane_col = col.lower()
        
        sane_col = ''.join(
            c for c in unicodedata.normalize('NFD', sane_col)
            if unicodedata.category(c) != 'Mn'
        )
        
        for old, new in replacements.items():
            sane_col = sane_col.replace(old, new)
        
        sane_col = re.sub(r'[^a-z0-9_]', '_', sane_col)
        
        sane_col = re.sub(r'_+', '_', sane_col).strip('_')
        
        if sane_col and sane_col[0].isdigit():
            sane_col = f"_{sane_col}"
        
        if not sane_col:
            sane_col = "columna_generica"
        
        if sane_col in name_counts:
            name_counts[sane_col] += 1
            sane_col = f"{sane_col}_{name_counts[sane_col]}"
        else:
            name_counts[sane_col] = 1
        
        new_columns[col] = sane_col
    
    return df.rename(columns=new_columns)
    
def wait_for_element(driver, locator, timeout=20):
    """
    Espera explícitamente a que un elemento sea visible en la página.
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    except (TimeoutException, NoSuchElementException) as e:
        print(f"❌ Error: El elemento con locator {locator} no se encontró en {timeout} segundos.")
        return None