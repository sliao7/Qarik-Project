import camelot
import os

source_dir = "../world_bank_loans_full_upload"
out_dir = "world_bank_loans_tables"

files = os.listdir(source_dir)
for i in range(10):
  f = files[i]
  if f[-4:] != '.pdf':
    continue
  tables = camelot.read_pdf(os.path.join(source_dir,f),flavor='stream',pages="2-end")
  for table in tables:
    print(table.df)

  

