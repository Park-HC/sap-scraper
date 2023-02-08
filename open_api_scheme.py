from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from variables import *
from pprint import pprint
import os.path
import json


def search_deep_table(element, base_dict, api_package_name):
    while True:
        buttons = element.find_elements(By.TAG_NAME, 'button')
        if len(buttons) == 0:
            return
        if '[' in buttons[-1].text:
            buttons[-1].click()
            break
        buttons[-1].click()
    table = element.find_elements(By.CLASS_NAME, 'model-title__text')
    if len(table) == 0:
        return
    base_dict["table"] = table[0].text

    get_open_api_scheme(api_package_name, table[0].text)


def parse_table(table, base_dict, api_package_name):
    trs = table.find_elements(By.TAG_NAME, "tr")

    for tr in trs:
        is_optional = 'required' not in tr.get_attribute("class")
        parameter_name = tr.find_element(By.TAG_NAME, 'td').text
        if not parameter_name.strip():
            continue
        parameter_name = parameter_name.replace('*', '')

        base_dict[parameter_name] = {"Optional": is_optional}

        short_text = tr.find_elements(By.CLASS_NAME, "renderedMarkdown")
        if short_text and len(short_text) > 0:
            base_dict[parameter_name]["Short text"] = short_text[0].text

        conditions = tr.find_elements(By.CLASS_NAME, "primitive")

        for condition in conditions:
            condition_list = condition.text.split(':')
            base_dict[parameter_name][condition_list[0].strip()] = condition_list[1].strip()

        if len(conditions) == 0:
            search_deep_table(tr, base_dict[parameter_name], api_package_name)


def get_open_api_scheme(api_package_name, scheme_name):
    if scheme_name == 'Serial Numbers':
        print('?')

    print('get_open_api_scheme', api_package_name, scheme_name)
    file_root = OPEN_SCHEME_ROOT + api_package_name.replace(' ', '_') + '.json'

    parameters = {}

    if os.path.isfile(file_root):
        with open(file_root, 'r') as file:
            parameters = json.load(file)
            if parameters.get(scheme_name):
                print('Already Written!')
                return parameters[scheme_name]

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = webdriver.Chrome('chromedriver', options=options)
    driver.implicitly_wait(15)

    # 페이지 가져오기(이동)
    driver.get(OPEN_API_URL + api_package_name + OPEN_SCHEME_POST_FIX)

    driver.implicitly_wait(1)

    # 테이블 클릭
    table_headers = driver.find_elements(By.XPATH, f"//span[text()='{scheme_name}']")
    if len(table_headers) == 0:
        print("none scheme!")
        return None
    for item in table_headers:
        try:
            item.click()
            break
        except Exception:
            continue

    tables = driver.find_elements(By.TAG_NAME, "table")
    table = tables[-1]

    tr_data = {}

    parse_table(table, tr_data, api_package_name)

    time.sleep(2)
    driver.quit()

    parameters[scheme_name] = tr_data

    with open(file_root, 'w') as file:
        file.write(json.dumps(parameters))
        return parameters[scheme_name]


# pprint(get_open_api_scheme(
#     api_package_name='API_MATERIAL_DOCUMENT_SRV',
#     scheme_name='Document Header (for create)'
# ))
#
# pprint(get_open_api_scheme(
#     api_package_name='API_MATERIAL_DOCUMENT_SRV',
#     scheme_name='Document Header'
# ))

