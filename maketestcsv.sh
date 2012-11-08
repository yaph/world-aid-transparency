#!/bin/sh
head -n1 WDI_GDF_Data.csv > test.csv
grep "$1" WDI_GDF_Data.csv >> test.csv
