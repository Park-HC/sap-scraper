import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint

ROOT_URL = 'https://www.sapdatasheet.org/'
FUNC_URL = 'abap/func/'
POST_FIX = '.html#'
result = {}


def get_function_scheme(function_name):
    function_name = function_name.lower()
    if function_name in result:
        return result[function_name]

    page = requests.get(ROOT_URL + FUNC_URL + function_name + POST_FIX)
    soup = bs(page.text, "html.parser")

    description = soup.select('title')[0].text.replace(')', '(').split('(')[1]

    elements = soup.select('table.table-sm tr')

    def td_text_parser(td_data):
        if td_data.text and td_data.text.strip():
            td_text = td_data.text.strip()
            return td_text
        elif td_data.select('input'):
            return True if td_data.select('input')[0].get('checked') else False
        else:
            return None

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
            parameter_dict[parameter_list[i]] = data

    result['function_name'] = api_parameter_dict

    pprint(result)
    return api_parameter_dict


get_function_scheme('bapi_goodsmvt_create')
