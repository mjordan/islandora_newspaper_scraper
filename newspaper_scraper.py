import json
import os
import re
import csv

import requests
from bs4 import BeautifulSoup

def get_page_urls(issue_page_url):
    issue_page_response = requests.get(config['hostname'] + issue_page_url)
    soup = BeautifulSoup(issue_page_response.text, 'html.parser')
    scraped_page_urls = []
    for a in soup.find_all('a', {'href': re.compile(config['page_link_pattern'])}):
        if a['href'] not in scraped_page_urls:
            scraped_page_urls.append(a['href'])

    return scraped_page_urls

with open("config.json", "r") as config_file:
    config = json.load(config_file)

if not os.path.exists(config['output_dir']):
    os.makedirs(config['output_dir'])

# As a way to restart after a crash, get a list of all the issue-level
# directories in the output directory, so we can skip issues that have
# already been successfully exported.
existing_issues = os.listdir(config['output_dir'])

csv_writer_file_handle = open(os.path.join(config['output_dir'], config['issue_list_output_csv_path']), 'w', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(csv_writer_file_handle, fieldnames=['PID', 'issue_date', 'issue_path', 'num_pages'])
csv_writer.writeheader()

issue_list_url = config['issue_list_url_path']
issue_url = config['hostname'] + issue_list_url
print(f"Scraping issue list from {config['hostname']}/{config['issue_list_url_path']}...", end='')
issue_list_response = requests.get(issue_url)
soup = BeautifulSoup(issue_list_response.text, 'html.parser')
scraped_issue_urls = soup.findAll('a', {'href': re.compile(config['issue_link_pattern'])})
print("done.")
csv_output_row = dict()
for scraped_issue_url in scraped_issue_urls:
    csv_output_row['issue_date'] = scraped_issue_url.get_text()
    csv_output_row['issue_path'] = scraped_issue_url.get('href')

    # PIDs have a -, not a :, in URL aliases.
    pid_search = re.search(r'/.*/', csv_output_row['issue_path'])
    pid = pid_search.group().strip('/')
    # Assumes that the PID doesn't contain any other -.
    pid = pid.replace('-', ':')
    csv_output_row['PID'] = pid

    page_urls = get_page_urls(scraped_issue_url.get('href'))
    if page_urls is None:
        continue

    num_pages = len(page_urls)

    issue_dc_url = config['hostname'] + '/islandora/object/' + pid + '/datastream/DC/download'
    issue_dc_response = requests.get(issue_dc_url)
    # We're parsing XML, not HTML, but html.parser works fine.
    issue_dc_soup = BeautifulSoup(issue_dc_response.content, features="html.parser")
    date_published = issue_dc_soup.find("dc:date").text

    if date_published in existing_issues:
        continue

    print(f"Exporting issue for {scraped_issue_url.get_text()} ({date_published}) ({num_pages} pages)...", end='')
    issue_path = os.path.join(config['output_dir'], date_published)

    issue_mods_url = config['hostname'] + '/islandora/object/' + pid + '/datastream/MODS/download'
    issue_mods_response = requests.get(issue_mods_url)
    issue_mods_download_path = os.path.join(os.path.join(issue_path, 'MODS.xml'))

    if not os.path.exists(issue_path):
        os.makedirs(issue_path)

    f = open(issue_mods_download_path, 'wb')
    f.write(issue_mods_response.content)
    f.close()

    # Process each page in the current issue. Assumes that URLs listed in
    # page_urls are in reading order.
    for idx, page_url in enumerate(page_urls, start=1):
        # Pad the page directory names with leading zeros.
        page_index = f'{idx:03d}'

        # PIDs have a -, not a :, in URL aliases.
        pid_search = re.search(config['page_pid_in_url_alias_pattern'], page_url)
        page_pid = pid_search.group().strip('/')
        # Assumes that the PID doesn't contain any other -.
        page_pid = page_pid.replace('-', ':')

        page_path = os.path.join(os.path.join(issue_path, page_index))
        if not os.path.exists(page_path):
            os.makedirs(page_path)

        if pid is not None:
            for datastream in config['datastreams']:
                dsid, extension = datastream.split('.')
                ds_url = config['hostname'] + '/islandora/object/' + page_pid + '/datastream/' + dsid + '/download'
                ds_response = requests.get(ds_url)
                if ds_response.status_code == 200:
                    ds_download_path = os.path.join(os.path.join(page_path, dsid + '.' + extension))
                    f = open(ds_download_path, 'wb')
                    f.write(ds_response.content)
                    f.close()

    csv_output_row['num_pages'] = num_pages

    csv_writer.writerow(csv_output_row)
    print("done.")

csv_writer_file_handle.close()
print(f"Issue list written to {config['issue_list_output_csv_path']}.")
