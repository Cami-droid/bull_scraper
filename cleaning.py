# cleaning.py
# --------------------------------------------
# Utilidades para limpiar tablas scrapeadas de BullMarketBrokers
# Adaptado al formato argentino (punto = miles, coma = decimales)
# Conserva información de unidades (ARS, USD, %, etc.)
# --------------------------------------------

import pandas as pd
import re

# ----------------------------------------------------------
# 1️⃣ Limpieza básica de columnas numéricas con formato argentino
# ----------------------------------------------------------
def clean_numeric_column(series):
    """
    Limpia una columna numérica en formato argentino.
    - Convierte "1.234,56" → 1234.56
    - Maneja K/M como multiplicadores.
    - Si hay letras o símbolos, los deja afuera (usar split_value_and_unit si querés conservarlos).
    """
    if series.dtype != "object":
        return series

    s = series.astype(str).str.strip()

    # Multiplicadores
    s = s.str.replace("K", "e3", regex=False)
    s = s.str.replace("M", "e6", regex=False)

    # Eliminar cualquier símbolo o letra excepto dígitos, coma, punto, signo, y e/E
    s = s.str.replace(r"[^\d,.\-eE]", "", regex=True)

    # Quitar puntos de miles y cambiar coma por punto
    s = s.str.replace(".", "", regex=False)
    s = s.str.replace(",", ".", regex=False)

    return pd.to_numeric(s, errors="coerce")


# ----------------------------------------------------------
# 2️⃣ Separación de valor y unidad (ARS, USD, %, etc.)
# ----------------------------------------------------------
def split_value_and_unit(series):
    """
    Separa una columna que contiene valores con unidades como:
        "1.234,56 ARS" → valor=1234.56, unidad="ARS"
        "0,75 %" → valor=0.75, unidad="%"
        "1.200 USD" → valor=1200.0, unidad="USD"

    Devuelve un DataFrame con dos columnas: <col>_valor y <col>_unidad
    """
    s = series.astype(str).str.strip()

    # Extraer unidad (últimos caracteres alfabéticos o símbolos como %,$)
    units = s.str.extract(r"([A-Za-z%$]+)$")[0].str.upper().fillna("")

    # Quitar unidad del texto
    values = s.str.replace(r"[A-Za-z%$]+$", "", regex=True).str.strip()

    # Formato argentino → internacional
    values = values.str.replace(".", "", regex=False)
    values = values.str.replace(",", ".", regex=False)

    # Multiplicadores
    values = values.str.replace("K", "e3", regex=False)
    values = values.str.replace("M", "e6", regex=False)

    # Convertir a float
    values = pd.to_numeric(values, errors="coerce")

    return pd.DataFrame({"valor": values, "unidad": units})


# ----------------------------------------------------------
# 3️⃣ Limpieza de columna de símbolo (Ticker | Descripción)
# ----------------------------------------------------------
def clean_symbol_column(series):
    """
    Divide una columna tipo 'AE38 | Bonos del Tesoro' en dos columnas:
    - ticker: 'AE38'
    - descripcion: 'Bonos del Tesoro'
    """
    parts = series.astype(str).str.split("|", n=1, expand=True)
    df = pd.DataFrame({
        "ticker": parts[0].str.strip(),
        "descripcion": parts[1].str.strip() if parts.shape[1] > 1 else None
    })
    return df


# ----------------------------------------------------------
# 4️⃣ Limpieza completa de un DataFrame
# ----------------------------------------------------------
def clean_dataframe(df):
    """
    Aplica limpieza automática a un DataFrame de cotizaciones.
    - Detecta columnas numéricas con unidades y las separa.
    - Corrige formato argentino.
    - Divide la columna de símbolo si existe.

    Devuelve un nuevo DataFrame limpio.
    """
    df = df.copy()

    # Procesar columna de símbolo si existe
    symbol_cols = [c for c in df.columns if "símbolo" in c.lower() or "simbolo" in c.lower()]
    for col in symbol_cols:
        extra = clean_symbol_column(df[col])
        df = pd.concat([extra, df.drop(columns=[col])], axis=1)

    # Limpiar columnas con posibles unidades (ARS, USD, %, etc.)
    for col in df.columns:
        if df[col].dtype == "object":
            # Detectar si hay texto con unidades o símbolos
            if df[col].astype(str).str.contains(r"[A-Za-z%$]").any():
                cleaned = split_value_and_unit(df[col])
                df[col] = cleaned["valor"]
                df[f"{col}_unidad"] = cleaned["unidad"]
            else:
                df[col] = clean_numeric_column(df[col])

    return df


# ----------------------------------------------------------
# Ejemplo de uso
# ----------------------------------------------------------
if __name__ == "__main__":
    data = {
        "Símbolo": ["AE38 | Bonos del Tesoro", "GGAL | Grupo Financiero"],
        "Precio": ["1.234,56 ARS", "12,3 USD"],
        "Variación": ["0,75 %", "-1,2 %"],
        "Volumen": ["2,3K", "1.000"]
    }
    df = pd.DataFrame(data)
    print("Antes:")
    print(df)
    print("\nDespués:")
    print(clean_dataframe(df))
