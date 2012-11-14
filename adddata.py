# -*- coding: utf-8 -*-
import csv, geonamescache

gc = geonamescache.GeonamesCache()
countryinfo = gc.get_countries()

def add(data, years):
    """Add tansparency and google user requests data to given dict for given years."""

    with open('google-user-data-requests.csv', 'rb') as f:
        r = csv.reader(f)
        headings = r.next()
        for row in r:
            year = row[0].split('/')[-1]
            if year not in years: continue

            iso3 = countryinfo[row[2]]['iso3']
            data[year][iso3]['userrequests'] = int(row[3])

    with open('scrape_aid_transparency_2010.csv', 'rb') as f:
        r = csv.reader(f)
        headings = r.next()
        for row in r:
            iso3 = row[0]
            if '' != iso3:
                data['2010'][iso3]['aidtransparency'] = int(row[2])
