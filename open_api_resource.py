from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from variables import *
from pprint import pprint
import os.path
import json
from open_api_scheme import get_open_api_scheme
import re


def get_table_title(table):
    title_boxes = table.find_elements(By.CLASS_NAME, 'model-title__text')
    return title_boxes[-1].text


def parse_body_block(api_body_block, api_data, api_package_name):
    # schema 탭 클릭
    schema_buttons = api_body_block.find_elements(By.CLASS_NAME, 'tablinks')

    long_description_blocks = api_body_block.find_elements(By.CLASS_NAME, 'opblock-description')
    if len(long_description_blocks):
        api_data['Long description'] = long_description_blocks[0].text

    for index, button in enumerate(schema_buttons):
        if index % 2:
            button.click()

    api_data['parameter'] = {}

    # parameter
    parameter_container = api_body_block.find_element(By.CLASS_NAME, 'parameters-container')
    trs = parameter_container.find_elements(By.TAG_NAME, 'tr')
    for tr in trs:
        tds = tr.find_elements(By.TAG_NAME, 'td')
        if not len(tds):
            continue

        td_dict = {
            'Name': "",
            'Type': "",
            'In': ""
        }

        td = tds[0]
        for attribute in td_dict:
            data_div = td.find_elements(By.CLASS_NAME, "parameter__" + attribute.lower())
            if len(data_div):
                td_dict[attribute] = data_div[0].text
        data_required = td.find_elements(By.CLASS_NAME, "required")
        if len(data_required):
            td_dict['Optional'] = False
        else:
            td_dict['Optional'] = True

        td = tds[1]
        data_div = td.find_elements(By.CLASS_NAME, "renderedMarkdown")
        if len(data_div):
            td_dict["Short text"] = data_div[0].text
        data_div = td.find_elements(By.TAG_NAME, "p")
        if len(data_div):
            if ':' in data_div[0].text:
                td_dict[data_div[0].text.split(' : ')[0]] = data_div[0].text.split(' : ')[1]
            else:
                td_dict['description'] = data_div[0].text

        if td_dict.get('Name'):
            td_dict['Name'] = td_dict['Name'].replace(' *', '')
            api_data['parameter'][td_dict['Name']] = td_dict
        if td_dict.get('In'):
            td_dict['In'] = td_dict['In'].replace('(', '').replace(')', '')

    # request_scheme
    request_bodies = api_body_block.find_elements(By.CLASS_NAME, 'opblock-section-request-body')
    if len(request_bodies):
        # request_table = request_body.find_element(By.TAG_NAME, 'table')
        request_body = request_bodies[0]
        api_data['request_table'] = {'name': get_table_title(request_body).strip(), 'is_list': False}
        request_table_dict = api_data['request_table']
        while True:
            is_table = get_open_api_scheme(api_package_name, request_table_dict['name'])
            if bool(is_table):
                break
            else:
                buttons = request_body.find_elements(By.TAG_NAME, 'button')
                if len(buttons) == 0:
                    break
                buttons[-1].click()
                request_table_dict['name'] = get_table_title(request_body).strip()
                request_table_dict['is_list'] = True

    # response_scheme
    response_bodies = api_body_block.find_elements(By.CLASS_NAME, 'responses-table')
    if len(response_bodies):
        response_body = response_bodies[0].find_element(By.CLASS_NAME, 'response')
        api_data['response_table'] = {'name': get_table_title(response_body).strip(), 'is_list': False}
        response_table_dict = api_data['response_table']
        while True:
            is_table = get_open_api_scheme(api_package_name, response_table_dict['name'])
            if bool(is_table):
                break
            else:
                buttons = response_body.find_elements(By.TAG_NAME, 'button')
                if len(buttons) == 0:
                    break
                buttons[-1].click()
                response_table_dict['name'] = get_table_title(response_body).strip()
                response_table_dict['is_list'] = True


def get_open_api_resource(api_name, api_package_name, menu_name, method):
    print('get_open_api_resource', api_name, api_package_name, menu_name, method)
    method_name = method + re.sub(r'\W', '_', api_name)
    id_name = 'operations-' + re.sub(r'\W', '_', menu_name) + '-' + method_name
    file_root = OPEN_RESOURCE_ROOT + api_package_name + '.json'

    parameters = {}
    if os.path.isfile(file_root):
        with open(file_root, 'r') as file:
            parameters = json.load(file)
            if parameters.get(method_name):
                return parameters[method_name]

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = webdriver.Chrome('chromedriver', options=options)
    # driver = webdriver.Chrome('chromedriver')
    driver.implicitly_wait(15)

    # 페이지 가져오기(이동)
    driver.get(OPEN_API_URL + api_package_name + OPEN_RESOURCE_POST_FIX)

    driver.implicitly_wait(3)

    # 메뉴 클릭
    side_menu = driver.find_element(By.ID, menu_name)
    side_menu.click()

    # api 클릭
    api = driver.find_element(By.ID, id_name)
    collapse_button = api.find_element(By.CLASS_NAME, 'opblock-summary-control')
    collapse_button.click()

    # 파라미터 블록
    api_body_block = driver.find_element(By.CLASS_NAME, "opblock-body")
    parameters[method_name] = {}

    # api 설명 등록
    api_description_blocks = api.find_elements(By.CLASS_NAME, 'opblock-summary-description')
    if len(api_description_blocks):
        api_description = api_description_blocks[0].text
        parameters[method_name]['Description'] = api_description

    driver.implicitly_wait(2)

    parse_body_block(
        api_body_block,
        parameters[method_name],
        api_package_name
    )

    time.sleep(5)
    driver.quit()

    with open(file_root, 'w') as file:
        file.write(json.dumps(parameters))

    return parameters[method_name]


get_open_api_resource(
    api_name='/A_MaterialDocumentHeader',
    api_package_name='API_MATERIAL_DOCUMENT_SRV',
    menu_name="Document Header",
    method="post",
)
get_open_api_resource(
    api_name='/A_MaterialDocumentHeader',
    api_package_name='API_MATERIAL_DOCUMENT_SRV',
    menu_name="Document Header",
    method="get",
)
get_open_api_resource(
    api_name="/A_MaterialDocumentItem(MaterialDocumentYear='{MaterialDocumentYear}',MaterialDocument='{MaterialDocument}',MaterialDocumentItem='{MaterialDocumentItem}')",
    api_package_name='API_MATERIAL_DOCUMENT_SRV',
    menu_name="Document Items",
    method="get",
)


