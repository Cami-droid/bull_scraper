import pandas as pd
import re
import unicodedata

def sanitize_column_names(df):
    replacements = {
        ' ': '_', '/': '_', '.': '_', '-': '_',
        '(': '', ')': '', '%': 'pct'
    }
    
    def clean(col):
        # 1️⃣ Pasar a minúsculas
        col = col.lower()
        
        # 2️⃣ Eliminar acentos y tildes
        col = ''.join(
            c for c in unicodedata.normalize('NFD', col)
            if unicodedata.category(c) != 'Mn'
        )

        # 3️⃣ Aplicar reemplazos simples
        for a, b in replacements.items():
            col = col.replace(a, b)

        # 4️⃣ Sustituir cualquier cosa rara por guión bajo
        col = re.sub(r'[^a-z0-9_]', '_', col)

        # 5️⃣ Unificar guiones bajos múltiples
        col = re.sub(r'_+', '_', col).strip('_')

        # 6️⃣ Asegurarse de que no empiece con número
        if col and not col[0].isalpha():
            col = f"_{col}"

        return col or "columna_generica"

    df.columns = [clean(col) for col in df.columns]
    return df

