# -*- coding: utf-8 -*-
import csv, json, countryinfo, adddata, geonamescache
from collections import defaultdict
from operator import itemgetter

# used for checks
gc = geonamescache.GeonamesCache()
isos = [i['iso3'] for i in gc.get_countries().values()]

# recent years with most comprehensive datasets
# convert to strings to be able to get field position
years = [str(r) for r in range(2009, 2012)]

# dict keyed by year of lists of donation links from donor to receiver
donations = {}

# dict keyed by year containing country info
countries = defaultdict(dict)

# dict keyed by year of ranks
ranks = defaultdict(dict)
rankkeys = ['donated', 'received', 'userrequests']

# worldbank aid from donor country indicators
donors = {
    'AUS': 'DC.DAC.AUSL.CD',
    'AUT': 'DC.DAC.AUTL.CD',
    'BEL': 'DC.DAC.BELL.CD',
    'CAN': 'DC.DAC.CANL.CD',
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
    'USA': 'DC.DAC.USAL.CD'
}
# make accessible by indicator id
donors_iid = dict((v,k) for k,v in donors.items())

# selected worldbank development indicators a list of dicts with types
# that determine usage in visualization, e.g. type relation is used for 
# "By Population" and "By GDB" views, recipient for scatterplot
# rating is used for ratings like CPIA, global can be used for donors
# and recipients
indicators = [
    {'type': 'relation', 'id': 'SP.POP.TOTL', 'label': 'Population, total'},
    {'type': 'relation', 'id': 'NY.GDP.MKTP.CD', 'label': 'GDP (current US$)'},

    {'type': 'rating', 'id': 'IQ.CPA.TRAN.XQ', 'label': 'CPIA transparency, accountability, and corruption in the public sector rating (1=low to 6=high)'},

    {'type': 'global', 'id': 'SE.XPD.TOTL.GB.ZS', 'label': 'Public spending on education, total (% of government expenditure)'},
    {'type': 'global', 'id': 'SE.XPD.TOTL.GD.ZS', 'label': 'Public spending on education, total (% of GDP)'},

    {'type': 'global', 'id': 'IT.CEL.SETS.P2', 'label': 'Mobile cellular subscriptions (per 100 people)'},
    {'type': 'global', 'id': 'IT.MLT.MAIN.P2', 'label': 'Telephone lines (per 100 people)'},
    {'type': 'global', 'id': 'IT.NET.BBND.P2', 'label': 'Fixed broadband Internet subscribers (per 100 people)'},
    {'type': 'global', 'id': 'IT.NET.USER.P2', 'label': 'Internet users (per 100 people)'},

    {'type': 'global', 'id': 'MS.MIL.TOTL.TF.ZS', 'label': 'Armed forces personnel (% of total labor force)'},
    {'type': 'global', 'id': 'MS.MIL.XPND.GD.ZS', 'label': 'Military expenditure (% of GDP)'},
    {'type': 'global', 'id': 'MS.MIL.XPND.ZS', 'label': 'Military expenditure (% of central government expenditure)'},
    {'type': 'global', 'id': 'NE.IMP.GNFS.CD', 'label': 'Imports of goods and services (current US$)'},

    {'type': 'global', 'id': 'IC.REG.DURS', 'label': 'Time required to start a business (days)'},
    {'type': 'global', 'id': 'BN.CAB.XOKA.GD.ZS', 'label': 'Current account balance (% of GDP)'},
    {'type': 'global', 'id': 'DT.DOD.DECT.CD', 'label': 'External debt stocks, total (DOD, current US$)'}
]
indicator_ids = [i['id'] for i in indicators]

def skipval(val):
    if val in [None, False, 0, '']:
        return True
    return False

def proc_row(row):
    for year in years:
        if year not in headings: continue
        val = row[headings.index(year)].strip()
        if skipval(val): continue

        val = float(val)
        iso = row[1].strip()

        # only consider aid data at country level
        if iso not in isos: continue

        indicator = row[3].strip()

        if val > 0 and indicator in donors_iid:
            src = donors_iid[indicator]
            donations[year] = donations.get(year, []) + [{
                'source': donors_iid[indicator],
                'target': row[1].strip(),
                'usd': val
            }]
            # update donation totals for donors and recipients
            countries[year][iso]['received'] = countries[year][iso].get('received', 0) + val
            countries[year][src]['donated'] = countries[year][src].get('donated', 0) + val

        elif indicator in indicator_ids:
            countries[year][iso][indicator] = val

def proc_worldbank(reader):
    for row in reader:
        proc_row(row)

# main program flow
for year in years:
    countries[year] = defaultdict(dict)

#for testing use worldbank.csv
#with open('worldbank.csv', 'rb') as f:
with open('WDI_GDF_Data.csv', 'rb') as f:
    r = csv.reader(f)
    headings = r.next()
    proc_worldbank(r)

# add google transparency data
adddata.add(countries, years)

# genarate rank lists needed for initial selection of countries
for y, cdict in countries.items():
    ranks[y] = defaultdict(dict)
    for rk in rankkeys:
        ranks[y][rk] = []
        for iso, data in cdict.items():
            if rk in data:
                ranks[y][rk].append({'label': iso, 'val': data[rk]})
        # sort ranking by val
        ranks[y][rk].sort(key=itemgetter('val'))

with open('countrystats.js', 'w') as f:
    f.write('var donations = %s, countrystats = %s, indicators = %s, ranks = %s;' % (
        json.dumps(donations),
        json.dumps(countries),
        json.dumps(indicators),
        json.dumps(ranks)
    ))

# write sample csv for exploration
with open('country-stats-2010.csv', 'wb') as f:
    records = countries['2010']
    fields = ['iso3'] + indicator_ids + rankkeys

    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(fields)

    for cid, record in records.items():
        row = [cid]
        for f in fields[1:]:
            if f in record:
                val = record[f]
            else:
                val = ''
            row.append(val)
        writer.writerow(row)

# set capitals data
countryinfo.write()
