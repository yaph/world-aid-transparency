# -*- coding: utf-8 -*-
import re #FIXME remove
import csv, json, countryinfo, googletransparency
from collections import defaultdict
from operator import itemgetter

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

indicators = {
    # below are indicators tested for enough data
    'IT.CEL.SETS.P2': 'Mobile cellular subscriptions (per 100 people)',
    'IT.MLT.MAIN.P2': 'Telephone lines (per 100 people)',
    'IT.NET.BBND.P2': 'Fixed broadband Internet subscribers (per 100 people)',
    'IT.NET.USER.P2': 'Internet users (per 100 people)'
}

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
            countries[year][src]['donated'] = countries[year][iso].get('donated', 0) + val

        elif indicator in indicators:
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
googletransparency.add(countries, years)

# genarate rank lists needed for initial selection of countries
for y, cdict in countries.items():
    ranks[y] = defaultdict(dict)
    for rk in rankkeys:
        ranks[y][rk] = []
        for iso, data in cdict.items():
            if rk in data:
                ranks[y][rk].append({'iso': iso, 'val': data[rk]})
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
    fields = ['iso3'] + indicators.keys() + rankkeys

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
