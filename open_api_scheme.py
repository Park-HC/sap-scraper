import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import os.path
from variables import *
import json


def get_open_api_scheme(service_name, schema_name):
    service_name = service_name.upper()

    # if '-' in table_name:
    #     name_list = table_name.split('-')
    #
    #     return get_table_scheme(name_list[0])[name_list[1].upper()]
    #
    # file_root = RFC_TABLE_ROOT + table_name + '.json'
    #
    # if os.path.isfile(file_root):
    #     with open(file_root, 'r') as file:
    #         components = json.load(file)
    #         return components

    # headers = {"User-Agent": ""}
    print('https://api.sap.com/api/' + service_name + '/schema')
    # 셀레늄 필
    page = requests.get('https://api.sap.com/api/' + service_name + '/schema')
    soup = bs(page.text, "html.parser")
    pprint(soup)

    # description = soup.select('title')[0].text.replace(')', '(').split('(')[1]
    # field_dict = {'description': description}
    #
    # caption = soup.find('caption', {'class': 'text-right sapds-alv'})
    #
    # thead = caption.next_sibling.next_sibling
    # ths = thead.select('th')
    # attribute_list = [th.text.strip() if th.text and th.text.strip() else 'index' for th in ths]
    #
    # tbody = thead.next_sibling.next_sibling
    # trs = tbody.select('tr')


get_open_api_scheme('OP_API_MATERIAL_DOCUMENT_SRV', 'Document Header (for create)')
