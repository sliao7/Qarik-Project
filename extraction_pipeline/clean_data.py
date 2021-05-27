import os
import re

source_dir = "../world_bank_loans_txt_tika"
out_dir = "../world_bank_loans_txt_clean"

public_disclosure_regex = re.compile(r"(P\s*u\s*b\s*l\s*i\s*c\s*D\s*i\s*s\s*c\s*l\s*o\s*s\s*u\s*r\s*e\s*A\s*u\s*t\s*h\s*o\s*r\s*i\s*z\s*e\s*d\s*){1,4}")
page_number_regex = re.compile(r"(\s*-\s*\d+\s*-\s*)|(\n\n *\d\d? *\n\n)")
newline_regex = re.compile(r"(\n\s*){3,}")

files = os.listdir(source_dir)

def process_file(f):
  path = os.path.join(source_dir,f)
  if path[-4:] != '.txt':
    return path, ''
  with open(path,'r') as fh:
    text = fh.read()
  text = public_disclosure_regex.sub('',text)
  text = page_number_regex.sub('\n',text)
  text = newline_regex.sub('\n\n',text)
  if len(text) < 1000 or not check_character_proportion(text):
    f = f + '.bad'
    print('tagging file as bad:', f)
  out_path = os.path.join(out_dir,f)
  with open(out_path,'w') as fh:
    fh.write(text)
  return path, out_path

def check_character_proportion(text):
  bad_chars = '~&^#'
  weird_chars = [ord(c) > 128 or c in bad_chars for c in text]
  weird_char_count = float(sum(weird_chars))
  proportion = weird_char_count/len(text)
  if proportion > 0.01:
    return False
  else:
    return True

outputs = [process_file(f) for f in files]


  
  