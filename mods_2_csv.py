import logging
import json
from bs4 import BeautifulSoup
import os
import csv


with open("config.json", "r") as config_file:
    config = json.load(config_file)

mods_dir = 'mods'
csv_columns = ['objid', 'dc:title', 'dc:publisher', 'dc:date', 'dc:subject', 'dc:subject.chi', 'dc:description']

csv_writer_file_handle = open(config['mods_metadata_output_csv_path'], 'w', encoding='utf-8')
csv_writer = csv.DictWriter(csv_writer_file_handle, fieldnames=csv_columns)
csv_writer.writeheader()

dir_contents = os.listdir(mods_dir)
mods_files = [f for f in dir_contents if os.path.isfile(os.path.join(mods_dir, f))]

for mods_file in mods_files:
    with open(os.path.join(mods_dir, mods_file)) as file:
        soup = BeautifulSoup(file, features="lxml")

        csv_output_row = {}

        '''
        # date_issued = soup.find("originInfo").find("dateIssued", {"keyDate": "yes"})
        print(date_issued)
        # if date_issued is not None:
            # print(date_issued)
            # keyDate = date_issued.find("keyDate")
            # if keyDate is not None:
                # print("DEBUG keyDate", keyDate)
        '''

        publisher = soup.find("publisher").text
        csv_output_row['dc:publisher'] = publisher

        local_identifier = soup.find("identifier", {"type":"local"}).text
        csv_output_row['objid'] = local_identifier

        date_published = local_identifier.replace('ctimes-', '')
        csv_output_row['dc:date'] = date_published

        csv_output_row['dc:title'] = "Chinese Times"

        subjects_en = soup.find("subject", {"authority":"lcsh"})
        subjects_en_list = []
        for subject_en in subjects_en:
            if subject_en != '\n':
                subjects_en_list.append(subject_en.text)
        subjects_en_string = '||'.join(subjects_en_list)
        csv_output_row['dc:subject'] = subjects_en_string

        subjects_chi = soup.find("subject", {"lang":"chi"})
        subjects_chi_list = []
        for subject_chi in subjects_chi:
            if subject_chi != '\n':
                subjects_chi_list.append(subject_chi.text)
        subjects_chi_string = '||'.join(subjects_chi_list)
        csv_output_row['dc:subject.chi'] = subjects_chi_string

        abstract = soup.find("abstract")
        if len(abstract.text) > 0:
            csv_output_row['dc:description'] = abstract.text.replace('<br>', ' ')
            if not csv_output_row['dc:description'].endswith('.'):
                csv_output_row['dc:description'] = csv_output_row['dc:description'] + '.'
        else:
            csv_output_row['dc:description'] = ''

        csv_writer.writerow(csv_output_row)

csv_writer_file_handle.close()
print(f"All MODS files processed.")