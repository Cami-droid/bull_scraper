import pandas as pd
import re

def sanitize_column_names(df):
    replacements = {
        ' ': '_', '/': '_', '.': '_', '-': '_',
        '(': '', ')': '', '%': 'pct',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'
    }
    def clean(col):
        for a, b in replacements.items():
            col = col.replace(a, b)
        col = re.sub('_+', '_', col).strip('_').lower()
        if not col[0].isalpha():
            col = f"_{col}"
        return col or "columna_generica"

    df.columns = [clean(col) for col in df.columns]
    return df
