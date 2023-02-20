import logging
import json
from bs4 import BeautifulSoup
import os
import csv
import re
import copy


with open("config.json", "r") as config_file:
    config = json.load(config_file)

mods_dir = 'mods'
csv_columns = ['objid', 'dc:title', 'dc:title.chi', 'dc:publisher', 'dc:date', 'dc:date.chi', 'dc:language', 'dc:source', 'dc:subject', 'dc:subject.chi', 'dc:description']

csv_writer_file_handle = open(config['mods_metadata_output_csv_path'], 'w', encoding='utf-8')
csv_writer = csv.DictWriter(csv_writer_file_handle, fieldnames=csv_columns)
csv_writer.writeheader()

dir_contents = os.listdir(mods_dir)
mods_files = [f for f in dir_contents if os.path.isfile(os.path.join(mods_dir, f))]

for mods_file in mods_files:
    with open(os.path.join(mods_dir, mods_file)) as file:
        raw_mods_xml = file.read()
        raw_mods_xml_for_chinese_date = copy.copy(raw_mods_xml)

        soup = BeautifulSoup(raw_mods_xml, features="xml")

        csv_output_row = {}

        # No idea why this is returning None.
        # chi_date_issued = soup.find(re.compile(r'<dateIssued lang="chi" script="Hant">'))
        # print(chi_date_issued)
        # And no idea why this is returning an empty list.
        # dates_issued = soup.find_all('dateIssued')

        # Good ole parsing XML with regexes.
        mods = soup.find('mods')
        chi_date_issued_regex = re.search(r'<dateIssued lang="chi" script="Hant">(.*)</dateIssued>', raw_mods_xml_for_chinese_date)
        if chi_date_issued_regex is not None:
            chi_date_issued = chi_date_issued_regex.group(1)
            csv_output_row['dc:date.chi'] = chi_date_issued

        local_identifier = soup.find("identifier", {"type":"local"}).text

        date_published = local_identifier.replace('ctimes-', '')
        csv_output_row['dc:date'] = date_published

        csv_output_row['objid'] = f"BVAS.00001.{date_published.replace('-', '')}"

        publisher = soup.find("publisher").text
        csv_output_row['dc:publisher'] = f"Vancouver, British Columbia : {publisher}, {date_published[:4]}"

        csv_output_row['dc:title'] = f"Chinese Times : [{date_published}]"
        csv_output_row['dc:title.chi'] = f"大漢公報 : [{chi_date_issued}]"

        csv_output_row['dc:language'] = 'chi'
        csv_output_row['dc:source'] = "University of British Columbia Library"

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
            csv_output_row['dc:description'] = abstract.text.replace('<br>', ' ').strip()
            if not csv_output_row['dc:description'].endswith('.'):
                csv_output_row['dc:description'] = csv_output_row['dc:description'] + '.'
        else:
            csv_output_row['dc:description'] = ''

        csv_writer.writerow(csv_output_row)

csv_writer_file_handle.close()
print(f"All MODS files processed.")