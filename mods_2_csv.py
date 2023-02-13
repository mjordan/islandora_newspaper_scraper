import logging
import json
from bs4 import BeautifulSoup
import os
import csv


with open("config.json", "r") as config_file:
    config = json.load(config_file)

mods_dir = 'mods'
csv_columns = ['PID', 'issue_date', 'issue_path', 'num_pages', 'abstract']

csv_writer_file_handle = open(config['mods_metadata_output_csv_path'], 'w', encoding='utf-8')
csv_writer = csv.DictWriter(csv_writer_file_handle, fieldnames=csv_columns)
csv_writer.writeheader()

dir_contents = os.listdir(mods_dir)
mods_files = [f for f in dir_contents if os.path.isfile(os.path.join(mods_dir, f))]

for mods_file in mods_files:
    with open(os.path.join(mods_dir, mods_file)) as file:
        soup = BeautifulSoup(file, features="lxml")

        date_issued = soup.find_all("originInfo")
        print(date_issued)
        # if date_issued is not None:
            # print(date_issued)
            # keyDate = date_issued.find("keyDate")
            # if keyDate is not None:
                # print("DEBUG keyDate", keyDate)

        abstract = soup.find("abstract")
        if len(abstract.contents) > 0:
            # print("DEBUG abstract", abstract.contents[0])
            pass




        # csv_writer.writerow(csv_output_row)

csv_writer_file_handle.close()
print(f"All MODS files processed.")