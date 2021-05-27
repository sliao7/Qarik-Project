import io
from pathlib import Path
import pandas as pd
import glob
import pickle
import pycountry
import time



files = []
for filepath in glob.iglob('../world_bank_loans_txt_clean/*.txt'):
    file_txt = Path(filepath).read_text()
    file_name = filepath.split('/')[2]
    year, month, day, id_, name = file_name.split('_')
    files.append([year, month, day, id_, name, file_txt])

df = pd.DataFrame(files, columns = ['year', 'month', 'day', 'id', 'name', 'file_content'])

## Extract all countries named in the agreement text

def get_country(x):
    ans = []
    for country in pycountry.countries:
        if country.name in x:
            ans.append(country.name)
    return ans
df['named_countries'] = df['file_content'].apply(lambda x: get_country(x))


## Separate agreement into sections

sec_names = ['LOAN AGREEMENT', 'ARTICLE I', 'ARTICLE II', 'ARTICLE III', 'ARTICLE IV', 'ARTICLE V', 'ARTICLE VI',
'ARTICLE VII', 'ARTICLE VIII','ARTICLE IX','ARTICLE X','ARTICLE XI', 'SCHEDULE 1', 'SCHEDULE 2', 'SCHEDULE 3', 
             'SCHEDULE 4', 'SCHEDULE 5','SCHEDULE 6','SCHEDULE 7','SCHEDULE 8']

def get_sections(x):
    keys = ['TITLE']
    inds = [0]
    start, stop = 0, len(x)
    for sec in sec_names:
        ss = sec.split(' ')
        for name in [sec + '\n', sec + ' ', sec + '-', ss[0] + ss[1] + ' ',ss[0] + ss[1] + '\n', ss[0] + '  ' + ss[1] + ' ',ss[0] + '  ' + ss[1] + '\n']:
            if name in x:
#                 print(name)
                index = x.find(name, start, stop)
#                 print(index)
                keys.append(sec)
                inds.append(index)
                start = index
                break
#     print(keys, inds)   
    res = {}
    for i, key in enumerate(keys[:-1]):
        res[key] = (inds[i], inds[i+1])
    res[keys[-1]] = (inds[-1], stop)
    return res

def get_section(df, section):
    try:
        start, stop = df['sections'][section]

        return df['file_content'][start:stop]
    except:
        return

df['sections'] = df['file_content'].apply(get_sections)

## Get project name

title = df.apply(lambda x: get_section(x, 'TITLE'),axis=1)
df.loc[title.index,'TITLE'] =  title
df['ARTICLE II'] = df.apply(lambda x:get_section(x,'ARTICLE II'),axis=1)
def get_project_name(x):
    start, end = None, None
    if '(' in x:
        start = x.find('(')
    if ')' in x:
        end = x.find(')')
    if start and end:
        return x[start+1:end]
df['Project Name'] = df['TITLE'].apply(get_project_name)

## Extract project descriptions

def get_project_description(df):
    s1 = get_section(df, 'SCHEDULE 1')
    s2 = get_section(df, 'SCHEDULE 2')
  
    try:
        if s1 and 'description' in s1.lower():
            return s1
        elif s2 and 'description' in s2.lower():
            return s2
       
    except:
        return 

df['project_desc'] = df.apply(get_project_description, axis = 1)   


## Extract loan closing date

Months = ['January', 'February', 'March', 'April','May','June',
          'July','August','September','October','November','December']

def next_three_lines(x):
    index = 0
    for i in range(3):
        if '\n' in x:
            index += x.find('\n')
            x = x[index+1:]
    return index if index else 150

def get_closing(x,print_ = False):
    if not x:
        return None
    month_ = ''
    day_year = ''
    while 'Closing' in x:
        
        index = x.find('Closing')
        if index == -1:         
            return None
        next_index = next_three_lines(x[index:])
        piece = x[index:index+next_index]
        for month in Months:
            if month in piece:
                if print_:
                    print(piece)
                month_ = month
                index = piece.find(month) + len(month)
                break
        if not month_:
            x = x[index + next_index:]
            continue
        for i in range(index, min(index+20, len(piece))):
            if piece[i].isdigit() or piece[i] in [' ', ',', '\n']:
                day_year += piece[i]
            else:
                break
        
        if month_ and day_year:
            break
        else:
            x = x[index + next_index:]

        
    date = month_ + ' ' + day_year.strip().replace('\n', ' ').replace(',','')
    try:      
        res = pd.Series(date.split(' '), index=['closing_month', 'closing_day', 'closing_year'])
        return res
    except:
        return pd.Series(['','',''], index=['closing_month', 'closing_day', 'closing_year'])

df[['closing_month', 'closing_day', 'closing_year']] = df['file_content'].apply(get_closing)

def get_loan_length(x):
    try:
        start = int(x['year'])
        end = int(x['closing_year'].strip())
        return end - start
    except:
        return None
df['loan_length in year'] = df.apply(get_loan_length,axis=1)

df.to_pickle("sections.pkl")

