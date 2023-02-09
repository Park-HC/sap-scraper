import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import os.path
from variables import *
import json
from util import td_text_parser
from table_scheme import get_table_scheme


def get_function_scheme(function_name):
    function_name = function_name.lower()
    file_root = RFC_FUNC_ROOT + function_name + '.json'

    if os.path.isfile(file_root):
        with open(file_root, 'r') as file:
            parameters = json.load(file)
            return parameters

    page = requests.get(RFC_FUNC_URL + function_name + RFC_POST_FIX)
    soup = bs(page.text, "html.parser")

    description = soup.select('title')[0].text.replace(')', '(').split('(')[1]

    elements = soup.select('table.table-sm tr')

    parameter_list = []
    api_parameter_dict = {
        'description': description,
        'Exporting': {},
        'Importing': {},
        'Tables': {}
    }

    for index, element in enumerate(elements):
        if not index:
            ths = element.select('th')
            for idx, th in enumerate(ths):
                key = th.text.strip() if th.text.strip() else ('inx' + str(idx) if idx else '')
                parameter_list.append(key)
            continue

        tds = element.select('td')
        td_data_list = [td_text_parser(td) for td in tds]

        if not td_data_list[0]:
            continue
        if not api_parameter_dict.get(td_data_list[0]):
            api_parameter_dict[td_data_list[0]] = {}
        api_parameter_dict[td_data_list[0]][td_data_list[1]] = {}
        parameter_dict = api_parameter_dict[td_data_list[0]][td_data_list[1]]

        for i, data in enumerate(td_data_list):
            if i < 2:
                continue
            if parameter_list[i] == 'Associated Type' and data:
                get_table_scheme(data)

            parameter_dict[parameter_list[i]] = data

    with open(file_root, 'w') as file:
        file.write(json.dumps(api_parameter_dict))

        return api_parameter_dict


# pprint(get_function_scheme('bapi_goodsmvt_create'))
# get_function_scheme('BAPI_USER_GET_DETAIL')
# get_function_scheme('BAPI_GOODSMVT_GETITEMS')
# get_function_scheme('BAPI_GOODSMVT_GETDETAIL')
get_function_scheme('BAPI_PO_UPDATE_HISTORY')
get_function_scheme('BAPI_PO_RESET_RELEASE')
get_function_scheme('BAPI_PO_RELEASE')
get_function_scheme('BAPI_PO_GETITEMSREL')
get_function_scheme('BAPI_PO_GETITEMS')
get_function_scheme('BAPI_PO_GETDETAIL')
get_function_scheme('BAPI_PO_GET_LIST')
get_function_scheme('BAPI_PO_CHANGE')
