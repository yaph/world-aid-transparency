# -*- coding: utf-8 -*-
import csv, geonamescache
from collections import defaultdict

gc = geonamescache.GeonamesCache()
countryinfo = gc.get_countries()

def add(data, years):
    """Add user google requests data to given dict for given years."""

    with open('google-user-data-requests.csv', 'rb') as f:
        r = csv.reader(f)
        headings = r.next()
        for row in r:
            year = row[0].split('/')[-1]
            if year not in years: continue

            iso3 = countryinfo[row[2]]['iso3']
            data[year][iso3]['userrequests'] = int(row[3])
