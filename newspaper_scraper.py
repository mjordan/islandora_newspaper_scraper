import requests
import json
import logging
from bs4 import BeautifulSoup
import os
import re
import csv
import datetime

# MODS are at /islandora/object/[pid]/datastream/MODS/download

with open("config.json", "r") as config_file:
    config = json.load(config_file)

def get_num_pages(issue_page_url):
    issue_page_response = requests.get(config['hostname'] + issue_page_url)
    soup = BeautifulSoup(issue_page_response.text, 'html.parser')
    page_pattern = '.*\-page\-'
    scraped_page_urls = soup.findAll('a', {'href': re.compile(page_pattern)})
    return len(scraped_page_urls)


csv_writer_file_handle = open(config['issue_list_output_csv_path'], 'w', encoding='utf-8')
csv_writer = csv.DictWriter(csv_writer_file_handle, fieldnames=['PID', 'issue_date', 'issue_path', 'num_pages'])
csv_writer.writeheader()

issue_list_url = config['issue_list_url_path']
issue_url = config['hostname'] + issue_list_url
issue_list_response = requests.get(issue_url)
soup = BeautifulSoup(issue_list_response.text, 'html.parser')
scraped_urls = soup.findAll('a', {'href': re.compile(r'^/ctimes\-\d.*')})
csv_output_row = dict()
for scraped_url in scraped_urls:
    csv_output_row['issue_date'] = scraped_url.get_text()
    csv_output_row['issue_path'] = scraped_url.get('href')

    # PIDs have a -, not a :, in this case.
    pid_search = re.search(r'/.*/', csv_output_row['issue_path'])
    pid = pid_search.group().strip('/')
    # Assumes that the PID doesn't contain any other -.
    pid = pid.replace('-', ':')
    csv_output_row['PID'] = pid

    if pid is not None:
        mods_url = config['hostname'] + '/islandora/object/' + pid + '/datastream/MODS/download'
        mods_response = requests.get(mods_url)
        if mods_response.status_code == 200:
            mods_download_path = os.path.join('mods', pid.replace(':', '_') + '.mods')
            f = open(mods_download_path, 'wb')
            f.write(mods_response.content)
            f.close()

    num_pages = get_num_pages(scraped_url.get('href'))
    csv_output_row['num_pages'] = num_pages

    csv_writer.writerow(csv_output_row)
    print(f"Issue info for {scraped_url.get_text()} scraped.")

csv_writer_file_handle.close()
print(f"Issue list written to {config['issue_list_output_csv_path']}.")