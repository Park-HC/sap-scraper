import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint

ROOT_URL = 'https://www.sapdatasheet.org/'
FUNC_URL = 'abap/tabl/'
POST_FIX = '.html#'
result = {}


def get_table_scheme(table_name):
    table_name = table_name.lower()

    if '-' in table_name:
        name_list = table_name.split('-')

        pprint(get_table_scheme(name_list[0])[name_list[1].upper()])
        return get_table_scheme(name_list[0])[name_list[1].upper()]

    if table_name in result:
        return result[table_name]

    page = requests.get(ROOT_URL + FUNC_URL + table_name + POST_FIX)
    soup = bs(page.text, "html.parser")

    description = soup.select('title')[0].text.replace(')', '(').split('(')[1]
    field_dict = {'description': description}

    caption = soup.find('caption', {'class': 'text-right sapds-alv'})

    thead = caption.next_sibling.next_sibling
    ths = thead.select('th')
    attribute_list = [th.text.strip() if th.text and th.text.strip() else 'index' for th in ths]

    tbody = thead.next_sibling.next_sibling
    trs = tbody.select('tr')

    def td_text_parser(td_data):
        if td_data.text and td_data.text.strip():
            td_text = td_data.text.strip()
            return td_text
        elif td_data.select('input'):
            return True if td_data.select('input')[0].get('checked') else False
        else:
            return None

    for tr in trs:
        tds = tr.select('td')
        td_list = [td_text_parser(td) for td in tds]

        if not field_dict.get(td_list[1]):
            field_dict[td_list[1]] = {}

        for idx, td in enumerate(td_list):
            if idx < 2:
                continue

            field_dict[td_list[1]][attribute_list[idx]] = td

    result[table_name] = field_dict

    pprint(result)
    return field_dict


get_table_scheme('bapi2017_gm_head_ret')
get_table_scheme('bapi2017_gm_head_ret-mat_doc')
