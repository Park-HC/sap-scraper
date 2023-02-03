import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import os.path
from variables import *
import json
from util import td_text_parser


def get_table_scheme(table_name):
    table_name = table_name.lower()

    if '-' in table_name:
        name_list = table_name.split('-')

        return get_table_scheme(name_list[0])[name_list[1].upper()]

    file_root = RFC_TABLE_ROOT + table_name + '.json'

    if os.path.isfile(file_root):
        with open(file_root, 'r') as file:
            components = json.load(file)
            return components

    page = requests.get(RFC_TABLE_URL + table_name + RFC_POST_FIX)
    soup = bs(page.text, "html.parser")

    description = soup.select('title')[0].text.replace(')', '(').split('(')[1]
    field_dict = {'description': description}

    caption = soup.find('caption', {'class': 'text-right sapds-alv'})

    thead = caption.next_sibling.next_sibling
    ths = thead.select('th')
    attribute_list = [th.text.strip() if th.text and th.text.strip() else 'index' for th in ths]

    tbody = thead.next_sibling.next_sibling
    trs = tbody.select('tr')

    for tr in trs:
        tds = tr.select('td')
        td_list = [td_text_parser(td) for td in tds]

        if not field_dict.get(td_list[1]):
            field_dict[td_list[1]] = {}

        for idx, td in enumerate(td_list):
            if idx < 2:
                continue

            field_dict[td_list[1]][attribute_list[idx]] = td

    with open(file_root, 'w') as file:
        file.write(json.dumps(field_dict))

        return field_dict


pprint(get_table_scheme('bapi2017_gm_head_ret'))
pprint(get_table_scheme('bapi2017_gm_head_ret-mat_doc'))
