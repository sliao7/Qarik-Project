import os
import io
from pathlib import Path
import pandas as pd
import glob
import pickle
import pycountry
import time
from google.cloud import language_v1
from text2int import text2int



#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'flash-surge-313319-fb0596b2676b.json'
client = language_v1.LanguageServiceClient()

df = pd.read_pickle("sections.pkl")

def get_price(text_content):
    """
    Analyzing Entities in a String

    Args:
      text_content The text content to analyze
    """

    
    if not text_content or '2.02' not in text_content:
        return None
    else:
        text_content = text_content[:text_content.find('2.02')-3]
    
    # text_content = 'California is a state.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entities(request = {'document': document, 'encoding_type': encoding_type})

    # Loop through entitites returned from the API
    ans = []
    for entity in response.entities:
        if language_v1.Entity.Type(entity.type_).name == 'PRICE':
#             return entity.name
            ans.append(entity.name)
#             print(entity.name, language_v1.Entity.Type(entity.type_).name)
    time.sleep(0.25)
    return ans

df['Amount_G'] = df['ARTICLE II'].apply(get_price)

def get_amount(x):
    if not x:
        return None
    if len(x) == 1:
        return x[0]
    elif len(x) == 2:
        return x[1]
    elif len(x) == 4:
        # loan has two parts
        return [x[1], x[3]]
    else:
        # loan has
        return x[1]

df['Amount_G_num'] = df['Amount_G'].apply(get_amount)

def get_amount(x):
    curr = ''
    num = '0'
    if x:
        for i, s in enumerate(x):
            if not s.isdigit():
                curr += s
            else:
                num = x[i:]
                break
    return pd.Series([curr.strip(), num], index=['currency', 'Amount'])

df[['currency', 'Amount']] = df['Amount_G_num'].apply(get_amount)

def get_first_amount(x):
    amt = ''
    curr = ''
    if x:
        res = text2int(x[0].lower()).strip()
        if res[0].isdigit():
            for i,s in enumerate(res):
                if s.isdigit():
                    amt += s
                else:
                    curr = res[i:].strip()
                    break
        else:
            for i,s in enumerate(res):
                if not s.isdigit():
                    curr += s
                else:
                    amt = res[i:].strip()
                    break
    return pd.Series([curr, amt], index=['currency1', 'Amount1'])
df[['currency1', 'Amount1']] = df['Amount_G'].apply(get_first_amount)

def standard_curr(x):
    if 'dollar' in x or 'usd' in x or '$' in x:
        return 'us dollar'
    if 'japan' in x:
        return 'yen'
    if 'eur' in x:
        return 'euro'
    return x.strip()
df['currency_standard'] = df['currency1'].apply(standard_curr)

def standard_amt(x):
    if not x:
        return None
    else:
        return int(x.replace(',',''))
df['amount_standard'] = df['Amount1'].apply(standard_amt)

df.to_pickle("world_bank_amounts.pickle")


