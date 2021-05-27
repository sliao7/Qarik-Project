import os
from pdfminer.high_level import extract_text
from tika import parser
from multiprocessing import Pool

pdf_dir = "../../world_bank_loans_full_upload"
out_dir = "../world_bank_loans_txt_tika"

def process_file(f):
  path = pdf_dir + '/' + f
  if path[-4:] != '.pdf':
    return '', False
  if path[-7:] == 'ocr.pdf':
    return '', False
  ocr = False
  #pdfminer_text = extract_text(path)
  tika_text = parser.from_file(path)['content']
  #only attempt to ocr if we get less text than expected
  if tika_text is None or len(tika_text) < 5000:
    ocr = True
    ocr_path = path[:-4] + "_ocr" + path[-4:]
    if not os.path.exists(ocr_path):
      print('ocring ' + path)
      cmd = 'ocrmypdf --optimize 0 --output-type pdf --force-ocr --deskew --fast-web-view 0 ' + path + ' ' + ocr_path 
      os.system(cmd)
    tika_text = parser.from_file(ocr_path)['content']
  out_path = out_dir + '/' + f[:-4] + ".txt"
  if os.path.exists(out_path):
    return(out_path, ocr)
  with open(out_path,'w+') as out_fd:
    out_fd.write(tika_text.strip())
  return out_path, ocr

if __name__ == "__main__":
  files_list = os.listdir(pdf_dir)
  with Pool(5) as p:
    out_files = p.map(process_file,files_list)
  ocr_files = [file for (file,ocr) in out_files if ocr == True]
  with open(out_dir + "/ocr_files.list", "w+") as f:
    for filename in ocr_files:
      f.write(filename + "\n")