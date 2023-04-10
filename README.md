## Overview

Script to export the contents of a newspaper hosted in Islandora 7.x. Output is suitable for ingesting into another Islandora 7.x using the [Islandora Newspaper Batch](https://github.com/Islandora/islandora_newspaper_batch) module.

## Usage

Set values in `config.json`, then run:

`python newspaper_scraper.py`

## Configuration

THe configuration file is `config.json`, and looks like this

```json
{
  "hostname": "https://newspapers.lib.sfu.ca",
  "issue_list_url_path": "/soleildecolombie-4/le-soleil-de-vancouver-april-26-1968-december-21-1973",
  "issue_list_output_csv_path": "issue_list.csv",
  "output_dir": "output",
  "issue_link_pattern": "^/soleildecolombie\\-\\d.*",
  "page_link_pattern": ".*page\\-\\d*",
  "page_pid_in_url_alias_pattern": "soleildecolombie\\-\\d*",
  "datastreams": ["MODS.xml", "TN.jpeg", "OCR.asc", "JP2.jp2", "JPG.jpeg"]
}
```

* `hostname`:
* `issue_list_url_path`:
* `issue_list_output_csv_path`:
* `output_dir`:
* `issue_link_pattern`:
* `page_pid_in_url_alias_pattern`:
* `datastreams`:
* `mods_metadata_output_csv_path`:


## Installation

* Python 3.7
* requests
* BeautifulSoup

## Running multiple copies at once

Running multiple copies at once is a good way to speed up the export. They can use the same config.json file.


