# -*- coding: utf-8 -*-
#import numpy as np
#import pandas as pd
#df = pd.read_csv('worldbank.csv')
#aidfrom = df[df['Indicator Code'] == 'DC.DAC.DEUL.CD'][['Country Code', 'Country Name', 'Indicator Code', '2009', '2010', '2011']]

import csv, json

# list of donation links from donor to receiver
donations = []

# worldbank aid from donor country indicators
donors = {
    'AUS': 'DC.DAC.AUSL.CD',
    'AUT': 'DC.DAC.AUTL.CD',
    'BEL': 'DC.DAC.BELL.CD',
    'CAN': 'DC.DAC.CANL.CD',
    'CEC': 'DC.DAC.CECL.CD',
    'CHE': 'DC.DAC.CHEL.CD',
    'DEU': 'DC.DAC.DEUL.CD',
    'DNK': 'DC.DAC.DNKL.CD',
    'ESP': 'DC.DAC.ESPL.CD',
    'FIN': 'DC.DAC.FINL.CD',
    'FRA': 'DC.DAC.FRAL.CD',
    'GBR': 'DC.DAC.GBRL.CD',
    'GRC': 'DC.DAC.GRCL.CD',
    'IRL': 'DC.DAC.IRLL.CD',
    'ITA': 'DC.DAC.ITAL.CD',
    'JPN': 'DC.DAC.JPNL.CD',
    'KOR': 'DC.DAC.KORL.CD',
    'LUX': 'DC.DAC.LUXL.CD',
    'NLD': 'DC.DAC.NLDL.CD',
    'NOR': 'DC.DAC.NORL.CD',
    'NZL': 'DC.DAC.NZLL.CD',
    'PRT': 'DC.DAC.PRTL.CD',
    'SWE': 'DC.DAC.SWEL.CD',
#    'TOTAL': 'DC.DAC.TOTL.CD',
    'USA': 'DC.DAC.USAL.CD'
}
# make accessible by indicator id
donors_iid = dict((v,k) for k,v in donors.items())

with open('worldbank.csv', 'rb') as f:
    r = csv.reader(f)
    headings = r.next()
    for row in r:
        indicator = row[3].strip()
        amount = row[headings.index('2010')].strip()
        if amount and float(amount) > 0 and indicator in donors_iid:
            donations.append({
                'source': donors_iid[indicator],
                'target': row[1].strip(),
                'usdollars': float(amount)
            })

with open('donations.js', 'w') as f:
    f.write('var donations = %s;' % json.dumps(donations))
