iso_fixes = {
    'ADO': 'AND', # Andorra
    'CHI': None, # Channel Islands
    'ZAR': 'COD', # Congo, Dem. Rep.
    'IMY': None, # Isle of Man
    'KSV': None, # Kosovo
    'ROM': 'ROU', # Romania
    'TMP': 'TLS', # Timor-Leste
    'WBG': None, # West Bank Gaza
}

def get_iso(iso):
    if iso in iso_fixes:
        return iso_fixes[iso]
    return iso
