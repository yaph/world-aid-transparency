# -*- coding: utf-8 -*-
import re, json, yaml, geonamescache

countries = {}
re_capital = re.compile(r'<i>name: </i>([^<]+?)<br />.*?<i>geographica?l? coordinates: </i>([^<]+?)<br />')
re_coords = re.compile(r'(\d+ \d+)')
gc = geonamescache.GeonamesCache()

def get_country_by_fips(fips):
    cs = gc.get_countries().values()
    for c in cs:
        if c['fips'] == fips:
            return c

def get_coords(cstr):
    dim = cstr.strip()
    m = re_coords.match(dim)
    if m is not None:
        factor = 1
        # multiply by -1 for western and southern values
        if dim[-1] in ['S', 'W']:
            factor = -1
        return float(m.group(1).replace(' ', '.')) * factor

def write():
    with open('factbook-capitals.yaml', 'r') as f:
        cdata = yaml.load(f)

    for c in cdata:
        fips = c['xmlid'].upper()
        geodat = get_country_by_fips(fips)
        if geodat is None:
            print('No geonames data for %r' % c)
            continue

        cid = geodat['iso3']
        countries[cid] = {
            'fips': fips,
            'iso2': geodat['iso'],
            'iso': geodat['iso3'],
            'capital': geodat['capital'],
            'name': geodat['name']
        }

        # by default assign country coords and name to cope with exceptions like
        # Nauru, Tokelau and Western Sahara, that have no official capital
        if 4 == c['fieldid']:
            countries[cid]['coords'] = c['value'].split(',')
        # if capital coords can be extracted use them, because the centroid of a
        # country may be outside it, e.g. USA because of Alaska split
        else:
            match = re.search(re_capital, c['value'])
            if match is None:
                # remove from dict as coords are not known
                del countries[cid]
                print('Matching error: %r' % c)
                continue
            name = match.group(1)
            coords = match.group(2).split(',')
            countries[cid]['coords'] = coords

    # fix coordinates
    for cid, data in countries.items():
        lon = get_coords(data['coords'][1])
        lat = get_coords(data['coords'][0])
        countries[cid]['coords'] = [lon, lat]

    with open('countryinfo.js', 'w') as f:
        f.write('var countryinfo = %s;' % json.dumps(countries))
        return countries

