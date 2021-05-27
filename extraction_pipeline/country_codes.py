#Extracts country codes from the agreements and saves them to a table.

import re
import os
import pandas as pd
from datetime import date

source_dir = "../world_bank_loans_txt_clean"

ccmatch = re.compile(r"(?:loan|credit agreement)\s*(?:numbers?|no[.]?)\s*(ibrd)?\s*([0-9\s]{4,5}(?:-?[0-9]?)*)[-\s]*([a-z]{2,4})")

grantmatch = re.compile(r"grant\s*number\s*(tf[0-9]*)[-\s]*([a-z]{2,4})")

id_date_regex = re.compile(r"([0-9]{4})\_(\w*)\_([0-9]{1,2})\_([0-9]*)")

file_list = os.listdir(source_dir)
bad_captures = []
ids = []
country_codes = []
dates = []
filenames = []
months = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
for f in file_list:
    if f[-3:] != 'txt':
        continue
    info = id_date_regex.match(f)
    id = info.groups()[3]
    ids.append(id)
    y = info.groups()[0]
    m = info.groups()[1]
    d = info.groups()[2]
    dates.append(date(int(y),months[m],int(d)))
    filenames.append(f)
    with open(source_dir + '/' + f,'r') as fh:
        agreement = fh.read()
        captures = ccmatch.search(agreement.lower())
        if captures is None:
            captures = grantmatch.search(agreement.lower())
            if captures is None:
                bad_captures.append(f)
                country_codes.append(None)
            else:
                country_codes.append(captures.groups()[1])
        else:
            country_codes.append(captures.groups()[2])

print("Extracting country code failed on files:")
for f in bad_captures:
  print(f)


iso_codes = pd.read_csv("wikipedia-iso-country-codes.csv")
country_code_dict = dict()
for idx, row in iso_codes.iterrows():
    code2 = str(row['Alpha-2 code']).lower()
    code3 = row['Alpha-3 code'].lower()
    country_name = row['English short name lower case']
    country_code_dict[code2] = country_name
    country_code_dict[code3] = country_name

#Some nonstandard codes extracted by hand
country_code_dict['ma'] = 'Malaysia'
country_code_dict['yu'] = 'Yugoslavia'
country_code_dict['cha'] = "China"
country_code_dict['egt'] = "Egypt"
country_code_dict['sw'] = "Swaziland"
country_code_dict['mor'] = "Morocco"
country_code_dict['waf'] = "West African Monetary Union"
country_code_dict['le'] = "Lebanon"
country_code_dict['bul'] = "Bulgaria"
country_code_dict['ko'] = "Korea"
country_code_dict['tu'] = "Turkey"
country_code_dict['yf'] = "Serbia"
country_code_dict['cob'] = "People's Republic of the Congo" #should just be Republic of the Congo, its modern name?
country_code_dict['slu'] = "Saint Lucia"
country_code_dict['ur'] = "Uruguay"
country_code_dict['zim'] = "Zimbabwe"
country_code_dict['fij'] = "Fiji"
country_code_dict['uni'] = "Nigeria"
country_code_dict['mas'] = "Mauritius"
country_code_dict['rom'] = "Romania"
country_code_dict['slo'] = "Slovenia"
country_code_dict['ld'] = "Indonesia" #ocr error
country_code_dict['nd'] = "Indonesia" #ocr error
country_code_dict['mi'] = "Moldova" #ocr error
country_code_dict['he'] = "Mexico" #ocr error
country_code_dict['oro'] = "Romania" #ocr error
country_code_dict['bot'] = "Botswana"
country_code_dict['na'] = "Namibia"
country_code_dict['bar'] = "Barbados"
country_code_dict['crg'] = "Caribbean Development Bank"
country_code_dict['ivc'] = "Cote d'Ivoire"
country_code_dict['sivc'] = "Cote d'Ivoire" #ocr error
country_code_dict['ho'] = "Honduras"
country_code_dict['sey'] = "Seychelles"
country_code_dict['cs'] = "Slovak Republic"
country_code_dict['loan'] = None #ocr/regex error
country_code_dict['dear'] = None #ocr/regex error
country_code_dict['addi'] = None #ocr/regex error
country_code_dict['cred'] = None #ocr/regex error

countries_frame = pd.DataFrame({"id": ids, "date": dates, "country_code": country_codes, "country_name": ['']*len(ids), "filename":filenames})

for i in range(len(countries_frame)):
    code = countries_frame.country_code.iloc[i]
    if code is not None:
        if code in country_code_dict:
            countries_frame.country_name.iloc[i] = country_code_dict[code]
        else:
            print("No country name for code", code, "in agreement", countries_frame.id.iloc[i])

countries_frame = countries_frame.sort_values("date",axis=0)

countries_frame.to_csv("id_date_country.csv",index=False)