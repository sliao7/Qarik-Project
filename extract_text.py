import os
from pdfminer.high_level import extract_text
from multiprocessing import Pool

pdf_dir = "world_bank_loans_full_upload"
out_dir = "world_bank_loans_txt"

def process_file(f):
  path = pdf_dir + '/' + f
  year = int(f[:4])
  if path[-4:] != '.pdf':
    return ''
  if path[-7:] == 'ocr.pdf':
    return ''
  text = extract_text(path)
  #only attempt to ocr if we get less text than expected
  if len(text) < 5000:
    ocr_path = path[:-4] + "_ocr" + path[-4:]
    if not os.path.exists(ocr_path):
      cmd = 'ocrmypdf --optimize 0 --output-type pdf --force-ocr --deskew --fast-web-view 0 ' + path + ' ' + ocr_path 
      os.system(cmd)
    text = extract_text(ocr_path)
  out_path = out_dir + '/' + f[:-4] + ".txt"
  with open(out_path,'w+') as out_fd:
    out_fd.write(text)
  return out_path

if __name__ == "__main__":
  files_list = os.listdir(pdf_dir)
  with Pool(2) as p:
    out_files = p.map(process_file,files_list)