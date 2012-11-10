#!/bin/sh
# call with indicator ID like EN.POP.DNST   
head -n1 WDI_GDF_Data.csv | cut -d "," -f 1,45-55 > $1.csv

# use perl for problematic country names like "Bahamas, The" or "Egypt, Arab Rep."
grep "$1" WDI_GDF_Data.csv | perl -pe 's/^"([^,]+)[^"]+"/\1/' | cut -d "," -f 1,45-55 >> $1.csv
